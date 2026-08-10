from pathlib import Path

from core.project import Project, ProjectMetadata

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider


def test_full_pipeline_updates_embedding_state(
    tmp_path: Path,
) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text(
        "def hello():\n"
        "    return 42\n\n"
        "class User:\n"
        "    def login(self):\n"
        "        return True\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()
    chunker.chunk_project(project)

    engine = EmbeddingEngine(
        FakeEmbeddingProvider(dimensions=5)
    )

    engine.embed_project(project)

    assert project.embedding_result is not None

    embeddings = project.embedding_result.embeddings

    assert [embedding.chunk_id for embedding in embeddings] == [
        "src/main.py::User",
        "src/main.py::User.login",
        "src/main.py::hello",
    ]

    assert all(
        len(embedding.vector) == 5
        for embedding in embeddings
    )

    assert project.embedding_result.provider.name == "fake"
