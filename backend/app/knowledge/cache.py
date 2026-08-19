"""Persistent, disposable cache for incremental analysis artifacts.

This cache is deliberately separate from PersistentProjectKnowledge. The
knowledge snapshot is the authoritative identity/history contract; cached
runtime artifacts are an optimization and may always be discarded.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from core.project import Project

from app.chunking.models import CodeChunk
from app.embeddings.models import Embedding, EmbeddingProviderInfo
from app.indexing.models import DependencyEntry, FileEntry, SymbolEntry
from app.parser.models import ParsedFile
from app.knowledge.models import PersistentProjectKnowledge


class CachedFileAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_id: str
    path: str
    content_hash: str
    parsed_file: ParsedFile | None = None
    index_file: FileEntry | None = None
    symbols: list[SymbolEntry] = Field(default_factory=list)
    dependencies: list[DependencyEntry] = Field(default_factory=list)
    chunks: list[CodeChunk] = Field(default_factory=list)
    embeddings: list[Embedding] = Field(default_factory=list)


class IncrementalAnalysisCache(BaseModel):
    """Reconstructable runtime results from one successful execution."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    project_id: str
    provider: EmbeddingProviderInfo
    files: list[CachedFileAnalysis] = Field(default_factory=list)


class IncrementalAnalysisCacheBuilder:
    """Build disposable artifacts from committed Project knowledge."""

    def build(
        self,
        project: Project,
        knowledge: PersistentProjectKnowledge,
        provider,
    ) -> IncrementalAnalysisCache:
        root = project.metadata.root_path
        file_id_by_path = {
            location.path: file.file_id
            for file in knowledge.files
            for location in file.locations
            if location.is_current
        }
        hash_by_path = {
            location.path: next(
                fingerprint.content_hash
                for fingerprint in file.fingerprints
                if fingerprint.is_current
            )
            for file in knowledge.files
            for location in file.locations
            if location.is_current
        }
        parsed_by_path = {
            self._relative_path(root, item.path): item
            for item in project.parser_result.files
        }
        index = project.index_result
        chunks = project.chunk_result.chunks
        embeddings = {
            item.chunk_id: item
            for item in project.embedding_result.embeddings
        }

        files = []
        for relative_path in sorted(file_id_by_path):
            index_file = index.files.get(relative_path)
            symbol_ids = set(index_file.symbols if index_file else [])
            file_chunks = [
                chunk for chunk in chunks if chunk.file_path == relative_path
            ]
            files.append(
                CachedFileAnalysis(
                    file_id=file_id_by_path[relative_path],
                    path=relative_path,
                    content_hash=hash_by_path[relative_path],
                    parsed_file=parsed_by_path.get(relative_path),
                    index_file=index_file,
                    symbols=[
                        index.symbols[symbol_id]
                        for symbol_id in sorted(symbol_ids)
                    ],
                    dependencies=[
                        item
                        for item in index.dependencies
                        if item.source_file == relative_path
                    ],
                    chunks=file_chunks,
                    embeddings=[
                        embeddings[chunk.id]
                        for chunk in file_chunks
                        if chunk.id in embeddings
                    ],
                )
            )
        return IncrementalAnalysisCache(
            project_id=knowledge.metadata.project_id,
            provider=provider.info,
            files=files,
        )

    @staticmethod
    def _relative_path(root: Path, path: Path) -> str:
        return path.resolve().relative_to(root.resolve()).as_posix()
