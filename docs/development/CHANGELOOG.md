# Changelog

## v0.4.0

Stable Symbol Index milestone completed.

### Added

- Indexing package
- Stable symbol identifiers
- Relative path strategy
- SymbolKind enum
- SymbolEntry
- FileEntry
- DependencyEntry
- ProjectIndex
- Indexer builders
- Function indexing
- Class indexing
- Method indexing
- Import indexing
- Deterministic indexing order
- ProjectIndexer
- Indexer integration with Project
- Indexer unit tests
- Pipeline integration test
- ADR-005 — Stable Symbol Index

### Changed

- Architecture updated for navigable indexes
- Project index_result now contains files, symbols and dependencies
- Indexing responsibilities separated from parsing responsibilities

### Validation

- 12 indexing tests passing
- 40 total automated tests passing

---

## v0.3.0

Python Parser milestone completed.

### Added

- Parser package
- Language detector
- Python AST parser
- Import extraction
- Function extraction
- Class extraction
- Method extraction
- Method-to-class association
- ParsedFile model
- ParsedProject model
- Parser integration with Project
- Parser diagnostics propagation
- Parser unit tests
- Parser integration tests
- ADR-004 — Python AST Parser

### Changed

- ProjectStatistics now stores scanned_files
- Scanner now propagates scanned files into the Project aggregate
- Architecture updated to include the Parser implementation

### Validation

- 11 parser tests passing
- 28 total automated tests passing

---

## v0.2.2

Project Domain Model and Scanner Integration.

### Added

- Project aggregate root
- ProjectMetadata
- ProjectConfiguration
- ProjectStatistics
- Public domain API (`core.project`)
- Scanner integration with Project
- Safe tree serialization without circular references
- Domain model tests
- Scanner integration tests
- pytest configuration for backend package imports

### Changed

- Scanner can now enrich an existing Project instance
- Project tree stored as a serialization-safe representation
- Architecture updated to use Project as the central aggregate

### Preserved

- Existing `scan()` API
- Existing scanner behaviour
- Existing scanner tests

### Validation

- 17 automated tests passing

---

## v0.2.1

Initial implementation of the Project Scanner.

### Added

- ProjectScanner
- TreeNode
- ScanResult
- ScanFilter
- Deterministic scanning
- Recursive traversal
- Unit tests