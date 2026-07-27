from abc import ABC, abstractmethod
from pathlib import Path

from .constants import IGNORED_DIRECTORIES


class ScanFilter(ABC):
    """
    Base class for project scan filters.
    """

    @abstractmethod
    def should_ignore_directory(self, directory: Path) -> bool:
        """Return True if the directory should be ignored."""

    @abstractmethod
    def should_ignore_file(self, file: Path) -> bool:
        """Return True if the file should be ignored."""


class DefaultScanFilter(ScanFilter):
    """
    Default implementation of the scanner filter.

    This filter ignores common development directories such as
    `.git`, `.venv` and `node_modules`.

    File filtering rules are intentionally minimal at this stage and
    will be extended in future milestones.
    """

    def should_ignore_directory(self, directory: Path) -> bool:
        return directory.name in IGNORED_DIRECTORIES

    def should_ignore_file(self, file: Path) -> bool:
        return False