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
        previous: PersistentProjectKnowledge | None = None,
    ) -> PersistentProjectKnowledge:
        """
        Build persistent knowledge from a Project instance.
        """

        if project_id is None:
            project_id = project.metadata.name

        if previous is not None:
            metadata = PersistentKnowledgeMetadata(
                project_id=project_id,
                version=previous.metadata.version,
                created_at=previous.metadata.created_at,
                updated_at=PersistentKnowledgeMetadata.model_fields[
                    "updated_at"
                ].default_factory(),
            )

        else:
            metadata = PersistentKnowledgeMetadata(
                project_id=project_id
            )

        previous_files = {}

        if previous is not None:
            previous_files = {
                file.path: file
                for file in previous.files
            }


        files = []

        for path in project.statistics.scanned_files:

            path_str = str(path)

            existing = previous_files.get(
                path_str
            )

            if existing:
                files.append(
                    PersistentFileIdentity(
                        file_id=existing.file_id,
                        path=path_str,
                        content_hash=existing.content_hash,
                    )
                )

            else:
                files.append(
                    PersistentFileIdentity(
                        file_id=path_str,
                        path=path_str,
                        content_hash="",
                    )
                )

        return PersistentProjectKnowledge(
            metadata=metadata,
            files=files,
        )
