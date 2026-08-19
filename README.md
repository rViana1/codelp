# Codelp

Deterministic code understanding pipeline for AI-ready software knowledge bases.

Codelp transforms a software repository into structured, navigable and semantic knowledge through a progressive pipeline:

```text
Repository
    ↓
Scanner
    ↓
Parser
    ↓
Indexer
    ↓
Chunker
    ↓
Embedding Engine
    ↓
Vector Store
    ↓
Retriever
    ↓
Context Builder
    ↓
Project Knowledge
    ↓
MCP Server
    ↓
External Tools / IDE Integrations / LLM Consumers
```

The project is designed around **determinism, modularity and testability**, providing a strong foundation for semantic search, retrieval-augmented generation (RAG), persistent project knowledge and incremental project understanding.

---

## Current Status

**Version:** `v0.10.4`

Implemented:

- Repository Scanner
- Python AST Parser
- Stable Symbol Index
- Deterministic Semantic Chunker
- Provider-independent Embedding Engine
- Vector Store abstraction
- Semantic Retrieval Engine
- Context Builder
- Model Context Protocol (MCP) integration
- Persistent project knowledge lifecycle foundation
- Canonical persistent knowledge model
- Project knowledge serialization and restoration
- Knowledge schema validation and evolution
- Deterministic knowledge persistence
- Atomic knowledge storage workflow
- Pipeline knowledge lifecycle integration
- Persistent identity independent from current file location
- Historical file locations and content fingerprints
- Deterministic identity tracking and conflict resolution
- File change detection and knowledge invalidation
- Selective incremental parser, indexer, chunker and embedding execution
- Deterministic knowledge merging and rollback protection
- Full pipeline integration
- Architecture documentation
- ADRs (Architecture Decision Records)

Validation:

- **361 automated tests passing**
- **30 architecture boundary tests passing**
- Deterministic outputs across executions
- Stable symbol, chunk, embedding, retrieval and context identities
- Stable persistent identities after file updates, moves and renames
- Persistent knowledge round-trip validation
- Deterministic project restoration across executions
- Full and incremental analysis consistency validation

---

## Implemented Features

### Scanner

- Recursive repository discovery
- Ignore rules
- Deterministic tree ordering
- Symbolic link protection
- Project integration

---

### Parser

- Python AST parsing
- Import extraction
- Function extraction
- Class extraction
- Method extraction
- Source location metadata
- Diagnostics propagation

---

### Indexer

- Stable symbol identifiers
- O(1) file lookup
- O(1) symbol lookup
- Dependency indexing
- Deterministic ordering
- File and symbol navigation structures

---

### Chunker

- Function chunks
- Class chunks
- Method chunks
- Exact source extraction
- Stable chunk identifiers
- Deterministic ordering
- Semantic chunk boundaries

---

### Embedding Engine

- Provider abstraction
- Deterministic embedding generation
- Embedding metadata tracking
- Chunk identity preservation
- In-memory vector storage
- Project integration

The Embedding Engine remains independent from concrete embedding providers.

---

### Vector Store

- Vector storage abstraction
- Vector store lifecycle management
- Project-based store registration
- Replaceable storage implementations
- In-memory vector store implementation

The vector storage layer remains independent from retrieval logic and prepares the architecture for future persistent vector databases.

---

### Retriever

- Semantic similarity search
- Cosine similarity ranking
- Deterministic result ordering
- Query result limiting
- Vector storage abstraction
- Project retrieval integration

The Retriever consumes existing project knowledge without introducing a new identity system.

---

### Context Builder

- Retrieval result consumption
- Chunk identity resolution
- Structured context generation
- Deterministic context ordering
- Project context integration
- Diagnostics propagation

The Context Builder prepares structured project knowledge for future LLM consumers without depending on any LLM provider.

---

### Persistent Project Knowledge

- Persistent knowledge lifecycle foundation
- Project knowledge storage abstraction
- Knowledge loading and restoration boundaries
- Separation between runtime project state and persisted knowledge
- Pipeline integration with persistent knowledge workflows
- Stable persistent file, symbol, chunk and embedding identities
- Historical location and content fingerprint tracking
- Deterministic change reports and selective knowledge invalidation
- Incremental analysis artifact reuse

The persistence architecture preserves the Project aggregate as the runtime source of truth while allowing project knowledge to evolve across executions.

---

### Knowledge Persistence Foundation

- Canonical `PersistentProjectKnowledge` model
- Runtime state and persistent state separation
- Project knowledge serialization boundaries
- Project to persistent knowledge mapping
- Persistent knowledge restoration workflow
- Knowledge schema versioning
- Compatibility validation
- Deterministic knowledge normalization
- Deterministic serialization and loading
- Corrupted knowledge detection
- Atomic persistence operations
- Knowledge lifecycle validation

The persistence layer preserves the Project aggregate as the runtime source of truth while enabling deterministic restoration of project knowledge across executions.

Persistent knowledge now supports:

- project identity restoration;
- metadata restoration;
- parser knowledge restoration;
- index knowledge restoration;
- chunk identity preservation;
- embedding metadata preservation;
- retrieval metadata preservation.

---

### Persistent Identity and Incremental Analysis

- Project-scoped deterministic file identities
- File identity separated from current physical location
- Historical locations and fingerprints retained across executions
- Existing, modified, moved, renamed, removed and reappeared file tracking
- Conservative duplicate-content and ambiguity handling
- Stable symbol and chunk identities derived from persistent ownership
- Embedding identity defined by persistent chunk and provider
- Deterministic changed, unchanged, invalidated and reusable element sets
- Selective execution for parser, indexer, chunker and embedding stages
- Disposable runtime cache separated from authoritative knowledge
- Deterministic knowledge updates with validation and rollback protection

Every execution still scans the current repository. After discovery, the
Knowledge lifecycle resolves identities and changes before semantic analysis.
Unchanged artifacts can then be reused without making Scanner, Parser,
Indexer, Chunker or Embedding Engine aware of persistence.

---

### MCP Integration

- Model Context Protocol server
- Project knowledge exposure
- Structured context access
- External tool integration boundary
- IDE integration foundation

The MCP layer exposes Codelp project knowledge without coupling the core pipeline to specific clients, IDEs or LLM providers.

---

## Knowledge Identity Flow

Codelp distinguishes execution-local navigation identifiers from persistent
entity identities. Navigation IDs may contain paths, while persistent IDs are
resolved by the Knowledge layer and survive later location changes.

Example:

```text
src/main.py::hello
src/models/user.py::User
src/models/user.py::User.login
```

The persistent identity chain is:

```text
Current file observation
    ↓
Persistent file identity + location history
    ↓
Persistent symbol identity
    ↓
Persistent chunk identity
    ↓
Embedding identity (chunk ID + provider)
    ↓
Retrieval metadata
    ↓
Future executions reuse the same identities
```

This strategy simplifies:

- embeddings;
- retrieval;
- caching strategies;
- persistence;
- incremental updates.

---

## Project Structure

```text
backend/
├── app/
│   ├── scanner/
│   ├── parser/
│   ├── indexing/
│   ├── chunking/
│   ├── embeddings/
│   ├── knowledge/
│   ├── pipeline/
│   ├── vectorstore/
│   ├── retrieval/
│   ├── context/
│   └── mcp/
├── core/
│   └── project/
└── tests/

docs/
├── architecture/
│   └── adr/
├── development/
└── user/
```

---

## Installation

```bash
git clone https://github.com/rViana1/codelp.git
cd codelp

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Run Tests

```bash
pytest backend/tests -v
```

Expected result: **361 passed**.

---

## Architecture

The domain model is centered around a single aggregate root:

```text
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
├── knowledge_state
├── knowledge_analysis_plan
├── knowledge_change_result
├── incremental_analysis_result
└── diagnostics
```

Persistent project knowledge is represented separately:

```text
Project Runtime State

        ↓

PersistentProjectKnowledge

        ↓

KnowledgeStorage

        ↓

Storage Implementation
```

Each application module enriches the same `Project` instance.

The complete processing pipeline is:

```text
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
Project
    ↓
Context Builder
    ↓
Project
    ↓
MCP Server
    ↓
External Tools / IDE Integrations / LLM Consumers
```

---

## Milestones

| Milestone | Status |
|---|---|
| Project Domain | Completed |
| Scanner | Completed |
| Parser | Completed |
| Indexer | Completed |
| Chunker | Completed |
| Embedding Engine | Completed |
| Retriever | Completed |
| Context Builder | Completed |
| MCP Integration | Completed |
| Persistent Project Knowledge Boundary | Completed |
| Pipeline Knowledge Integration | Completed |
| Knowledge Persistence Foundation | Completed |
| Persistent Identity & Incremental Knowledge | Completed |
| API / CLI | Planned |

---

## Roadmap

The architecture now exposes project knowledge through MCP and provides
persistent identity, project evolution tracking and selective incremental
analysis while preserving existing pipeline boundaries.

Persistent knowledge can be restored, compared, selectively updated,
validated and persisted deterministically across executions.

### Next — Milestone 10.5

Milestone 10.5 can build higher-level project intelligence on the stable
identity and incremental knowledge foundation completed in Milestone 10.4.

- Knowledge graph relationships
- Dependency-aware cross-file invalidation
- Structural matching for files moved and modified simultaneously
- Higher-level project evolution insights
- Improved retrieval using persistent relationships

### Future

- Persistent vector database implementations
- Multi-language parsing
- Retrieval-optimized chunking
- Cross-file context
- Distributed indexing
- API and CLI interfaces
- LLM provider integration
- Prompt generation
- Context optimisation
- IDE integration
- External development tools
- AI-assisted workflows

---

## Documentation

### Architecture

- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/adr/`

Architecture Decision Records:

- `ADR-001` — Project Model
- `ADR-002` — Scanner Permission Handling
- `ADR-003` — Scanner Integration with Project
- `ADR-004` — Python AST Parser
- `ADR-005` — Stable Symbol Index
- `ADR-006` — Stable Chunk Identity
- `ADR-007` — Embedding Provider Abstraction
- `ADR-008` — Retrieval Engine Abstraction
- `ADR-009` — Context Builder Abstraction
- `ADR-010` — Vector Store Lifecycle Management
- `ADR-011` — MCP Integration Boundary
- `ADR-012` — Persistent Project Knowledge Boundary
- `ADR-013` — Pipeline Knowledge Integration
- `ADR-014` — Persistent Entity Identity and Historical File Tracking
- `ADR-015` — Deterministic Knowledge Updates and Rollback

---

### Development

- `docs/development/ROADMAP.md`
- `docs/development/LESSONS_LEARNED.md`
- `docs/development/DEFINITION_OF_DONE.md`
- `docs/development/DEVELOPMENT_GUIDELINES.md`
- `docs/development/CHANGELOG.md`

---

### User Documentation

- `docs/user/GETTING_STARTED.md`
- `docs/user/CONFIGURATION.md`

---

## Engineering Principles

- **Determinism** — same input, same output
- **Domain First** — Project aggregate is the source of truth
- **Modularity** — replaceable components
- **Testability** — public behavior is validated
- **Extensibility** — future languages and providers
- **Persistence Independence** — persistent knowledge evolves independently from storage technology
- **Identity Preservation** — knowledge entities maintain deterministic identities across executions
- **Conservative Resolution** — ambiguous entities are never merged arbitrarily
- **Incremental Equivalence** — selective analysis must match a complete analysis of the same state

---

## License

No license has been granted yet.

The repository is public for portfolio and review purposes.

---

## Why Codelp?

Most code-assistant systems treat repositories as collections of text files.

Codelp treats a repository as **structured knowledge**:

- files become indexed artifacts;
- symbols become stable entities;
- chunks become semantic retrieval units;
- embeddings become reusable knowledge vectors;
- retrieval becomes semantic project understanding;
- contexts become structured knowledge prepared for AI consumption.

The goal is not only to search code, but to build a **deterministic and evolvable understanding of a software project**.
