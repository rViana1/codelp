from __future__ import annotations

from core.project import Project

from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer


class KnowledgeLifecycleService:
    """
    Coordinates the knowledge lifecycle of a project.

    Responsible for:
    - loading previous knowledge;
    - restoring compatible state;
    - persisting updated knowledge.

    Does not execute project analysis.
    """

    def __init__(
        self,
        loader: KnowledgeLoader,
        restorer: KnowledgeRestorer,
        persistence: KnowledgePersistenceService,
    ) -> None:

        self.loader = loader
        self.restorer = restorer
        self.persistence = persistence


    def prepare(
        self,
        project: Project,
    ) -> Project:
        """
        Loads and restores previous knowledge when available.
        """

        project_id = project.metadata.root_path.name

        knowledge = self.loader.load(
            project_id,
        )

        if knowledge is None:
            return project

        return self.restorer.restore(
            project,
            knowledge,
        )


    def finalize(
        self,
        project: Project,
    ):
        """
        Persists updated project knowledge.
        """

        return self.persistence.persist(
            project
        )