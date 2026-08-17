from core.project.models import Project
from core.project.persistence import ProjectPersistentState

from app.knowledge.models import (
    PersistentFileIdentity,
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
                version=previous.metadata.version,
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

        previous_files = {}

        if previous is not None:

            previous_files = {
                file.path: file
                for file in previous.files
            }

        files = []

        file_identity_map = {}

        for path in project.statistics.scanned_files:

            path_str = str(path)

            existing = previous_files.get(
                path_str
            )

            if existing:

                file_id = existing.file_id
                content_hash = existing.content_hash

            else:

                file_id = path_str

                content_hash = (
                    FileContentHasher.hash_file(path)
                    if path.exists()
                    else ""
                )

            file_identity_map[path_str] = file_id

            files.append(
                PersistentFileIdentity(
                    file_id=file_id,
                    path=path_str,
                    content_hash=content_hash,
                )
            )

        if project.index_result is not None:

            symbols = IndexKnowledgeMapper.from_index(
                project.index_result
            )

            for symbol in symbols:

                matching_file_id = None

                for file_path, file_id in file_identity_map.items():

                    if file_path.endswith(
                        symbol.file_id
                    ):
                        matching_file_id = file_id
                        break

                if matching_file_id is not None:
                    symbol.file_id = matching_file_id

        else:

            symbols = ParserKnowledgeMapper.from_parser(
                project.parser_result
            )

            for symbol in symbols:

                symbol.file_id = file_identity_map.get(
                    symbol.file_id,
                    symbol.file_id,
                )

        chunks = ChunkKnowledgeMapper.from_chunks(
            project.chunk_result
        )

        embeddings = EmbeddingKnowledgeMapper.from_embeddings(
            project.embedding_result
        )

        retrieval = RetrievalKnowledgeMapper.from_retrieval(
            project.retrieval_result
        )

        return PersistentProjectKnowledge(
            metadata=metadata,
            configuration=configuration,
            files=files,
            symbols=symbols,
            chunks=chunks,
            embeddings=embeddings,
            retrieval=retrieval,
        )