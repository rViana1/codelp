"""Deterministic local fingerprint vectors requiring no model or network."""

from __future__ import annotations

import hashlib
import math
import re

from app.chunking.models import CodeChunk

from .models import Embedding, EmbeddingCollection, EmbeddingProviderInfo


class LocalHashEmbeddingProvider:
    """Provide reproducible lexical vectors for model-free retrieval.

    Tokens are projected into a fixed-size vector with signed feature hashing.
    These vectors preserve lexical overlap but are not learned semantic
    embeddings. Structural graph evidence remains the principal intelligence
    source in no-model mode.
    """

    def __init__(self, dimensions: int = 8) -> None:
        if dimensions <= 0 or dimensions > 4096:
            raise ValueError(
                "Local hash dimensions must be between 1 and 4096"
            )
        self._dimensions = dimensions

    @property
    def info(self) -> EmbeddingProviderInfo:
        return EmbeddingProviderInfo(
            name="local_hash",
            model=f"signed-feature-hash-v1-{self._dimensions}",
            dimensions=self._dimensions,
        )

    def generate_embedding(self, chunk: CodeChunk) -> Embedding:
        vector = [0.0] * self._dimensions
        for token in self._tokens(chunk.content):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % self._dimensions
            vector[index] += -1.0 if digest[8] & 1 else 1.0
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude:
            vector = [value / magnitude for value in vector]
        return Embedding(
            chunk_id=chunk.id,
            vector=vector,
        )

    def generate_embeddings(
        self, chunks: list[CodeChunk]
    ) -> EmbeddingCollection:
        return EmbeddingCollection(
            provider=self.info,
            embeddings=[self.generate_embedding(chunk) for chunk in chunks],
        )

    @staticmethod
    def _tokens(content: str) -> tuple[str, ...]:
        tokens = []
        for raw in re.findall(r"[A-Za-z][A-Za-z0-9_]*", content):
            expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw)
            parts = [part.lower() for part in expanded.replace("_", " ").split()]
            tokens.extend(parts)
            combined = raw.lower()
            if len(parts) > 1:
                tokens.append(combined)
        return tuple(tokens)
