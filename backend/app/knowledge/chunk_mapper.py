from __future__ import annotations

import hashlib

from app.chunking.models import ChunkCollection

from app.knowledge.models import (
    PersistentChunkIdentity,
)


class ChunkKnowledgeMapper:
    """
    Converts chunking results into persistent knowledge.

    Does not modify chunk data.
    Does not persist data.
    """

    @staticmethod
    def from_chunks(
        chunks: ChunkCollection | None,
    ) -> list[PersistentChunkIdentity]:

        if chunks is None:
            return []

        result = []

        for chunk in sorted(
            chunks.chunks,
            key=lambda item: item.id,
        ):

            result.append(
                PersistentChunkIdentity(
                    chunk_id=chunk.id,
                    symbol_id=chunk.symbol_id or "",
                    content_hash=ChunkKnowledgeMapper._hash_content(
                        chunk.content
                    ),
                )
            )

        return result


    @staticmethod
    def _hash_content(
        content: str,
    ) -> str:

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()
