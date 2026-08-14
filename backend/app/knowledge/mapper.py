from core.project.models import Project

from app.knowledge.models import (
    PersistentFileIdentity,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


class KnowledgeMapper:
    """
    Converts Project domain state into persistent project knowledge.

    Responsibility
    --------------
    Creates a persistence representation from the Project aggregate.

    Boundaries
    ----------
    - Does not modify Project.
    - Does not persist data.
    - Does not own storage lifecycle.

    The mapper only transforms domain state into persistent knowledge.
    """

    @staticmethod
    def from_project(
        project: Project,
        project_id: str | None = None,
    ) -> PersistentProjectKnowledge:
        """
        Build persistent knowledge from a Project instance.
        """

        if project_id is None:
            project_id = project.metadata.name

        metadata = PersistentKnowledgeMetadata(
            project_id=project_id
        )

        files = [
            PersistentFileIdentity(
                file_id=str(path),
                path=str(path),
                content_hash="",
            )
            for path in project.statistics.scanned_files
        ]

        return PersistentProjectKnowledge(
            metadata=metadata,
            files=files,
        )
