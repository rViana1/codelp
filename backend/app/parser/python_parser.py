from __future__ import annotations

import ast
from pathlib import Path

from .exceptions import PythonSyntaxError
from .models import ParsedFile
from .visitors import ClassVisitor, FunctionVisitor, ImportVisitor


class PythonParser:
    """
    Parses Python source files using the built-in AST module.
    """

    def parse(self, path: Path) -> ParsedFile:
        """
        Parses a Python file and returns structured information.
        """

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)

        except SyntaxError as ex:
            raise PythonSyntaxError(path, ex.msg) from ex

        import_visitor = ImportVisitor()
        import_visitor.visit(tree)

        function_visitor = FunctionVisitor()
        function_visitor.visit(tree)

        class_visitor = ClassVisitor()
        class_visitor.visit(tree)

        return ParsedFile(
            path=path,
            language="python",
            imports=import_visitor.imports,
            functions=function_visitor.functions,
            classes=class_visitor.classes,
        )