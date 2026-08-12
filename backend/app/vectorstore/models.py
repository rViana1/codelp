"""
Vector store abstractions and configuration models.
"""

from __future__ import annotations

from pydantic import BaseModel


class VectorStoreConfig(BaseModel):
    """
    Configuration for vector storage selection.

    This abstraction allows future support for
    multiple vector storage implementations.
    """

    provider: str = "memory"