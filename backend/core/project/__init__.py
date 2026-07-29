"""
Public API for the core.project package.

This package contains the central domain entities used by every
major module of Codelp.
"""

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
]
