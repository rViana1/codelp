from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)


def test_retrieval_query_creation() -> None:
    query = RetrievalQuery(text="find authentication code")

    assert query.text == "find authentication code"
    assert query.limit == 5


def test_retrieval_result_creation() -> None:
    result = RetrievalResult(
        chunk_id="src/auth.py::login",
        score=0.95,
    )

    assert result.chunk_id == "src/auth.py::login"
    assert result.score == 0.95


def test_retrieval_collection_defaults() -> None:
    collection = RetrievalCollection(
        query=RetrievalQuery(text="search"),
    )

    assert collection.results == []


def test_retrieval_collection_preserves_order() -> None:
    collection = RetrievalCollection(
        query=RetrievalQuery(text="search"),
        results=[
            RetrievalResult(
                chunk_id="chunk-a",
                score=0.9,
            ),
            RetrievalResult(
                chunk_id="chunk-b",
                score=0.8,
            ),
        ],
    )

    assert collection.results[0].chunk_id == "chunk-a"
    assert collection.results[1].chunk_id == "chunk-b"
