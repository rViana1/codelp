# ADR-005 — Stable Symbol Index

**Status:** Accepted

**Date:** 2026-07-30

---

# Context

After introducing the Project aggregate and the Python Parser, Codelp required a navigable representation of parsed knowledge.

The Indexer needed to support:

- fast symbol lookup;
- file-based navigation;
- deterministic behaviour;
- future cross-file references;
- future semantic retrieval.

A key architectural decision was defining how symbols would be uniquely identified across the entire project.

---

# Decision

Codelp will implement a **Stable Symbol Index**.

The Indexer becomes responsible for transforming `ParsedProject` into a `ProjectIndex` containing:

- files;
- symbols;
- dependencies.

---

# Stable Symbol Identifier

Every indexed symbol receives a deterministic identifier.

Format

```text
<project_relative_path>::<symbol_path>
```

Examples

```text
src/main.py::hello
src/models/user.py::User
src/models/user.py::User.login
```

Rules

- paths are relative to the project root;
- POSIX separators are always used;
- methods include the owning class;
- identifiers are deterministic across executions.

---

# Index Structure

```text
ProjectIndex
├── files
├── symbols
└── dependencies
```

---

# Storage Strategy

Files and symbols are stored in dictionaries keyed by their stable identifiers.

```python
files: dict[str, FileEntry]
symbols: dict[str, SymbolEntry]
```

Dependencies are stored as an ordered list.

This provides:

- O(1) file lookup;
- O(1) symbol lookup;
- deterministic iteration order.

---

# Parser Independence

Stable identifiers are **not stored in parser models**.

The parser remains responsible only for structural extraction:

- imports;
- functions;
- classes;
- methods.

The Indexer derives identifiers from:

- project root;
- parsed file path;
- symbol ownership information.

This preserves the dependency direction:

```text
Parser -> ParsedProject
Indexer -> ParsedProject
Project -> ProjectIndex
```

---

# Determinism

The Indexer explicitly sorts:

- files;
- functions;
- classes;
- methods;
- imports.

Deterministic ordering is required for:

- reproducible tests;
- caching;
- serialization;
- persistent project knowledge;
- future incremental indexing.

---

# Public APIs

Technical API

```python
build(project_root: Path, parsed_project: ParsedProject) -> ProjectIndex
```

Domain API

```python
index_project(project: Project) -> Project
```

This mirrors the architecture already adopted by the Scanner and Parser.

---

# Consequences

## Advantages

Stable and human-readable identifiers.

Fast lookups.

Deterministic indexes.

Simple serialization.

Clear separation between parsing and indexing.

Strong foundation for future reference graphs.

---

## Disadvantages

Identifiers change when files are moved.

No semantic resolution yet.

No cross-file references yet.

No fully-qualified module resolution yet.

---

# Alternatives Considered

## Simple symbol names

Rejected because collisions occur immediately.

---

## Global numeric identifiers

Rejected because they are not deterministic across executions.

---

## Hash-based identifiers

Rejected because they reduce debuggability and are unnecessary at this stage.

---

# Future Evolution

Future milestones may extend the index with:

- reference graph;
- semantic dependency graph;
- fully-qualified symbol resolution;
- inheritance relationships;
- call graph;
- retrieval metadata.

The current identifier format is considered sufficient for these future extensions.

---

# Validation

The implementation is validated by automated tests covering:

- relative paths;
- function identifiers;
- class identifiers;
- method identifiers;
- deterministic identifiers;
- empty indexes;
- function indexing;
- class indexing;
- method indexing;
- dependency indexing;
- full project integration.

Current indexing validation:

- 12 indexing tests passing.

Current project validation:

- 40 total automated tests passing.
