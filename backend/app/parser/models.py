from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


"""
Parser domain models.

These models represent the structured knowledge extracted from
source files.

They are intentionally language-agnostic whenever possible so that
future parsers (JavaScript, Java, C#, etc.) can reuse the same
high-level contracts.
"""


class ImportSymbol(BaseModel):
    """
    Represents an import statement.

    Examples:
        import os
        import os as operating_system
        from pathlib import Path
    """

    module: str

    name: str | None = None

    alias: str | None = None


class FunctionSymbol(BaseModel):
    """
    Represents a top-level function.
    """

    name: str


class MethodSymbol(BaseModel):
    """
    Represents a class method.
    """

    name: str
    class_name: str


class ClassSymbol(BaseModel):
    """
    Represents a class declaration.
    """

    name: str

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
