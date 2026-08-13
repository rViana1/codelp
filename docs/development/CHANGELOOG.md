# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

Future changes will be documented here.

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