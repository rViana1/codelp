from pathlib import Path

import pytest

from core.project import Project, ProjectMetadata

from app.pipeline import PipelineAnalyzer

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.exceptions import KnowledgeWriteError


class FailingStorage:

    def load(
        self,
        project_id,
    ):
        return None


    def save(
        self,
        knowledge,
    ):
        raise KnowledgeWriteError(
            "Storage unavailable"
        )


    def exists(
        self,
        project_id,
    ):
        return False


    def delete(
        self,
        project_id,
    ):
        pass


def create_project(
    path: Path,
):

    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=path,
        )
    )


def create_analyzer():

    storage = FailingStorage()

    lifecycle = KnowledgeLifecycleService(
        KnowledgeLoader(
            storage
        ),
        KnowledgeRestorer(),
        KnowledgePersistenceService(
            KnowledgeBuilder(),
            storage,
        ),
    )

    return PipelineAnalyzer(
        scanner=ProjectScanner(),
        parser=ProjectParser(),
        indexer=ProjectIndexer(),
        chunker=ProjectChunker(),
        embedding_engine=EmbeddingEngine(
            FakeEmbeddingProvider(
                dimensions=5
            )
        ),
        knowledge_lifecycle=lifecycle,
    )


def test_persistence_failure_does_not_corrupt_project_state(
    tmp_path,
):

    file = tmp_path / "main.py"

    file.write_text(
        "def hello():\n"
        "    return 42\n"
    )

    project = create_project(
        tmp_path
    )

    analyzer = create_analyzer()

    with pytest.raises(
        KnowledgeWriteError
    ):
        analyzer.analyze(
            project
        )


    assert project.statistics.files == 1

    assert project.parser_result is not None

    assert project.index_result is not None

    assert project.chunk_result is not None

    assert project.embedding_result is not None
