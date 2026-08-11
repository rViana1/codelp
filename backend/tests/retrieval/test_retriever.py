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


def test_retrieve_single_result() -> None:

    retriever = Retriever()

    result = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    assert result.results[0].chunk_id == "chunk_a"


def test_results_are_ranked_by_similarity() -> None:

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


def test_limit_is_respected() -> None:

    retriever = Retriever()

    result = retriever.retrieve(
        RetrievalQuery(
            text="authentication",
            limit=2,
        ),
        [1.0, 0.0, 0.0],
        create_store(),
    )

    assert len(result.results) == 2


def test_order_is_deterministic() -> None:

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