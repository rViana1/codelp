# Codelp

> **Code Development Platform**

Version: 1.0

Status: In Development

---

# 1. Vision

## Mission

Codelp is an extensible platform capable of understanding an entire software project rather than individual source files.

Its long-term goal is to transform any source code repository into structured knowledge that can be consumed by developers, AI systems and development tools.

Instead of simply reading source code, Codelp progressively builds richer semantic representations of a project, enabling intelligent navigation, semantic search, documentation generation and AI-assisted software development.

---

# 2. Engineering Principles

The project follows a set of core engineering principles.

## Single Responsibility

Every module has one clear responsibility.

## Modularity

Modules should remain independent whenever possible.

## Extensibility

New languages, parsers and AI providers should be added without modifying the core architecture.

## Determinism

The same repository should always produce the same internal representation.

## Testability

Every public behaviour must be validated through automated tests.

## Documentation First

Architectural decisions are documented before implementation.

## Simplicity

Prefer explicit and maintainable solutions over clever ones.

## Domain First

The domain model is the central source of truth of the platform.

## Dependency Direction

Application modules may depend on the domain; the domain must never depend on application modules.

---

# 3. High-Level Architecture

```
Repository
      │
      ▼
Scanner
      │
      ▼
Project (Aggregate Root)
      │
      ▼
Parser
      │
      ▼
Indexer
      │
      ▼
Chunker
      │
      ▼
Embedding Engine
      │
      ▼
Knowledge Store
      │
      ▼
Retriever
      │
      ▼
Context Builder
      │
      ▼
LLM
```

Each application module enriches the same `Project` aggregate.

---

# 4. Core Modules

## Scanner

Responsible for discovering the project structure.

Responsibilities

- scan directories
- ignore configured paths
- build project tree
- register files
- register directories
- update Project scan state

Outputs

- `ScanResult`
- `Project` enrichment

---

## Parser

Responsible for understanding source code.

Responsibilities

- language detection
- AST generation
- symbol extraction
- import detection

Output

`ParsedProject`

---

## Indexer

Responsible for organising project knowledge.

Responsibilities

- symbol index
- dependency graph
- reference graph
- file index

Output

`ProjectIndex`

---

## Chunker

Responsible for preparing semantic chunks.

Responsibilities

- semantic chunking
- metadata generation
- context preservation

Output

`ChunkCollection`

---

## Embedding Engine

Responsible for vector generation.

Responsibilities

- embedding providers
- batching
- cache

Output

`EmbeddingCollection`

---

## Retriever

Responsible for semantic retrieval.

Responsibilities

- similarity search
- hybrid retrieval
- ranking

---

## Context Builder

Responsible for constructing LLM prompts.

Responsibilities

- retrieve knowledge
- merge context
- token optimisation

Output

`PromptContext`

---

# 5. Domain Model

The central entity of the system is the `Project` aggregate.

```
Project
├── metadata
├── configuration
├── statistics
├── root_tree
├── parser_result
├── index_result
├── chunk_result
├── embedding_result
└── diagnostics
```

The domain is implemented in `backend/core/project`.

Application modules enrich the same Project instance during analysis.

---

# 6. Milestones

## Milestone 1 — Repository Setup

Status

Completed

---

## Milestone 2.1 — Project Scanner

Status

Completed

Deliverables

- Recursive scanner
- Project tree
- Scan filters
- Deterministic traversal
- Unit tests
- Documentation
- Architecture Review
- Code Review

---

## Milestone 2.2 — Project Domain Model

Status

Completed

Deliverables

- Project aggregate root
- ProjectMetadata
- ProjectConfiguration
- ProjectStatistics
- Public domain API
- Timezone-aware UTC handling
- Scanner integration
- Safe tree serialization
- Domain tests
- Integration tests
- Backwards compatibility preserved
- Architecture Review
- Code Review

Validation

- 17 automated tests passing

---

## Milestone 3 — Python Parser

Status

Completed

Deliverables

- Parser package
- Language detector
- Unknown language handling
- Python AST parser
- Import extraction
- Function extraction
- Class extraction
- Method extraction
- Method-to-class association
- ParsedFile model
- ParsedProject model
- Project integration
- Diagnostics propagation
- Parser unit tests
- Integration tests
- Architecture Review
- Code Review

Validation

- 11 parser tests passing
- 28 total automated tests passing

Future Reviews

- Stable symbol identifiers before Milestone 4
- Richer symbol metadata (decorators, docstrings, line ranges) before Milestone 4
- Parser result strategy before advanced indexing

---

## Milestone 4 — Indexer

Status

Completed

Deliverables

- Indexing package
- Stable symbol identifiers
- Relative path strategy
- File index
- Symbol index
- Dependency index
- Function indexing
- Class indexing
- Method indexing
- Import indexing
- Deterministic indexing order
- Project integration
- Indexer unit tests
- Pipeline integration test
- Architecture Review
- Code Review

Validation

- 12 indexing tests passing
- 40 total automated tests passing

Future Reviews

- Stable cross-file references before advanced indexing
- Reference graph before retrieval features
- Richer symbol metadata before semantic indexing
- File navigation optimization before retrieval features

---

## Milestone 5 — Chunker

Status

Planned

Goals

- Semantic chunking
- Metadata
- Context preservation
- Project integration

---

## Milestone 6 — Embedding Engine

Status

Planned

Goals

- Provider abstraction
- Cache
- Persistence
- Project integration

---

## Milestone 7 — Retriever

Status

Planned

Goals

- Semantic search
- Hybrid retrieval
- Ranking

---

## Milestone 8 — Context Builder

Status

Planned

Goals

- Prompt optimisation
- Context windows
- Ranking
- Context compression

---

## Milestone 9 — MCP Integration

Status

Planned

Goals

- Model Context Protocol
- IDE integration
- External tools

---

## Milestone 10 — Production Ready

Status

Planned

Goals

- CLI
- REST API
- Configuration
- Plugin system
- Documentation
- Release pipeline

---

# 7. Versioning

Development follows incremental milestones.

Every completed milestone requires:

- implementation
- tests
- code review
- architecture review
- updated documentation
- git tag

---

# 8. Architecture Decision Records

All significant architectural decisions must be documented as ADRs.

Current ADRs

- ADR-001 — Project Model
- ADR-002 — Scanner Permission Handling
- ADR-003 — Scanner Integration with Project

Planned ADRs

- Persistent Project Knowledge
- Incremental Scanner
- Indexer Design
- Plugin System
- Configuration System
- Multi-language Support

---

# 9. Long-Term Vision

Codelp aims to become a complete software knowledge platform.

Instead of analysing isolated files, it will progressively understand an entire software system, preserve that knowledge over time and provide intelligent assistance to developers and AI systems.

The platform should remain:

- language agnostic
- deterministic
- modular
- extensible
- AI-ready
- maintainable
- domain-centric