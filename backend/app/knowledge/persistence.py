from __future__ import annotations

from core.project import Project

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.diff import ChangeDetectionEngine
from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.normalizer import KnowledgeNormalizer
from app.knowledge.storage import KnowledgeStorage
from app.knowledge.validator import KnowledgeValidator
from app.knowledge.update import KnowledgeUpdateEngine


_PREVIOUS_NOT_PROVIDED = object()


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
        change_detector=None,
        update_engine=None,
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

        self.change_detector = (
            change_detector
            if change_detector is not None
            else ChangeDetectionEngine()
        )

        self.update_engine = (
            update_engine
            if update_engine is not None
            else KnowledgeUpdateEngine()
        )


    def persist(
        self,
        project: Project,
        previous: PersistentProjectKnowledge | None | object = (
            _PREVIOUS_NOT_PROVIDED
        ),
    ) -> PersistentProjectKnowledge:
        """
        Creates, normalizes and persists project knowledge.
        """

        project_id = project.metadata.root_path.name

        if previous is _PREVIOUS_NOT_PROVIDED:
            previous = self.storage.load(
                project_id
            )

        candidate = self.builder.build(
            project,
            previous=previous,
        )

        knowledge = self.update_engine.merge(
            previous,
            candidate,
        )

        knowledge = self.normalizer.normalize(
            knowledge
        )

        change_report = self.change_detector.compare(
            previous,
            knowledge,
        )

        self.validator.validate(
            knowledge
        )

        try:
            self.storage.save(knowledge)
        except Exception:
            self._rollback(previous, project_id)
            raise

        project.knowledge_change_result = change_report

        return knowledge

    def _rollback(
        self,
        previous: PersistentProjectKnowledge | None,
        project_id: str,
    ) -> None:
        """Best-effort rollback for storage implementations.

        Atomic stores retain the previous snapshot automatically. Stores
        that failed after a partial write get one explicit restoration
        attempt. Rollback errors never hide the original commit failure.
        """
        try:
            if previous is not None:
                self.storage.save(previous)
            elif self.storage.exists(project_id):
                self.storage.delete(project_id)
        except Exception:
            pass
