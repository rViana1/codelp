"""Deterministic merge policy for authoritative knowledge snapshots."""

from __future__ import annotations

from collections.abc import Callable
from typing import Hashable, TypeVar

from app.knowledge.models import (
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


T = TypeVar("T")


class KnowledgeUpdateEngine:
    """Merge an analyzed snapshot with its persisted predecessor.

    The analyzed snapshot is authoritative for current derived entities.
    Missing symbols, chunks, embeddings and retrieval entries are obsolete
    and are removed. File identities are different: their location and
    fingerprint histories are durable and are never discarded.
    """

    def merge(
        self,
        previous: PersistentProjectKnowledge | None,
        current: PersistentProjectKnowledge,
    ) -> PersistentProjectKnowledge:
        if previous is None:
            return self._ordered_copy(current)
        if previous.metadata.project_id != current.metadata.project_id:
            raise ValueError("Cannot merge knowledge from different projects")

        previous_files = self._index_unique(
            previous.files,
            key=lambda file: file.file_id,
            label="file identity",
        )
        current_files = self._index_unique(
            current.files,
            key=lambda file: file.file_id,
            label="file identity",
        )
        files = [
            self._merge_file(
                previous_files.get(file_id),
                current_files.get(file_id),
            )
            for file_id in sorted(set(previous_files) | set(current_files))
        ]

        return PersistentProjectKnowledge(
            metadata=PersistentKnowledgeMetadata(
                project_id=current.metadata.project_id,
                version=current.metadata.version,
                created_at=previous.metadata.created_at,
                updated_at=current.metadata.updated_at,
            ),
            configuration=current.configuration.model_copy(deep=True),
            files=files,
            symbols=self._merge_authoritative(
                previous.symbols,
                current.symbols,
                key=lambda item: item.symbol_id,
            ),
            chunks=self._merge_authoritative(
                previous.chunks,
                current.chunks,
                key=lambda item: item.chunk_id,
            ),
            embeddings=self._merge_authoritative(
                previous.embeddings,
                current.embeddings,
                key=lambda item: (item.chunk_id, item.provider),
            ),
            retrieval=self._merge_authoritative(
                previous.retrieval,
                current.retrieval,
                key=lambda item: (item.chunk_id, item.query_hash),
            ),
        )

    def _merge_file(
        self,
        previous: PersistentFileIdentity | None,
        current: PersistentFileIdentity | None,
    ) -> PersistentFileIdentity:
        source = current or previous
        if source is None:
            raise ValueError("File merge requires at least one identity")

        previous_locations = self._index_unique(
            previous.locations if previous is not None else [],
            key=lambda item: item.path,
            label="file location",
        )
        current_locations = self._index_unique(
            current.locations if current is not None else [],
            key=lambda item: item.path,
            label="file location",
        )
        locations = []
        for path in sorted(set(previous_locations) | set(current_locations)):
            before = previous_locations.get(path)
            after = current_locations.get(path)
            item = after or before
            locations.append(
                PersistentFileLocation(
                    path=item.path,
                    first_seen=(
                        min(before.first_seen, after.first_seen)
                        if before is not None and after is not None
                        else item.first_seen
                    ),
                    last_seen=(
                        max(before.last_seen, after.last_seen)
                        if before is not None and after is not None
                        else item.last_seen
                    ),
                    is_current=after.is_current if after is not None else False,
                )
            )

        previous_fingerprints = self._index_unique(
            previous.fingerprints if previous is not None else [],
            key=lambda item: item.content_hash,
            label="file fingerprint",
        )
        current_fingerprints = self._index_unique(
            current.fingerprints if current is not None else [],
            key=lambda item: item.content_hash,
            label="file fingerprint",
        )
        fingerprints = []
        for content_hash in sorted(
            set(previous_fingerprints) | set(current_fingerprints)
        ):
            before = previous_fingerprints.get(content_hash)
            after = current_fingerprints.get(content_hash)
            item = after or before
            fingerprints.append(
                PersistentFileFingerprint(
                    content_hash=item.content_hash,
                    size_bytes=item.size_bytes,
                    generated_at=(
                        min(before.generated_at, after.generated_at)
                        if before is not None and after is not None
                        else item.generated_at
                    ),
                    last_seen=(
                        max(before.last_seen, after.last_seen)
                        if before is not None and after is not None
                        else item.last_seen
                    ),
                    is_current=after.is_current if after is not None else False,
                )
            )

        return PersistentFileIdentity(
            file_id=source.file_id,
            locations=sorted(
                locations,
                key=lambda item: (item.first_seen, item.path),
            ),
            fingerprints=sorted(
                fingerprints,
                key=lambda item: (item.generated_at, item.content_hash),
            ),
        )

    @staticmethod
    def _merge_authoritative(
        previous: list[T],
        current: list[T],
        *,
        key: Callable[[T], Hashable],
    ) -> list[T]:
        previous_by_key = KnowledgeUpdateEngine._index_unique(
            previous,
            key=key,
            label="knowledge identity",
        )
        current_by_key = KnowledgeUpdateEngine._index_unique(
            current,
            key=key,
            label="knowledge identity",
        )
        merged = []
        for identity in sorted(current_by_key, key=str):
            current_item = current_by_key[identity]
            previous_item = previous_by_key.get(identity)
            source = (
                previous_item
                if previous_item == current_item
                else current_item
            )
            merged.append(source.model_copy(deep=True))
        return merged

    @staticmethod
    def _index_unique(
        items: list[T],
        *,
        key: Callable[[T], Hashable],
        label: str,
    ) -> dict[Hashable, T]:
        result = {}
        for item in items:
            identity = key(item)
            if identity in result:
                raise ValueError(f"Duplicate {label} detected: {identity}")
            result[identity] = item
        return result

    def _ordered_copy(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> PersistentProjectKnowledge:
        files_by_id = self._index_unique(
            knowledge.files,
            key=lambda item: item.file_id,
            label="file identity",
        )
        return PersistentProjectKnowledge(
            metadata=knowledge.metadata.model_copy(deep=True),
            configuration=knowledge.configuration.model_copy(deep=True),
            files=[
                self._merge_file(None, files_by_id[file_id])
                for file_id in sorted(files_by_id)
            ],
            symbols=self._merge_authoritative(
                [], knowledge.symbols, key=lambda item: item.symbol_id
            ),
            chunks=self._merge_authoritative(
                [], knowledge.chunks, key=lambda item: item.chunk_id
            ),
            embeddings=self._merge_authoritative(
                [],
                knowledge.embeddings,
                key=lambda item: (item.chunk_id, item.provider),
            ),
            retrieval=self._merge_authoritative(
                [],
                knowledge.retrieval,
                key=lambda item: (item.chunk_id, item.query_hash),
            ),
        )
