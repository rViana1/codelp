"""Pre-analysis planning owned by the Knowledge lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from core.project import Project

from app.knowledge.cache import IncrementalAnalysisCache
from app.knowledge.diff import (
    ChangeDetectionEngine,
    FileChangeReport,
    ProjectChangeKind,
)
from app.knowledge.hash import FileContentHasher
from app.knowledge.identity import (
    DuplicateFileContent,
    FileIdentityDecision,
    FileObservation,
    IdentityConflict,
)
from app.knowledge.models import (
    PersistentFileIdentity,
    PersistentProjectKnowledge,
)
from app.knowledge.tracking import IdentityTrackingEngine


class FileAnalysisAction(str, Enum):
    ANALYZE = "analyze"
    REUSE = "reuse"


@dataclass(frozen=True)
class FileAnalysisInstruction:
    """Persistence-independent instruction consumed by the pipeline."""

    path: str
    file_id: str
    action: FileAnalysisAction
    change_kind: ProjectChangeKind


@dataclass(frozen=True)
class KnowledgeAnalysisPlan:
    """Identity and change decisions available before semantic analysis."""

    project_id: str
    incremental: bool
    instructions: tuple[FileAnalysisInstruction, ...]
    removed_file_ids: tuple[str, ...]
    resolved_files: tuple[PersistentFileIdentity, ...]
    identity_decisions: tuple[FileIdentityDecision, ...]
    conflicts: tuple[IdentityConflict, ...]
    duplicated_file_contents: tuple[DuplicateFileContent, ...]
    file_changes: FileChangeReport
    cache: IncrementalAnalysisCache | None

    @property
    def analyzed_paths(self) -> tuple[str, ...]:
        return tuple(
            instruction.path
            for instruction in self.instructions
            if instruction.action == FileAnalysisAction.ANALYZE
        )

    @property
    def reused_paths(self) -> tuple[str, ...]:
        return tuple(
            instruction.path
            for instruction in self.instructions
            if instruction.action == FileAnalysisAction.REUSE
        )


class KnowledgeExecutionPlanner:
    """Resolve identity and detect file changes after scan, before analysis."""

    def __init__(
        self,
        identity_tracker: IdentityTrackingEngine | None = None,
        change_detector: ChangeDetectionEngine | None = None,
    ) -> None:
        self.identity_tracker = identity_tracker or IdentityTrackingEngine()
        self.change_detector = change_detector or ChangeDetectionEngine()

    def create_plan(
        self,
        *,
        project: Project,
        previous: PersistentProjectKnowledge | None,
        cache: IncrementalAnalysisCache | None,
        now: datetime | None = None,
    ) -> KnowledgeAnalysisPlan:
        project_id = project.metadata.root_path.name
        observations = [
            FileObservation(
                path=self._relative_path(
                    project.metadata.root_path,
                    path,
                ),
                content_hash=FileContentHasher.hash_file(path),
                size_bytes=path.stat().st_size,
            )
            for path in project.statistics.scanned_files
        ]
        resolution = self.identity_tracker.track_files(
            project_id=project_id,
            observations=observations,
            previous_files=previous.files if previous is not None else [],
            now=now or datetime.now(timezone.utc),
        )
        file_changes = self.change_detector.compare_files(
            previous.files if previous is not None else [],
            list(resolution.files),
        )

        compatible_cache = (
            cache
            if previous is not None
            and cache is not None
            and cache.version == "1.0"
            and cache.project_id == project_id
            else None
        )
        cache_by_file_id = {
            item.file_id: item
            for item in compatible_cache.files
        } if compatible_cache is not None else {}
        kind_by_file_id = self._change_kinds(file_changes)

        instructions = []
        for file in resolution.files:
            path = self._current_path(file)
            if path is None:
                continue
            kind = kind_by_file_id[file.file_id]
            cached = cache_by_file_id.get(file.file_id)
            reusable = (
                kind
                in {
                    ProjectChangeKind.UNCHANGED,
                    ProjectChangeKind.MOVED,
                    ProjectChangeKind.RENAMED,
                    ProjectChangeKind.MOVED_AND_RENAMED,
                }
                and cached is not None
                and cached.content_hash == self._current_hash(file)
            )
            instructions.append(
                FileAnalysisInstruction(
                    path=path,
                    file_id=file.file_id,
                    action=(
                        FileAnalysisAction.REUSE
                        if reusable
                        else FileAnalysisAction.ANALYZE
                    ),
                    change_kind=kind,
                )
            )

        return KnowledgeAnalysisPlan(
            project_id=project_id,
            incremental=(
                previous is not None and compatible_cache is not None
            ),
            instructions=tuple(
                sorted(instructions, key=lambda item: item.path)
            ),
            removed_file_ids=tuple(
                sorted(file.file_id for file in file_changes.removed_files)
            ),
            resolved_files=resolution.files,
            identity_decisions=resolution.decisions,
            conflicts=resolution.conflicts,
            duplicated_file_contents=resolution.duplicated_contents,
            file_changes=file_changes,
            cache=compatible_cache,
        )

    @staticmethod
    def _change_kinds(
        report: FileChangeReport,
    ) -> dict[str, ProjectChangeKind]:
        result = {}
        for kind, files in (
            (ProjectChangeKind.NEW, report.new_files),
            (ProjectChangeKind.MOVED, report.moved_files),
            (ProjectChangeKind.RENAMED, report.renamed_files),
            (
                ProjectChangeKind.MOVED_AND_RENAMED,
                report.moved_and_renamed_files,
            ),
            (ProjectChangeKind.MODIFIED, report.modified_files),
            (ProjectChangeKind.UNCHANGED, report.unchanged_files),
        ):
            for file in files:
                result[file.file_id] = kind
        return result

    @staticmethod
    def _current_path(file: PersistentFileIdentity) -> str | None:
        return next(
            (
                location.path
                for location in file.locations
                if location.is_current
            ),
            None,
        )

    @staticmethod
    def _current_hash(file: PersistentFileIdentity) -> str | None:
        return next(
            (
                fingerprint.content_hash
                for fingerprint in file.fingerprints
                if fingerprint.is_current
            ),
            None,
        )

    @staticmethod
    def _relative_path(root: Path, path: Path) -> str:
        return path.resolve().relative_to(root.resolve()).as_posix()
