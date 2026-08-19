from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from core.project.models import (
    ProjectConfiguration,
    ProjectMetadata,
)

if TYPE_CHECKING:
    from core.project.models import Project


# Persistence boundary contract

PERSISTABLE_PROJECT_FIELDS = {
    "metadata",
    "configuration",
}


NON_PERSISTABLE_PROJECT_FIELDS = {
    "root_tree",
    "parser_result",
    "index_result",
    "chunk_result",
    "embedding_result",
    "retrieval_result",
    "context_result",
    "knowledge_state",
    "knowledge_change_result",
    "incremental_analysis_result",
    "knowledge_analysis_plan",
    "understanding_result",
    "diagnostics",
}


class ProjectPersistentState(BaseModel):
    """
    Represents the subset of Project state that is eligible
    for persistence.

    This model is the boundary between the runtime Project
    aggregate and persistent knowledge.

    It must never contain runtime objects.
    """

    metadata: ProjectMetadata

    configuration: ProjectConfiguration = Field(
        default_factory=ProjectConfiguration
    )

    @classmethod
    def from_project(
        cls,
        project: Project,
    ) -> ProjectPersistentState:
        """
        Creates the persistent representation of a Project.

        Only state explicitly considered eligible for
        persistence is extracted.

        Runtime analysis objects are intentionally ignored.
        """

        return cls(
            metadata=ProjectMetadata(
                **project.metadata.model_dump()
            ),
            configuration=ProjectConfiguration(
                **project.configuration.model_dump()
            ),
        )
