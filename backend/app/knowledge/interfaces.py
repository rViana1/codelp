from abc import ABC, abstractmethod

from .models import PersistentProjectKnowledge


class KnowledgeStorage(ABC):
    """
    Abstract contract for persistent project knowledge storage.
    """

    @abstractmethod
    def save(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:
        """
        Persist project knowledge snapshot.
        """
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:
        """
        Load project knowledge snapshot.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        project_id: str,
    ) -> bool:
        """
        Check if project knowledge exists.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        project_id: str,
    ) -> None:
        """
        Remove persisted project knowledge.
        """
        raise NotImplementedError
