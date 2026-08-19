from pathlib import Path

from core.project import Project, ProjectMetadata

from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.indexing.indexer import ProjectIndexer
from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer
from app.parser.parser import ProjectParser
from app.pipeline import PipelineAnalyzer
from app.scanner.scanner import ProjectScanner


def create_project(path: Path) -> Project:
    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=path,
        )
    )


def create_analyzer(storage) -> PipelineAnalyzer:
    lifecycle = KnowledgeLifecycleService(
        KnowledgeLoader(storage),
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
            FakeEmbeddingProvider(dimensions=5)
        ),
        knowledge_lifecycle=lifecycle,
    )


def test_move_preserves_file_symbol_chunk_and_embedding_identity(
    tmp_path,
):
    project_path = tmp_path / "project"
    project_path.mkdir()
    source = project_path / "main.py"
    source.write_text(
        "def hello():\n"
        "    return 42\n"
    )
    storage = FileKnowledgeStorage(
        str(tmp_path / "knowledge")
    )
    analyzer = create_analyzer(storage)

    analyzer.analyze(create_project(project_path))
    first = storage.load("project")
    assert first is not None

    destination = project_path / "src" / "renamed.py"
    destination.parent.mkdir()
    source.rename(destination)
    analyzer.analyze(create_project(project_path))
    second = storage.load("project")
    assert second is not None

    assert second.files[0].file_id == first.files[0].file_id
    assert second.symbols[0].symbol_id == first.symbols[0].symbol_id
    assert second.chunks[0].chunk_id == first.chunks[0].chunk_id
    assert (
        second.embeddings[0].chunk_id
        == first.embeddings[0].chunk_id
    )
    assert [
        (location.path, location.is_current)
        for location in second.files[0].locations
    ] == [
        ("main.py", False),
        ("src/renamed.py", True),
    ]
