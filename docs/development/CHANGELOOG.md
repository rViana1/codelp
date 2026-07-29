# Changelog

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