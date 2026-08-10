from app.embeddings.models import Embedding
from app.embeddings.store import InMemoryVectorStore


def make_embedding(chunk_id: str) -> Embedding:

    return Embedding(
        chunk_id=chunk_id,
        vector=[0.1, 0.2],
    )


def test_store_single_embedding() -> None:

    store = InMemoryVectorStore()

    embedding = make_embedding("a")

    store.add(embedding)

    assert store.contains("a")

    assert store.get("a") == embedding


def test_store_many_embeddings() -> None:

    store = InMemoryVectorStore()

    store.add_many(
        [
            make_embedding("a"),
            make_embedding("b"),
        ]
    )

    assert store.contains("a")

    assert store.contains("b")

    assert len(store.all()) == 2


def test_get_unknown_embedding_returns_none() -> None:

    store = InMemoryVectorStore()

    assert store.get("missing") is None


def test_insertion_order_is_preserved() -> None:

    store = InMemoryVectorStore()

    store.add(make_embedding("a"))

    store.add(make_embedding("b"))

    store.add(make_embedding("c"))

    assert [
        embedding.chunk_id
        for embedding in store.all()
    ] == ["a", "b", "c"]
