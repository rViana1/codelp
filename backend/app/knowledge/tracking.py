"""Identity tracking orchestration for project knowledge executions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.knowledge.identity import (
    DuplicateFileContent,
    FileIdentityDecision,
    FileIdentityResolver,
    FileIdentityResolutionResult,
    FileObservation,
    IdentityConflict,
    SymbolIdentityResolver,
)
from app.knowledge.models import (
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileIdentity,
    PersistentSymbolIdentity,
)


@dataclass(frozen=True)
class DuplicateSymbol:
    """Symbols with the same type and name in different files."""

    name: str
    symbol_type: str
    file_ids: tuple[str, ...]
    symbol_ids: tuple[str, ...]


@dataclass(frozen=True)
class IdentityTrackingResult:
    """Deterministic and auditable result of one tracking execution."""

    files: tuple[PersistentFileIdentity, ...]
    symbols: tuple[PersistentSymbolIdentity, ...]
    source_symbol_identities: tuple[tuple[str, str], ...]
    file_decisions: tuple[FileIdentityDecision, ...]
    duplicated_file_contents: tuple[DuplicateFileContent, ...]
    duplicated_symbols: tuple[DuplicateSymbol, ...]
    conflicts: tuple[IdentityConflict, ...]
    known_file_ids: tuple[str, ...]
    known_symbol_ids: tuple[str, ...]
    known_chunk_ids: tuple[str, ...]
    known_embedding_identities: tuple[tuple[str, str], ...]

    @property
    def source_symbol_identity_map(self) -> dict[str, str]:
        return dict(self.source_symbol_identities)


class IdentityTrackingEngine:
    """Tracks known entities and resolves a new analysis execution.

    The engine owns identity decisions. Analysis components continue to
    produce execution-local paths and identifiers and remain unaware of
    persistence or historical tracking.
    """

    def __init__(
        self,
        file_resolver: FileIdentityResolver | None = None,
        symbol_resolver: SymbolIdentityResolver | None = None,
    ) -> None:
        self.file_resolver = file_resolver or FileIdentityResolver()
        self.symbol_resolver = symbol_resolver or SymbolIdentityResolver()

    def track_files(
        self,
        *,
        project_id: str,
        observations: list[FileObservation],
        previous_files: list[PersistentFileIdentity],
        now: datetime,
    ) -> FileIdentityResolutionResult:
        """Resolve file identities before semantic analysis begins."""
        return self.file_resolver.resolve_with_report(
            previous_files,
            observations,
            project_id,
            now,
        )

    def track_symbols(
        self,
        *,
        resolved_files: list[PersistentFileIdentity],
        source_symbols: list[PersistentSymbolIdentity],
        previous_symbols: list[PersistentSymbolIdentity],
        project_id: str,
    ) -> tuple[list[PersistentSymbolIdentity], dict[str, str]]:
        """Resolve symbols against file identities fixed by the lifecycle."""
        file_identity_by_path = {
            location.path: file.file_id
            for file in resolved_files
            for location in file.locations
            if location.is_current
        }
        return self.symbol_resolver.resolve(
            source_symbols,
            file_identity_by_path,
            previous_symbols,
            project_id,
        )

    def track(
        self,
        *,
        project_id: str,
        observations: list[FileObservation],
        source_symbols: list[PersistentSymbolIdentity],
        previous_files: list[PersistentFileIdentity],
        previous_symbols: list[PersistentSymbolIdentity],
        previous_chunks: list[PersistentChunkIdentity] | None = None,
        previous_embeddings: (
            list[PersistentEmbeddingMetadata] | None
        ) = None,
        now: datetime,
    ) -> IdentityTrackingResult:
        file_result = self.track_files(
            project_id=project_id,
            observations=observations,
            previous_files=previous_files,
            now=now,
        )
        symbols, source_map = self.track_symbols(
            resolved_files=list(file_result.files),
            source_symbols=source_symbols,
            previous_symbols=previous_symbols,
            project_id=project_id,
        )
        ordered_symbols = tuple(
            sorted(symbols, key=lambda symbol: symbol.symbol_id)
        )

        return IdentityTrackingResult(
            files=file_result.files,
            symbols=ordered_symbols,
            source_symbol_identities=tuple(sorted(source_map.items())),
            file_decisions=file_result.decisions,
            duplicated_file_contents=file_result.duplicated_contents,
            duplicated_symbols=self._duplicated_symbols(
                ordered_symbols
            ),
            conflicts=file_result.conflicts,
            known_file_ids=file_result.known_file_ids,
            known_symbol_ids=tuple(
                sorted(symbol.symbol_id for symbol in previous_symbols)
            ),
            known_chunk_ids=tuple(
                sorted(
                    chunk.chunk_id
                    for chunk in previous_chunks or []
                )
            ),
            known_embedding_identities=tuple(
                sorted(
                    (embedding.chunk_id, embedding.provider)
                    for embedding in previous_embeddings or []
                )
            ),
        )

    @staticmethod
    def _duplicated_symbols(
        symbols: tuple[PersistentSymbolIdentity, ...],
    ) -> tuple[DuplicateSymbol, ...]:
        symbols_by_key: dict[
            tuple[str, str],
            list[PersistentSymbolIdentity],
        ] = {}
        for symbol in symbols:
            symbols_by_key.setdefault(
                (symbol.symbol_type, symbol.name),
                [],
            ).append(symbol)

        duplicates = []
        for (symbol_type, name), matches in sorted(
            symbols_by_key.items()
        ):
            distinct_file_ids = {
                symbol.file_id
                for symbol in matches
            }
            if len(distinct_file_ids) < 2:
                continue
            duplicates.append(
                DuplicateSymbol(
                    name=name,
                    symbol_type=symbol_type,
                    file_ids=tuple(sorted(distinct_file_ids)),
                    symbol_ids=tuple(
                        sorted(symbol.symbol_id for symbol in matches)
                    ),
                )
            )

        return tuple(duplicates)
