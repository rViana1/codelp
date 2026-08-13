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

## Milestone 10 — External Integration & Production Ready

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

Planned ADRs

- Persistent Project Knowledge
- Incremental Scanner
- Plugin System
- Configuration System
- Multi-language Support
- Persistent Vector Database Implementation
- LLM Provider Abstraction

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