import pytest

from app.retrieval.exceptions import SimilarityError
from app.retrieval.similarity import cosine_similarity


def test_equal_vectors_return_one() -> None:
    result = cosine_similarity(
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
    )

    assert result == 1.0


def test_orthogonal_vectors_return_zero() -> None:
    result = cosine_similarity(
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    )

    assert result == 0.0


def test_opposite_vectors_return_negative_one() -> None:
    result = cosine_similarity(
        [1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
    )

    assert result == -1.0


def test_similarity_is_deterministic() -> None:
    first = cosine_similarity(
        [0.5, 0.5, 0.0],
        [1.0, 0.0, 0.0],
    )

    second = cosine_similarity(
        [0.5, 0.5, 0.0],
        [1.0, 0.0, 0.0],
    )

    assert first == second


def test_empty_vector_raises_error() -> None:
    with pytest.raises(SimilarityError):
        cosine_similarity(
            [],
            [1.0],
        )


def test_different_dimensions_raise_error() -> None:
    with pytest.raises(SimilarityError):
        cosine_similarity(
            [1.0, 0.0],
            [1.0],
        )


def test_zero_vector_raises_error() -> None:
    with pytest.raises(SimilarityError):
        cosine_similarity(
            [0.0, 0.0],
            [1.0, 0.0],
        )