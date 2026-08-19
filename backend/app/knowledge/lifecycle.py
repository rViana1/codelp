from __future__ import annotations

from core.project import Project

from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.cache import (
    IncrementalAnalysisCache,
    IncrementalAnalysisCacheBuilder,
)
from app.knowledge.planning import (
    KnowledgeAnalysisPlan,
    KnowledgeExecutionPlanner,
)


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
        planner: KnowledgeExecutionPlanner | None = None,
        cache_builder: IncrementalAnalysisCacheBuilder | None = None,
    ) -> None:

        self.loader = loader
        self.restorer = restorer
        self.persistence = persistence
        self.planner = planner or KnowledgeExecutionPlanner()
        self.cache_builder = (
            cache_builder or IncrementalAnalysisCacheBuilder()
        )
        self._prepared_knowledge = {}
        self._prepared_cache = {}


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

        self._prepared_knowledge[id(project)] = knowledge
        self._prepared_cache[id(project)] = self._load_analysis_cache(
            project.metadata.root_path.name
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
        provider=None,
    ):
        """
        Persists updated project knowledge.
        """

        previous = self._prepared_knowledge.pop(
            id(project),
            None,
        )
        self._prepared_cache.pop(id(project), None)

        knowledge = self.persistence.persist(
            project,
            previous=previous,
        )
        if provider is not None:
            cache = self.cache_builder.build(
                project,
                knowledge,
                provider,
            )
            try:
                self.save_analysis_cache(cache)
            except Exception as exc:
                project.diagnostics.append(
                    f"Incremental cache unavailable: {exc}"
                )
        return knowledge

    def prepared_knowledge(self, project: Project):
        """Return the snapshot prepared for this execution."""
        return self._prepared_knowledge.get(id(project))

    def load_analysis_cache(
        self,
        project: Project,
    ) -> IncrementalAnalysisCache | None:
        return self._prepared_cache.get(id(project))

    def plan_analysis(
        self,
        project: Project,
    ) -> KnowledgeAnalysisPlan:
        """Resolve identity and changes after scan, before analysis."""
        plan = self.planner.create_plan(
            project=project,
            previous=self._prepared_knowledge.get(id(project)),
            cache=self._prepared_cache.get(id(project)),
        )
        project.knowledge_analysis_plan = plan
        return plan

    def save_analysis_cache(
        self,
        cache: IncrementalAnalysisCache,
    ) -> None:
        storage = getattr(self.persistence, "storage", None)
        if storage is None:
            return
        saver = getattr(
            storage,
            "save_analysis_cache",
            None,
        )
        if saver is not None:
            saver(cache)

    def _load_analysis_cache(
        self,
        project_id: str,
    ) -> IncrementalAnalysisCache | None:
        storage = getattr(self.loader, "storage", None)
        if storage is None:
            return None
        loader = getattr(
            storage,
            "load_analysis_cache",
            None,
        )
        if loader is None:
            return None
        return loader(project_id)
