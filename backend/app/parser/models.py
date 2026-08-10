from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ImportSymbol(BaseModel):
    """
    Represents an import statement.
    """

    module: str

    name: str | None = None


class FunctionSymbol(BaseModel):
    """
    Represents a top-level function.
    """

    name: str

    start_line: int

    end_line: int


class MethodSymbol(BaseModel):
    """
    Represents a class method.
    """

    name: str

    class_name: str

    start_line: int

    end_line: int


class ClassSymbol(BaseModel):
    """
    Represents a class and its methods.
    """

    name: str

    start_line: int

    end_line: int

    methods: list[MethodSymbol] = Field(default_factory=list)


class ParsedFile(BaseModel):
    """
    Structured information extracted from a source file.
    """

    path: Path

    language: str

    imports: list[ImportSymbol] = Field(default_factory=list)

    functions: list[FunctionSymbol] = Field(default_factory=list)

    classes: list[ClassSymbol] = Field(default_factory=list)

    diagnostics: list[str] = Field(default_factory=list)


class ParsedProject(BaseModel):
    """
    Collection of parsed files.
    """

    files: list[ParsedFile] = Field(default_factory=list)

    diagnostics: list[str] = Field(default_factory=list)