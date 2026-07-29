---

# Milestone 2.2 — Project Domain Model

## Objective

Introduce the central `Project` aggregate root and integrate the scanner with the domain model without breaking the existing scanner API.

This milestone established the architectural foundation for all future modules (Parser, Indexer, Chunker, Embeddings and Retrieval).

---

## What Went Well

- The `Project` aggregate created a clear central source of truth.
- Separating metadata, configuration and statistics improved cohesion.
- Timezone-aware UTC handling was introduced from the beginning.
- The scanner was integrated without breaking backwards compatibility.
- Existing scanner tests continued to pass unchanged.
- Integration tests validated the interaction between the scanner and the domain.

---

## Lessons Learned

### Domain First Simplifies Evolution

Introducing a dedicated domain model early makes future modules significantly easier to design.

Instead of connecting modules directly, every module enriches the same `Project` instance.

---

### Preserve Stable APIs When Evolving Architecture

The original `scan()` API remained untouched.

Adding a new `scan_project()` method was safer than replacing the existing contract.

Incremental architectural evolution is usually less risky than disruptive redesign.

---

### Rich Domain Models Need Clear Boundaries

The domain should store knowledge, not implementation details.

The scanner owns `TreeNode`; the domain stores a serialization-safe representation of the tree.

Keeping this boundary explicit prevents accidental coupling.

---

### Circular References Become a Real Problem Quickly

The `parent` reference in `TreeNode` created circular serialization issues.

Navigation models and persistence models are often different concerns.

A dedicated serialization step solved the problem while preserving navigation capabilities.

---

### Default Factories Prevent Shared Mutable State

Pydantic `Field(default_factory=...)` was essential for sets, lists and nested models.

This avoided shared mutable state between `Project` instances.

---

### Timezone Awareness Should Be Decided Early

Using `datetime.now(timezone.utc)` from the beginning prevents future migration problems.

Timezone-aware timestamps should be the default for all persistent project data.

---

### Package Structure Matters

The integration tests revealed that a clear package root and a configured `pytest.ini` are necessary for reliable imports.

Import strategy should be defined early and applied consistently across the project.

---

## Architectural Decisions Reinforced

- `Project` is the Aggregate Root.
- The domain depends on no application modules.
- Application modules may depend on the domain.
- Scanner enriches the `Project` instead of communicating with future modules.
- Tree serialization excludes parent references.
- Backwards compatibility is preserved during architectural evolution.

---

## Future Improvements Identified

### Domain

- Dedicated `ProjectTree` domain model.
- Stronger validation rules.
- Immutable metadata sections.

### Scanner Integration

- Make `scan_project()` the primary public API.
- Incremental tree updates.
- Change tracking between scans.

### Knowledge Persistence

- Persist serialized trees.
- Store scan snapshots.
- Track repository evolution over time.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (17 automated tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 3 — Parser.