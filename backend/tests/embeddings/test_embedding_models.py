from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)


def test_embedding_creation() -> None:

    embedding = Embedding(
        chunk_id="src/main.py::hello",
        vector=[0.1, 0.2, 0.3],
    )

    assert embedding.chunk_id == "src/main.py::hello"

    assert embedding.vector == [0.1, 0.2, 0.3]


def test_provider_info_creation() -> None:

    provider = EmbeddingProviderInfo(
        name="fake",
        model="fake-small",
        dimensions=3,
    )

    assert provider.name == "fake"

    assert provider.model == "fake-small"

    assert provider.dimensions == 3


def test_embedding_collection_defaults() -> None:

    provider = EmbeddingProviderInfo(
        name="fake",
        model="fake-small",
        dimensions=3,
    )

    collection = EmbeddingCollection(
        provider=provider,
    )

    assert collection.provider.name == "fake"

    assert collection.embeddings == []
