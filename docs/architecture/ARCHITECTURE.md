# Codelp Architecture

> **Version:** 1.1  
> **Status:** In Development  
> **Last Updated:** Milestone 2.2

---

# 1. Purpose

The purpose of this document is to describe the architecture of the Codelp platform.

It defines the major system components, their responsibilities, how they interact, and the engineering principles that guide the evolution of the project.

This document is intentionally technology-independent whenever possible. It focuses on architectural decisions rather than implementation details.

---

# 2. Vision

Codelp is designed to transform a software repository into structured knowledge.

Instead of treating source code as plain text, Codelp progressively enriches the information extracted from the project until it becomes a searchable, navigable and AI-ready knowledge base.

Every stage of the architecture contributes to that transformation.

---

# 3. Architecture Principles

The architecture follows a small set of non-negotiable principles.

## Single Responsibility

Every module has one clear responsibility.

No module should perform work belonging to another component.

---

## Modularity

Every component should be replaceable without requiring changes to unrelated modules.

---

## Extensibility

Support for new programming languages, embedding providers or storage engines must be added through extension rather than modification.

---

## Determinism

The same repository must always produce the same internal representation.

Independent executions should generate identical results.

---

## Testability

Public behaviour must always be validated through automated tests.

Private implementation details are not tested directly.

---

## Documentation

Important engineering decisions must be documented through ADRs.

---

## Domain First

The domain model is the central source of truth of the platform.

---

## Dependency Direction

Application modules may depend on the domain.

The domain must never depend on application modules.

---

# 4. High-Level Architecture

Repository

↓

Scanner

↓

Project (Aggregate Root)

↓

Parser

↓

Indexer

↓

Chunker

↓

Embedding Engine

↓

Knowledge Store

↓

Retriever

↓

Context Builder

↓

LLM

Each application module enriches the same Project aggregate.

---

# 5. Core Components

## Scanner

Responsible for discovering the repository.

Responsibilities

- discover files
- discover directories
- ignore configured paths
- build the project tree
- update Project scan state

Outputs

- ScanResult
- Project enrichment

---

## Parser

Responsible for understanding source code.

Responsibilities

- parse files
- detect programming language
- extract imports
- extract classes
- extract methods
- extract functions

Output

ParsedProject

---

## Indexer

Responsible for organising project knowledge.

Responsibilities

- symbol index
- dependency index
- file index
- reference index

Output

ProjectIndex

---

## Chunker

Responsible for preparing semantic chunks.

Responsibilities

- preserve context
- generate chunk metadata
- optimise chunk boundaries

Output

ChunkCollection

---

## Embedding Engine

Responsible for generating vector representations.

Responsibilities

- embedding generation
- cache
- batching

Output

EmbeddingCollection

---

## Retriever

Responsible for semantic search.

Responsibilities

- similarity search
- ranking
- filtering

---

## Context Builder

Responsible for constructing prompts.

Responsibilities

- retrieve information
- merge context
- enforce token limits

Output

PromptContext

---

# 6. Domain Model

The central entity of the architecture is the Project aggregate root.

Every application module enriches the same Project instance.

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

The domain is implemented in `backend/core/project`.

---

## Aggregate Root

The Project is the single source of truth for all analysis state.

Modules do not communicate directly with each other.

Communication always happens through the Project model.

Examples

- scanner.scan_project(project)
- parser.parse(project)
- indexer.index(project)
- chunker.chunk(project)

---

# 7. Data Flow

Repository

↓

Scanner

↓

Project

↓

Parser

↓

Project

↓

Indexer

↓

Project

↓

Chunker

↓

Project

↓

Embedding Engine

↓

Project

↓

Retriever

↓

Context Builder

↓

LLM

---

# 8. Dependency Rules

Allowed dependencies

- app.scanner → core.project
- app.parser → core.project
- app.indexing → core.project
- app.chunking → core.project
- app.embeddings → core.project
- app.rag → core.project

Forbidden dependencies

- scanner → parser
- parser → chunker
- chunker → retriever
- retriever → scanner
- core → app

No module should depend on a future processing stage.

The domain must remain independent from application modules.

---

# 9. Layered Architecture

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Current mapping

- Application → app/*
- Domain → core/*
- Infrastructure → storage, vector stores, external APIs

The Scanner is an application component that enriches the domain.

The Project model belongs to the domain layer.

Business rules belong to the domain layer.

External APIs belong to the infrastructure layer.

---

# 10. Tree Serialization

The scanner internally uses a TreeNode graph with parent references.

TreeNode

├── parent

└── children

This structure is suitable for navigation but creates circular references during serialization.

When the scanner updates the Project aggregate, the tree is converted into a serialization-safe dictionary representation that excludes parent references.

This representation is:

- deterministic
- JSON-friendly
- persistence-friendly
- independent from the scanner implementation

---

# 11. Testing Strategy

Every module must include automated tests.

Priority

1. Public API

2. Business rules

3. Regression tests

Implementation details should not be tested directly.

Current validation

- Domain model tests
- Scanner tests
- Scanner integration tests

---

# 12. Performance Goals

Future milestones should optimise

- incremental scanning
- caching
- lazy loading
- parallel parsing
- embedding batching

Performance optimisations should never compromise determinism.

---

# 13. Extensibility

The architecture must support

- multiple programming languages
- multiple embedding providers
- multiple LLM providers
- multiple vector databases

without changing the core architecture.

---

# 14. Architecture Decision Records

Major engineering decisions are documented separately.

Current ADRs

- ADR-001 — Project Model
- ADR-002 — Scanner Permission Handling
- ADR-003 — Scanner Integration with Project

Future ADRs

- Persistent Project Knowledge
- Incremental Scanner
- Plugin System
- Cache
- Configuration
- Language Support

---

# 15. Future Evolution

Planned architectural improvements include

- dedicated ProjectTree model
- incremental scanning
- persistent project knowledge
- remote repository support
- distributed indexing
- streaming parser
- parallel chunking
- multi-language parsing

---

# 16. Engineering Philosophy

Codelp is designed as an engineering platform rather than a collection of utilities.

The architecture favours maintainability, modularity and deterministic behaviour over short-term implementation speed.

Every new feature should strengthen the architecture rather than increase technical debt.