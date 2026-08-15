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

**Version:** `v0.10.2`

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
- Pipeline knowledge integration
- Full pipeline integration
- Architecture documentation
- ADRs (Architecture Decision Records)

Validation:

- **206+ automated tests passing**
- Deterministic outputs across executions
- Stable symbol, chunk, embedding, retrieval and context identities

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
- Foundation for future incremental analysis

The persistence architecture preserves the Project aggregate as the runtime source of truth while allowing project knowledge to evolve across executions.

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

Codelp uses deterministic identifiers throughout the pipeline.

Example:

```text
src/main.py::hello
src/models/user.py::User
src/models/user.py::User.login
```

The identity chain is:

```text
Source File
    ↓
Parser Symbol
    ↓
Symbol ID
    ↓
Chunk ID
    ↓
Embedding Identity
    ↓
RetrievalResult.chunk_id
    ↓
ContextChunk.chunk_id
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
└── lessons/
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

Expected result:

175+ passed

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
└── diagnostics
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
| Incremental Knowledge Analysis | Planned |
| API / CLI | Planned |

---

## Roadmap

The architecture now exposes project knowledge through MCP and establishes the foundation for persistent knowledge lifecycle management while preserving existing pipeline boundaries.

### Next — Incremental Knowledge Analysis

- File identity persistence
- Symbol identity persistence
- Chunk identity persistence
- Change detection strategy
- Knowledge invalidation rules
- Incremental scanner support
- Incremental parser updates
- Incremental indexing
- Incremental chunk regeneration
- Incremental embedding updates

### Future

- Persistent vector database implementations
- Multi-language parsing
- Incremental scanning
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