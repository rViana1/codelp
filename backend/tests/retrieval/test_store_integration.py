from app.embeddings.models import Embedding
from app.embeddings.store import InMemoryVectorStore
from app.retrieval.models import RetrievalQuery
from app.retrieval.retriever import Retriever


def create_store() -> InMemoryVectorStore:

    store = InMemoryVectorStore()

    store.add_many(
        [
            Embedding(
                chunk_id="chunk_a",
                vector=[1.0, 0.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_b",
                vector=[0.0, 1.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_c",
                vector=[0.5, 0.0, 0.0],
            ),
        ]
    )

    return store


def test_retriever_works_with_vector_store() -> None:

    retriever = Retriever()

    result = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    assert result.results[0].chunk_id == "chunk_a"


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
        "chunk_a",
        "chunk_c",
        "chunk_b",
    ]
