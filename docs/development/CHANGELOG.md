# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

Future changes will be documented here.

---

## [Milestone 11 — Phases 5–11] — Public Runtime Completion

### Added

- Added FastAPI workspace, analysis, execution, query, context, knowledge,
  symbol and exploration contracts with generated OpenAPI.
- Added asynchronous analysis identities, per-workspace exclusion,
  cross-project concurrency, queued cancellation and wait timeouts.
- Added canonical workspace allowlists, symlink escape protection and resource
  limits shared by every public transport.
- Added structured correlation, duration, incremental reuse, graph and
  retrieval provenance metrics with content-safe diagnostics.
- Added public-interface consistency and consolidated architecture tests.
- Added ADR-018 and ADR-019.

### Architecture

- Project remains Aggregate Root.
- CLI, MCP and REST use `CodelpApplication` and cannot assemble the pipeline or
  access persistent Knowledge models.
- Codelp remains useful without embeddings and has no generative LLM
  dependency.

### Validation

- Validated 471 backend tests under two deterministic hash seeds and 59
  architecture boundary tests.
- Validated editable packaging and the `codelp`, `codelp-mcp` and `codelp-api`
  entry points.
- Validated Python compilation and diff formatting.

---

## [Milestone 11 — Phase 4] — Real MCP Transport

### Added

- Added stateless MCP `2026-07-28` JSON-RPC stdio transport.
- Added compatibility negotiation for `2025-11-25` initialize clients.
- Added workspace, analysis, exploration, graph-aware query and close tools.
- Added dynamic workspace status, knowledge and context resources.
- Added deterministic MCP schemas, cache metadata and protocol error mapping.

### Validation

- Validated the complete 76-test MCP suite and 444 backend tests.

---

## [Milestone 11 — Phase 3] — Command-Line Interface

### Added

- Added project initialization, analysis, status, query, context and
  exploration CLI commands.
- Added canonical JSON output and stable exit codes.
- Added CLI contract and architecture boundary tests.

---

## [Milestone 11 — Phase 2] — Workspace & Configuration Management

### Added

- Added strict typed scanner, persistence, embedding, retrieval and interface
  configuration.
- Added deterministic configuration precedence across file, environment and
  explicit override sources.
- Added project-local configured application composition.
- Added explicit disabled embeddings and deterministic local hash vectors.
- Added configurable retrieval fusion weights and similarity threshold.

### Validation

- Added precedence, invalid-value, secret exclusion, scanner policy,
  project-local persistence and no-model runtime tests.
- Validated 433 backend tests.

---

## [Milestone 11 — Phase 1] — Application Runtime Foundation

### Added

- Added the transport-neutral `CodelpApplication` runtime facade.
- Added managed project workspaces with deterministic identity and lifecycle.
- Added coordinated analysis, understanding, retrieval, context and project
  exploration operations.
- Added stable workspace status and capability reporting.
- Added a default local composition root with no generative LLM dependency.

### Changed

- Successful knowledge finalization now publishes the current restored
  knowledge graph back into the active Project Aggregate Root.

### Validation

- Added runtime lifecycle, persistence reuse, retrieval, exploration and
  architecture boundary tests.
- Validated 425 backend tests.

---

## [Milestone 10.5 — Phase 8] — Documentation

### Updated

- Updated README, roadmap, changelog, lessons learned and architecture
  references for the completed milestone.
- Documented graph entities, relationships, persistence boundaries, historical
  evolution, duplicate and structural similarity models.
- Documented project understanding, explainable retrieval, context provenance
  and external consumer access.

### Architecture Decisions

- Retained ADR-016 for deterministic persistent graph projection.
- Added ADR-017 because graph-aware score fusion and mandatory external
  application-service access are new architectural policies.

### Validation

- Validated 417 backend tests under two deterministic hash seeds.
- Validated 45 architecture boundary tests, Python compilation and diff
  formatting.

---

## [Milestone 10.5 — Phase 7] — Architecture Validation

### Validated

- Validated Project Aggregate Root ownership and graph representation scope.
- Validated domain, Knowledge, Understanding, Retrieval, Context and MCP
  dependency directions.
- Validated storage abstraction independence and prevention of persistence
  leakage.
- Validated deterministic graph identities, relationship endpoint consistency
  and historical traceability.

### Added

- Added a consolidated Milestone 10.5 architecture acceptance matrix.
- Expanded focused architecture tests for understanding, retrieval and MCP
  consumer boundaries.

---

## [Milestone 10.5 — Phase 6] — Testing

### Added

- Added end-to-end graph persistence, restoration, understanding, intelligent
  retrieval, external exploration and context acceptance tests.
- Added explicit entity and relationship identity round-trip validation.

### Validation

- Covered graph creation, identity preservation, relationship preservation,
  persistence, restoration, file and symbol relationships, history,
  duplicates, structural similarity, graph-aware retrieval and provenance-rich
  context generation.
- Validated the complete backend regression suite.

---

## [Milestone 10.5 — Phase 5] — MCP / External Consumer Integration

### Added

- Added a storage-independent Project Knowledge exploration service.
- Added project, symbol, dependency, history, duplicate, similarity and
  contextual knowledge views.
- Added the `project://knowledge` MCP resource.
- Added the `project_exploration` MCP tool and executable composition-root
  registration.

### Validation

- Added service, resource, tool and server execution tests.
- Added architecture tests preventing MCP consumers from importing Knowledge
  persistence or storage internals.
- Validated the complete MCP test suite.

---

## [Milestone 10.5 — Phase 4] — Intelligent Retrieval Foundation

### Added

- Added graph-aware enrichment of semantic retrieval results.
- Added deterministic semantic, structural and historical score fusion.
- Added explainable reasons, graph relationship evidence and entity
  provenance to retrieval results.
- Propagated retrieval evidence into context chunks.
- Made generated context identity deterministic for the same query and
  evidence.

### Validation

- Added graph expansion, historical evidence, ordering, explanation,
  provenance and deterministic context tests.
- Added architecture tests keeping retrieval independent from graph storage
  and context generation independent from graph traversal.

---

## [Milestone 10.5 — Phase 3] — Project Understanding Layer

### Added

- Added a deterministic, storage-independent project understanding engine.
- Added architectural-area, important-component and dependency-flow models.
- Added circular dependency, related-code, refactoring and evolution analysis.
- Added project insights and structural summaries derived from graph facts.
- Added Project runtime enrichment without persisting derived understanding.

### Validation

- Added behavioural tests for architecture areas, component importance,
  dependency cycles, related code, evolution and deterministic output.
- Added architecture tests for storage independence, aggregate ownership and
  the Knowledge-to-Understanding dependency direction.

---

## [Milestone 10.5 — Phase 2] — Entity Relationships

### Added

- Added persistent import references and conservative internal target
  resolution.
- Added module, import and file dependency graph relationships.
- Added deterministic duplicate relationships for files, symbols and chunks.
- Added normalized structural chunk fingerprints and similarity scores.
- Added moved, renamed, moved-and-renamed and content-evolution historical
  relationships.
- Preserved removed and reappearing relationship identities over time.

### Validation

- Added relationship, ambiguity, similarity, history and ordering tests.
- Validated the complete backend regression suite.

---

## [Milestone 10.5 — Phase 1] — Knowledge Graph Foundation

### Added

- Added persistent project knowledge graph models and deterministic graph
  projection.
- Added typed project, file, historical location, historical content,
  symbol, chunk, embedding and retrieval graph entities.
- Added foundational directed relationship types.
- Added temporal observation windows and inactive historical preservation.
- Added deterministic graph, entity and relationship identities derived from
  existing persistent identities.
- Added graph normalization, validation, JSON persistence and Project
  restoration.
- Added knowledge graph foundation and architecture boundary tests.
- Added ADR-016 — Persistent Knowledge Graph Projection.

### Changed

- Evolved the current persistent knowledge schema to `3.0` while preserving
  read compatibility with schema `2.0` snapshots.
- Integrated graph projection into candidate knowledge building and the
  authoritative update merge.

---

## [Milestone 10.4 — Phase 9] — Documentation

### Updated

- Consolidated persistent identity, identity tracking, change detection and
  incremental analysis documentation across the README, roadmap and main
  architecture reference.
- Added the completed Milestone 10.4 lessons learned.
- Corrected stale descriptions that still presented implemented incremental
  capabilities as planned work.
- Renamed the misspelled `CHANGELOOG.md` to the canonical `CHANGELOG.md`
  already referenced by the project documentation.
- Recorded the Phase 7 test matrix and Phase 8 architecture matrix as
  executable acceptance references.

### Architecture Decisions

- Reviewed ADR-013, ADR-014 and ADR-015 against the completed implementation.
- No additional ADR was created because Phase 9 introduced no new
  architectural decision.

### Validation

- Completed all nine Milestone 10.4 phases.
- Validated 361 automated backend tests and 30 architecture tests.
- Validated Python module compilation and repository diff formatting.

---

## [Milestone 10.4 — Phase 8] — Architecture Validation

### Added

- Added executable AST-based boundary tests for Core, analysis facades,
  pipeline and Knowledge.
- Added explicit public responsibility contracts for Scanner, Parser,
  Indexer, Chunker and Embedding Engine.
- Added Aggregate Root contract validation across every analysis facade.
- Added deterministic identity primitive validation.
- Added a Phase 8 architecture acceptance matrix.

### Architecture

- Confirmed that Project carries opaque runtime state without owning identity
  tracking or incremental execution logic.
- Confirmed that identity tracking, change detection, planning, merging,
  persistence and lifecycle intelligence remain inside Knowledge.
- Prevented the pipeline from bypassing the lifecycle through direct imports
  of persistence-intelligence internals.
- Preserved analysis-module independence from Knowledge and persistence.

### Validation

- Added 13 dedicated Phase 8 architecture tests.
- Validated the complete architecture test suite.

---

## [Milestone 10.4 — Phase 7] — Testing

### Added

- Added an executable acceptance matrix covering every Phase 7 requirement.
- Added end-to-end pure rename detection and identity-preservation coverage.
- Added duplicate-content reporting coverage through the lifecycle plan.
- Added modified incremental snapshot persistence across fresh storage and
  analyzer instances.
- Strengthened modification coverage across file, symbol, chunk and
  embedding identities.
- Strengthened full/incremental consistency to include authoritative
  persisted knowledge as well as runtime outputs.

### Validation

- Covered new, deleted, moved, renamed, modified, unchanged and duplicate
  files.
- Covered identity preservation after updates, moves and renames.
- Covered selective incremental execution and durable cache reuse.
- Covered deterministic reports, updates, conflicts and rollback as
  supporting acceptance requirements.

---

## [Milestone 10.4 — Phase 6] — Pipeline Integration

### Added

- Added lifecycle-owned pre-analysis knowledge planning.
- Added file identity resolution and file change detection between scanner
  discovery and semantic analysis.
- Added deterministic analyze/reuse instructions stored in Project runtime
  state.
- Integrated planned file identities into final knowledge mapping.
- Moved incremental cache construction and persistence into lifecycle
  finalization.

### Architecture

- Removed identity resolution, fingerprinting and persistent snapshot
  handling from the pipeline incremental helper.
- Preserved persistence independence in parser, indexer, chunker and
  embedding modules.
- Extended ADR-013 with the pre-analysis planning lifecycle.

### Testing

- Added execution-order coverage for scan, identity, changes and parser.
- Added pre-analysis versus final identity consistency validation.
- Added source-boundary tests preventing persistence intelligence from
  returning to analysis modules or the pipeline helper.

---

## [Milestone 10.4 — Phase 5] — Knowledge Update Strategy

### Added

- Added a dedicated deterministic knowledge update engine.
- Added explicit merge rules for new, modified, unchanged and obsolete
  derived knowledge.
- Added cumulative file location and fingerprint history merging.
- Added inactive historical preservation for removed file identities.
- Added validation-before-commit and publish-after-commit boundaries.
- Added best-effort rollback for storage implementations that can partially
  write before raising an error.
- Added ADR-015 documenting update and rollback semantics.

### Testing

- Added merge tests for additions, modifications, removals and unchanged
  entries.
- Added historical timestamp and deterministic ordering tests.
- Added validation of merged snapshot invariants.
- Added partial-write rollback and validation-failure isolation tests.

---

## [Milestone 10.4 — Phase 4] — Incremental Analysis Pipeline

### Added

- Added a disposable per-file analysis cache, separate from authoritative
  persistent knowledge.
- Added selective parser, indexer and chunker execution for invalidated
  files.
- Added selective embedding generation for changed chunks or providers.
- Added deterministic merging of cached and newly generated runtime results.
- Added cached artifact relocation for unchanged file moves and renames.
- Added runtime metrics describing analyzed, reused, removed and regenerated
  components.
- Added file and in-memory cache storage with safe fallback to full analysis.

### Testing

- Added call-count tests proving unchanged stages are skipped.
- Added partial modification, removal, move, provider-change and identity
  preservation coverage.
- Added equivalence validation between incremental and complete analysis.
- Added separate file-cache round-trip and deletion tests.

---

## [Milestone 10.4 — Phase 3] — Change Detection Engine

### Added

- Added a deterministic change engine that compares resolved current
  knowledge with the previous persisted snapshot.
- Added stable-identity classification for new, removed, moved, renamed,
  moved-and-renamed, modified and unchanged files.
- Added explicit changed, unchanged, invalidated and reusable element sets
  for files, symbols, chunks, embeddings and retrieval metadata.
- Added dependency invalidation from modified chunks to embedding and
  retrieval knowledge.
- Exposed the immutable change report as non-persistent Project runtime
  state during knowledge persistence.
- Preserved the former file-only diff interface through a compatibility
  adapter.

### Testing

- Added tests for every file change type, deterministic ordering, first-run
  behavior, element classification, dependency invalidation and persistence
  lifecycle integration.

---

## [Milestone 10.4 — Phase 2] — Identity Tracking Engine

### Added

- Added a dedicated identity tracking engine to knowledge mapping.
- Added deterministic resolution decisions with types and confidence.
- Added known-entity inventories for files, symbols, chunks and embeddings.
- Added probable move, rename and combined move/rename classification.
- Added duplicate file-content and duplicate-symbol detection.
- Added explicit conflicts for ambiguous path and fingerprint candidates.
- Added deterministic conflict policy that creates a new identity instead of
  choosing an arbitrary candidate.

### Testing

- Added tracking engine tests for existing entities, moves, renames,
  duplicates, conflicts, histories and input-order independence.

---

## [Milestone 10.4 — Phase 1] — Persistent Identity Foundation

### Added

- Added deterministic persistent identities independent from current paths.
- Added historical file locations and content fingerprint states.
- Added conservative file identity resolution and move/rename detection.
- Added removal, reappearance, duplicate-content ambiguity and content
  reversion handling.
- Added stable symbol and chunk identities across file moves and renames.
- Defined embedding identity as `(chunk_id, provider)`.
- Added strict schema `2.0` persistent models and identity invariants.

### Improved

- Canonicalized persistent paths as project-relative POSIX paths.
- Preserved configuration during deterministic normalization.
- Reused one prepared knowledge snapshot through lifecycle finalization.
- Preserved current fingerprint semantics when content returns to a previous
  state.

### Testing

- Added deterministic identity, move, rename, removal, reappearance,
  ambiguity and multi-entity pipeline tests.

---

## [Milestone 10.3] — Knowledge Persistence Foundation

### Added

- Added complete persistent knowledge architecture.
- Added canonical `PersistentProjectKnowledge` model.
- Added Project to persistent knowledge mapping.
- Added persistent knowledge restoration workflow.
- Added knowledge validation and schema versioning strategy.
- Added deterministic knowledge normalization.
- Added deterministic persistence serialization.
- Added complete knowledge lifecycle:
  - load;
  - validate;
  - restore;
  - analyse;
  - update;
  - persist.
- Added identity preservation across project knowledge entities.

### Improved

- Improved separation between:
  - runtime Project state;
  - persistent knowledge state;
  - storage implementations.
- Preserved Project aggregate as runtime source of truth.
- Preserved pipeline module independence from persistence concerns.
- Improved storage reliability through deterministic writes and validation.
- Prepared architecture for future incremental analysis.

### Architecture

- Validated persistence boundaries across the complete pipeline.
- Confirmed Scanner, Parser, Indexer, Chunker, Embedding Engine, Retrieval and Context Builder remain persistence unaware.
- Confirmed lifecycle ownership remains independent from storage implementations.
- Preserved replaceable storage architecture.

### Testing

- Added persistent knowledge mapping tests.
- Added restoration tests.
- Added schema validation tests.
- Added identity preservation tests.
- Added round-trip persistence tests.
- Added architecture boundary tests.

Validation:

- Knowledge persistence lifecycle validated.
- Restoration workflow validated.
- Architecture boundaries validated.
- 300 automated tests passing.


## [Milestone 10.2] — Pipeline Knowledge Integration

### Added

- Added knowledge lifecycle orchestration into the analysis pipeline.
- Added project knowledge loading before analysis execution.
- Added project knowledge restoration workflow.
- Added updated project knowledge snapshot generation after analysis.
- Added automatic persistence of project knowledge after pipeline completion.
- Added lifecycle coordination through `KnowledgeLifecycleService`.
- Added PipelineAnalyzer integration with persistent knowledge lifecycle.
- Added stable project identity restoration between executions.

### Improved

- Preserved existing analysis pipeline responsibilities.
- Kept Scanner, Parser, Indexer, Chunker and Embedding Engine independent from persistence concerns.
- Preserved Retriever and Context Builder independence from knowledge storage lifecycle.
- Improved separation between:
  - analysis execution;
  - knowledge lifecycle;
  - storage implementation.
- Prepared the architecture for future incremental analysis workflows.

### Architecture

- Added knowledge lifecycle integration boundary.
- Preserved Project aggregate as the single source of truth.
- Preserved storage replaceability through existing abstractions.
- Added ADR-013 — Knowledge Lifecycle Integration Boundary.

### Testing

- Added knowledge lifecycle integration tests.
- Added pipeline persistence tests.
- Added project knowledge restoration tests.
- Added stable identity restoration tests.
- Added architecture boundary validation tests.

Validation:

- Pipeline knowledge restoration validated.
- Knowledge persistence workflow validated.
- Existing pipeline behaviour preserved.
- Architecture boundaries validated.
- 225 automated tests passing.


## [Milestone 10.1] — Persistent Project Knowledge Boundary

### Added

- Added the architectural foundation for Persistent Project Knowledge.
- Added persistent knowledge boundary definition.
- Added separation between:
  - runtime Project state;
  - persisted project knowledge;
  - future storage implementations.
- Added knowledge storage abstraction foundation.
- Added replaceable storage architecture without coupling the domain model to persistence concerns.
- Added persistent knowledge lifecycle ownership definition.
- Preserved deterministic project identity strategy.

### Improved

- Clarified the responsibility boundary between:
  - Project aggregate;
  - analysis pipeline;
  - persistence layer.
- Preserved Project aggregate as the single source of truth during execution.
- Prevented persistence concerns from leaking into domain models.
- Prepared the architecture for future:
  - knowledge restoration;
  - incremental analysis;
  - persisted identity reconstruction.
- Maintained compatibility with existing Scanner, Parser, Indexer, Chunker, Embedding, Retrieval, Context and MCP components.

### Architecture

- Split Persistent Project Knowledge implementation into independent milestones.
- Established Milestone 10.1 as the architectural boundary phase.
- Deferred serialization, restoration and incremental synchronisation to future milestones.
- Added ADR-012 — Persistent Project Knowledge Boundary.

### Testing

- Preserved all existing pipeline behaviour.
- Validated compatibility with existing project lifecycle.
- Full regression validation completed.

Validation:

- 206 automated tests passing.

---
## [Milestone 9] — MCP Integration

### Added

- Added Model Context Protocol (MCP) integration layer.
- Added MCP domain models:
  - `MCPRequest`
  - `MCPResponse`
  - `MCPToolDefinition`
  - `MCPResourceDefinition`
  - `MCPToolRequest`
  - `MCPToolResponse`
  - `MCPRetrievalResult`
  - `MCPRetrievalResponse`
- Added MCP server architecture.
- Added MCP lifecycle management:
  - server creation;
  - initialization;
  - shutdown handling.
- Added MCP tool registry.
- Added MCP resource registry.
- Added MCP tool execution layer.
- Added MCP bootstrap workflow.
- Added MCP resources:
  - `ProjectInformationResource`
  - `ProjectStructureResource`
  - `ContextResource`
  - `SymbolResource`
- Added MCP tools:
  - `SymbolLookupTool`
  - `SemanticSearchTool`
  - `ContextRetrievalTool`.

### Improved

- Exposed project knowledge through a structured MCP interface.
- Added a clear separation between:
  - MCP contracts;
  - MCP resources and tools;
  - application services;
  - domain models.
- Preserved domain independence from MCP implementation details.
- Extended project knowledge access capabilities for future IDE and external tool integrations.
- Preserved deterministic behaviour across MCP operations.

### Architecture

- Added MCP integration boundary.
- Added MCP adapter layer between external consumers and application services.
- Validated dependency boundaries ensuring MCP does not depend on internal implementation details.
- Added ADR-011 — Model Context Protocol Integration.

### Testing

- Added MCP model tests.
- Added MCP resource tests.
- Added MCP tool tests.
- Added MCP registry tests.
- Added MCP execution tests.
- Added MCP server lifecycle tests.
- Added MCP bootstrap tests.
- Added deterministic failure validation tests.
- Added architecture boundary validation tests.

Validation:

- 67 MCP tests passing.
- 175 total automated tests passing.

---

## [Milestone 8] — Context Builder

### Added

- Added Context Builder architecture.
- Added context domain models:
  - `ContextChunk`
  - `PromptContext`
- Added context generation workflow:
  - retrieval result consumption;
  - chunk identity resolution;
  - structured context generation.
- Added deterministic context ordering.
- Added project context integration through:
  - `build(...)`
  - `build_project(...)`
- Added context diagnostics propagation.

### Improved

- Extended the project knowledge pipeline with structured context generation.
- Added a clear boundary between:
  - retrieval;
  - context preparation;
  - future LLM consumption.
- Preserved chunk identity throughout the complete knowledge pipeline.
- Maintained LLM provider independence by keeping context generation separate from LLM integration.

### Testing

- Added context model tests.
- Added context ordering tests.
- Added retrieval-to-context integration validation.
- Added project context integration tests.
- Added missing chunk handling validation.
- Added full pipeline regression tests.

Validation:

- 8 context tests passing.
- 103 total automated tests passing.

--- 

## [Milestone 7.1] — Vector Store Lifecycle Management

### Added

- Added Vector Store lifecycle management architecture.
- Added `VectorStoreManager`.
- Added project vector store registration workflow.
- Added project vector store retrieval workflow.
- Added project vector store removal workflow.
- Added vector store lifecycle abstraction.
- Added `VectorStoreFactory` for vector store creation.
- Added support for replaceable vector storage implementations.
- Added project-specific vector store management.

### Improved

- Decoupled vector storage lifecycle from retrieval logic.
- Preserved Retriever independence from storage implementations.
- Improved separation between:
  - retrieval;
  - vector storage management;
  - vector storage implementation.
- Prepared architecture for future persistent vector databases.
- Preserved project domain independence from storage concerns.

### Architecture

- Added Vector Store lifecycle management layer:

  - `RetrievalService`
  - `VectorStoreManager`
  - `VectorStoreFactory`
  - `VectorStore`

- Added ADR-010 — Vector Store Lifecycle Management.

### Testing

- Added VectorStoreManager tests.
- Added project vector store registration tests.
- Added project vector store retrieval tests.
- Added missing vector store handling tests.
- Added vector store lifecycle regression tests.
- Added retrieval regression validation.

Validation:

- 108 automated tests passing.

---

## [Milestone 7] — Retrieval Engine

### Added

- Added Retrieval Engine architecture.
- Added retrieval domain models:
  - `RetrievalQuery`
  - `RetrievalResult`
  - `RetrievalCollection`
- Added cosine similarity calculation.
- Added deterministic similarity validation.
- Added vector comparison error handling.
- Added vector store abstraction through `VectorStore`.
- Added retrieval workflow:
  - embedding retrieval;
  - similarity ranking;
  - deterministic result ordering;
  - result limiting.
- Added chunk identity preservation during retrieval.
- Added project retrieval integration through:
  - `retrieve(...)`
  - `retrieve_project(...)`
- Added retrieval diagnostics propagation.

### Improved

- Extended the project knowledge pipeline with semantic search capabilities.
- Extended the architecture to support future vector database implementations.
- Preserved independence between:
  - embedding providers;
  - retrieval engine;
  - vector storage implementation.
  - Prepared retrieval output for future Context Builder integration.

### Testing

- Added retrieval unit tests.
- Added similarity tests.
- Added vector store integration tests.
- Added project retrieval integration tests.
- Added deterministic retrieval validation.
- Added full retrieval regression tests.

Validation:

- 23 retrieval tests passing.

---

## [Milestone 6] — Embedding Engine

### Added

- Added provider-independent Embedding Engine architecture.
- Added `EmbeddingProvider` protocol abstraction.
- Added embedding domain models:
  - `Embedding`
  - `EmbeddingCollection`
  - `EmbeddingProviderInfo`
- Added deterministic `FakeEmbeddingProvider` for testing.
- Added embedding generation workflow:
  - single chunk embedding;
  - multiple chunk embedding;
  - deterministic ordering.
- Added in-memory vector store implementation.
- Added project integration through:
  - `embed(...)`
  - `embed_project(...)`
- Added embedding metadata propagation into project state.

### Improved

- Extended the project analysis pipeline with embedding generation.
- Extended the architecture to support future embedding providers.
- Preserved stable identity flow from symbols to chunks and embeddings.

### Testing

- Added embedding unit tests.
- Added provider abstraction tests.
- Added deterministic vector generation tests.
- Added embedding store tests.
- Added full pipeline regression tests.

Validation:

- 72 automated tests passing.

---

## [Milestone 5] — Chunker

### Added

- Added deterministic semantic chunking.
- Added chunk models:
  - `CodeChunk`
  - `ChunkCollection`
  - `ChunkKind`
- Added source extraction for:
  - functions;
  - classes;
  - methods.
- Added stable chunk identifiers derived from symbol identifiers.
- Added project chunk integration.

### Testing

- Added chunking tests.
- Added deterministic ordering tests.
- Added exact source extraction tests.

Validation:

- 55 automated tests passing.

## v0.5.0

Semantic Chunking and Full Pipeline Integration.

### Added

- `ProjectChunker`
- `CodeChunk`
- `ChunkCollection`
- `ChunkKind`
- Exact source extractors for functions
- Exact source extractors for classes
- Exact source extractors for methods
- Chunk builders
- Deterministic semantic chunking
- Stable chunk identifiers derived from symbol identifiers
- Project integration for chunking
- Full pipeline integration tests

### Changed

- Parser symbols now include `start_line` and `end_line`
- Architecture updated for semantic chunking
- Documentation updated for chunk identity and pipeline integration

### Validation

- Stable chunk identifiers
- Deterministic ordering
- Exact source extraction
- Full Scanner → Parser → Indexer → Chunker pipeline validation
- 55 passing automated tests


## v0.4.0

Stable Symbol Index milestone completed.

### Added

- Indexing package
- Stable symbol identifiers
- Relative path strategy
- SymbolKind enum
- SymbolEntry
- FileEntry
- DependencyEntry
- ProjectIndex
- Indexer builders
- Function indexing
- Class indexing
- Method indexing
- Import indexing
- Deterministic indexing order
- ProjectIndexer
- Indexer integration with Project
- Indexer unit tests
- Pipeline integration test
- ADR-005 — Stable Symbol Index

### Changed

- Architecture updated for navigable indexes
- Project index_result now contains files, symbols and dependencies
- Indexing responsibilities separated from parsing responsibilities

### Validation

- 12 indexing tests passing
- 40 total automated tests passing

---

## v0.3.0

Python Parser milestone completed.

### Added

- Parser package
- Language detector
- Python AST parser
- Import extraction
- Function extraction
- Class extraction
- Method extraction
- Method-to-class association
- ParsedFile model
- ParsedProject model
- Parser integration with Project
- Parser diagnostics propagation
- Parser unit tests
- Parser integration tests
- ADR-004 — Python AST Parser

### Changed

- ProjectStatistics now stores scanned_files
- Scanner now propagates scanned files into the Project aggregate
- Architecture updated to include the Parser implementation

### Validation

- 11 parser tests passing
- 28 total automated tests passing

---

## v0.2.2

Project Domain Model and Scanner Integration.

### Added

- Project aggregate root
- ProjectMetadata
- ProjectConfiguration
- ProjectStatistics
- Public domain API (`core.project`)
- Scanner integration with Project
- Safe tree serialization without circular references
- Domain model tests
- Scanner integration tests
- pytest configuration for backend package imports

### Changed

- Scanner can now enrich an existing Project instance
- Project tree stored as a serialization-safe representation
- Architecture updated to use Project as the central aggregate

### Preserved

- Existing `scan()` API
- Existing scanner behaviour
- Existing scanner tests

### Validation

- 17 automated tests passing

---

## v0.2.1

Initial implementation of the Project Scanner.

### Added

- ProjectScanner
- TreeNode
- ScanResult
- ScanFilter
- Deterministic scanning
- Recursive traversal
- Unit tests
