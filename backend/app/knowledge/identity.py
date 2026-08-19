"""Deterministic identity resolution for persistent knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import PurePosixPath
from uuid import NAMESPACE_URL, uuid5

from app.knowledge.models import (
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentSymbolIdentity,
)


@dataclass(frozen=True)
class FileObservation:
    """The canonical current state observed for one scanned file."""

    path: str
    content_hash: str
    size_bytes: int


class FileIdentityDecisionKind(str, Enum):
    NEW = "new"
    EXISTING = "existing"
    MODIFIED = "modified"
    MOVED = "moved"
    RENAMED = "renamed"
    MOVED_AND_RENAMED = "moved_and_renamed"
    REAPPEARED = "reappeared"
    REMOVED = "removed"
    CONFLICT_NEW = "conflict_new"


@dataclass(frozen=True)
class FileIdentityDecision:
    """Auditable deterministic decision for one current or removed file."""

    path: str
    file_id: str
    kind: FileIdentityDecisionKind
    confidence: float
    previous_path: str | None = None


@dataclass(frozen=True)
class IdentityConflict:
    """Ambiguous candidates resolved conservatively as a new identity."""

    path: str
    conflict_type: str
    candidate_file_ids: tuple[str, ...]
    resolution: str = "created_new_identity"


@dataclass(frozen=True)
class DuplicateFileContent:
    """Current files sharing the same content fingerprint."""

    content_hash: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class FileIdentityResolutionResult:
    files: tuple[PersistentFileIdentity, ...]
    decisions: tuple[FileIdentityDecision, ...]
    duplicated_contents: tuple[DuplicateFileContent, ...]
    conflicts: tuple[IdentityConflict, ...]
    known_file_ids: tuple[str, ...]


def deterministic_identity(
    project_id: str,
    entity_type: str,
    *parts: str,
) -> str:
    """Create a deterministic, project-scoped persistent identifier."""

    value = ":".join(("codelp", project_id, entity_type, *parts))
    return str(uuid5(NAMESPACE_URL, value))


class FileIdentityResolver:
    """Reconciles a scan with previous historical file identities.

    Resolution is intentionally conservative.  A current location wins;
    otherwise an identity is reused only when exactly one *unobserved*
    previous file has the same current content fingerprint.  This detects
    an unchanged move or rename without merging files that merely share
    identical content.
    """

    def resolve(
        self,
        previous_files: list[PersistentFileIdentity],
        observations: list[FileObservation],
        project_id: str,
        now: datetime,
    ) -> list[PersistentFileIdentity]:
        return list(
            self.resolve_with_report(
                previous_files,
                observations,
                project_id,
                now,
            ).files
        )

    def resolve_with_report(
        self,
        previous_files: list[PersistentFileIdentity],
        observations: list[FileObservation],
        project_id: str,
        now: datetime,
    ) -> FileIdentityResolutionResult:
        ordered_observations = sorted(
            observations,
            key=lambda observation: observation.path,
        )
        observed_paths = {
            observation.path
            for observation in ordered_observations
        }
        resolved_ids: set[str] = set()
        result: list[PersistentFileIdentity] = []
        decisions: list[FileIdentityDecision] = []
        conflicts: list[IdentityConflict] = []

        for observation in ordered_observations:
            exact_matches = [
                file
                for file in previous_files
                if file.file_id not in resolved_ids
                and any(
                    location.is_current
                    and location.path == observation.path
                    for location in file.locations
                )
            ]

            candidates: list[PersistentFileIdentity] = []
            conflict_type = None

            if len(exact_matches) == 1:
                existing = exact_matches[0]
                previous_path = observation.path
                kind = (
                    FileIdentityDecisionKind.EXISTING
                    if self._current_content_hash(existing)
                    == observation.content_hash
                    else FileIdentityDecisionKind.MODIFIED
                )
                confidence = 1.0
            else:
                candidates = [
                    file
                    for file in previous_files
                    if file.file_id not in resolved_ids
                    and self._is_unobserved(file, observed_paths)
                    and self._current_content_hash(file)
                    == observation.content_hash
                ]
                if len(exact_matches) > 1:
                    existing = None
                    conflict_type = "ambiguous_current_path"
                    candidates = exact_matches
                elif len(candidates) == 1:
                    existing = candidates[0]
                    previous_path = self._current_path(existing)
                    kind = self._movement_kind(
                        previous_path,
                        observation.path,
                    )
                    confidence = 0.9
                else:
                    existing = None
                    if len(candidates) > 1:
                        conflict_type = "ambiguous_fingerprint"

            if existing is None:
                new_file = self._new_file(
                    observation,
                    project_id,
                    now,
                )
                result.append(new_file)
                decision_kind = (
                    FileIdentityDecisionKind.CONFLICT_NEW
                    if conflict_type is not None
                    else FileIdentityDecisionKind.NEW
                )
                decisions.append(
                    FileIdentityDecision(
                        path=observation.path,
                        file_id=new_file.file_id,
                        kind=decision_kind,
                        confidence=1.0,
                    )
                )
                if conflict_type is not None:
                    conflicts.append(
                        IdentityConflict(
                            path=observation.path,
                            conflict_type=conflict_type,
                            candidate_file_ids=tuple(
                                sorted(
                                    file.file_id
                                    for file in candidates
                                )
                            ),
                        )
                    )
                continue

            resolved_ids.add(existing.file_id)
            result.append(
                self._updated_file(
                    existing,
                    observation,
                    now,
                )
            )
            decisions.append(
                FileIdentityDecision(
                    path=observation.path,
                    file_id=existing.file_id,
                    kind=kind,
                    confidence=confidence,
                    previous_path=previous_path,
                )
            )

        for previous in previous_files:
            if previous.file_id not in resolved_ids:
                result.append(self._mark_removed(previous))
                previous_path = self._current_path(previous)
                if previous_path is not None:
                    decisions.append(
                        FileIdentityDecision(
                            path=previous_path,
                            file_id=previous.file_id,
                            kind=FileIdentityDecisionKind.REMOVED,
                            confidence=1.0,
                            previous_path=previous_path,
                        )
                    )

        return FileIdentityResolutionResult(
            files=tuple(sorted(result, key=lambda file: file.file_id)),
            decisions=tuple(
                sorted(
                    decisions,
                    key=lambda decision: (
                        decision.path,
                        decision.kind.value,
                        decision.file_id,
                    ),
                )
            ),
            duplicated_contents=self._duplicated_contents(
                ordered_observations
            ),
            conflicts=tuple(
                sorted(
                    conflicts,
                    key=lambda conflict: (
                        conflict.path,
                        conflict.conflict_type,
                        conflict.candidate_file_ids,
                    ),
                )
            ),
            known_file_ids=tuple(
                sorted(file.file_id for file in previous_files)
            ),
        )

    @staticmethod
    def _current_path(
        file: PersistentFileIdentity,
    ) -> str | None:
        return next(
            (
                location.path
                for location in file.locations
                if location.is_current
            ),
            None,
        )

    @staticmethod
    def _movement_kind(
        previous_path: str | None,
        current_path: str,
    ) -> FileIdentityDecisionKind:
        if previous_path is None:
            return FileIdentityDecisionKind.REAPPEARED

        previous = PurePosixPath(previous_path)
        current = PurePosixPath(current_path)
        same_parent = previous.parent == current.parent
        same_name = previous.name == current.name

        if same_name and not same_parent:
            return FileIdentityDecisionKind.MOVED
        if same_parent and not same_name:
            return FileIdentityDecisionKind.RENAMED
        return FileIdentityDecisionKind.MOVED_AND_RENAMED

    @staticmethod
    def _duplicated_contents(
        observations: list[FileObservation],
    ) -> tuple[DuplicateFileContent, ...]:
        paths_by_hash: dict[str, list[str]] = {}
        for observation in observations:
            paths_by_hash.setdefault(
                observation.content_hash,
                [],
            ).append(observation.path)

        return tuple(
            DuplicateFileContent(
                content_hash=content_hash,
                paths=tuple(sorted(paths)),
            )
            for content_hash, paths in sorted(paths_by_hash.items())
            if len(paths) > 1
        )

    @staticmethod
    def _is_unobserved(
        file: PersistentFileIdentity,
        observed_paths: set[str],
    ) -> bool:
        return all(
            not location.is_current
            or location.path not in observed_paths
            for location in file.locations
        )

    @staticmethod
    def _current_content_hash(
        file: PersistentFileIdentity,
    ) -> str | None:
        current = next(
            (
                fingerprint.content_hash
                for fingerprint in file.fingerprints
                if fingerprint.is_current
            ),
            None,
        )
        if current is not None:
            return current
        if file.fingerprints:
            return file.fingerprints[-1].content_hash
        return None

    @staticmethod
    def _new_file(
        observation: FileObservation,
        project_id: str,
        now: datetime,
    ) -> PersistentFileIdentity:
        return PersistentFileIdentity(
            file_id=deterministic_identity(
                project_id,
                "file",
                observation.path,
                observation.content_hash,
            ),
            locations=[
                PersistentFileLocation(
                    path=observation.path,
                    first_seen=now,
                    last_seen=now,
                    is_current=True,
                )
            ],
            fingerprints=[
                PersistentFileFingerprint(
                    content_hash=observation.content_hash,
                    size_bytes=observation.size_bytes,
                    generated_at=now,
                    last_seen=now,
                    is_current=True,
                )
            ],
        )

    def _updated_file(
        self,
        existing: PersistentFileIdentity,
        observation: FileObservation,
        now: datetime,
    ) -> PersistentFileIdentity:
        locations = [
            PersistentFileLocation(
                path=location.path,
                first_seen=location.first_seen,
                last_seen=(
                    now
                    if location.path == observation.path
                    else location.last_seen
                ),
                is_current=location.path == observation.path,
            )
            for location in existing.locations
        ]

        if not any(
            location.path == observation.path
            for location in locations
        ):
            locations.append(
                PersistentFileLocation(
                    path=observation.path,
                    first_seen=now,
                    last_seen=now,
                    is_current=True,
                )
            )

        fingerprints = []
        found_fingerprint = False
        for fingerprint in existing.fingerprints:
            is_current = (
                fingerprint.content_hash == observation.content_hash
            )
            found_fingerprint = found_fingerprint or is_current
            fingerprints.append(
                PersistentFileFingerprint(
                    content_hash=fingerprint.content_hash,
                    size_bytes=fingerprint.size_bytes,
                    generated_at=fingerprint.generated_at,
                    last_seen=(
                        now
                        if is_current
                        else fingerprint.last_seen
                    ),
                    is_current=is_current,
                )
            )

        if not found_fingerprint:
            fingerprints.append(
                PersistentFileFingerprint(
                    content_hash=observation.content_hash,
                    size_bytes=observation.size_bytes,
                    generated_at=now,
                    last_seen=now,
                    is_current=True,
                )
            )

        return PersistentFileIdentity(
            file_id=existing.file_id,
            locations=locations,
            fingerprints=fingerprints,
        )

    @staticmethod
    def _mark_removed(
        file: PersistentFileIdentity,
    ) -> PersistentFileIdentity:
        return PersistentFileIdentity(
            file_id=file.file_id,
            locations=[
                PersistentFileLocation(
                    path=location.path,
                    first_seen=location.first_seen,
                    last_seen=location.last_seen,
                    is_current=False,
                )
                for location in file.locations
            ],
            fingerprints=[
                PersistentFileFingerprint(
                    content_hash=fingerprint.content_hash,
                    size_bytes=fingerprint.size_bytes,
                    generated_at=fingerprint.generated_at,
                    last_seen=fingerprint.last_seen,
                    is_current=False,
                )
                for fingerprint in file.fingerprints
            ],
        )


class SymbolIdentityResolver:
    """Assign stable symbol identities after file identity resolution."""

    def resolve(
        self,
        symbols: list[PersistentSymbolIdentity],
        file_identity_by_path: dict[str, str],
        previous_symbols: list[PersistentSymbolIdentity],
        project_id: str,
    ) -> tuple[list[PersistentSymbolIdentity], dict[str, str]]:
        previous_by_key: dict[
            tuple[str, str, str],
            list[PersistentSymbolIdentity],
        ] = {}
        for previous in previous_symbols:
            key = (
                previous.file_id,
                previous.name,
                previous.symbol_type,
            )
            previous_by_key.setdefault(key, []).append(previous)

        resolved = []
        source_to_persistent: dict[str, str] = {}
        for symbol in sorted(symbols, key=lambda item: item.symbol_id):
            file_id = file_identity_by_path.get(
                symbol.file_id,
                symbol.file_id,
            )
            key = (file_id, symbol.name, symbol.symbol_type)
            candidates = previous_by_key.get(key, [])
            symbol_id = (
                candidates[0].symbol_id
                if len(candidates) == 1
                else deterministic_identity(
                    project_id,
                    "symbol",
                    file_id,
                    symbol.symbol_type,
                    symbol.name,
                )
            )
            resolved.append(
                PersistentSymbolIdentity(
                    symbol_id=symbol_id,
                    file_id=file_id,
                    name=symbol.name,
                    symbol_type=symbol.symbol_type,
                )
            )
            source_to_persistent[symbol.symbol_id] = symbol_id

        return resolved, source_to_persistent
