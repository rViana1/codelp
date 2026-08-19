"""Selective pipeline execution backed by disposable analysis artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.project import Project

from app.chunking.models import ChunkCollection
from app.embeddings.models import EmbeddingCollection
from app.indexing.models import ProjectIndex
from app.knowledge.cache import CachedFileAnalysis
from app.knowledge.planning import (
    FileAnalysisAction,
    KnowledgeAnalysisPlan,
)
from app.parser.models import ParsedProject


@dataclass(frozen=True)
class IncrementalAnalysisResult:
    """Auditable stage work performed by one pipeline execution."""

    full_analysis: bool
    analyzed_files: tuple[str, ...]
    reused_files: tuple[str, ...]
    removed_file_ids: tuple[str, ...]
    parsed_files: int
    indexed_files: int
    chunked_files: int
    embedded_chunks: int


class IncrementalAnalysisEngine:
    """Execute expensive stages only for invalidated file artifacts."""

    def analyze(
        self,
        *,
        project: Project,
        plan: KnowledgeAnalysisPlan,
        parser,
        indexer,
        chunker,
        embedding_engine,
    ) -> IncrementalAnalysisResult:
        root = project.metadata.root_path
        cache = plan.cache
        if cache is None:
            raise ValueError("Incremental analysis requires a prepared cache")
        current_paths = {
            self._relative_path(root, path): path
            for path in project.statistics.scanned_files
        }
        cache_by_file_id = {item.file_id: item for item in cache.files}

        reused = []
        changed_paths = []
        current_cached_artifacts = []
        for instruction in plan.instructions:
            relative_path = instruction.path
            path = current_paths[relative_path]
            cached = cache_by_file_id.get(instruction.file_id)
            if instruction.action == FileAnalysisAction.REUSE:
                if cached is None:
                    raise ValueError("Reuse instruction requires cached file")
                current_cached_artifacts.append(
                    self._relocate_cached_file(cached, relative_path, root)
                )
                reused.append(relative_path)
            else:
                changed_paths.append(path)

        parsed_changed = []
        parser_diagnostics = []
        for path in changed_paths:
            try:
                parsed_changed.append(parser.parse_file(path))
            except Exception as exc:
                parser_diagnostics.append(str(exc))

        cached_parsed = [
            item.parsed_file
            for item in current_cached_artifacts
            if item.parsed_file is not None
        ]
        project.parser_result = ParsedProject(
            files=sorted(
                cached_parsed + parsed_changed,
                key=lambda item: item.path.as_posix(),
            ),
            diagnostics=parser_diagnostics,
        )
        project.diagnostics.extend(parser_diagnostics)

        if parsed_changed:
            changed_parsed_project = ParsedProject(files=parsed_changed)
            changed_index = indexer.build(root, changed_parsed_project)
        else:
            changed_parsed_project = ParsedProject()
            changed_index = ProjectIndex()
        project.index_result = self._merge_index(
            current_cached_artifacts,
            changed_index,
        )
        project.diagnostics.extend(project.index_result.diagnostics)

        if changed_index.symbols:
            changed_chunks = chunker.build(
                root,
                changed_parsed_project,
                changed_index,
            )
        else:
            changed_chunks = ChunkCollection()
        cached_chunks = [
            chunk
            for item in current_cached_artifacts
            for chunk in item.chunks
        ]
        project.chunk_result = ChunkCollection(
            chunks=sorted(
                cached_chunks + changed_chunks.chunks,
                key=lambda item: item.id,
            ),
            diagnostics=list(changed_chunks.diagnostics),
        )
        project.diagnostics.extend(project.chunk_result.diagnostics)

        current_artifacts_by_id = {
            instruction.file_id: self._relocate_cached_file(
                cached,
                instruction.path,
                root,
            )
            for instruction in plan.instructions
            for cached in [cache_by_file_id.get(instruction.file_id)]
            if cached is not None
        }
        cached_chunk_state = {
            chunk.id: (chunk.content, embedding)
            for item in current_artifacts_by_id.values()
            for chunk in item.chunks
            for embedding in item.embeddings
            if embedding.chunk_id == chunk.id
        }
        provider_matches = cache.provider == embedding_engine.provider.info
        reused_embeddings = []
        chunks_to_embed = []
        for chunk in project.chunk_result.chunks:
            cached_state = cached_chunk_state.get(chunk.id)
            if (
                provider_matches
                and cached_state is not None
                and cached_state[0] == chunk.content
            ):
                reused_embeddings.append(cached_state[1])
            else:
                chunks_to_embed.append(chunk)

        if chunks_to_embed:
            generated_embeddings = embedding_engine.embed(
                ChunkCollection(chunks=chunks_to_embed)
            ).embeddings
        else:
            generated_embeddings = []
        project.embedding_result = EmbeddingCollection(
            provider=embedding_engine.provider.info,
            embeddings=sorted(
                reused_embeddings + generated_embeddings,
                key=lambda item: item.chunk_id,
            ),
        )

        changed_relative = tuple(
            sorted(self._relative_path(root, path) for path in changed_paths)
        )
        return IncrementalAnalysisResult(
            full_analysis=False,
            analyzed_files=changed_relative,
            reused_files=tuple(sorted(reused)),
            removed_file_ids=plan.removed_file_ids,
            parsed_files=len(parsed_changed),
            indexed_files=len(changed_index.files),
            chunked_files=len({chunk.file_path for chunk in changed_chunks.chunks}),
            embedded_chunks=len(chunks_to_embed),
        )

    @staticmethod
    def _merge_index(cached_files, changed_index):
        files = {
            item.index_file.path: item.index_file
            for item in cached_files
            if item.index_file is not None
        }
        files.update(changed_index.files)
        symbols = {
            symbol.id: symbol
            for item in cached_files
            for symbol in item.symbols
        }
        symbols.update(changed_index.symbols)
        dependencies = [
            dependency
            for item in cached_files
            for dependency in item.dependencies
        ] + list(changed_index.dependencies)
        return ProjectIndex(
            files=dict(sorted(files.items())),
            symbols=dict(sorted(symbols.items())),
            dependencies=sorted(
                dependencies,
                key=lambda item: (item.source_file, item.imported_module),
            ),
            diagnostics=list(changed_index.diagnostics),
        )

    @staticmethod
    def _relocate_cached_file(cached, new_path, root):
        old_prefix = f"{cached.path}::"
        new_prefix = f"{new_path}::"

        def relocate_id(value):
            if value.startswith(old_prefix):
                return new_prefix + value[len(old_prefix):]
            return value

        parsed_file = (
            cached.parsed_file.model_copy(
                update={"path": root / new_path},
                deep=True,
            )
            if cached.parsed_file is not None
            else None
        )
        symbols = [
            symbol.model_copy(
                update={"id": relocate_id(symbol.id), "file_path": new_path},
                deep=True,
            )
            for symbol in cached.symbols
        ]
        symbol_ids = [symbol.id for symbol in symbols]
        index_file = (
            cached.index_file.model_copy(
                update={"path": new_path, "symbols": symbol_ids},
                deep=True,
            )
            if cached.index_file is not None
            else None
        )
        chunks = [
            chunk.model_copy(
                update={
                    "id": relocate_id(chunk.id),
                    "symbol_id": (
                        relocate_id(chunk.symbol_id)
                        if chunk.symbol_id is not None
                        else None
                    ),
                    "file_path": new_path,
                },
                deep=True,
            )
            for chunk in cached.chunks
        ]
        embeddings = [
            embedding.model_copy(
                update={"chunk_id": relocate_id(embedding.chunk_id)},
                deep=True,
            )
            for embedding in cached.embeddings
        ]
        return CachedFileAnalysis(
            file_id=cached.file_id,
            path=new_path,
            content_hash=cached.content_hash,
            parsed_file=parsed_file,
            index_file=index_file,
            symbols=symbols,
            dependencies=[
                dependency.model_copy(
                    update={"source_file": new_path},
                    deep=True,
                )
                for dependency in cached.dependencies
            ],
            chunks=chunks,
            embeddings=embeddings,
        )

    @staticmethod
    def _relative_path(root: Path, path: Path) -> str:
        return path.resolve().relative_to(root.resolve()).as_posix()
