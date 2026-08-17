"""
Public API for the core.project package.

This package contains the central domain entities used by every
major module of Codelp.
"""

from .knowledge import (
    ProjectChunkKnowledge,
    ProjectEmbeddingKnowledge,
    ProjectFileKnowledge,
    ProjectKnowledgeState,
    ProjectRetrievalKnowledge,
    ProjectSymbolKnowledge,
)

from .models import (
    Project,
    ProjectConfiguration,
    ProjectMetadata,
    ProjectStatistics,
)

__all__ = [
    "Project",
    "ProjectMetadata",
    "ProjectConfiguration",
    "ProjectStatistics",
    "ProjectKnowledgeState",
    "ProjectFileKnowledge",
    "ProjectSymbolKnowledge",
    "ProjectChunkKnowledge",
    "ProjectEmbeddingKnowledge",
    "ProjectRetrievalKnowledge",
]