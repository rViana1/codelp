from pathlib import Path

from app.scanner.constants import (
    IGNORED_DIRECTORIES,
    IGNORED_FILE_EXTENSIONS,
)
from app.scanner.filters import ScanFilter

from .models import ScannerSettings


class ConfiguredScanFilter(ScanFilter):
    """Apply scanner settings without moving policy into Scanner."""

    def __init__(self, settings: ScannerSettings) -> None:
        self.settings = settings
        self.directories = IGNORED_DIRECTORIES | settings.ignored_directories
        self.extensions = IGNORED_FILE_EXTENSIONS | settings.ignored_extensions

    def should_ignore_directory(self, directory: Path) -> bool:
        return directory.name in self.directories or (
            self.settings.ignore_hidden and directory.name.startswith(".")
        )

    def should_ignore_file(self, file: Path) -> bool:
        if self.settings.ignore_hidden and file.name.startswith("."):
            return True
        if file.suffix.lower() in self.extensions:
            return True
        try:
            return file.stat().st_size > self.settings.max_file_size_bytes
        except OSError:
            return True
