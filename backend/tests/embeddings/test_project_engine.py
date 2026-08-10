from core.project import Project, ProjectMetadata

from app.chunking.models import (
    ChunkCollection,
    ChunkKind,
    CodeChunk,
)
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider


def test_embed_project_updates_domain_state() -> None:

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path="/tmp",
        )
    )

    project.chunk_result = ChunkCollection(
        chunks=[
            CodeChunk(
                id="src/main.py::hello",
                kind=ChunkKind.FUNCTION,
                file_path="src/main.py",
                symbol="hello",
                content="def hello():\n    return 42\n",
                start_line=1,
                end_line=2,
            )
        ]
    )

    engine = EmbeddingEngine(
        FakeEmbeddingProvider(dimensions=4)
    )

    result = engine.embed_project(project)

    assert result is project

    assert project.embedding_result is not None

    assert project.embedding_result.provider.name == "fake"

    assert len(project.embedding_result.embeddings) == 1

    embedding = project.embedding_result.embeddings[0]

    assert embedding.chunk_id == "src/main.py::hello"

    assert len(embedding.vector) == 4
