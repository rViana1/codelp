from pathlib import Path

from core.project import Project
from core.project.models import ProjectMetadata

from app.chunking.models import (
    ChunkCollection,
    CodeChunk,
    ChunkKind,
)

from app.knowledge.builder import KnowledgeBuilder


def test_builder_persists_chunks():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        )
    )

    project.chunk_result = ChunkCollection(
        chunks=[
            CodeChunk(
                id="chunk-1",
                file_path="main.py",
                symbol_id="symbol-1",
                kind=ChunkKind.FUNCTION,
                content="def hello(): pass",
                start_line=1,
                end_line=1,
            )
        ]
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    assert len(
        knowledge.chunks
    ) == 1

    assert (
        knowledge.chunks[0].chunk_id
        == "chunk-1"
    )

    assert (
        knowledge.chunks[0].symbol_id
        == "symbol-1"
    )

    assert (
        knowledge.chunks[0].content_hash
        != ""
    )
