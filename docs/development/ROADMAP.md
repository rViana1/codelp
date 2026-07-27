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

---

# 3. High-Level Architecture

```
Repository
      │
      ▼
Scanner
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

Each stage only depends on the previous one.

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

Output

`ScanResult`

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

# 5. Planned Domain Model

The long-term central entity of the system is the `Project`.

```
Project

├── metadata
├── scan_result
├── parsed_project
├── project_index
├── chunks
├── embeddings
├── diagnostics
└── knowledge
```

Each module progressively enriches the same Project object.

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

## Milestone 2.2 — Project Model

Status

Planned

Goals

- Introduce Project entity
- Metadata model
- Scanner integration
- Rich domain model foundation

---

## Milestone 3 — Parser

Status

Planned

Goals

- Language detection
- Python parser
- AST support
- Symbols
- Imports
- Classes
- Functions
- Methods

---

## Milestone 4 — Indexer

Status

Planned

Goals

- Symbol index
- Dependency graph
- Reference graph
- File index

---

## Milestone 5 — Chunker

Status

Planned

Goals

- Semantic chunking
- Metadata
- Context preservation

---

## Milestone 6 — Embedding Engine

Status

Planned

Goals

- Provider abstraction
- Cache
- Persistence

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