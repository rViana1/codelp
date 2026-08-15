from __future__ import annotations

from app.knowledge.constants import CURRENT_KNOWLEDGE_VERSION
from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.storage import KnowledgeStorage


class KnowledgeLoader:
    """
    Loads persisted project knowledge.

    Responsible only for retrieving and validating
    persisted knowledge.
    """

    def __init__(
        self,
        storage: KnowledgeStorage,
    ) -> None:
        self.storage = storage

    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:
        """
        Loads existing project knowledge.

        Returns None when no knowledge exists.

        Raises ValueError when stored knowledge
        is incompatible.
        """

        try:
            knowledge = self.storage.load(
                project_id
            )

        except Exception:
            return None


        if knowledge is None:
            return None


        self._validate_version(
            knowledge
        )

        return knowledge


    def _validate_version(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        if (
            knowledge.metadata.version
            != CURRENT_KNOWLEDGE_VERSION
        ):
            raise ValueError(
                "Unsupported knowledge version: "
                f"{knowledge.metadata.version}"
            )