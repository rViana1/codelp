from pathlib import Path

from core.project import Project
from core.project.models import ProjectMetadata

from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)

from app.knowledge.builder import KnowledgeBuilder


def test_builder_persists_embedding_metadata():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        )
    )

    project.embedding_result = EmbeddingCollection(
        provider=EmbeddingProviderInfo(
            name="test-provider",
            model="test-model",
            dimensions=3,
        ),
        embeddings=[
            Embedding(
                chunk_id="chunk-1",
                vector=[
                    0.1,
                    0.2,
                    0.3,
                ],
            )
        ],
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    assert len(
        knowledge.embeddings
    ) == 1

    assert (
        knowledge.embeddings[0].chunk_id
        == "chunk-1"
    )

    assert (
        knowledge.embeddings[0].provider
        == "test-provider"
    )

    assert (
        knowledge.embeddings[0].embedding_hash
        != ""
    )
