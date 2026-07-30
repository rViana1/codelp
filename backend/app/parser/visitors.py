import ast

from .models import (
    ClassSymbol,
    FunctionSymbol,
    ImportSymbol,
    MethodSymbol,
)


class ImportVisitor(ast.NodeVisitor):
    """
    Extracts import statements.
    """

    def __init__(self) -> None:
        self.imports: list[ImportSymbol] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportSymbol(
                    module=alias.name,
                    alias=alias.asname,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""

        for alias in node.names:
            self.imports.append(
                ImportSymbol(
                    module=module,
                    name=alias.name,
                    alias=alias.asname,
                )
            )


class FunctionVisitor(ast.NodeVisitor):
    """
    Extracts only top-level functions.
    """

    def __init__(self) -> None:
        self.functions: list[FunctionSymbol] = []

    def visit_Module(self, node: ast.Module) -> None:
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.functions.append(FunctionSymbol(name=item.name))

class ClassVisitor(ast.NodeVisitor):
    """
    Extracts classes and their methods.
    """

    def __init__(self) -> None:
        self.classes: list[ClassSymbol] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        methods: list[MethodSymbol] = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(
                    MethodSymbol(
                        name=item.name,
                        class_name=node.name,
                    )
                )

        self.classes.append(
            ClassSymbol(
                name=node.name,
                methods=methods,
            )
        )