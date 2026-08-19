from __future__ import annotations

import hashlib

from app.chunking.models import ChunkCollection

from app.knowledge.models import (
    PersistentChunkIdentity,
)
from app.knowledge.identity import deterministic_identity


class ChunkKnowledgeMapper:
    """
    Converts chunking results into persistent knowledge.

    Does not modify chunk data.
    Does not persist data.
    """

    @staticmethod
    def from_chunks(
        chunks: ChunkCollection | None,
        symbol_identity_by_source: dict[str, str] | None = None,
        previous_chunks: list[PersistentChunkIdentity] | None = None,
        project_id: str = "",
    ) -> list[PersistentChunkIdentity]:

        if chunks is None:
            return []

        result = []
        symbol_identity_by_source = (
            symbol_identity_by_source or {}
        )
        previous_by_symbol: dict[
            str,
            list[PersistentChunkIdentity],
        ] = {}
        for previous in previous_chunks or []:
            previous_by_symbol.setdefault(
                previous.symbol_id,
                [],
            ).append(previous)

        for chunk in sorted(
            chunks.chunks,
            key=lambda item: item.id,
        ):

            symbol_id = symbol_identity_by_source.get(
                chunk.symbol_id or "",
                chunk.symbol_id or "",
            )
            candidates = previous_by_symbol.get(
                symbol_id,
                [],
            )
            chunk_id = (
                candidates[0].chunk_id
                if len(candidates) == 1
                else deterministic_identity(
                    project_id,
                    "chunk",
                    symbol_id,
                    chunk.kind.value,
                )
            )

            result.append(
                PersistentChunkIdentity(
                    chunk_id=chunk_id,
                    symbol_id=symbol_id,
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
