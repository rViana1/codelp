from __future__ import annotations

from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeNormalizer:
    """
    Creates deterministic representations
    of project knowledge snapshots.

    Does not mutate the original snapshot.
    """

    def normalize(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> PersistentProjectKnowledge:
        """
        Returns a deterministically ordered copy
        of project knowledge.
        """

        return PersistentProjectKnowledge(
            metadata=knowledge.metadata,
            files=sorted(
                knowledge.files,
                key=lambda item: item.file_id,
            ),
            symbols=sorted(
                knowledge.symbols,
                key=lambda item: item.symbol_id,
            ),
            chunks=sorted(
                knowledge.chunks,
                key=lambda item: item.chunk_id,
            ),
            embeddings=sorted(
                knowledge.embeddings,
                key=lambda item: item.chunk_id,
            ),
            retrieval=sorted(
                knowledge.retrieval,
                key=lambda item: item.chunk_id,
            ),
        )
