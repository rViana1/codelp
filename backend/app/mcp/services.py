from __future__ import annotations

from core.project.models import Project


class ProjectInformationService:
    """
    Application service responsible for exposing
    public project information.

    This service does not modify the Project aggregate.
    It only translates domain information into
    external-facing representations.
    """

    def get_information(
        self,
        project: Project,
    ) -> dict[str, object]:
        return {
            "name": project.metadata.name,
            "root_path": str(project.metadata.root_path),
            "statistics": {
                "scanned_files": [
                    str(path)
                    for path in project.statistics.scanned_files
                ],
            },
        }
        
class ProjectStructureService:
    """
    Application service responsible for exposing
    public project structure information.

    This service does not modify the Project aggregate.
    It only translates domain information into
    external-facing representations.
    """

    def get_structure(
        self,
        project: Project,
    ) -> dict[str, object]:
        return {
            "root_tree": project.root_tree,
        }
from app.indexing.models import SymbolEntry


class SymbolInformationService:
    """
    Application service responsible for exposing
    public symbol information.

    This service does not modify the Project aggregate.
    It only translates index information into
    external-facing representations.
    """

    def get_symbol(
        self,
        project,
        symbol_id: str,
    ) -> dict[str, object] | None:
        if project.index_result is None:
            return None

        symbol = project.index_result.symbols.get(symbol_id)

        if symbol is None:
            return None

        return {
            "id": symbol.id,
            "name": symbol.name,
            "kind": symbol.kind.value,
            "file_path": symbol.file_path,
            "qualified_name": symbol.qualified_name,
        }
