from __future__ import annotations

from core.project import (
    Project,
    ProjectChunkKnowledge,
    ProjectEmbeddingKnowledge,
    ProjectFileKnowledge,
    ProjectKnowledgeState,
    ProjectRetrievalKnowledge,
    ProjectSymbolKnowledge,
)
from core.project.models import ProjectConfiguration

from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeRestorer:
    """
    Restores persistent knowledge into a Project aggregate.

    Responsible only for translating persisted state
    back into domain state.

    Does not access storage.
    Does not persist data.
    """

    def restore(
        self,
        project: Project,
        knowledge: PersistentProjectKnowledge,
    ) -> Project:
        """
        Restores compatible knowledge into the project.
        """

        project.configuration = ProjectConfiguration(
            follow_symlinks=knowledge.configuration.follow_symlinks,
            ignore_hidden=knowledge.configuration.ignore_hidden,
            max_file_size_bytes=knowledge.configuration.max_file_size_bytes,
            ignored_directories=set(
                knowledge.configuration.ignored_directories
            ),
            ignored_extensions=set(
                knowledge.configuration.ignored_extensions
            ),
        )

        project.knowledge_state = ProjectKnowledgeState(
            files=[
                ProjectFileKnowledge(
                    file_id=file.file_id,
                    path=file.path,
                    content_hash=file.content_hash,
                )
                for file in knowledge.files
            ],
            symbols=[
                ProjectSymbolKnowledge(
                    symbol_id=symbol.symbol_id,
                    file_id=symbol.file_id,
                    name=symbol.name,
                    symbol_type=symbol.symbol_type,
                )
                for symbol in knowledge.symbols
            ],
            chunks=[
                ProjectChunkKnowledge(
                    chunk_id=chunk.chunk_id,
                    symbol_id=chunk.symbol_id,
                    content_hash=chunk.content_hash,
                )
                for chunk in knowledge.chunks
            ],
            embeddings=[
                ProjectEmbeddingKnowledge(
                    chunk_id=embedding.chunk_id,
                    provider=embedding.provider,
                    embedding_hash=embedding.embedding_hash,
                )
                for embedding in knowledge.embeddings
            ],
            retrieval=[
                ProjectRetrievalKnowledge(
                    chunk_id=item.chunk_id,
                    query_hash=item.query_hash,
                    score=item.score,
                )
                for item in knowledge.retrieval
            ],
        )

        project.diagnostics.append(
            f"Restored knowledge for project "
            f"{knowledge.metadata.project_id}"
        )

        return project