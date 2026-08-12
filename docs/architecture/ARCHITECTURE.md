# Codelp Architecture

> **Version:** 1.8
> **Status:** In Development  
> **Last Updated:** Milestone 7.1 — Vector Store Lifecycle Management

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

Current implementation: **Python AST Parser**.

Responsibilities

- detect programming language
- parse Python source files
- extract imports
- extract top-level functions
- extract classes
- extract methods
- associate methods with their owning class
- update Project parser state

Outputs

- ParsedFile
- ParsedProject
- Project enrichment

Public APIs

```python
parse_file(path: Path) -> ParsedFile
parse_project(project: Project) -> Project
```

The parser is designed to be language-agnostic at the orchestration level while using language-specific parsers internally.

---

## Indexer

Responsible for organising parsed knowledge into navigable indexes.

Current implementation: **Stable Symbol Index**.

Responsibilities

- build stable symbol identifiers
- build file index
- build symbol index
- build dependency index
- preserve deterministic order
- update Project index state

Outputs

- FileEntry
- SymbolEntry
- DependencyEntry
- ProjectIndex
- Project enrichment

Public APIs

```python
build(project_root: Path, parsed_project: ParsedProject) -> ProjectIndex
index_project(project: Project) -> Project
```

The current indexer performs structural indexing only.

Cross-file references, semantic relationships and advanced dependency analysis are intentionally deferred to future milestones.

---

## Chunker

Responsible for preparing semantic chunks from indexed project knowledge.

Responsibilities

- build chunks for functions
- build chunks for classes
- build chunks for methods
- preserve exact source text
- preserve semantic boundaries
- preserve deterministic ordering
- generate chunk metadata
- derive chunk identifiers from symbol identifiers
- update Project chunk state

Outputs

- CodeChunk
- ChunkCollection
- Project enrichment

Public APIs

```python
build(
    project_root: Path,
    parsed_project: ParsedProject,
    index: ProjectIndex,
) -> ChunkCollection

chunk_project(project: Project) -> Project
```

The current chunker performs semantic chunking only.

Token-based chunking, sliding windows, large-symbol splitting and hybrid retrieval chunking are intentionally deferred to future milestones.

---

## Embedding Engine

Responsible for transforming semantic chunks into vector embeddings.

Current implementation: Provider-independent Embedding Engine.

Responsibilities

- generate embeddings from chunks
- preserve deterministic ordering
- attach chunk identity
- attach provider metadata
- update Project embedding state

Outputs

- EmbeddingCollection
- Project enrichment

Public APIs

embed(chunks: ChunkCollection) -> EmbeddingCollection

embed_project(project: Project) -> Project

The embedding engine depends on an abstract EmbeddingProvider and is independent from concrete embedding implementations.

Caching, batching and persistent vector storage are intentionally deferred to future milestones.

---

## Vector Store Management

Responsible for managing the lifecycle of vector storage associated with projects.

The Vector Store layer separates storage lifecycle concerns from retrieval logic.

Responsibilities

- create project vector stores;
- register project vector stores;
- retrieve project vector stores;
- remove project vector stores;
- hide concrete storage implementations;
- prepare the architecture for persistent vector databases.

Outputs

- VectorStore instances
- Project vector store registrations

Public APIs

```python
register_project(
    project_path: Path,
    embeddings: EmbeddingCollection,
) -> None

get_project_store(
    project_path: Path,
) -> VectorStore | None

remove_project(
    project_path: Path,
) -> None
```

The VectorStoreManager is responsible for storage lifecycle only.
It does not perform similarity search, ranking or retrieval decisions.

Current implementation:

InMemoryVectorStore

Future implementations may include:
- persistent vector databases;
- remote vector services;
- distributed vector storage.

The Vector Store layer belongs to the application/infrastructure boundary and is intentionally independent from the Project domain model.

---

## Retriever

Responsible for semantic retrieval from project embeddings.

Responsibilities

- similarity calculation
- vector comparison
- deterministic ranking
- result limiting
- chunk identity preservation
- retrieval through VectorStore abstraction
- Project knowledge integration

Outputs

- RetrievalResult
- RetrievalCollection
- Project enrichment

Public APIs

retrieve(
    query: RetrievalQuery,
    query_vector: list[float],
    store: VectorStore,
) -> RetrievalCollection

retrieve_project(
    project: Project,
    query: RetrievalQuery,
    query_vector: list[float],
) -> Project

The Retriever is independent from:

- embedding providers;
- VectorStore implementations;
- storage lifecycle management.

Vector storage creation and management are handled by VectorStoreManager.

Similarity strategy currently uses cosine similarity.

Hybrid retrieval, filtering strategies and advanced ranking strategies are intentionally deferred to future milestones.

---

## Context Builder

Responsible for transforming retrieved project knowledge into structured context.

Responsibilities

- consume RetrievalCollection results
- resolve retrieved chunk identities
- preserve retrieval ranking
- preserve deterministic ordering
- preserve chunk-to-context relationships
- build structured PromptContext
- update Project context state
- prepare project knowledge for future LLM consumers

Outputs

- PromptContext
- Project enrichment

Public APIs

```python
build(
    retrieval: RetrievalCollection,
    chunks: ChunkCollection,
) -> PromptContext

```

build_project(project: Project) -> Project
The Context Builder is independent from LLM providers.
It does not perform retrieval, embedding generation or prompt execution.
Token optimisation, context compression and prompt templates are intentionally deferred to future milestones.

---

# 6. Domain Model

The central entity of the architecture is the Project aggregate root.

Every application module enriches the same Project instance.

Project

├── metadata

├── configuration

├── statistics
│   └── scanned_files

├── root_tree

├── parser_result

├── index_result
│   ├── files
│   ├── symbols
│   └── dependencies

├── chunk_result
│   ├── chunks

├── embedding_result
│   ├── embeddings
│   └── provider_metadata

├── retrieval_result

├── context_result
│   ├── context_id
│   ├── query
│   └── chunks

└── diagnostics

The domain is implemented in `backend/core/project`.

---

## Aggregate Root

The Project is the single source of truth for all analysis state.

Modules do not communicate directly with each other.

Communication always happens through the Project model.

Examples

- scanner.scan_project(project)
- parser.parse_project(project)
- indexer.build(project.metadata.root_path, project.parser_result)
- indexer.index_project(project)
- chunker.chunk_project(project)
- embedding.embed_project(project)
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

## Allowed dependencies

- app.scanner → core.project
- app.parser → core.project
- app.indexing → core.project
- app.chunking → core.project
- app.embeddings → core.project
- app.retrieval → core.project
- app.retrieval → app.vectorstore
- app.vectorstore → app.embeddings
- app.context → core.project

## Forbidden dependencies

- scanner → parser
- parser → chunker
- chunker → retriever
- retriever → scanner
- core → app
- core → vectorstore
- retriever → concrete vector database implementations

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
'''
---

# 11. Chunk Identity

The Chunker does not generate independent semantic identifiers.

Chunk identifiers are derived directly from the stable symbol identifiers produced by the Indexer.

Relationship:

```text
chunk.id == symbol.id
```

Examples:

- `src/main.py::hello`
- `src/models/user.py::User`
- `src/models/user.py::User.login`

This creates a deterministic identity chain:

```text
Source File
    ↓
Parser Symbol
    ↓
Indexer Symbol ID
    ↓
Chunk ID
    ↓
Embedding ID
```

The strategy provides a stable foundation for future embedding caching, incremental updates and vector store synchronization.

---

# 12. Testing Strategy

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
- Parser tests
- Parser integration tests
- Indexer tests
- Chunker tests
- Embedding tests
- Vector Store tests
- Retrieval tests
- Context Builder tests
- Pipeline integration tests

Current total: 108 passing automated tests.

---

# 13. Performance Goals

Future milestones should optimise

- incremental scanning
- caching
- lazy loading
- parallel parsing
- embedding batching

Performance optimisations should never compromise determinism.

---

# 14. Extensibility

The architecture must support

- multiple programming languages
- multiple embedding providers
- multiple LLM providers
- multiple vector databases

without changing the core architecture.

---

# 15. Architecture Decision Records

Major engineering decisions are documented separately.

Current ADRs

- ADR-001 — Project Model
- ADR-002 — Scanner Permission Handling
- ADR-003 — Scanner Integration with Project
- ADR-004 — Python AST Parser
- ADR-005 — Stable Symbol Index
- ADR-006 — Stable Chunk Identity
- ADR-007 — Embedding Provider Abstraction
- ADR-008 — Retrieval Engine Abstraction
- ADR-009 — Context Builder Abstraction
- ADR-010 — Vector Store Lifecycle Management

Future ADRs

- Persistent Project Knowledge
- Incremental Scanner
- Plugin System
- Cache
- Configuration
- Multi-language Parsing
- Reference Graph

---

# 16. Future Evolution

Planned architectural improvements include

- dedicated ProjectTree model
- incremental scanning
- persistent project knowledge
- remote repository support
- distributed indexing
- streaming parser
- parallel chunking
- multi-language parsing
- richer symbol metadata
- cross-file symbol resolution
- multi-chunk symbols
- embedding caching
- persistent vector database implementations
- similarity retrieval

---

# 17. Stable Symbol Identifiers

The Indexer assigns a stable identifier to every indexed symbol.

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

The identifier is calculated by the Indexer and is not stored directly in parser symbol models.

This decision keeps the parser independent from indexing concerns while providing a stable foundation for future reference graphs, retrieval and navigation.

---

# 18. Engineering Philosophy

Codelp is designed as an engineering platform rather than a collection of utilities.

The architecture favours maintainability, modularity and deterministic behaviour over short-term implementation speed.

Every new feature should strengthen the architecture rather than increase technical debt.