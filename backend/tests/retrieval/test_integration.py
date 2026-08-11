from app.embeddings.models import Embedding
from app.embeddings.store import InMemoryVectorStore

from app.retrieval.models import RetrievalQuery
from app.retrieval.retriever import Retriever


def create_store() -> InMemoryVectorStore:

    store = InMemoryVectorStore()

    store.add_many(
        [
            Embedding(
                chunk_id="chunk_auth",
                vector=[1.0, 0.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_database",
                vector=[0.0, 1.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_partial",
                vector=[0.8, 0.0, 0.0],
            ),
        ]
    )

    return store


def test_retrieval_preserves_chunk_identity() -> None:
    retriever = Retriever()

    result = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    assert [
        item.chunk_id
        for item in result.results
    ] == [
        "chunk_auth",
        "chunk_partial",
        "chunk_database",
    ]


def test_retrieval_returns_deterministic_results() -> None:
    retriever = Retriever()

    first = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    second = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    assert first == second
