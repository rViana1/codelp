from .interfaces import KnowledgeStorage
from .models import PersistentProjectKnowledge


class InMemoryKnowledgeStorage(KnowledgeStorage):
    """
    In-memory implementation of knowledge storage.

    Used as the initial persistence backend while
    keeping storage independent from the domain.
    """

    def __init__(self) -> None:
        self._storage: dict[str, PersistentProjectKnowledge] = {}

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

    def get(self, project_id: str):
        return self._storage.get(project_id)