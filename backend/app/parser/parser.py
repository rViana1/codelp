from __future__ import annotations

from pathlib import Path

from core.project import Project

from .detector import LanguageDetector
from .exceptions import UnsupportedLanguageError
from .models import ParsedFile, ParsedProject
from .python_parser import PythonParser


class ProjectParser:
    """
    Orchestrates file and project parsing.
    """

    def __init__(self) -> None:
        self._detector = LanguageDetector()
        self._python_parser = PythonParser()

    def parse_file(self, path: Path) -> ParsedFile:
        """
        Parses a single source file.
        """

        language = self._detector.detect(path)

        if language == "python":
            return self._python_parser.parse(path)

        raise UnsupportedLanguageError(path, language)

    def parse_project(self, project: Project) -> Project:
        """
        Parses all supported files discovered in the project.
        """

        parsed_files: list[ParsedFile] = []
        diagnostics: list[str] = []

        for file_path in project.statistics.scanned_files:

            language = self._detector.detect(file_path)

            if language == "unknown":
                diagnostics.append(f"Unsupported language: {file_path}")
                continue

            try:
                parsed_files.append(self.parse_file(file_path))

            except Exception as ex:
                diagnostics.append(str(ex))

        project.parser_result = ParsedProject(
            files=parsed_files,
            diagnostics=diagnostics,
        )

        project.diagnostics.extend(diagnostics)

        return project