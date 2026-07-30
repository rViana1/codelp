from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


"""
Indexer domain models.

These models represent the navigable and query-oriented view of a
project after parsing.

The parser extracts structural knowledge.

The indexer organises that knowledge for efficient lookup.
"""


class SymbolKind(str, Enum):
    """
    Supported symbol kinds.
    """

    FUNCTION = "function"

    CLASS = "class"

    METHOD = "method"


class SymbolEntry(BaseModel):
    """
    Represents a symbol stored in the project index.
    """

    id: str

    name: str

    kind: SymbolKind

    file_path: str

    qualified_name: str


class FileEntry(BaseModel):
    """
    Represents the indexed view of a file.
    """

    path: str

    symbols: list[str] = Field(default_factory=list)

    imports: list[str] = Field(default_factory=list)


class DependencyEntry(BaseModel):
    """
    Represents a dependency relationship discovered through imports.
    """

    source_file: str

    imported_module: str


class ProjectIndex(BaseModel):
    """
    Complete navigable index of a project.
    """

    files: dict[str, FileEntry] = Field(default_factory=dict)

    symbols: dict[str, SymbolEntry] = Field(default_factory=dict)

    dependencies: list[DependencyEntry] = Field(default_factory=list)

    diagnostics: list[str] = Field(default_factory=list)