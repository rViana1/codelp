from __future__ import annotations

import os
import threading
import time
from pathlib import Path

from core.project import Project

from .filters import DefaultScanFilter, ScanFilter
from .models import ScanResult, TreeNode


class ProjectScanner:
    """
    Scans a project directory and builds its tree representation.
    """

    def __init__(self, scan_filter: ScanFilter | None = None) -> None:
        self._filter = scan_filter or DefaultScanFilter()

        self._files: list[Path] = []
        self._directories: list[Path] = []
        self._errors: list[str] = []
        self._scan_lock = threading.RLock()

    def scan(self, root: Path) -> ScanResult:
        """Serialize discovery because Scanner owns reusable traversal buffers."""
        with self._scan_lock:
            return self._scan(root)

    def _scan(self, root: Path) -> ScanResult:
        """
        Scans a project directory and returns its structure.
        """

        if not root.exists():
            raise FileNotFoundError(root)

        if not root.is_dir():
            raise NotADirectoryError(root)

        self._files.clear()
        self._directories.clear()
        self._errors.clear()

        start = time.perf_counter()

        root_node = TreeNode(
            name=root.name,
            path=root,
            is_directory=True,
        )

        self._scan_directory(root, root_node)

        duration = time.perf_counter() - start

        return ScanResult(
            root=root,
            files=self._files,
            directories=self._directories,
            tree=root_node,
            duration=duration,
            errors=self._errors,
        )

    def _serialize_tree(self, node: TreeNode) -> dict:
        """
        Serializes a TreeNode without parent references.
        """

        return {
            "name": node.name,
            "path": str(node.path),
            "is_directory": node.is_directory,
            "children": {
                name: self._serialize_tree(child)
                for name, child in node.children.items()
            },
    }

    def scan_project(self, project: Project) -> Project:
        """
        Scans a project and updates its domain state.

        This method preserves the existing scanner behaviour by reusing
        the scan() method and copying the relevant information into the
        Project aggregate.

        The scanner remains responsible for discovery, while the Project
        remains the single source of truth for domain state.
        """

        result = self.scan(project.metadata.root_path)

        project.statistics.files = len(result.files)
        
        project.statistics.scanned_files = list(result.files)

        project.statistics.directories = len(result.directories)

        project.statistics.scan_duration_seconds = result.duration

        project.root_tree = self._serialize_tree(result.tree)

        project.diagnostics.extend(result.errors)

        return project    

    def _create_node(self, path: Path) -> TreeNode:
        """
        Creates a TreeNode from a filesystem path.
        """

        return TreeNode(
            name=path.name,
            path=path,
            is_directory=path.is_dir(),
        )
        
    def _create_and_attach_node(
        self,
        path: Path,
        parent: TreeNode,
    ) -> TreeNode:
        """
        Creates a node, attaches it to its parent and returns it.
        """

        node = self._create_node(path)

        parent.add_child(node)

        return node
    
    def _register_file(self, path: Path) -> None:
        """
        Registers a file found during the scan.
        """

        self._files.append(path)

    def _register_directory(self, path: Path) -> None:
        """
        Registers a directory found during the scan.
        """

        self._directories.append(path)

    def _sorted_entries(
        self,
        directory: Path,
    ) -> list[os.DirEntry]:
        """
        Returns the directory entries sorted in a deterministic order.

        Rules:
            1. Directories first.
            2. Files second.
            3. Alphabetically (case-insensitive).
        """

        with os.scandir(directory) as entries:
            return sorted(
                entries,
                key=lambda entry: (
                    not entry.is_dir(follow_symlinks=False),
                    entry.name.lower(),
                ),
            )
     
    def _scan_directory(
        self,
        directory: Path,
        parent: TreeNode,
    ) -> None:
        """
        Recursively scans a directory and builds the project tree.
        """

        try:
            for entry in self._sorted_entries(directory):

                path = Path(entry.path)

                if entry.is_symlink():
                    continue

                if entry.is_dir(follow_symlinks=False):

                    if self._filter.should_ignore_directory(path):
                        continue

                    self._register_directory(path)

                    node = self._create_and_attach_node(path, parent)

                    self._scan_directory(path, node)

                else:

                    if self._filter.should_ignore_file(path):
                        continue

                    self._register_file(path)

                    self._create_and_attach_node(path, parent)

        except PermissionError:
            self._errors.append(f"Permission denied: {directory}")

        except OSError as ex:
            self._errors.append(str(ex))
