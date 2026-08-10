from app.embeddings.providers import EmbeddingProvider


def test_provider_protocol_is_runtime_checkable() -> None:

    class DummyProvider:
        info = None

        def generate_embedding(self, chunk):
            return None

        def generate_embeddings(self, chunks):
            return None

    provider = DummyProvider()

    assert isinstance(provider, EmbeddingProvider)