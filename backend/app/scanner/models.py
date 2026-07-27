from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    """
    Represents a node in the project tree.
    A node can be either a directory or a file.
    """

    name: str
    path: Path
    is_directory: bool

    parent: TreeNode | None = None

    children: dict[str, TreeNode] = Field(default_factory=dict)

    def add_child(self, child: TreeNode) -> None:
        """Adds a child node and sets its parent."""
        child.parent = self
        self.children[child.name] = child

    def get_child(self, name: str) -> TreeNode | None:
        """Returns a child node by name."""
        return self.children.get(name)

    @property
    def is_leaf(self) -> bool:
        """Returns True if the node has no children."""
        return not self.children


class ScanResult(BaseModel):
    """
    Result of a project scan.
    """

    root: Path

    files: list[Path] = Field(default_factory=list)

    directories: list[Path] = Field(default_factory=list)

    tree: TreeNode

    duration: float = 0.0

    errors: list[str] = Field(default_factory=list)