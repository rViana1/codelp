from __future__ import annotations

import ast

from .models import (
    ClassSymbol,
    FunctionSymbol,
    ImportSymbol,
    MethodSymbol,
)


class ImportVisitor(ast.NodeVisitor):
    """
    Collects import statements.
    """

    def __init__(self) -> None:
        self.imports: list[ImportSymbol] = []

    def visit_Import(self, node: ast.Import) -> None:

        for alias in node.names:

            self.imports.append(
                ImportSymbol(
                    module=alias.name,
                )
            )

    def visit_ImportFrom(
        self,
        node: ast.ImportFrom,
    ) -> None:

        module = node.module or ""

        for alias in node.names:

            self.imports.append(
                ImportSymbol(
                    module=module,
                    name=alias.name,
                )
            )


class FunctionVisitor(ast.NodeVisitor):
    """
    Collects only top-level functions.
    """

    def __init__(self) -> None:
        self.functions: list[FunctionSymbol] = []

    def visit_Module(self, node: ast.Module) -> None:

        for item in node.body:

            if isinstance(item, ast.FunctionDef):

                self.functions.append(
                    FunctionSymbol(
                        name=item.name,
                        start_line=item.lineno,
                        end_line=item.end_lineno,
                    )
                )


class ClassVisitor(ast.NodeVisitor):
    """
    Collects classes and their methods.
    """

    def __init__(self) -> None:
        self.classes: list[ClassSymbol] = []

    def visit_Module(self, node: ast.Module) -> None:

        for item in node.body:

            if not isinstance(item, ast.ClassDef):
                continue

            methods: list[MethodSymbol] = []

            for child in item.body:

                if isinstance(child, ast.FunctionDef):

                    methods.append(
                        MethodSymbol(
                            name=child.name,
                            class_name=item.name,
                            start_line=child.lineno,
                            end_line=child.end_lineno,
                        )
                    )

            self.classes.append(
                ClassSymbol(
                    name=item.name,
                    start_line=item.lineno,
                    end_line=item.end_lineno,
                    methods=methods,
                )
            )