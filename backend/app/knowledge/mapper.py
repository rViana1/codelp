from datetime import datetime, timezone
from pathlib import Path

from core.project.models import Project
from core.project.persistence import ProjectPersistentState

from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectConfiguration,
    PersistentProjectKnowledge,
)

from app.knowledge.parser_mapper import ParserKnowledgeMapper
from app.knowledge.index_mapper import IndexKnowledgeMapper
from app.knowledge.chunk_mapper import ChunkKnowledgeMapper
from app.knowledge.embedding_mapper import EmbeddingKnowledgeMapper
from app.knowledge.retrieval_mapper import RetrievalKnowledgeMapper
from app.knowledge.hash import FileContentHasher
from app.knowledge.identity import FileObservation
from app.knowledge.tracking import IdentityTrackingEngine
from app.knowledge.planning import KnowledgeAnalysisPlan


class KnowledgeMapper:
    """
    Converts Project domain state into persistent project knowledge.

    Responsibility
    --------------
    Creates a persistence representation from the Project aggregate.

    Boundaries
    ----------
    - Does not modify Project.
    - Does not persist data.
    - Does not own storage lifecycle.

    The mapper only transforms domain state into persistent knowledge.
    """

    @staticmethod
    def from_project(
        project: Project,
        project_id: str | None = None,
        previous: PersistentProjectKnowledge | None = None,
    ) -> PersistentProjectKnowledge:
        """
        Build persistent knowledge from a Project instance.
        """

        persistent_state = ProjectPersistentState.from_project(
            project
        )

        if project_id is None:
            project_id = persistent_state.metadata.name

        if previous is not None:

            metadata = PersistentKnowledgeMetadata(
                project_id=project_id,
                created_at=previous.metadata.created_at,
                updated_at=PersistentKnowledgeMetadata.model_fields[
                    "updated_at"
                ].default_factory(),
            )

        else:

            metadata = PersistentKnowledgeMetadata(
                project_id=project_id
            )

        configuration = PersistentProjectConfiguration(
            follow_symlinks=project.configuration.follow_symlinks,
            ignore_hidden=project.configuration.ignore_hidden,
            max_file_size_bytes=project.configuration.max_file_size_bytes,
            ignored_directories=set(
                project.configuration.ignored_directories
            ),
            ignored_extensions=set(
                project.configuration.ignored_extensions
            ),
        )

        if project.index_result is not None:

            source_symbols = IndexKnowledgeMapper.from_index(
                project.index_result
            )

        else:
            source_symbols = ParserKnowledgeMapper.from_parser(
                project.parser_result
            )

        for symbol in source_symbols:
            symbol.file_id = KnowledgeMapper._relative_path(
                project.metadata.root_path,
                Path(symbol.file_id),
            )

        identity_tracker = IdentityTrackingEngine()
        analysis_plan = project.knowledge_analysis_plan
        if (
            isinstance(analysis_plan, KnowledgeAnalysisPlan)
            and analysis_plan.project_id == project_id
        ):
            files = list(analysis_plan.resolved_files)
            symbols, source_symbol_identity_map = (
                identity_tracker.track_symbols(
                    resolved_files=files,
                    source_symbols=source_symbols,
                    previous_symbols=(
                        previous.symbols if previous is not None else []
                    ),
                    project_id=project_id,
                )
            )
            symbols = sorted(
                symbols,
                key=lambda symbol: symbol.symbol_id,
            )
        else:
            now = datetime.now(timezone.utc)
            observations = [
                FileObservation(
                    path=KnowledgeMapper._relative_path(
                        project.metadata.root_path,
                        path,
                    ),
                    content_hash=(
                        FileContentHasher.hash_file(path)
                        if path.exists()
                        else ""
                    ),
                    size_bytes=(
                        path.stat().st_size
                        if path.exists()
                        else 0
                    ),
                )
                for path in project.statistics.scanned_files
            ]
            tracking = identity_tracker.track(
                project_id=project_id,
                observations=observations,
                source_symbols=source_symbols,
                previous_files=(
                    previous.files if previous is not None else []
                ),
                previous_symbols=(
                    previous.symbols if previous is not None else []
                ),
                previous_chunks=(
                    previous.chunks if previous is not None else []
                ),
                previous_embeddings=(
                    previous.embeddings if previous is not None else []
                ),
                now=now,
            )
            files = list(tracking.files)
            symbols = list(tracking.symbols)
            source_symbol_identity_map = (
                tracking.source_symbol_identity_map
            )

        chunks = ChunkKnowledgeMapper.from_chunks(
            project.chunk_result,
            source_symbol_identity_map,
            previous.chunks if previous is not None else [],
            project_id,
        )

        source_chunk_identity_map = {
            source.id: persistent.chunk_id
            for source, persistent in zip(
                sorted(
                    project.chunk_result.chunks
                    if project.chunk_result is not None
                    else [],
                    key=lambda item: item.id,
                ),
                chunks,
            )
        }

        embeddings = EmbeddingKnowledgeMapper.from_embeddings(
            project.embedding_result,
            source_chunk_identity_map,
        )

        retrieval = RetrievalKnowledgeMapper.from_retrieval(
            project.retrieval_result,
            source_chunk_identity_map,
        )

        file_identity_by_path = {
            location.path: file.file_id
            for file in files
            for location in file.locations
            if location.is_current
        }
        imports = IndexKnowledgeMapper.imports_from_index(
            project.index_result,
            file_identity_by_path,
            project_id,
        )

        return PersistentProjectKnowledge(
            metadata=metadata,
            configuration=configuration,
            files=files,
            symbols=symbols,
            chunks=chunks,
            embeddings=embeddings,
            retrieval=retrieval,
            imports=imports,
        )

    @staticmethod
    def _relative_path(
        project_root: Path,
        path: Path,
    ) -> str:
        """Return the canonical project-relative persistence path."""

        try:
            return path.resolve().relative_to(
                project_root.resolve()
            ).as_posix()
        except ValueError:
            return path.as_posix()
