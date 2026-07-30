from __future__ import annotations

from pathlib import Path

from core.project import Project

from app.parser.models import ParsedProject

from .builders import (
    class_id,
    function_id,
    method_id,
    relative_file_path,
)
from .models import (
    DependencyEntry,
    FileEntry,
    ProjectIndex,
    SymbolEntry,
    SymbolKind,
)


class ProjectIndexer:
    """
    Builds navigable indexes from ParsedProject.
    """

    def build(
        self,
        project_root: Path,
        parsed_project: ParsedProject,
    ) -> ProjectIndex:
        """
        Builds a ProjectIndex from parsed files.
        """

        index = ProjectIndex()

        for parsed_file in sorted(
            parsed_project.files,
            key=lambda f: f.path.as_posix(),
        ):

            relative_path = relative_file_path(
                project_root,
                parsed_file.path,
            )

            file_entry = FileEntry(path=relative_path)

            # Functions

            for function in sorted(
                parsed_file.functions,
                key=lambda f: f.name,
            ):

                symbol_id = function_id(relative_path, function)

                index.symbols[symbol_id] = SymbolEntry(
                    id=symbol_id,
                    name=function.name,
                    kind=SymbolKind.FUNCTION,
                    file_path=relative_path,
                    qualified_name=function.name,
                )

                file_entry.symbols.append(symbol_id)

            # Classes

            for cls in sorted(
                parsed_file.classes,
                key=lambda c: c.name,
            ):

                class_symbol_id = class_id(relative_path, cls)

                index.symbols[class_symbol_id] = SymbolEntry(
                    id=class_symbol_id,
                    name=cls.name,
                    kind=SymbolKind.CLASS,
                    file_path=relative_path,
                    qualified_name=cls.name,
                )

                file_entry.symbols.append(class_symbol_id)

                # Methods

                for method in sorted(
                    cls.methods,
                    key=lambda m: m.name,
                ):

                    method_symbol_id = method_id(relative_path, method)

                    index.symbols[method_symbol_id] = SymbolEntry(
                        id=method_symbol_id,
                        name=method.name,
                        kind=SymbolKind.METHOD,
                        file_path=relative_path,
                        qualified_name=f"{cls.name}.{method.name}",
                    )

                    file_entry.symbols.append(method_symbol_id)

            # Dependencies

            for import_symbol in sorted(
                parsed_file.imports,
                key=lambda i: (i.module, i.name or ""),
            ):

                file_entry.imports.append(import_symbol.module)

                index.dependencies.append(
                    DependencyEntry(
                        source_file=relative_path,
                        imported_module=import_symbol.module,
                    )
                )

            index.files[relative_path] = file_entry

        return index

    def index_project(self, project: Project) -> Project:
        """
        Builds indexes for the project and updates domain state.
        """

        if project.parser_result is None:
            project.diagnostics.append(
                "Project has no parser_result"
            )
            return project

        project.index_result = self.build(
            project.metadata.root_path,
            project.parser_result,
        )

        project.diagnostics.extend(
            project.index_result.diagnostics
        )

        return project
