from __future__ import annotations

from app.knowledge.constants import CURRENT_KNOWLEDGE_VERSION
from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeValidator:
    """
    Validates persisted project knowledge consistency.
    """

    def validate(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:
        """
        Validates knowledge invariants.
        """

        if (
            knowledge.metadata.version
            != CURRENT_KNOWLEDGE_VERSION
        ):
            raise ValueError(
                "Unsupported knowledge version"
            )

        if not knowledge.metadata.project_id:
            raise ValueError(
                "Knowledge requires project_id"
            )

        file_ids = [
            file.file_id
            for file in knowledge.files
        ]

        if len(file_ids) != len(set(file_ids)):
            raise ValueError(
                "Duplicate file identities detected"
            )

        file_id_set = set(file_ids)

        symbol_ids = [
            symbol.symbol_id
            for symbol in knowledge.symbols
        ]

        if len(symbol_ids) != len(set(symbol_ids)):
            raise ValueError(
                "Duplicate symbol identities detected"
            )

        for symbol in knowledge.symbols:
            if symbol.file_id not in file_id_set:
                raise ValueError(
                    "Symbol references unknown file identity"
                )

        symbol_id_set = set(symbol_ids)

        chunk_ids = [
            chunk.chunk_id
            for chunk in knowledge.chunks
        ]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError(
                "Duplicate chunk identities detected"
            )

        for chunk in knowledge.chunks:
            if chunk.symbol_id not in symbol_id_set:
                raise ValueError(
                    "Chunk references unknown symbol identity"
                )