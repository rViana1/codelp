"""
Deprecated module.

InMemoryVectorStore was moved to app.vectorstore.inmemory
during Milestone 7.1.
"""

from app.vectorstore.inmemory import InMemoryVectorStore

__all__ = ["InMemoryVectorStore"]