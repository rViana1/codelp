"""Deterministic project change detection.

The change detector compares two resolved knowledge snapshots. Entity
identity has already been reconciled by the identity tracking layer, so
paths are mutable file attributes rather than identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Callable, Hashable, TypeVar

from pydantic import BaseModel, Field

from app.knowledge.models import (
    PersistentFileIdentity,
    PersistentProjectKnowledge,
)


class ProjectElementKind(str, Enum):
    FILE = "file"
    SYMBOL = "symbol"
    CHUNK = "chunk"
    EMBEDDING = "embedding"
    RETRIEVAL = "retrieval"


class ProjectChangeKind(str, Enum):
    NEW = "new"
    REMOVED = "removed"
    MOVED = "moved"
    RENAMED = "renamed"
    MOVED_AND_RENAMED = "moved_and_renamed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class ProjectElementChange:
    """One deterministic change to a persistent project entity."""

    element_kind: ProjectElementKind
    element_id: str
    change_kind: ProjectChangeKind
    previous_path: str | None = None
    current_path: str | None = None


@dataclass(frozen=True)
class KnowledgeElementReference:
    """A stable reference to knowledge that can be reused or invalidated."""

    element_kind: ProjectElementKind
    element_id: str
    reason: str


@dataclass(frozen=True)
class ProjectChangeReport:
    """Complete, immutable result of comparing two executions."""

    new_files: tuple[PersistentFileIdentity, ...]
    removed_files: tuple[PersistentFileIdentity, ...]
    moved_files: tuple[PersistentFileIdentity, ...]
    renamed_files: tuple[PersistentFileIdentity, ...]
    moved_and_renamed_files: tuple[PersistentFileIdentity, ...]
    modified_files: tuple[PersistentFileIdentity, ...]
    unchanged_files: tuple[PersistentFileIdentity, ...]
    changed_elements: tuple[ProjectElementChange, ...]
    unchanged_elements: tuple[ProjectElementChange, ...]
    invalidated_elements: tuple[KnowledgeElementReference, ...]
    reusable_elements: tuple[KnowledgeElementReference, ...]


@dataclass(frozen=True)
class FileChangeReport:
    """File-only change set available before semantic analysis."""

    new_files: tuple[PersistentFileIdentity, ...]
    removed_files: tuple[PersistentFileIdentity, ...]
    moved_files: tuple[PersistentFileIdentity, ...]
    renamed_files: tuple[PersistentFileIdentity, ...]
    moved_and_renamed_files: tuple[PersistentFileIdentity, ...]
    modified_files: tuple[PersistentFileIdentity, ...]
    unchanged_files: tuple[PersistentFileIdentity, ...]


class KnowledgeDiffResult(BaseModel):
    """Backward-compatible file-only view of a change report."""

    added_files: list[PersistentFileIdentity] = Field(default_factory=list)
    modified_files: list[PersistentFileIdentity] = Field(default_factory=list)
    removed_files: list[PersistentFileIdentity] = Field(default_factory=list)
    unchanged_files: list[PersistentFileIdentity] = Field(default_factory=list)
    moved_files: list[PersistentFileIdentity] = Field(default_factory=list)
    renamed_files: list[PersistentFileIdentity] = Field(default_factory=list)
    moved_and_renamed_files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )


T = TypeVar("T")


class ChangeDetectionEngine:
    """Compare current resolved knowledge with its persisted predecessor."""

    def compare(
        self,
        previous: PersistentProjectKnowledge | None,
        current: PersistentProjectKnowledge,
    ) -> ProjectChangeReport:
        previous_files = previous.files if previous is not None else []
        file_changes = self._compare_files(previous_files, current.files)

        changed = list(file_changes["changed"])
        unchanged = list(file_changes["unchanged"])
        invalidated = list(file_changes["invalidated"])
        reusable = list(file_changes["reusable"])

        self._compare_entities(
            previous.symbols if previous is not None else [],
            current.symbols,
            key=lambda item: item.symbol_id,
            state=lambda item: (item.file_id, item.name, item.symbol_type),
            kind=ProjectElementKind.SYMBOL,
            changed=changed,
            unchanged=unchanged,
            invalidated=invalidated,
            reusable=reusable,
        )

        reusable_chunk_ids = self._compare_entities(
            previous.chunks if previous is not None else [],
            current.chunks,
            key=lambda item: item.chunk_id,
            state=lambda item: (item.symbol_id, item.content_hash),
            kind=ProjectElementKind.CHUNK,
            changed=changed,
            unchanged=unchanged,
            invalidated=invalidated,
            reusable=reusable,
        )

        self._compare_entities(
            previous.embeddings if previous is not None else [],
            current.embeddings,
            key=lambda item: (item.chunk_id, item.provider),
            state=lambda item: item.embedding_hash,
            kind=ProjectElementKind.EMBEDDING,
            changed=changed,
            unchanged=unchanged,
            invalidated=invalidated,
            reusable=reusable,
            parent_reusable=lambda item: item.chunk_id in reusable_chunk_ids,
        )

        self._compare_entities(
            previous.retrieval if previous is not None else [],
            current.retrieval,
            key=lambda item: (item.chunk_id, item.query_hash),
            state=lambda item: item.score,
            kind=ProjectElementKind.RETRIEVAL,
            changed=changed,
            unchanged=unchanged,
            invalidated=invalidated,
            reusable=reusable,
            parent_reusable=lambda item: item.chunk_id in reusable_chunk_ids,
        )

        return ProjectChangeReport(
            new_files=file_changes["new_files"],
            removed_files=file_changes["removed_files"],
            moved_files=file_changes["moved_files"],
            renamed_files=file_changes["renamed_files"],
            moved_and_renamed_files=file_changes[
                "moved_and_renamed_files"
            ],
            modified_files=file_changes["modified_files"],
            unchanged_files=file_changes["unchanged_files"],
            changed_elements=self._ordered_changes(changed),
            unchanged_elements=self._ordered_changes(unchanged),
            invalidated_elements=self._ordered_references(invalidated),
            reusable_elements=self._ordered_references(reusable),
        )

    def compare_files(
        self,
        previous_files: list[PersistentFileIdentity],
        current_files: list[PersistentFileIdentity],
    ) -> FileChangeReport:
        """Compare resolved file state before semantic analysis runs."""
        comparison = self._compare_files(previous_files, current_files)
        return FileChangeReport(
            new_files=comparison["new_files"],
            removed_files=comparison["removed_files"],
            moved_files=comparison["moved_files"],
            renamed_files=comparison["renamed_files"],
            moved_and_renamed_files=comparison[
                "moved_and_renamed_files"
            ],
            modified_files=comparison["modified_files"],
            unchanged_files=comparison["unchanged_files"],
        )

    def _compare_files(self, previous_files, current_files):
        previous_active = {
            file.file_id: file
            for file in previous_files
            if self._current_path(file) is not None
        }
        current_active = {
            file.file_id: file
            for file in current_files
            if self._current_path(file) is not None
        }
        categories = {
            "new_files": [],
            "removed_files": [],
            "moved_files": [],
            "renamed_files": [],
            "moved_and_renamed_files": [],
            "modified_files": [],
            "unchanged_files": [],
        }
        changed = []
        unchanged = []
        invalidated = []
        reusable = []

        for file_id in sorted(set(previous_active) | set(current_active)):
            before = previous_active.get(file_id)
            after = current_active.get(file_id)

            if before is None:
                categories["new_files"].append(after)
                changed.append(self._file_change(after, ProjectChangeKind.NEW))
                continue
            if after is None:
                categories["removed_files"].append(before)
                changed.append(
                    self._file_change(
                        before, ProjectChangeKind.REMOVED, previous=True
                    )
                )
                invalidated.append(
                    self._reference(ProjectElementKind.FILE, file_id, "removed")
                )
                continue

            previous_path = self._current_path(before)
            current_path = self._current_path(after)
            same_content = (
                self._current_content_hash(before)
                == self._current_content_hash(after)
            )
            if not same_content:
                kind = ProjectChangeKind.MODIFIED
                category = "modified_files"
            elif previous_path != current_path:
                kind = self._movement_kind(previous_path, current_path)
                category = f"{kind.value}_files"
            else:
                categories["unchanged_files"].append(after)
                unchanged.append(
                    self._file_change(after, ProjectChangeKind.UNCHANGED)
                )
                reusable.append(
                    self._reference(
                        ProjectElementKind.FILE, file_id, "unchanged"
                    )
                )
                continue

            categories[category].append(after)
            changed.append(
                ProjectElementChange(
                    ProjectElementKind.FILE,
                    file_id,
                    kind,
                    previous_path,
                    current_path,
                )
            )
            if kind == ProjectChangeKind.MODIFIED:
                invalidated.append(
                    self._reference(
                        ProjectElementKind.FILE,
                        file_id,
                        "content_modified",
                    )
                )
            else:
                reusable.append(
                    self._reference(
                        ProjectElementKind.FILE,
                        file_id,
                        "identity_preserved_after_location_change",
                    )
                )

        result = {
            name: tuple(sorted(files, key=lambda file: file.file_id))
            for name, files in categories.items()
        }
        result.update(
            changed=changed,
            unchanged=unchanged,
            invalidated=invalidated,
            reusable=reusable,
        )
        return result

    def _compare_entities(
        self,
        previous: list[T],
        current: list[T],
        *,
        key: Callable[[T], Hashable],
        state: Callable[[T], Hashable],
        kind: ProjectElementKind,
        changed: list[ProjectElementChange],
        unchanged: list[ProjectElementChange],
        invalidated: list[KnowledgeElementReference],
        reusable: list[KnowledgeElementReference],
        parent_reusable: Callable[[T], bool] | None = None,
    ) -> set[str]:
        previous_by_key = {key(item): item for item in previous}
        current_by_key = {key(item): item for item in current}
        reusable_ids: set[str] = set()

        for identity in sorted(
            set(previous_by_key) | set(current_by_key),
            key=self._identity_text,
        ):
            before = previous_by_key.get(identity)
            after = current_by_key.get(identity)
            element_id = self._identity_text(identity)

            if before is None:
                changed.append(
                    ProjectElementChange(kind, element_id, ProjectChangeKind.NEW)
                )
            elif after is None:
                changed.append(
                    ProjectElementChange(
                        kind, element_id, ProjectChangeKind.REMOVED
                    )
                )
                invalidated.append(self._reference(kind, element_id, "removed"))
            elif state(before) != state(after):
                changed.append(
                    ProjectElementChange(
                        kind, element_id, ProjectChangeKind.MODIFIED
                    )
                )
                invalidated.append(
                    self._reference(kind, element_id, "modified")
                )
            elif parent_reusable is not None and not parent_reusable(after):
                changed.append(
                    ProjectElementChange(
                        kind, element_id, ProjectChangeKind.MODIFIED
                    )
                )
                invalidated.append(
                    self._reference(kind, element_id, "dependency_invalidated")
                )
            else:
                unchanged.append(
                    ProjectElementChange(
                        kind, element_id, ProjectChangeKind.UNCHANGED
                    )
                )
                reusable.append(self._reference(kind, element_id, "unchanged"))
                reusable_ids.add(element_id)

        return reusable_ids

    @staticmethod
    def _identity_text(identity: Hashable) -> str:
        if isinstance(identity, tuple):
            return "::".join(str(part) for part in identity)
        return str(identity)

    @staticmethod
    def _current_path(file: PersistentFileIdentity) -> str | None:
        return next(
            (location.path for location in file.locations if location.is_current),
            None,
        )

    @staticmethod
    def _current_content_hash(file: PersistentFileIdentity) -> str | None:
        return next(
            (
                fingerprint.content_hash
                for fingerprint in file.fingerprints
                if fingerprint.is_current
            ),
            None,
        )

    @staticmethod
    def _movement_kind(
        previous_path: str | None, current_path: str | None
    ) -> ProjectChangeKind:
        if previous_path is None or current_path is None:
            return ProjectChangeKind.MOVED_AND_RENAMED
        previous = PurePosixPath(previous_path)
        current = PurePosixPath(current_path)
        if previous.name == current.name:
            return ProjectChangeKind.MOVED
        if previous.parent == current.parent:
            return ProjectChangeKind.RENAMED
        return ProjectChangeKind.MOVED_AND_RENAMED

    def _file_change(
        self,
        file: PersistentFileIdentity,
        kind: ProjectChangeKind,
        *,
        previous: bool = False,
    ) -> ProjectElementChange:
        path = self._current_path(file)
        return ProjectElementChange(
            ProjectElementKind.FILE,
            file.file_id,
            kind,
            path if previous else None,
            None if previous else path,
        )

    @staticmethod
    def _reference(
        kind: ProjectElementKind, element_id: str, reason: str
    ) -> KnowledgeElementReference:
        return KnowledgeElementReference(kind, element_id, reason)

    @staticmethod
    def _ordered_changes(items):
        return tuple(
            sorted(
                items,
                key=lambda item: (
                    item.element_kind.value,
                    item.element_id,
                    item.change_kind.value,
                ),
            )
        )

    @staticmethod
    def _ordered_references(items):
        return tuple(
            sorted(
                items,
                key=lambda item: (
                    item.element_kind.value,
                    item.element_id,
                    item.reason,
                ),
            )
        )


class KnowledgeDiff:
    """Compatibility adapter for the former file-only diff API."""

    def compare(
        self,
        previous_files: list[PersistentFileIdentity],
        current_files: list[PersistentFileIdentity],
    ) -> KnowledgeDiffResult:
        comparison = ChangeDetectionEngine()._compare_files(
            previous_files, current_files
        )
        return KnowledgeDiffResult(
            added_files=list(comparison["new_files"]),
            modified_files=list(comparison["modified_files"]),
            removed_files=list(comparison["removed_files"]),
            unchanged_files=list(comparison["unchanged_files"]),
            moved_files=list(comparison["moved_files"]),
            renamed_files=list(comparison["renamed_files"]),
            moved_and_renamed_files=list(
                comparison["moved_and_renamed_files"]
            ),
        )
