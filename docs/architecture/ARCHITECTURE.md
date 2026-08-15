# Codelp Architecture

> **Version:** 2.0
> **Status:** In Development  
> **Last Updated:** Milestone 10.2 — Pipeline Knowledge Integration

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

Vector Store Management

↓

Retriever

↓

Context Builder

↓

┌───────────────┐
│               │
▼               ▼
MCP Integration  LLM
│
▼
External AI Clients / Developer Tools

Each application module enriches the same Project aggregate.

MCP exposes project knowledge through application boundaries and does not access domain internals directly.

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

## MCP Integration

Responsible for exposing Codelp project knowledge through Model Context Protocol.

The MCP layer provides external consumers access to structured project knowledge while preserving existing architecture boundaries.

Responsibilities

- expose project information resources
- expose project structure resources
- expose symbol resources
- expose context resources
- provide semantic search tools
- provide context retrieval tools
- preserve deterministic responses
- isolate external protocol concerns from domain logic
- communicate through application services

Outputs

- MCP Resources
- MCP Tools
- MCP Responses

Current implementation

- MCP server abstraction
- MCP lifecycle management
- MCP resource registry
- MCP tool registry
- MCP execution layer
- MCP application services

Supported capabilities

- Project information
- Project structure
- Symbol lookup
- Semantic search
- Context retrieval

The MCP layer does not:

- modify the Project aggregate directly;
- access parser internals;
- access index internals;
- manage vector storage;
- generate embeddings.

Future improvements

- Real MCP transport implementation
- IDE integrations
- External MCP clients
- Authentication and permissions

---

## Persistent Project Knowledge

Responsible for managing the lifecycle of persisted project knowledge.

Persistent Project Knowledge is an external representation of analysed project state.

The persistence layer does not replace the Project aggregate.

The runtime Project remains the source of truth during execution.

Responsibilities

- prepare project knowledge before analysis;
- persist analysed project knowledge;
- restore previously persisted knowledge;
- coordinate persistence lifecycle;
- maintain storage independence.

Outputs

- PersistentProjectKnowledge

Current implementation

- Knowledge lifecycle service
- Knowledge storage abstraction

Architecture rules

The Persistent Project Knowledge layer:

- does not modify domain behaviour;
- does not bypass application services;
- does not become the source of truth;
- does not couple the domain to storage technology.

The dependency direction remains:

Analysis Pipeline

↓

Knowledge Lifecycle

↓

Knowledge Storage Abstraction

↓

Storage Implementation

Future improvements

- incremental knowledge updates;
- persisted identity reconstruction;
- knowledge versioning;
- selective restoration.

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

├── knowledge_state

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

Knowledge Lifecycle

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

Project

↓

Knowledge Lifecycle

↓

Knowledge Storage

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
- app.mcp → application services
- app.mcp → core.project
- app.knowledge → core.project
- app.pipeline → app.knowledge

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

- Presentation → future CLI/API/MCP transports
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
- MCP lifecycle tests
- MCP resource tests
- MCP tool tests
- MCP execution tests
- MCP resilience tests
- MCP architecture boundary tests
- Pipeline integration tests
- Knowledge lifecycle tests
- Knowledge storage contract tests
- Persistence boundary tests
- Architecture boundary tests

Current validation includes:

- Pipeline regression tests
- Knowledge lifecycle tests
- Knowledge storage tests
- Architecture boundary tests

Current total: 225 passing automated tests.

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
- ADR-011 — MCP Integration Boundary
- ADR-012 — Persistent Project Knowledge Boundary
- ADR-013 — Pipeline Knowledge Integration

Future ADRs

- Incremental Scanner
- Plugin System
- Cache
- Configuration
- Multi-language Parsing
- Reference Graph

---

# 16. Future Evolution

Planned architectural improvements include

- persistent project knowledge lifecycle
- incremental knowledge loading
- knowledge reconstruction
- dedicated ProjectTree model
- incremental scannings
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
- MCP transport implementation
- IDE integrations
- external AI client support

## Persistent Knowledge Evolution

Persistent Project Knowledge was intentionally divided into multiple milestones.

Milestone 10.1 established the architectural boundary between the active analysis pipeline and persistent knowledge storage.

Milestone 10.2 integrated the persistent knowledge lifecycle into the analysis execution flow without coupling pipeline components to persistence concerns.

This milestone introduces the foundations required for persistence:

- persistent knowledge boundary definition;
- storage independence;
- deterministic identity preservation;
- separation between domain state and storage implementation.

The following milestones will extend this foundation with:

- knowledge serialization;
- knowledge restoration;
- update lifecycle;
- incremental analysis compatibility;
- persistent identity reconstruction.

This separation avoids coupling unfinished persistence behaviour into the existing pipeline and preserves the stability achieved by previous milestones.

Milestone 10.2 introduced:

- knowledge lifecycle coordination;
- pipeline preparation and finalization hooks;
- persistence lifecycle independence from storage implementation;
- architecture validation for persistence boundaries.

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

# 17.1 Persistent Project Knowledge Boundary

Persistent knowledge is treated as an external representation of the Project aggregate state.

The Project aggregate remains the source of truth during execution.

Persistence layers must not:

- modify domain behaviour;
- own project lifecycle;
- bypass application services;
- replace runtime project state.

The persistence boundary exists to allow knowledge produced by the analysis pipeline to survive between executions without coupling the domain model to storage mechanisms.

The first implementation phase focuses on defining ownership and boundaries.

Serialization and restoration strategies are still evolving and remain isolated behind the knowledge lifecycle boundary.

Incremental synchronisation is intentionally deferred to future milestones.

---

# 17.2 Pipeline Knowledge Integration

Persistent Project Knowledge is integrated into the execution lifecycle through a dedicated knowledge lifecycle service.

The pipeline does not directly manage persistence.

The execution flow is:

```text
Prepare Knowledge

↓

Analyse Project

↓

Update Project State

↓

Persist Knowledge
```

The lifecycle service coordinates persistence operations while keeping:

- Scanner responsibility unchanged;
- Parser responsibility unchanged;
- Indexer responsibility unchanged;
- Chunker responsibility unchanged;
- Embedding responsibility unchanged;
- Retrieval responsibility unchanged;
- Context Builder responsibility unchanged.

This design preserves the modular pipeline architecture and prepares the foundation for future incremental analysis.

---

# 18. Engineering Philosophy

Codelp is designed as an engineering platform rather than a collection of utilities.

The architecture favours maintainability, modularity and deterministic behaviour over short-term implementation speed.

Every new feature should strengthen the architecture rather than increase technical debt.