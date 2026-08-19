from __future__ import annotations

from app.indexing.models import ProjectIndex

from app.knowledge.models import (
    PersistentImportReference,
    PersistentSymbolIdentity,
)
from app.knowledge.identity import deterministic_identity


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

    @staticmethod
    def imports_from_index(
        index: ProjectIndex | None,
        file_identity_by_path: dict[str, str],
        project_id: str,
    ) -> list[PersistentImportReference]:
        if index is None:
            return []

        references = {}
        for dependency in sorted(
            index.dependencies,
            key=lambda item: (item.source_file, item.imported_module),
        ):
            source_file_id = file_identity_by_path.get(
                dependency.source_file
            )
            if source_file_id is None or not dependency.imported_module:
                continue
            key = (source_file_id, dependency.imported_module)
            references[key] = PersistentImportReference(
                import_id=deterministic_identity(
                    project_id,
                    "import",
                    source_file_id,
                    dependency.imported_module,
                ),
                source_file_id=source_file_id,
                imported_module=dependency.imported_module,
                target_file_id=IndexKnowledgeMapper._resolve_target_file(
                    dependency.imported_module,
                    file_identity_by_path,
                ),
            )
        return [references[key] for key in sorted(references)]

    @staticmethod
    def _resolve_target_file(
        imported_module: str,
        file_identity_by_path: dict[str, str],
    ) -> str | None:
        module_path = imported_module.lstrip(".").replace(".", "/")
        if not module_path:
            return None
        expected = {
            f"{module_path}.py",
            f"{module_path}/__init__.py",
        }
        candidates = {
            file_id
            for path, file_id in file_identity_by_path.items()
            if path in expected
            or any(path.endswith(f"/{suffix}") for suffix in expected)
        }
        return next(iter(candidates)) if len(candidates) == 1 else None
