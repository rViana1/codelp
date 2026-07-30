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


---

# Milestone 3 — Python Parser

## Objective

Implement the first production-ready parser capable of transforming Python source files into structured knowledge integrated with the Project aggregate.

The parser extracts imports, top-level functions, classes and methods while remaining independent from Scanner internals.

---

## What Went Well

- The parser architecture remained highly modular.
- Separating detection, parsing, visitors and orchestration simplified testing.
- The dual API (`parse_file` and `parse_project`) proved consistent with the Scanner architecture.
- AST visitors avoided large monolithic parsing logic.
- Diagnostics propagation allowed project parsing to continue even when some files could not be parsed.
- Integration with the Project aggregate required minimal changes to the existing architecture.

---

## Lessons Learned

### Keep Extraction Separate from Traversal

Using dedicated AST visitors made symbol extraction easier to understand, test and evolve.

Traversal logic and extraction logic should remain independent.

---

### Top-Level Functions and Methods Are Different Concepts

A generic `visit_FunctionDef` initially risked extracting class methods as top-level functions.

Being explicit about extraction boundaries prevents symbol duplication and simplifies future indexing.

---

### A Minimal Symbol Model Is Often Enough

Only names and ownership information were required to unlock the next milestone.

Decorators, docstrings, line ranges and inheritance can be added later without changing the overall architecture.

---

### Domain APIs and Technical APIs Serve Different Purposes

`parse_file()` is ideal for unit tests and debugging.

`parse_project()` is ideal for orchestration and domain enrichment.

Maintaining both APIs increases flexibility without adding significant complexity.

---

### Unsupported Languages Should Produce Diagnostics, Not Failures

Repositories are frequently multi-language.

Recording diagnostics instead of raising exceptions keeps the pipeline robust while preserving visibility of what was not analysed.

---

### Ownership Information Becomes Important Earlier Than Expected

Adding `class_name` to `MethodSymbol` is a small change with significant future value for indexing, references and navigation.

---

### Determinism Must Be Preserved Across the Pipeline

The parser preserves the deterministic ordering already established by the Scanner.

Stable ordering is important for testing, caching and future persistent project knowledge.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Parser does not depend on Scanner internals.
- Visitors implement symbol extraction.
- Technical and domain APIs coexist.
- Diagnostics are propagated through the Project aggregate.
- Symbol extraction remains intentionally minimal.

---

## Future Improvements Identified

### Symbol Metadata

- decorators
- docstrings
- line ranges
- async functions
- class inheritance

### Indexing Support

- stable symbol identifiers
- fully-qualified names
- cross-file references

### Multi-language Parsing

- JavaScript
- TypeScript
- C#
- Java

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (11 parser tests, 28 total tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 4 — Indexer.