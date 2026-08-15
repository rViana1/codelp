from __future__ import annotations

from core.project import Project

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.normalizer import KnowledgeNormalizer
from app.knowledge.storage import KnowledgeStorage
from app.knowledge.validator import KnowledgeValidator


class KnowledgePersistenceService:
    """
    Application service responsible for persisting
    project knowledge.

    Coordinates transformation and storage.

    Does not own persistence implementation.
    """

    def __init__(
        self,
        builder,
        storage,
        validator=None,
        normalizer=None,
    ):
        self.builder = builder
        self.storage = storage

        self.normalizer = (
            normalizer
            if normalizer is not None
            else KnowledgeNormalizer()
        )

        self.validator = (
            validator
            if validator is not None
            else KnowledgeValidator()
        )


    def persist(
        self,
        project: Project,
    ) -> PersistentProjectKnowledge:
        """
        Creates, normalizes and persists project knowledge.
        """

        knowledge = self.builder.build(
            project
        )

        knowledge = self.normalizer.normalize(
            knowledge
        )

        self.validator.validate(
            knowledge
        )

        self.storage.save(
            knowledge
        )

        return knowledge