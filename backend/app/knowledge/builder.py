from pathlib import Path

from core.project.models import Project

from app.knowledge.mapper import KnowledgeMapper
from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeBuilder:
    """
    Coordinates creation of persistent project knowledge.
    """

    def build(
        self,
        project: Project,
    ) -> PersistentProjectKnowledge:

        project_id = self._create_project_id(
            project
        )

        return KnowledgeMapper.from_project(
            project,
            project_id=project_id,
        )


    def _create_project_id(
        self,
        project: Project,
    ) -> str:

        root_path = Path(
            project.metadata.root_path
        )

        return root_path.name