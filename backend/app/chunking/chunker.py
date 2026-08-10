from __future__ import annotations

from pathlib import Path

from core.project import Project

from app.indexing.models import ProjectIndex, SymbolKind
from app.parser.models import ParsedProject

from .builders import (
    build_class_chunk,
    build_function_chunk,
    build_method_chunk,
)
from .extractors import extract_source
from .models import ChunkCollection


class ProjectChunker:
    """
    Builds deterministic semantic chunks from parsed and indexed
    project knowledge.
    """

    def build(
        self,
        project_root: Path,
        parsed_project: ParsedProject,
        index_result: ProjectIndex,
    ) -> ChunkCollection:
        """
        Builds semantic chunks from parsed and indexed project
        knowledge.
        """

        collection = ChunkCollection()

        parsed_files = {
            parsed_file.path: parsed_file
            for parsed_file in parsed_project.files
        }

        for symbol_id, symbol in index_result.symbols.items():

            file_path = project_root / symbol.file_path

            parsed_file = parsed_files.get(file_path)

            if parsed_file is None:
                collection.diagnostics.append(
                    f"Missing parsed file for {symbol.file_path}"
                )
                continue

            if symbol.kind == SymbolKind.FUNCTION:

                function = next(
                    (
                        f
                        for f in parsed_file.functions
                        if f.name == symbol.name
                    ),
                    None,
                )

                if function is None:
                    continue

                content = extract_source(
                    file_path,
                    function.start_line,
                    function.end_line,
                )

                collection.chunks.append(
                    build_function_chunk(
                        chunk_id=symbol.id,
                        file_path=symbol.file_path,
                        content=content,
                        start_line=function.start_line,
                        end_line=function.end_line,
                    )
                )

            elif symbol.kind == SymbolKind.CLASS:

                cls = next(
                    (
                        c
                        for c in parsed_file.classes
                        if c.name == symbol.name
                    ),
                    None,
                )

                if cls is None:
                    continue

                content = extract_source(
                    file_path,
                    cls.start_line,
                    cls.end_line,
                )

                collection.chunks.append(
                    build_class_chunk(
                        chunk_id=symbol.id,
                        file_path=symbol.file_path,
                        content=content,
                        start_line=cls.start_line,
                        end_line=cls.end_line,
                    )
                )

            elif symbol.kind == SymbolKind.METHOD:

                target_class_name, _, method_name = (
                    symbol.qualified_name.partition(".")
                )

                target_method = None

                for cls in parsed_file.classes:

                    if cls.name != target_class_name:
                        continue

                    target_method = next(
                        (
                            m
                            for m in cls.methods
                            if m.name == method_name
                        ),
                        None,
                    )

                    if target_method is not None:
                        break

                if target_method is None:
                    continue

                content = extract_source(
                    file_path,
                    target_method.start_line,
                    target_method.end_line,
                )

                collection.chunks.append(
                    build_method_chunk(
                        chunk_id=symbol.id,
                        file_path=symbol.file_path,
                        content=content,
                        start_line=target_method.start_line,
                        end_line=target_method.end_line,
                    )
                )

        return collection

    def chunk_project(self, project: Project) -> Project:
        """
        Builds chunks for the project and updates domain state.
        """

        if project.parser_result is None:
            project.diagnostics.append(
                "Project has no parser_result"
            )
            return project

        if project.index_result is None:
            project.diagnostics.append(
                "Project has no index_result"
            )
            return project

        project.chunk_result = self.build(
            project.metadata.root_path,
            project.parser_result,
            project.index_result,
        )

        project.diagnostics.extend(
            project.chunk_result.diagnostics
        )

        return project