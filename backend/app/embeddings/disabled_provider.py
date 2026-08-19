from app.chunking.models import CodeChunk

from .models import Embedding, EmbeddingCollection, EmbeddingProviderInfo


class DisabledEmbeddingProvider:
    """Explicit no-model provider; analysis remains fully operational."""

    @property
    def info(self) -> EmbeddingProviderInfo:
        return EmbeddingProviderInfo(
            name="disabled",
            model="none",
            dimensions=0,
        )

    def generate_embedding(self, chunk: CodeChunk) -> Embedding:
        raise RuntimeError("Embedding generation is disabled")

    def generate_embeddings(
        self, chunks: list[CodeChunk]
    ) -> EmbeddingCollection:
        return EmbeddingCollection(provider=self.info, embeddings=[])
