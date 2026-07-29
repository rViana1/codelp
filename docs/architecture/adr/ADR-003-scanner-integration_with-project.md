```markdown
# ADR-003 — Scanner Integration with Project

**Status:** Accepted

**Date:** 2026-07-29

---

# Context

The initial implementation of the scanner was completed during Milestone 2.1.

The scanner exposed a single public API:

```python
scan(root: Path) -> ScanResult
```

This API was already covered by automated tests and represented a stable contract.

During Milestone 2.2 the `Project` aggregate root was introduced as the central domain entity of Codelp.

The architecture requires that future modules (Parser, Indexer, Chunker and Embeddings) communicate through the `Project` aggregate instead of depending directly on each other.

The scanner therefore needed to integrate with the domain model without breaking the existing public API.

---

# Decision

The existing scanner API will be preserved.

```python
scan(root: Path) -> ScanResult
```

This method remains the low-level scanning API.

A new domain-oriented API is introduced.

```python
scan_project(project: Project) -> Project
```

This method:

- reuses the existing `scan()` implementation;
- updates the `Project` aggregate;
- returns the same `Project` instance.

The scanner continues to be responsible only for project discovery.

It does not perform:

- parsing;
- indexing;
- chunking;
- embedding generation;
- retrieval.

When updating the `Project` aggregate, the project tree is converted into a serialization-safe dictionary representation that excludes parent references.

---

# Consequences

## Advantages

Backwards compatibility is preserved.

Existing scanner tests remain valid.

The `Project` aggregate becomes the single source of truth.

Future modules can operate on the same domain object.

Tree serialization becomes deterministic and JSON-friendly.

---

## Disadvantages

Two public scanner APIs now exist (`scan` and `scan_project`).

The domain currently stores a serialized tree instead of a dedicated domain tree model.

---

# Implementation

The scanner updates the following domain fields:

- `project.statistics.files`
- `project.statistics.directories`
- `project.statistics.scan_duration_seconds`
- `project.root_tree`
- `project.diagnostics`

Tree serialization is performed through a dedicated helper that removes circular references created by parent links.

---

# Validation

The decision was validated through automated tests.

Current test coverage:

- 7 domain tests
- 9 scanner tests
- 1 scanner integration test

Total: 17 passing tests.

---

# Future Review

Review whether `scan_project()` should become the primary public scanner API during Milestone 3.

Review the introduction of a dedicated `ProjectTree` domain model during Milestone 4.

Review incremental persistence of the serialized tree during Milestone 5.
```