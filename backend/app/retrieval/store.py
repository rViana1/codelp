"""
Deprecated module.

VectorStore was moved to app.vectorstore.interfaces
during Milestone 7.1.
"""

from app.vectorstore.interfaces import VectorStore

__all__ = ["VectorStore"]