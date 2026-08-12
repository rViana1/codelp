from app.vectorstore.inmemory import InMemoryVectorStore
from app.vectorstore.interfaces import VectorStore


class VectorStoreFactory:
    """
    Creates vector store implementations.
    """

    def create(self) -> VectorStore:
        return InMemoryVectorStore()
