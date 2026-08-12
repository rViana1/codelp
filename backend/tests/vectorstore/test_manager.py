from pathlib import Path

from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)
from app.vectorstore.manager import VectorStoreManager


def create_embeddings() -> EmbeddingCollection:

    return EmbeddingCollection(
        provider=EmbeddingProviderInfo(
            name="fake",
            model="test",
            dimensions=3,
        ),
        embeddings=[
            Embedding(
                chunk_id="chunk_a",
                vector=[1.0, 0.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_b",
                vector=[0.0, 1.0, 0.0],
            ),
        ],
    )


def test_register_project_creates_vector_store() -> None:

    manager = VectorStoreManager()

    project_path = Path("/tmp/project")

    manager.register_project(
        project_path,
        create_embeddings(),
    )

    store = manager.get_project_store(
        project_path
    )

    assert store is not None

    assert [
        embedding.chunk_id
        for embedding in store.all()
    ] == [
        "chunk_a",
        "chunk_b",
    ]


def test_get_unknown_project_returns_none() -> None:

    manager = VectorStoreManager()

    assert manager.get_project_store(
        Path("/tmp/missing")
    ) is None


def test_register_project_replaces_existing_store() -> None:

    manager = VectorStoreManager()

    project_path = Path("/tmp/project")

    manager.register_project(
        project_path,
        create_embeddings(),
    )

    manager.register_project(
        project_path,
        EmbeddingCollection(
            provider=EmbeddingProviderInfo(
                name="fake",
                model="test",
                dimensions=3,
            ),
            embeddings=[
                Embedding(
                    chunk_id="chunk_new",
                    vector=[0.5, 0.5, 0.0],
                ),
            ],
        ),
    )

    store = manager.get_project_store(
        project_path
    )

    assert store is not None

    assert [
        embedding.chunk_id
        for embedding in store.all()
    ] == [
        "chunk_new",
    ]


def test_remove_project_store() -> None:

    manager = VectorStoreManager()

    project_path = Path("/tmp/project")

    manager.register_project(
        project_path,
        create_embeddings(),
    )

    manager.remove_project(
        project_path
    )

    assert manager.get_project_store(
        project_path
    ) is None


def test_clear_removes_all_project_stores() -> None:

    manager = VectorStoreManager()

    manager.register_project(
        Path("/tmp/project_a"),
        create_embeddings(),
    )

    manager.register_project(
        Path("/tmp/project_b"),
        create_embeddings(),
    )

    manager.clear()

    assert manager.get_project_store(
        Path("/tmp/project_a")
    ) is None

    assert manager.get_project_store(
        Path("/tmp/project_b")
    ) is None
