# ADR-004 — Python AST Parser

**Status:** Accepted

**Date:** 2026-07-30

---

# Context

After completing the Project aggregate integration, Codelp required a parser capable of transforming Python source files into structured knowledge.

The parser needed to satisfy several architectural requirements:

- remain independent from Scanner internals;
- integrate with the Project aggregate;
- support deterministic analysis;
- expose a testable low-level API;
- allow future support for additional programming languages.

The implementation also needed to avoid premature complexity such as semantic analysis, type inference, decorators, docstrings and cross-file resolution.

---

# Decision

Codelp will implement a Python parser based on the standard library `ast` module.

The parser architecture is divided into four responsibilities:

- language detection;
- AST parsing;
- symbol extraction;
- project orchestration.

---

# Public APIs

The parser exposes two public APIs.

## Technical API

```python
parse_file(path: Path) -> ParsedFile
```

Parses a single file independently of the Project aggregate.

---

## Domain API

```python
parse_project(project: Project) -> Project
```

Parses all supported files discovered by the Scanner and enriches the Project aggregate.

This mirrors the architecture previously adopted by the Scanner.

---

# Symbol Model

The parser extracts a minimal structural model.

```text
ParsedFile
├── imports
├── functions
└── classes
    └── methods
```

Extracted symbols:

- ImportSymbol
- FunctionSymbol
- ClassSymbol
- MethodSymbol

Methods include their owning class name.

---

# AST Traversal

Symbol extraction is implemented through dedicated visitors.

- ImportVisitor
- FunctionVisitor
- ClassVisitor

Function extraction is limited to top-level functions.

Methods are extracted only from class bodies.

This prevents symbol duplication.

---

# Error Handling

Unsupported languages do not stop project parsing.

Instead, diagnostics are recorded.

Python syntax errors raise a dedicated exception during `parse_file()` and become diagnostics during `parse_project()`.

---

# Consequences

## Advantages

Uses only the Python standard library.

Deterministic parsing.

Clear separation of responsibilities.

Easy unit testing.

Easy future extension to additional languages.

Consistent with Scanner architecture.

---

## Disadvantages

No semantic analysis.

No type inference.

No decorator extraction.

No docstring extraction.

No line range information.

No cross-file symbol resolution.

---

# Alternatives Considered

## Regular-expression parser

Rejected because it would be fragile and inaccurate.

---

## Third-party parsing libraries

Rejected to keep dependencies minimal during early milestones.

---

## Single monolithic parser class

Rejected because it would mix detection, parsing, extraction and orchestration responsibilities.

---

# Implementation

Implemented modules:

- detector.py
- python_parser.py
- visitors.py
- parser.py
- models.py
- exceptions.py

---

# Validation

The implementation is validated by automated tests covering:

- language detection;
- unknown languages;
- empty files;
- imports;
- functions;
- classes;
- methods;
- duplicate prevention;
- syntax errors;
- project integration.

Current parser validation:

- 11 parser tests passing.

Current project validation:

- 28 total automated tests passing.

---

# Future Review

Review richer symbol metadata before Milestone 4.

Review stable symbol identifiers before the Indexer.

Review cross-file symbol resolution before advanced indexing.

Review support for additional programming languages before multi-language parsing.
