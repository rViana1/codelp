from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.file_storage import FileKnowledgeStorage
from app.pipeline import PipelineAnalyzer


from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider

from app.knowledge.loader import KnowledgeLoader
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.lifecycle import KnowledgeLifecycleService


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
        lifecycle=lifecycle,
    )


def test_pipeline_preserves_knowledge_identity_after_restore(
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

    assert len(first_knowledge.files) == 1
    assert len(first_knowledge.symbols) == 1
    assert len(first_knowledge.chunks) == 1

    first_file_id = (
        first_knowledge.files[0].file_id
    )

    first_symbol_id = (
        first_knowledge.symbols[0].symbol_id
    )

    first_chunk_id = (
        first_knowledge.chunks[0].chunk_id
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

    assert len(second_knowledge.files) == 1
    assert len(second_knowledge.symbols) == 1
    assert len(second_knowledge.chunks) == 1

    second_file_id = (
        second_knowledge.files[0].file_id
    )

    second_symbol_id = (
        second_knowledge.symbols[0].symbol_id
    )

    second_chunk_id = (
        second_knowledge.chunks[0].chunk_id
    )

    assert first_file_id == second_file_id
    assert first_symbol_id == second_symbol_id
    assert first_chunk_id == second_chunk_id