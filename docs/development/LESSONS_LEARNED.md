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

---

# Milestone 4 — Stable Symbol Index

## Objective

Implement the first navigable project index capable of transforming parsed knowledge into deterministic and query-efficient structures integrated with the Project aggregate.

The indexer builds stable identifiers for functions, classes and methods while preserving deterministic behaviour across the entire pipeline.

---

## What Went Well

- Stable identifiers proved simple and highly effective.
- Separating builders from orchestration kept the indexer focused.
- Dictionary-based indexes simplified lookup logic.
- Deterministic ordering made tests and debugging easier.
- Integration with the existing Project aggregate required minimal architectural changes.
- The full pipeline remained consistent from Scanner to Indexer.

---

## Lessons Learned

### Human-Readable Identifiers Are Extremely Valuable

Identifiers such as:

```text
src/models/user.py::User.login
```

are easy to debug, serialize, log and reason about.

Readability is often more valuable than compactness in early architecture stages.

---

### The Indexer Should Own Identity

The parser should describe structure, not identity.

Moving identifier generation to the Indexer preserves a clean separation between extraction and navigation concerns.

---

### Relative Paths Matter

Using project-relative POSIX paths avoids machine-specific identifiers and keeps indexes portable across environments.

---

### Determinism Must Be Explicit

Relying on upstream ordering is fragile.

The Indexer now sorts files, functions, classes, methods and imports explicitly, making reproducibility a property of the component itself.

---

### Dictionaries Are the Right Default for Knowledge Graphs

Using dictionaries keyed by stable identifiers immediately enables efficient navigation and prepares the architecture for future reference graphs.

---

### Avoid Premature Navigation Optimizations

`FileEntry` stores only symbol identifiers rather than full symbol objects.

This keeps the model lightweight and avoids duplication until a measurable performance or usability need appears.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Parser does not generate stable identifiers.
- Indexer owns symbol identity.
- Deterministic indexing is mandatory.
- Query structures are optimized for lookup, not serialization convenience.
- Cross-file references are intentionally deferred.

---

## Future Improvements Identified

### Reference Graph

- cross-file symbol references
- import resolution
- call graph
- inheritance graph

### Semantic Indexing

- fully-qualified names
- module resolution
- symbol aliases
- generic type information

### Retrieval

- symbol-to-file navigation helpers
- derived views
- ranking metadata

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (12 indexing tests, 40 total tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 5 — Chunker.


---

# Milestone 5 — Chunker

## Objective

Transform indexed project knowledge into deterministic semantic chunks suitable for embeddings, retrieval and LLM context generation.

The Chunker is responsible for preserving semantic boundaries while extracting the exact source code associated with functions, classes and methods.

---

## What Went Well

- Symbol-based chunking produced clear and predictable chunk boundaries.
- Exact source extraction preserved the original formatting and indentation.
- Reusing stable symbol identifiers avoided introducing a second identity system.
- Deterministic ordering simplified testing and future embedding synchronization.
- Separating extractors, builders and orchestration kept responsibilities clear.
- Full pipeline tests detected regressions introduced by parser model changes.

---

## Lessons Learned

### Stable Identity Should Flow Through the Pipeline

The most important architectural decision was deriving chunk identifiers directly from symbol identifiers.

A single identity chain:

```text
Source File
    ↓
Parser Symbol
    ↓
Indexer Symbol ID
    ↓
Chunk ID
```

greatly simplifies embeddings, retrieval, persistence and incremental updates.

---

### Exact Source Extraction Is More Important Than Pretty Formatting

The chunker must preserve the exact text from the source file.

Any normalization of whitespace, indentation or line endings would make future embeddings and diagnostics less reliable.

---

### Parser Metadata Enables Downstream Features

Adding `start_line` and `end_line` to parser symbols unlocked precise chunk extraction.

This reinforced the idea that parser metadata should be designed with downstream consumers in mind.

---

### Deterministic Ordering Prevents Hidden Instability

Explicit sorting of:

- files;
- functions;
- classes;
- methods;

eliminated non-deterministic behaviour and made chunk IDs and ordering reproducible across executions.

---

### Integration Tests Catch Real Regressions

The most valuable regression was not in the Chunker itself, but in older Indexer tests that instantiated parser models manually.

End-to-end pipeline tests proved essential for detecting compatibility issues between milestones.

---

### Keep Chunking Semantic Before Optimizing Retrieval

The first implementation intentionally prioritised semantic coherence over retrieval optimisation.

Future features such as token-based chunking, overlap or hybrid chunking should be introduced only after retrieval behaviour is measurable.

---

## Architectural Decisions Reinforced

- Chunk IDs are derived from symbol IDs.
- Semantic chunk boundaries are the default strategy.
- Exact source text is preserved.
- Deterministic ordering is mandatory.
- The Chunker remains independent from the AST and the Scanner.

---

## Future Improvements Identified

### Chunking

- Token-based chunking.
- Large-symbol splitting.
- Overlapping windows.
- Hybrid semantic + token chunking.
- Language-specific chunking strategies.

### Retrieval

- Parent-child chunk relationships.
- Context expansion around chunks.
- Retrieval-aware chunk metadata.

### Performance

- Lazy source extraction.
- Incremental chunk regeneration.
- Chunk hashing for cache invalidation.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 6 — Embeddings.

# Milestone 6 — Embedding Engine

## Provider Abstraction

Embedding generation should not be coupled to a concrete provider.

Using an explicit provider contract allows:

- replacing embedding implementations;
- testing without external dependencies;
- supporting multiple providers in the future;
- keeping orchestration logic independent.

The Embedding Engine depends on the provider abstraction, not on provider implementations.

---

## Stable Embedding Identity

Embeddings should not introduce a new independent identity system.

The identity chain remains:

Source File

↓

Symbol ID

↓

Chunk ID

↓

Embedding.chunk_id

Reusing chunk identity simplifies:

- navigation;
- caching strategies;
- incremental updates;
- vector store synchronization.

---

## Deterministic Testing

External AI services should not be required to validate embedding behaviour.

A deterministic fake provider provides:

- reproducible tests;
- stable vectors;
- dependency-free validation;
- predictable pipeline behaviour.

This keeps architectural validation independent from external providers.

---

## Domain Flexibility

The embedding domain should not assume fixed vector dimensions.

Vector size belongs to the provider metadata.

This allows future support for different embedding models without changing the domain model.

---

## Storage Boundaries

The first embedding storage implementation should remain simple.

An in-memory store is sufficient to validate:

- embedding persistence boundaries;
- lookup behaviour;
- insertion ordering;
- future vector store interfaces.

Persistent storage should only be introduced when retrieval requirements justify the additional complexity.

---

## Project Pipeline Integration

Each processing stage should enrich the Project aggregate without creating direct dependencies between stages.

The current pipeline remains:

Scanner

↓

Parser

↓

Indexer

↓

Chunker

↓

Embedding Engine

↓

Future Retrieval

This preserves modularity and allows each stage to evolve independently.