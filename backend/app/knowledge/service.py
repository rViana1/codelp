from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.storage import KnowledgeStorage


class KnowledgeService:

    def __init__(
        self,
        storage: KnowledgeStorage,
    ):
        self.storage = storage


    def save(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        self.storage.save(
            knowledge
        )


    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:

        return self.storage.get(
            project_id
        )


    def exists(
        self,
        project_id: str,
    ) -> bool:

        return self.storage.contains(
            project_id
        )


    def remove(
        self,
        project_id: str,
    ) -> None:

        self.storage.delete(
            project_id
        )


    def get_or_create(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge:

        existing = self.load(
            project_id
        )

        if existing is not None:
            return existing

        knowledge = PersistentProjectKnowledge(
            metadata={
                "project_id": project_id
            }
        )

        self.save(
            knowledge
        )

        return knowledge


    def update(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        self.save(
            knowledge
        )