"""
Similarity utilities for retrieval operations.
"""

from __future__ import annotations

import math

from app.retrieval.exceptions import SimilarityError


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns:
        float:
            Similarity score between -1 and 1.

    Raises:
        SimilarityError:
            When vectors cannot be compared.
    """

    if not vector_a or not vector_b:
        raise SimilarityError(
            "Cannot calculate similarity with empty vectors."
        )

    if len(vector_a) != len(vector_b):
        raise SimilarityError(
            "Vectors must have the same dimensions."
        )

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        raise SimilarityError(
            "Cannot calculate similarity with zero magnitude vectors."
        )

    return dot_product / (magnitude_a * magnitude_b)
