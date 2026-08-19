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


def current_hash(knowledge_file):
    return next(
        fingerprint.content_hash
        for fingerprint in knowledge_file.fingerprints
        if fingerprint.is_current
    )


def create_project(
    path: Path,
) -> Project:

    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=path,
        )
    )


def create_analyzer(
    storage,
):

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


def test_pipeline_updates_existing_knowledge(
    tmp_path: Path,
):

    project_path = tmp_path / "project"

    project_path.mkdir()

    file_path = project_path / "main.py"

    file_path.write_text(
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


    first_knowledge = storage.load(
        "project"
    )

    assert first_knowledge is not None

    first_file_id = (
        first_knowledge.files[0].file_id
    )

    first_hash = (
        current_hash(first_knowledge.files[0])
    )


    file_path.write_text(
        "def hello():\n"
        "    return 100\n"
    )


    second_project = create_project(
        project_path
    )

    analyzer.analyze(
        second_project
    )


    second_knowledge = storage.load(
        "project"
    )

    assert second_knowledge is not None

    second_file_id = (
        second_knowledge.files[0].file_id
    )

    second_hash = (
        current_hash(second_knowledge.files[0])
    )


    assert first_file_id == second_file_id

    assert first_hash != second_hash
