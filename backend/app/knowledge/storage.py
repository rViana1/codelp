from .interfaces import KnowledgeStorage
from .cache import IncrementalAnalysisCache
from .models import PersistentProjectKnowledge


class InMemoryKnowledgeStorage(KnowledgeStorage):
    """
    In-memory implementation of knowledge storage.

    Used as the initial persistence backend while
    keeping storage independent from the domain.
    """

    def __init__(self) -> None:
        self._storage: dict[str, PersistentProjectKnowledge] = {}
        self._analysis_cache: dict[str, IncrementalAnalysisCache] = {}

    def save(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:
        self._storage[knowledge.metadata.project_id] = knowledge

    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:
        return self._storage.get(project_id)

    def exists(
        self,
        project_id: str,
    ) -> bool:
        return project_id in self._storage

    def delete(
        self,
        project_id: str,
    ) -> None:
        self._storage.pop(project_id, None)
        self._analysis_cache.pop(project_id, None)

    def load_analysis_cache(
        self,
        project_id: str,
    ) -> IncrementalAnalysisCache | None:
        return self._analysis_cache.get(project_id)

    def save_analysis_cache(
        self,
        cache: IncrementalAnalysisCache,
    ) -> None:
        self._analysis_cache[cache.project_id] = cache

    def get(self, project_id: str):
        return self._storage.get(project_id)
