from app.chunking.models import ChunkKind, CodeChunk
from app.embeddings.local_hash_provider import LocalHashEmbeddingProvider
from app.retrieval.similarity import cosine_similarity


def chunk(identity: str, content: str) -> CodeChunk:
    return CodeChunk(
        id=identity,
        file_path="module.py",
        kind=ChunkKind.FUNCTION,
        content=content,
        start_line=1,
        end_line=1,
    )


def test_local_hash_vectors_are_deterministic_and_lexically_useful():
    provider = LocalHashEmbeddingProvider(dimensions=64)
    query = provider.generate_embedding(chunk("query", "authenticate user"))
    related = provider.generate_embedding(
        chunk("related", "def authenticate_user(user): return bool(user)")
    )
    unrelated = provider.generate_embedding(
        chunk("unrelated", "def calculate_invoice_total(items): pass")
    )

    assert query == provider.generate_embedding(
        chunk("query", "authenticate user")
    )
    assert cosine_similarity(query.vector, related.vector) > cosine_similarity(
        query.vector, unrelated.vector
    )
