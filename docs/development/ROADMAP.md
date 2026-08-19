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
Vector Store Management
      │
      ▼
Persistent Project Knowledge
      │
      ▼
Retriever
      │
      ▼
Context Builder
      │
      ├──────────────► MCP Integration
      │                     │
      │                     ▼
      │              External AI Clients
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
- deterministic embedding generation
- embedding metadata generation

Output

`EmbeddingCollection`

Deferred

- Embedding cache
- Provider batching optimization

---

## Vector Store Management

Responsible for managing the lifecycle of project vector stores.

Responsibilities

- create project vector stores
- register project vector stores
- retrieve project vector stores
- remove project vector stores
- hide concrete storage implementations
- prepare architecture for persistent vector databases

Output

`VectorStore`

Current implementation

- InMemoryVectorStore

Implemented

- VectorStore abstraction
- VectorStoreManager
- Project vector store registration
- Project vector store retrieval
- Project vector store removal
- Storage lifecycle separation from retrieval

Deferred

- Persistent vector database implementations
- Remote vector storage
- Distributed vector storage

---

## Persistent Project Knowledge

Responsible for preserving analysed project knowledge between executions.

Responsibilities

- define persistent knowledge boundary
- preserve project identity
- persist project metadata
- preserve analysis state
- restore project knowledge
- maintain storage independence from domain logic
- prepare architecture for incremental analysis

Output

Persistent Project Knowledge

Current implementation

- Knowledge storage abstraction
- Storage repository interface
- InMemory knowledge storage
- File-based knowledge storage

Implemented

- Persistent knowledge boundary definition
- Knowledge lifecycle separation
- Storage abstraction
- Project knowledge registration
- Project knowledge retrieval
- Project knowledge removal

Architecture Evolution

Milestone 10.4 introduces a persistent identity model where analysed project entities are no longer identified exclusively by their current physical location.

The architecture evolves from execution-based identity preservation into historical entity tracking.

The system will distinguish:

- entity identity;
- current physical location;
- historical locations;
- content evolution;
- knowledge lifecycle changes.

File identity becomes independent from file paths.

The persistence layer will maintain historical information required to understand project evolution across executions.

The following capabilities are introduced as architectural foundations:

- persistent file identity;
- file location history;
- file content fingerprinting;
- deterministic identity resolution;
- unchanged-file move detection;
- unchanged-file rename detection;
- deterministic entity tracking.

The intelligent analysis of project evolution remains part of future milestones.

Deferred

- Incremental project updates
- Symbol identity evolution
- Chunk identity evolution
- Embedding identity evolution
- Retrieval metadata evolution
- Knowledge version migration
- Intelligent knowledge invalidation

---

## Retriever

Responsible for semantic retrieval over project embeddings.

Responsibilities

- vector similarity search
- similarity scoring
- deterministic ranking
- retrieval result generation
- vector store abstraction

Deferred

- hybrid retrieval
- advanced ranking strategies

---

## Context Builder

Responsible for transforming retrieved project knowledge into structured context.

Responsibilities

- consume RetrievalCollection results
- resolve chunk identities
- preserve retrieval ranking
- preserve deterministic ordering
- build structured PromptContext
- prepare knowledge for future LLM consumers

Output

`PromptContext`

The Context Builder does not depend on any LLM provider.

Its responsibility is context preparation only.


## MCP Integration

Responsible for exposing project knowledge to external consumers.

Responsibilities

- expose project resources
- expose project tools
- provide structured project information
- provide semantic search capabilities
- provide context retrieval
- preserve application boundaries
- avoid domain coupling

Output

MCP Resources
MCP Tools

Current implementation

- MCP server abstraction
- MCP resource registry
- MCP tool registry
- MCP execution layer

Supported capabilities

- Project information
- Project structure
- Symbol lookup
- Semantic search
- Context retrieval

Deferred

- Real MCP transport implementation
- IDE integrations
- External client validation
- Authentication and permissions


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
├── retrieval_result
├── context_result
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

**Status:** Completed

### Goals

- Stable chunk identifiers
- Semantic chunk boundaries
- Exact source extraction
- Deterministic ordering
- Chunk metadata
- Project integration
- Full pipeline validation

---

## Milestone 6 — Embedding Engine

Status

Completed

Goals

- Provider abstraction
- Deterministic embedding generation
- Project integration

Implemented

- Embedding domain models
- EmbeddingProvider protocol
- Deterministic fake embedding provider
- Embedding engine
- In-memory vector store
- Project embedding state integration

Deferred

- Embedding cache
- Persistent vector storage
- Provider batching optimization

Validation

- Provider abstraction validated
- Stable embedding identity validated
- Deterministic embedding generation validated
- Full pipeline regression validated

Tests

- 72 passing automated tests

---

## Milestone 7 — Retriever

Status

Completed

Goals

- Semantic search
- Vector similarity retrieval
- Deterministic ranking
- Project knowledge retrieval
- VectorStore abstraction consumption

Implemented

- Retrieval package
- Retrieval domain models
- RetrievalQuery
- RetrievalResult
- RetrievalCollection
- Cosine similarity strategy
- Similarity validation
- Retriever engine
- Deterministic ranking
- VectorStore abstraction
- In-memory vector store integration
- Project retrieval integration
- Diagnostics propagation
- Retrieval through managed vector stores
- Separation between retrieval logic and vector storage lifecycle

Deferred

- Query embedding generation
- Hybrid retrieval
- Advanced ranking strategies
- Retrieval caching
- Advanced persistent vector database implementations

Validation

- Retrieval boundaries validated
- Vector store independence validated
- Embedding compatibility validated
- Future Context Builder compatibility considered
- Incremental retrieval strategy validated

Tests

- 23 retrieval tests passing
- Full regression suite validated

---

## Milestone 7.1 — Vector Store Lifecycle Management

Status

Completed

Goals

- Separate vector storage lifecycle from retrieval logic
- Introduce vector store management layer
- Prepare architecture for persistent vector databases
- Preserve domain boundaries

Implemented

- VectorStoreManager
- VectorStore lifecycle management
- Project vector store registration
- Project vector store retrieval
- Project vector store removal
- VectorStore abstraction preservation
- Retrieval integration through managed stores

Architecture Validation

- Vector storage responsibility separated from Retriever
- Domain remains independent from storage concerns
- Future vector database migration path validated

Tests

- VectorStoreManager tests
- Project registration tests
- Project retrieval tests
- Missing store handling tests
- Retrieval regression tests
- Full pipeline regression

Validation

- 108 automated tests passing

---

## Milestone 8 — Context Builder

Status

Completed

Goals

- Transform retrieval results into structured context
- Preserve chunk identity
- Prepare project knowledge for future LLM consumption
- Maintain deterministic context generation

Implemented

- Context package
- ContextChunk model
- PromptContext model
- Context metadata structure
- ContextBuilder
- RetrievalCollection integration
- Chunk identity resolution
- Project context integration
- Diagnostics propagation
- Deterministic context ordering

Deferred

- Token counting optimization
- Context compression strategies
- Prompt templates
- LLM provider integration

Validation

- Context boundaries validated
- Retrieval → Context flow validated
- Retrieval independence validated
- Chunk identity propagation validated
- LLM independence validated
- Deterministic context generation validated

Tests

- 8 context tests passing
- 103 total automated tests passing
- Context integration validated through MCP layer
- Full regression suite passing

---

## Milestone 9 — MCP Integration

Status

Completed

Goals

- Expose Codelp project knowledge through Model Context Protocol.
- Allow external AI clients and developer tools to consume project knowledge.
- Preserve existing architecture boundaries.
- Keep MCP independent from domain implementation details.
- Introduce external integration without modifying existing pipeline responsibilities.

Implemented

- MCP package structure
- MCP server abstraction
- MCP lifecycle management
- MCP tool registry
- MCP resource registry
- MCP execution layer
- MCP request/response models
- MCP resource definitions
- Project information resource
- Project structure resource
- Symbol information resource
- Context resource
- Symbol lookup tool
- Semantic search tool
- Context retrieval tool
- MCP application service boundaries
- Retrieval integration through existing abstractions
- Context integration through existing abstractions
- Deterministic MCP responses
- Diagnostics propagation
- Architecture boundary validation

Validation

- MCP boundaries validated
- Domain independence validated
- Application layer boundaries validated
- Retrieval abstraction preserved
- Context Builder independence preserved
- Vector storage hidden from MCP
- Deterministic behaviour validated

Tests

- MCP lifecycle tests passing
- MCP resource tests passing
- MCP tool tests passing
- MCP retrieval integration tests passing
- MCP context integration tests passing
- Architecture boundary tests passing

Validation

- 175 MCP and integration tests passing

---

## Milestone 10.1 — Persistent Project Knowledge Boundary

Status

Completed

Goals

- Introduce persistent storage for Codelp project knowledge.
- Allow analysed project knowledge to survive between executions.
- Preserve deterministic project identities.
- Keep persistence independent from domain logic.
- Preserve Project aggregate as source of truth.
- Prepare architecture for future incremental analysis.

Implemented

- Persistent knowledge boundary definition
- Knowledge storage abstraction
- Knowledge repository interface
- Storage lifecycle operations
- Project knowledge registration
- Project knowledge retrieval
- Project knowledge removal
- InMemory knowledge storage implementation
- File-based knowledge storage implementation
- Deterministic storage output
- Storage independence from domain layer

Architecture Validation

- Domain remains independent from persistence concerns
- Project aggregate remains the source of truth
- Existing pipeline responsibilities preserved
- Existing module boundaries preserved
- Vector storage remains independent
- Retrieval architecture remains unchanged

Deferred

- Persisted file identities
- Persisted symbol identities
- Persisted chunk identities
- Persisted embedding metadata
- Persisted retrieval metadata
- Knowledge versioning
- Incremental analysis workflows

Tests

- Knowledge storage contract tests
- Storage lifecycle tests
- Persistence regression tests
- Full pipeline regression tests

Validation

- Persistent knowledge boundary validated
- Existing pipeline compatibility validated
- Storage abstraction validated


---

## Milestone 10.2 — Pipeline Knowledge Integration

Status

Completed

Goals

- Integrate persistent project knowledge into the analysis lifecycle.
- Restore previous project knowledge before analysis execution.
- Preserve existing pipeline module responsibilities.
- Generate updated knowledge snapshots after analysis.
- Persist project knowledge independently from storage implementation.

Implemented

- Knowledge lifecycle orchestration
- Knowledge loading before pipeline execution
- Project knowledge restoration
- Existing pipeline execution preservation
- Knowledge snapshot generation after analysis
- Knowledge persistence after analysis completion
- Pipeline integration through PipelineAnalyzer
- Storage-independent persistence workflow
- Stable project identity restoration

Architecture Validation

- Scanner remains independent from persistence
- Parser remains independent from persistence
- Indexer remains independent from persistence
- Chunker remains independent from persistence
- Embedding Engine remains independent from persistence
- Retriever remains independent from persistence
- Context Builder remains independent from persistence
- Project remains the Aggregate Root
- Persistence lifecycle remains separated from storage implementation

Tests

- Pipeline knowledge integration tests
- Knowledge restoration tests
- Identity preservation tests
- Architecture boundary tests
- Full regression suite passing

Validation

- Pipeline lifecycle validated
- Knowledge restoration validated
- Knowledge persistence validated
- Existing analysis pipeline preserved
- 225 automated tests passing

---

## Milestone 10.3 — Knowledge Persistence Foundation

Status

Completed

Goals

- Establish the complete persistent knowledge architecture.
- Separate runtime Project state from persisted project knowledge.
- Preserve Project aggregate as the runtime source of truth.
- Restore project knowledge between executions.
- Define deterministic knowledge representation.
- Introduce schema versioning and validation strategy.
- Ensure persistence remains independent from storage implementations.

Implemented

- Canonical PersistentProjectKnowledge model
- Project to persistent knowledge mapping
- Persistent knowledge restoration
- Knowledge validation layer
- Schema version contract
- Knowledge normalization
- Deterministic serialization
- Storage lifecycle hardening
- Complete knowledge lifecycle:
  - Load
  - Validate
  - Restore
  - Analyse
  - Update
  - Persist
- Identity preservation across:
  - files
  - symbols
  - chunks
  - embeddings
  - retrieval metadata

Architecture Validation

- Domain remains independent from persistence
- Domain remains independent from storage
- Scanner remains persistence unaware
- Parser remains persistence unaware
- Indexer remains persistence unaware
- Chunker remains persistence unaware
- Embedding Engine remains persistence unaware
- Retrieval remains persistence unaware
- Context Builder remains persistence unaware
- Project remains Aggregate Root
- Project remains runtime source of truth
- Storage implementations remain replaceable
- Persistence lifecycle remains controlled through application abstractions

Deferred

- Incremental change detection
- Persistent entity tracking
- File history tracking
- File move and rename detection
- Content fingerprint analysis
- Incremental pipeline execution
- Knowledge invalidation rules
- Partial analysis execution

Validation

- Persistent knowledge architecture validated
- Knowledge restoration validated
- Schema validation validated
- Identity preservation validated
- Round-trip persistence validated
- Architecture boundaries validated

---

## Milestone 10.4 — Persistent Identity & Incremental Knowledge

Status

Completed — Phases 1 through 9 validated

Goals

- Introduce persistent entity identity across executions.
- Separate entity identity from physical file location.
- Track project evolution over time.
- Detect changes between project executions.
- Enable incremental knowledge updates.
- Preserve unaffected knowledge.
- Reduce unnecessary analysis execution.
- Maintain deterministic project evolution.

Implemented

- Lifecycle integration governed by ADR-013, with identity and update
  decisions documented by ADR-014 and ADR-015.
- Persistent identity strategy defined.
- Historical file identity approach defined.
- File tracking strategy defined.
- Fingerprint-based identity resolution strategy defined.
- Identity tracking responsibilities defined inside Knowledge layer.
- Persistent identity model separated from physical locations.
- Deterministic, project-scoped file identity generation.
- Historical location and content fingerprint tracking.
- Conservative identity resolution using current paths and unique
  content fingerprints.
- File move and rename detection with ambiguity protection.
- File removal and reappearance tracking.
- Stable symbol identities associated with persistent file identities.
- Stable chunk identities associated with persistent symbol identities.
- Stable embedding identity through `(chunk_id, provider)`.
- Canonical project-relative POSIX paths in persistent knowledge.
- Knowledge schema `2.0` for the persistent identity contract.

Phase 2 — Identity Tracking Engine

- Identity tracking engine integrated into persistent knowledge mapping.
- Known file, symbol, chunk and embedding identities inventoried.
- Existing files and symbols resolved during each new execution.
- Current paths associated with persistent file identities.
- Historical locations and fingerprints maintained through tracking.
- Probable moves and renames classified with deterministic confidence.
- Duplicate file-content groups detected without merging identities.
- Duplicate symbols detected across distinct persistent files.
- Ambiguous path or fingerprint candidates reported as conflicts.
- Conflict policy creates a new identity rather than choosing arbitrarily.
- Tracking decisions, duplicates and conflicts returned in stable order.

Phase 3 — Change Detection Engine

- Current resolved knowledge compared with the previous persisted snapshot.
- New, removed, moved, renamed, moved-and-renamed, modified and unchanged
  files classified by stable identity rather than by path.
- Immutable project change report returned in deterministic order.
- Changed and unchanged elements defined for files, symbols, chunks,
  embeddings and retrieval metadata.
- Invalidated and reusable knowledge references defined explicitly.
- Dependency invalidation propagated from changed chunks to embeddings and
  retrieval metadata.
- Location-only changes preserve reusable file identity and derived
  knowledge.
- Change report exposed as runtime Project state and excluded from the
  persistent snapshot.
- Legacy file-diff API retained as a compatibility adapter.

Phase 4 — Incremental Analysis Pipeline

- Scanner retained as the discovery boundary for every execution.
- Disposable analysis cache separated from authoritative persistent
  knowledge.
- Cached parser, index, chunk and embedding artifacts associated with stable
  file identities.
- Parser execution restricted to new or content-modified files.
- Index and chunk generation restricted to invalidated files.
- Embedding generation restricted to chunks whose content or provider
  changed.
- Unchanged files reconstructed from cached runtime artifacts.
- Removed-file artifacts excluded without recomputing unaffected files.
- Moved and renamed cached artifacts relocated without expensive analysis.
- Unaffected persistent file, symbol, chunk and embedding identities
  preserved.
- Incremental execution metrics exposed as non-persistent Project runtime
  state.
- Incremental and complete runtime analysis results validated as equivalent.
- Corrupted, missing or unwritable cache degrades safely to recomputation.

Phase 5 — Knowledge Update Strategy

- Dedicated knowledge update engine introduced before persistence.
- Candidate snapshot defined as authoritative for current derived knowledge.
- New and modified symbols, chunks, embeddings and retrieval entries merged
  by persistent identity.
- Obsolete derived entries removed when absent from current knowledge.
- Unchanged entries preserve their previous persisted values.
- File identity, location and fingerprint histories merged cumulatively.
- Removed files retained as inactive historical identities.
- Earliest observations and latest sightings preserved during history merge.
- All updated collections returned in deterministic identity order.
- Complete knowledge validation required before the storage commit.
- Runtime change report published only after a successful commit.
- Atomic file replacement retained as the primary rollback mechanism.
- Best-effort previous-snapshot restoration added for stores that fail after
  a partial write.
- Failed validation and failed commits leave authoritative knowledge and
  runtime update state unchanged.

Phase 6 — Pipeline Integration

- Knowledge lifecycle now owns a dedicated pre-analysis execution planner.
- File identity tracking executed after discovery and before semantic
  analysis.
- File change detection executed from resolved identities before semantic
  analysis.
- Deterministic per-file `analyze` or `reuse` instructions exposed to the
  pipeline.
- Pre-analysis plan stored as non-persistent Project runtime state.
- Pipeline execution selected exclusively from the lifecycle plan.
- Final knowledge mapping consumes the file identities resolved by the plan
  instead of resolving them a second time.
- Symbol identity resolution remains in Knowledge and runs against planned
  file identities after analysis.
- Incremental cache construction and storage moved into lifecycle finalize.
- Pipeline incremental helper no longer hashes files, loads snapshots,
  resolves identities or performs change detection.
- Scanner, parser, indexer, chunker and embedding engine remain unaware of
  Knowledge and persistence.
- Project remains the runtime source of the plan, analysis outputs, execution
  metrics and final change report.

Phase 7 — Testing

- Acceptance matrix created for all Phase 7 requirements.
- New, removed, moved, renamed, modified and unchanged file detection covered
  through pipeline executions.
- Duplicate file fingerprints validated through the pre-analysis lifecycle
  plan without merging distinct identities.
- Identity preservation validated after modifications, moves and pure
  renames for files, symbols, chunks and embeddings.
- Incremental skip and selective regeneration paths verified with exact
  parser, indexer, chunker and provider call counts.
- Incremental snapshot and cache persistence validated across new storage and
  analyzer instances.
- Full and incremental execution compared from the same persisted baseline.
- Runtime parser/index/chunk/embedding outputs validated as equivalent.
- Authoritative persistent identities and content hashes validated as
  equivalent.
- Supporting determinism, conflict and rollback tests included in the
  acceptance matrix.

Phase 8 — Architecture Validation

- Core dependency direction validated structurally through Python ASTs.
- Identity tracking engines, decisions and resolution methods excluded from
  domain models.
- Incremental planning and execution logic excluded from domain models;
  Project retains only opaque, non-persistent runtime result slots.
- Scanner, Parser, Indexer, Chunker and Embedding Engine public facades
  restricted to their declared responsibilities.
- Analysis facades prevented from importing Knowledge, pipeline,
  persistence or unrelated downstream stages.
- Identity tracking, change detection, execution planning, deterministic
  merging, persistence and lifecycle ownership confirmed inside Knowledge.
- Pipeline prevented from importing persistence-intelligence internals or
  concrete storage implementations.
- Project validated as the shared Aggregate Root accepted and returned by
  every analysis facade.
- Persistent identity generation protected from random generators, `uuid4`
  and process-randomized `hash()`.
- Dedicated executable architecture acceptance matrix and boundary tests
  added for every Phase 8 requirement.

Phase 9 — Documentation

- README updated to version `v0.10.4` with the completed identity and
  incremental analysis capabilities.
- Canonical changelog filename corrected to `CHANGELOG.md` and the complete
  milestone history recorded.
- Lessons learned updated with the identity, change-detection, incremental
  execution, update and architecture-boundary findings.
- Main architecture reference aligned with the implemented pre-analysis
  lifecycle and authoritative update flow.
- Persistent identity architecture, tracking resolution order, change
  classifications and incremental reuse rules documented explicitly.
- Phase 7 test matrix and Phase 8 architecture matrix retained as executable
  acceptance references.
- ADR-013, ADR-014 and ADR-015 reviewed and confirmed sufficient; no new
  architectural decision emerged during documentation.

Deferred

- Structural matching for files moved and modified simultaneously
- Cross-version incremental cache migration

Architecture Validation

- Project remains Aggregate Root.
- Persistence remains independent from domain logic.
- Scanner remains responsible only for discovery.
- Parser remains responsible only for parsing.
- Indexer remains responsible only for indexing.
- Chunker remains responsible only for chunk generation.
- Embedding Engine remains responsible only for embeddings.
- Knowledge layer owns persistence intelligence.
- Entity history does not replace runtime project state.

Completion

Milestone 10.4 extends the persistence foundation created in Milestone 10.3.

The objective is not only to preserve the latest analysed state, but to understand how project knowledge evolves between executions.

Future implementations may extend this foundation with structural matching,
cross-version cache migration and dependency-aware cross-file invalidation.

---

## Milestone 10.5 — Knowledge Graph & Intelligent Project Understanding

Status

Completed — Phases 1 through 8

Goals

- Build persistent relationships between project entities.
- Introduce a project knowledge graph without replacing Project runtime state.
- Use stable identities to connect files, symbols, chunks and dependencies.
- Improve retrieval with cross-entity and cross-file context.
- Produce higher-level project evolution and architecture insights.
- Define dependency-aware invalidation where relationships require it.

Phase 1 — Knowledge Graph Foundation

- Project knowledge graph model defined inside the Knowledge layer.
- Typed graph entities defined for projects, files, historical locations,
  historical content states, symbols, chunks, embeddings and retrieval.
- Typed directed foundational relationships defined.
- Graph embedded in the storage-independent persistent knowledge contract.
- Existing persistent identities retained as graph source identities.
- Graph, entity and relationship identifiers derived deterministically.
- Historical entities and relationships retained as inactive observations.
- Removed and reappearing entities preserve graph identity and observation
  history.
- Storage-independent runtime graph restored through
  `ProjectKnowledgeState` without replacing Project.
- Knowledge schema `3.0` introduced with read compatibility for `2.0`.
- Graph projection integrated with authoritative knowledge build and merge.
- Deterministic normalization, validation and JSON round-trip implemented.
- ADR-016 records graph ownership, identity, temporal and persistence
  boundaries.

Phase 2 — Entity Relationships

- Persistent import references associated with stable source file identities.
- Internal module targets resolved conservatively only when unique.
- External modules represented as graph entities without synthetic files.
- File import and internal dependency relationships projected.
- File, symbol and chunk duplicate relationships projected deterministically.
- Structural chunk fingerprints added using normalized token shingles.
- Deterministic chunk similarity relationships include an auditable score.
- Historical locations connected through moved, renamed and combined
  move/rename relationships.
- Historical content states connected through evolution relationships,
  including later state reversions.
- Existing ownership relationships retained for files, symbols, chunks,
  embeddings and retrieval metadata.
- Relationship identity derived from kind and stable graph endpoints.
- Removed relationships retained as inactive history and reactivated with the
  same identity when they reappear.

Phase 3 — Project Understanding Layer

- Storage-independent understanding engine derives higher-level knowledge
  exclusively from the restored runtime graph.
- Architectural areas grouped deterministically from current file locations.
- Important files and symbols ranked from dependency, ownership and
  connectivity evidence.
- Directed dependency flows and circular dependency components identified.
- Duplicate and structurally similar code regions exposed with graph
  provenance.
- Duplicate-code, similarity and dependency-cycle refactoring opportunities
  generated deterministically.
- Moved, renamed and content evolution transitions summarized from historical
  graph relationships.
- Project-level insights and a structural summary generated without changing
  authoritative persistent knowledge.
- Understanding remains opaque runtime state on the Project Aggregate Root.
- Architecture tests enforce the Knowledge-to-Understanding dependency
  direction and storage independence.

Phase 4 — Intelligent Retrieval Foundation

- Semantic retrieval results enriched with current structural graph evidence.
- Related chunks discovered through duplicate and similarity relationships.
- Historical graph observations contribute separately auditable evidence.
- Semantic, structural and historical scores retained independently and
  combined with a deterministic weighting policy.
- Every selected chunk preserves reasons, relationship identifiers and graph
  entity provenance.
- Context generation propagates selection explanations and provenance.
- Context identifiers derive deterministically from query and selected
  evidence.
- Retrieval consumes only the storage-independent runtime graph contract and
  remains independent from graph projection and storage implementations.

Phase 5 — MCP / External Consumer Integration

- Storage-independent Project Knowledge application service added as the
  mandatory external-consumer boundary.
- Project graph overview exposed through `project://knowledge`.
- Project, symbol, dependency, history, duplicate, similarity and contextual
  knowledge exploration exposed through one validated MCP tool contract.
- MCP composition root registers both the external definitions and executable
  implementations.
- External responses contain serialized values and persistent identities,
  never internal storage objects.
- MCP adapters do not import Knowledge persistence or storage modules.
- Architecture tests enforce that consumers cannot bypass the application
  service.

Phase 6 — Testing

- Graph creation covers all entity and relationship categories.
- Entity and relationship identities validated across updates, disappearance,
  reappearance and JSON round-trips.
- Persistence and restoration validated through the storage abstraction.
- File dependencies, history, symbols, duplicates and code similarity covered.
- Project Understanding analysis validated from restored graph state.
- Intelligent retrieval and final context generation validated with persistent
  structural and historical provenance.
- End-to-end acceptance test covers graph projection, persistence, load,
  restoration, understanding, retrieval, external exploration and context.
- Complete backend regression suite remains green.

Phase 7 — Architecture Validation

- Project remains the Aggregate Root; the graph is nested runtime knowledge
  state and never replaces the aggregate.
- Graph remains a Knowledge representation and persistence projection.
- Core domain remains free from application and storage dependencies.
- Knowledge persistence remains behind the `KnowledgeStorage` abstraction.
- Intelligent Retrieval depends on the runtime graph contract rather than its
  projection or storage implementation.
- MCP adapters depend on application services and cannot bypass them.
- Graph entity and relationship identity remains deterministic.
- Validator enforces unique entities, relationships and valid endpoints.
- Historical locations and evolution relationships remain traceable.
- Consolidated executable architecture acceptance matrix added.

Phase 8 — Documentation

- README updated with graph, understanding, intelligent retrieval and MCP
  exploration capabilities.
- Main and Knowledge architecture references updated.
- Dedicated knowledge graph architecture reference documents entities,
  relationships, persistence, history, structural similarity, understanding
  and retrieval provenance.
- Roadmap and changelog updated across all Milestone 10.5 phases.
- Milestone lessons learned recorded.
- ADR-016 retained for persistent graph projection.
- ADR-017 added because explainable score fusion and mandatory external
  application-service mediation are new architectural decisions.

---

## Milestone 11 — External Integration & Production Ready

Status

Planned

Goals

- CLI
- REST API
- Real MCP transport
- IDE integrations
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
- ADR-004 — Python AST Parser
- ADR-005 — Stable Symbol Index
- ADR-006 — Stable Chunk Identity
- ADR-007 — Embedding Provider Abstraction
- ADR-008 — Retrieval Engine Abstraction
- ADR-009 — Context Builder Abstraction
- ADR-010 — Vector Store Lifecycle Management
- ADR-011 — MCP Integration Boundary
- ADR-012 — Persistent Project Knowledge Boundary
- ADR-013 — Knowledge Lifecycle Integration Boundary
- ADR-014 — Persistent Identity & Incremental Knowledge Strategy
- ADR-015 — Deterministic Knowledge Updates & Rollback
- ADR-016 — Persistent Knowledge Graph Projection
- ADR-017 — Explainable Graph-Aware Retrieval and External Knowledge Access

Planned ADRs

- Plugin System
- Configuration System
- Multi-language Support
- Persistent Vector Database Implementation
- LLM Provider Abstraction

---

# 9. Long-Term Vision

Codelp aims to become a complete software knowledge platform.

Instead of analysing isolated files, it will progressively understand an entire software system, preserve that knowledge over time, track project evolution and provide intelligent assistance to developers and AI systems.

The platform should remain:

- language agnostic
- deterministic
- modular
- extensible
- AI-ready
- maintainable
- domain-centric
