from pathlib import Path

from core.project import Project, ProjectMetadata

from app.pipeline import PipelineAnalyzer

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer


def create_analyzer(
    storage,
):
    lifecycle = KnowledgeLifecycleService(
        loader=KnowledgeLoader(
            storage
        ),
        restorer=KnowledgeRestorer(),
        persistence=KnowledgePersistenceService(
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


def create_project(
    path: Path,
):
    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=path,
        )
    )


def test_pipeline_persists_and_restores_project_knowledge(
    tmp_path: Path,
):

    project_path = tmp_path / "project"

    project_path.mkdir()

    (project_path / "main.py").write_text(
        "def hello():\n"
        "    return 42\n"
    )

    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )

    analyzer = create_analyzer(
        storage
    )

    first_project = create_project(
        project_path
    )

    analyzer.analyze(
        first_project
    )

    assert storage.contains(
        project_path.name
    )


    second_project = create_project(
        project_path
    )

    analyzer.analyze(
        second_project
    )

    assert any(
        "Restored knowledge"
        in diagnostic
        for diagnostic
        in second_project.diagnostics
    )
