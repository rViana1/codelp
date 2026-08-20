# Codelp Architecture

> **Version:** 3.0
> **Status:** In Development  
> **Last Updated:** Milestone 10.5 — Knowledge Graph & Intelligent Project Understanding

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

### Persistent Project Knowledge

Responsible for managing the lifecycle of persisted project knowledge.

Persistent Project Knowledge is an external deterministic representation of analysed project state.

The persistence layer does not replace the Project aggregate.

The runtime Project remains the source of truth during execution.

Responsibilities

- define persistent knowledge structure;
- serialize project knowledge;
- validate persisted knowledge;
- restore compatible knowledge;
- coordinate persistence lifecycle;
- preserve stable identities;
- maintain storage independence.

Outputs

- PersistentProjectKnowledge

Current implementation

- PersistentProjectKnowledge model
- Knowledge lifecycle service
- Knowledge storage abstraction
- Knowledge validation layer
- Schema version contract

Architecture rules

The Persistent Project Knowledge layer:

- does not modify domain behaviour;
- does not bypass application services;
- does not become the source of truth;
- does not couple the domain to storage technology;
- does not create duplicate identity systems.

The dependency direction remains:

```text
Analysis Pipeline

↓

Knowledge Lifecycle

↓

Persistent Knowledge Model

↓

Knowledge Storage Abstraction

↓

Storage Implementation
```

Persistent knowledge lifecycle:

Load and validate previous knowledge
                ↓
Restore storage-independent Project state
                ↓
Scan current repository
                ↓
Resolve identity and detect changes
                ↓
Execute full or selective analysis
                ↓
Merge and validate authoritative knowledge
                ↓
Commit snapshot, then disposable cache

Current capabilities:

- project knowledge serialization;
- project knowledge restoration;
- schema compatibility validation;
- deterministic normalization;
- identity preservation;
- historical file locations and fingerprints;
- deterministic move and rename resolution;
- deterministic change detection and invalidation;
- selective parser, indexer, chunker and embedding execution;
- deterministic knowledge merge and obsolete-entry removal;
- incremental cache fallback and full-analysis equivalence;
- atomic persistence operations.

Future improvements:

- selective restoration;
- knowledge migrations;
- advanced project evolution analysis;
- Git-aware and structural identity resolution;
- dependency-aware cross-file invalidation.

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

Persistent Knowledge Load

↓

Validation

↓

Restoration

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

Persistent Knowledge Generation

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
- app.knowledge → persistent knowledge models
- app.knowledge → knowledge storage abstraction

## Forbidden dependencies

- scanner → parser
- parser → chunker
- chunker → retriever
- retriever → scanner
- core → app
- core → vectorstore
- retriever → concrete vector database implementations
- core → persistent knowledge
- core → knowledge storage
- pipeline modules → storage implementations

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
- Persistent knowledge model tests
- Knowledge serialization tests
- Knowledge restoration tests
- Schema compatibility tests
- Identity preservation tests
- Persistence round-trip tests
- Corrupted knowledge recovery tests
- Architecture boundary tests

Current validation includes:

- Pipeline regression tests
- Knowledge lifecycle tests
- Knowledge storage tests
- Architecture boundary tests

Current total: 300 passing automated tests.

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
- ADR-014 — Persistent Entity Identity & Evolution Tracking
- ADR-015 — Deterministic Knowledge Updates & Rollback
- ADR-016 — Persistent Knowledge Graph Projection
- ADR-017 — Explainable Graph-Aware Retrieval and External Knowledge Access
- ADR-018 — Application Runtime and Public Transport Boundary
- ADR-019 — Workspace Execution, Isolation and Operational Safety

Future ADRs

- Plugin System
- Configuration
- Multi-language Parsing
- Reference Graph

---

# 16. Future Evolution

Planned architectural improvements include

- dedicated ProjectTree model
- structural matching for moved and modified files
- dependency-aware cross-file invalidation
- cross-version incremental cache migration
- remote repository support
- distributed indexing
- streaming parser
- parallel chunking
- multi-language parsing
- richer symbol metadata
- cross-file symbol resolution
- multi-chunk symbols
- persistent vector database implementations
- MCP transport implementation
- IDE integrations
- external AI client support
- higher-level project evolution insights

## Persistent Knowledge Evolution

Persistent Project Knowledge was intentionally divided into multiple milestones.

Milestone 10.1 established the architectural boundary between active project analysis and persistent knowledge storage.

Milestone 10.2 integrated persistence lifecycle coordination into the analysis execution flow without coupling pipeline components to persistence concerns.

Milestone 10.3 established the persistence foundation:

- canonical persistent knowledge model;
- runtime state separation;
- deterministic serialization;
- knowledge restoration;
- schema versioning;
- compatibility validation;
- storage hardening;
- identity preservation across executions.

Milestone 10.4 completed the next evolution of this lifecycle with persistent
entity identity, historical file tracking, deterministic change detection,
selective pipeline execution and transactional knowledge updates.

Future milestones may build higher-level project intelligence on this stable
identity and incremental execution foundation.

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

Persistent identity mapping now separates symbol identity from execution-local
path-based navigation identifiers.

Persistent symbols are associated with persistent file identities rather than
relying exclusively on physical paths.

This allows symbol continuity across file moves, renames and incremental knowledge updates.

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

Serialization and restoration strategies are formalized through the PersistentProjectKnowledge model.

Schema validation, compatibility checks and deterministic restoration are handled inside the persistence boundary.

Incremental synchronization is coordinated outside the domain through the
Knowledge lifecycle described below.

---

# 17.2 Persistent Entity Identity & Evolution Tracking

Persistent knowledge does not identify project entities only by their current physical location.

Codelp separates:

- entity identity;
- physical location;
- historical evolution;
- current content state.

A file is treated as a persistent entity that can survive changes in its location.

The system does not assume that a path represents identity.

A path represents only the current known location of an entity.

The identity layer is responsible for maintaining continuity between executions.

## Identity Principles

Persistent identities must be:

- deterministic;
- stable across executions;
- independent from physical paths;
- preserved after moves and renames when confidence is sufficient;
- compatible with future incremental analysis.

The identity model applies to:

- files;
- symbols;
- chunks;
- embeddings;
- other persistent knowledge entities.

## File Identity Strategy

File tracking uses multiple signals instead of relying on a single identifier.

The identity resolution process considers:

- previous known identities and their current locations;
- the current canonical project-relative path;
- the current SHA-256 content fingerprint;
- historical locations and fingerprints;
- whether a previous entity has already been claimed in the execution.

Structural similarity and repository-history signals are deliberately
deferred; the current resolver does not pretend to have evidence it cannot
deterministically establish.

The objective is to determine whether a current file represents:

- a new entity;
- an existing entity at the same location;
- an existing entity moved to a new location;
- an existing entity renamed;
- a duplicated entity.

## Historical Tracking

Persistent knowledge maintains historical information about entities.

Historical data may include:

- previous locations;
- previous fingerprints;
- identity transitions;
- detected changes.

Historical tracking policy and mutation exist only inside the Knowledge
layer. The Project aggregate may carry a storage-independent restored
`ProjectKnowledgeState`, but it does not interpret or update history.

## Identity Resolution Boundary

Identity resolution belongs exclusively to the Knowledge layer.

The following components must remain unaware of identity tracking:

- Scanner;
- Parser;
- Indexer;
- Chunker;
- Embedding Engine;
- Retriever;
- Context Builder.

The execution flow remains:

```text
Restore previous knowledge
        ↓
Scanner discovers current files
        ↓
Knowledge resolves identity and detects changes
        ↓
Knowledge emits analyze/reuse instructions
        ↓
Pipeline performs full or selective analysis
        ↓
Knowledge merges, validates and commits the next snapshot
```

## Identity Tracking Engine

The Knowledge layer executes identity resolution through a dedicated
`IdentityTrackingEngine`. The engine inventories known persistent entities,
associates current paths with file identities and returns deterministic,
auditable tracking results.

Tracking results include:

- typed identity decisions and confidence;
- probable moves and renames;
- historical identity updates;
- duplicate file-content groups;
- duplicate symbol groups;
- explicit ambiguity conflicts and their conservative resolution.

Exact current-location matches take precedence. A unique fingerprint match
for an unobserved previous file is considered a probable move or rename.
Ambiguous candidates produce a new identity and a conflict record.

---

# 17.3 Change Detection Behaviour

`ChangeDetectionEngine` compares the resolved current state with the previous
authoritative snapshot by persistent identity. A path is evidence about
location; it is never used as the primary persistent identity.

File changes are classified as:

- new;
- removed;
- moved;
- renamed;
- moved and renamed;
- modified;
- unchanged.

The deterministic report also partitions files, symbols, chunks, embeddings
and retrieval metadata into changed, unchanged, invalidated and reusable
sets. A content change invalidates dependent chunks, embeddings and retrieval
metadata. A location-only change preserves the persistent identity and keeps
unchanged derived knowledge reusable.

Duplicate fingerprints are reported diagnostically. Different files retain
different identities, and an ambiguous historical match creates a new
identity rather than selecting an arbitrary candidate.

---

# 17.4 Incremental Analysis Strategy

Every execution performs Scanner discovery. Only semantic stages may be
skipped.

After scanning, `KnowledgeExecutionPlanner` fingerprints current files,
resolves identity, computes changes and verifies disposable cached artifacts.
It returns deterministic per-file `analyze` or `reuse` instructions.

The pipeline then applies these rules:

- new and modified files are parsed and indexed;
- chunks are regenerated only for invalidated indexed symbols;
- embeddings are regenerated only for changed chunks or a different provider;
- unchanged files reuse cached parser, index, chunk and embedding artifacts;
- unchanged moved or renamed artifacts are relocated deterministically;
- removed-file artifacts are omitted without recomputing survivors;
- a missing, stale or corrupt cache causes safe recomputation.

The incremental cache is reconstructable runtime data, not authoritative
persistent knowledge. The merged runtime outputs must equal a complete
analysis of the same repository state.

---

# 17.5 Pipeline Knowledge Integration

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

Milestone 10.3 extended this lifecycle with:

- persistent knowledge serialization;
- persistent knowledge restoration;
- schema validation;
- deterministic normalization;
- identity preservation;
- storage hardening.

Milestone 10.4 extends this lifecycle with:

- persistent entity identity tracking;
- separation between identity and location;
- historical entity evolution;
- file move and rename detection foundation;
- deterministic identity resolution;
- deterministic current-versus-persisted change reports;
- changed, unchanged, invalidated and reusable knowledge classification;
- selective parser, index, chunk and embedding execution;
- disposable per-file runtime artifact caching;
- deterministic merging of reused and regenerated analysis results;
- deterministic authoritative knowledge merge and obsolete-entry removal;
- validate-before-commit updates with atomic and best-effort rollback;
- lifecycle-owned identity resolution and change detection before analysis;
- plan-driven pipeline execution with persistence-unaware analysis modules;
- incremental knowledge preparation.

The lifecycle now supports incremental analysis and is prepared for more
advanced structural and dependency-aware update capabilities.

## Authoritative Knowledge Update

After analysis, `KnowledgeUpdateEngine` merges the current candidate with the
previous snapshot. Current derived entries are authoritative: new and
modified entries replace by identity, obsolete entries are removed and equal
entries preserve their prior value. File histories are merged cumulatively,
including inactive records for removed files.

The merged snapshot is normalized and validated before storage. File storage
uses atomic replacement, while other storage implementations receive a
best-effort rollback attempt after a partial failure. Runtime change state and
the disposable cache are published only after the authoritative commit
succeeds.

## Architecture Boundary Validation

The Project Aggregate Root carries analysis results and opaque runtime
planning/change slots. It owns none of their application logic. Scanner,
Parser, Indexer, Chunker and Embedding Engine receive and return Project while
remaining unaware of Knowledge and persistence.

AST-based architecture tests enforce these dependency directions and public
responsibility contracts. The Phase 7 test matrix validates behaviour; the
Phase 8 architecture matrix validates ownership and boundaries.

---

# 17.6 Persistent Knowledge Graph Foundation

Milestone 10.5 introduces a persistent knowledge graph as a deterministic
projection of authoritative project knowledge. The graph belongs to the
Knowledge representation layer and does not replace Project as Aggregate
Root.

Foundational graph entities represent projects, files, historical locations,
historical content states, symbols, chunks, embedding metadata and retrieval
metadata. Their source identities are the persistent identities established
in Milestone 10.4. Graph entity identity is a deterministic projection of
project, kind and source identity rather than a second identity system.

Directed relationships connect the foundational ownership chain from project
to file, file history and derived semantic knowledge. Relationship identities
are deterministic functions of relationship kind and stable endpoints.

Entities and relationships include first/last observation timestamps and a
current marker. Missing items are retained as inactive history; reappearing
items recover the same identity. This provides temporal traceability before
the richer evolution and similarity relationships of later phases.

The graph is embedded in `PersistentProjectKnowledge`, normalized, validated
and serialized independently from storage technology. Schema `3.0` introduces
this projection while retaining read compatibility with schema `2.0`.
Restoration places a storage-independent graph representation inside
`ProjectKnowledgeState`.

ADR-016 defines the complete ownership, identity, temporal and persistence
decision.

## 17.7 Project Understanding Projection

The Project Understanding layer consumes the storage-independent graph
restored into `ProjectKnowledgeState`. It never reads persistence adapters or
the persistent Knowledge implementation directly. This preserves the graph as
a knowledge representation boundary while allowing higher-level consumers to
remain independent from storage technology.

The deterministic understanding engine derives architectural areas,
component importance, dependency flows and cycles, related code regions,
refactoring opportunities, evolution patterns, insights and structural
summaries. These results are reproducible projections: graph facts remain the
authoritative persisted knowledge and derived understanding remains opaque
runtime state on the Project Aggregate Root.

## 17.8 Intelligent Retrieval and Context Provenance

Intelligent retrieval is a deterministic enrichment stage after semantic
vector retrieval. It consumes the runtime graph contract, discovers related
current chunks through structural relationships and evaluates historical
observations separately. Semantic, structural and historical contributions
remain visible instead of being collapsed into an unexplained score.

Each result records why it was selected, the relationship identifiers that
support the decision and the graph entities from which that evidence came.
The Context Builder only resolves chunk content and propagates this evidence;
it performs no graph traversal. This keeps semantic retrieval, graph
representation and final context construction replaceable independently.

## 17.9 External Project Knowledge Boundary

External consumers access graph-derived knowledge through the Project
Knowledge application service. The service accepts the Project Aggregate Root
and returns serialized, external-safe views for project exploration, symbols,
dependencies, history, duplicate and similarity evidence, and contextual
knowledge.

MCP resources and tools are adapters over this service. They do not import the
Knowledge persistence implementation or storage adapters, and they cannot
construct queries against the persistent representation directly. This keeps
MCP transport concerns replaceable and prevents external consumers from
bypassing application policy.

The complete entity, relationship, persistence, historical, similarity,
understanding and retrieval model is documented in
`docs/architecture/KNOWLEDGE_GRAPH.md`. ADR-017 records the explainable
retrieval fusion policy and mandatory external application-service boundary.

---

# 18. Application Runtime and Public Interfaces

`CodelpApplication` is the transport-neutral application facade. It manages
explicit workspace handles and coordinates the established pipeline,
Knowledge lifecycle, Understanding, Retrieval and Context services. Project
remains the only domain Aggregate Root; workspace and execution state are
application concerns.

Configuration precedence is defaults, automatically discovered or explicit
user configuration, project-local configuration, environment and CLI or
application overrides. Interface enablement is enforced by composition.
Configuration contains no credential value fields. Model-free operation is the default: static
analysis, persistent graph knowledge, deterministic understanding and
structural exploration remain available without embeddings or an LLM.

CLI, stateless MCP JSON-RPC and REST are adapters over the same runtime.
Architecture tests forbid these transports from assembling the pipeline or
accessing Knowledge persistence. MCP supports the current `2026-07-28`
stateless protocol and a `2025-11-25` compatibility handshake. The official
MCP SDK validates discovery, schemas and calls over a real stdio subprocess.

Analysis executions are isolated per workspace and may run concurrently only
across distinct projects. Canonical-root storage namespaces keep equal project
directory names isolated without changing public project identity. Workspace
allowlists, canonical path resolution, symlink escape prevention and aggregate
request/project/execution limits apply before transport-specific logic.
Execution phase, progress and wait timeouts are external contracts. Structured
events expose correlation, duration and aggregate metrics
without source code, query text, credentials or raw error details.
CLI, MCP and REST share explicit user, project, configuration, capability,
security, conflict, timeout and internal diagnostic categories.

ADR-018 records runtime and public transport ownership. ADR-019 records
execution, workspace security and observability policy.

---

# 19. Engineering Philosophy

Codelp is designed as an engineering platform rather than a collection of utilities.

The architecture favours maintainability, modularity and deterministic behaviour over short-term implementation speed.

Every new feature should strengthen the architecture rather than increase technical debt.
