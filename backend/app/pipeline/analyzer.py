from __future__ import annotations

from core.project import Project

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.knowledge.lifecycle import KnowledgeLifecycleService


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
    ) -> None:

        self.scanner = scanner
        self.parser = parser
        self.indexer = indexer
        self.chunker = chunker
        self.embedding_engine = embedding_engine

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

        self.parser.parse_project(
            project
        )

        self.indexer.index_project(
            project
        )

        self.chunker.chunk_project(
            project
        )

        self.embedding_engine.embed_project(
            project
        )

        if self.knowledge_lifecycle is not None:
            self.knowledge_lifecycle.finalize(
                project
            )

        return project