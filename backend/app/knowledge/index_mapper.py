from __future__ import annotations

from app.indexing.models import ProjectIndex

from app.knowledge.models import (
    PersistentSymbolIdentity,
)


class IndexKnowledgeMapper:
    """
    Converts project index information into persistent knowledge.

    Does not modify the index.
    Does not persist data.
    Only transforms index state.
    """

    @staticmethod
    def from_index(
        index: ProjectIndex | None,
    ) -> list[PersistentSymbolIdentity]:

        if index is None:
            return []

        symbols = []

        for symbol in sorted(
            index.symbols.values(),
            key=lambda item: item.id,
        ):

            symbols.append(
                PersistentSymbolIdentity(
                    symbol_id=symbol.id,
                    file_id=symbol.file_path,
                    name=symbol.name,
                    symbol_type=symbol.kind.value,
                )
            )

        return symbols
