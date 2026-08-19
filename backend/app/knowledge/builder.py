from pathlib import Path

from core.project.models import Project

from app.knowledge.mapper import KnowledgeMapper
from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.graph import KnowledgeGraphBuilder


class KnowledgeBuilder:
    """
    Coordinates creation of persistent project knowledge.
    """

    def __init__(
        self,
        graph_builder: KnowledgeGraphBuilder | None = None,
    ) -> None:
        self.graph_builder = graph_builder or KnowledgeGraphBuilder()

    def build(
        self,
        project: Project,
        previous: PersistentProjectKnowledge | None = None,
    ) -> PersistentProjectKnowledge:

        project_id = self._create_project_id(
            project
        )

        knowledge = KnowledgeMapper.from_project(
            project,
            project_id=project_id,
            previous=previous,
        )

        previous_graph = None
        if previous is not None:
            previous_graph = (
                previous.graph
                if previous.graph is not None
                else self.graph_builder.build(previous)
            )
        knowledge.graph = self.graph_builder.build(knowledge, previous_graph)
        return knowledge


    def _create_project_id(
        self,
        project: Project,
    ) -> str:

        root_path = Path(
            project.metadata.root_path
        )

        return root_path.name
