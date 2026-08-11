from app.embeddings.models import Embedding
from app.embeddings.store import InMemoryVectorStore


def test_vector_store_returns_embeddings() -> None:

    store = InMemoryVectorStore()

    store.add(
        Embedding(
            chunk_id="chunk_test",
            vector=[1.0, 0.0, 0.0],
        )
    )

    embeddings = store.all()

    assert len(embeddings) == 1

    assert embeddings[0].chunk_id == "chunk_test"