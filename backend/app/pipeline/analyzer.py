from __future__ import annotations

from core.project import Project

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.pipeline.incremental import (
    IncrementalAnalysisEngine,
    IncrementalAnalysisResult,
)


class PipelineAnalyzer:
    """
    Orchestrates the Codelp analysis pipeline.

    This class coordinates existing application services
    without owning their internal behaviour.

    The Project aggregate remains the source of truth.
    """

    def __init__(
        self,
        scanner: ProjectScanner,
        parser: ProjectParser,
        indexer: ProjectIndexer,
        chunker: ProjectChunker,
        embedding_engine: EmbeddingEngine,
        knowledge_lifecycle: KnowledgeLifecycleService | None = None,
        lifecycle: KnowledgeLifecycleService | None = None,
        incremental_engine: IncrementalAnalysisEngine | None = None,
    ) -> None:

        self.scanner = scanner
        self.parser = parser
        self.indexer = indexer
        self.chunker = chunker
        self.embedding_engine = embedding_engine
        self.incremental_engine = (
            incremental_engine or IncrementalAnalysisEngine()
        )

        # Backwards compatibility:
        # "knowledge_lifecycle" is the official name.
        # "lifecycle" is kept as an alias for existing callers.
        self.knowledge_lifecycle = (
            knowledge_lifecycle
            if knowledge_lifecycle is not None
            else lifecycle
        )

    def analyze(
        self,
        project: Project,
    ) -> Project:
        """
        Executes the complete project analysis pipeline.
        """

        if self.knowledge_lifecycle is not None:
            project = self.knowledge_lifecycle.prepare(
                project
            )

        self.scanner.scan_project(
            project
        )

        analysis_plan = None
        if self.knowledge_lifecycle is not None:
            analysis_plan = self.knowledge_lifecycle.plan_analysis(project)

        if analysis_plan is not None and analysis_plan.incremental:
            project.incremental_analysis_result = (
                self.incremental_engine.analyze(
                    project=project,
                    plan=analysis_plan,
                    parser=self.parser,
                    indexer=self.indexer,
                    chunker=self.chunker,
                    embedding_engine=self.embedding_engine,
                )
            )
        else:
            self.parser.parse_project(project)
            self.indexer.index_project(project)
            self.chunker.chunk_project(project)
            self.embedding_engine.embed_project(project)
            relative_files = tuple(
                sorted(
                    path.resolve().relative_to(
                        project.metadata.root_path.resolve()
                    ).as_posix()
                    for path in project.statistics.scanned_files
                )
            )
            project.incremental_analysis_result = IncrementalAnalysisResult(
                full_analysis=True,
                analyzed_files=relative_files,
                reused_files=(),
                removed_file_ids=(),
                parsed_files=len(project.parser_result.files),
                indexed_files=len(project.index_result.files),
                chunked_files=len(
                    {
                        chunk.file_path
                        for chunk in project.chunk_result.chunks
                    }
                ),
                embedded_chunks=len(
                    project.embedding_result.embeddings
                ),
            )

        if self.knowledge_lifecycle is not None:
            self.knowledge_lifecycle.finalize(
                project,
                provider=self.embedding_engine.provider,
            )

        return project
