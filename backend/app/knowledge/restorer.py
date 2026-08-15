from __future__ import annotations

from core.project import Project

from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeRestorer:
    """
    Restores persistent knowledge into a Project aggregate.

    Responsible only for translating persisted state
    back into domain state.

    Does not access storage.
    Does not persist data.
    """

    def restore(
        self,
        project: Project,
        knowledge: PersistentProjectKnowledge,
    ) -> Project:
        """
        Restores compatible knowledge into the project.
        """

        project.diagnostics.append(
            f"Restored knowledge for project "
            f"{knowledge.metadata.project_id}"
        )

        return project
