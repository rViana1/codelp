from pathlib import Path


class ParserError(Exception):
    """
    Base exception for parser errors.
    """


class UnsupportedLanguageError(ParserError):
    """
    Raised when attempting to parse an unsupported language.
    """

    def __init__(self, path: Path, language: str) -> None:
        super().__init__(f"Unsupported language '{language}' for file: {path}")


class PythonSyntaxError(ParserError):
    """
    Raised when a Python file contains invalid syntax.
    """

    def __init__(self, path: Path, message: str) -> None:
        super().__init__(f"Syntax error in {path}: {message}")