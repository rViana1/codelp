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
Retriever
    ↓
Context Builder
    ↓
LLM Context
```

The project is designed around **determinism, modularity and testability**, providing a strong foundation for semantic search, retrieval-augmented generation (RAG) and persistent project knowledge.

---

## Current Status

**Version:** `v0.8.0`

Implemented:

- Repository Scanner
- Python AST Parser
- Stable Symbol Index
- Deterministic Semantic Chunker
- Provider-independent Embedding Engine
- Vector Store abstraction
- Semantic Retrieval Engine
- Context Builder
- Full pipeline integration
- Architecture documentation
- ADRs (Architecture Decision Records)

Validation:

- **103 automated tests passing**
- Deterministic outputs across executions
- Stable symbol, chunk, embedding and context identities

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
Embedding.chunk_id
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
│   ├── retrieval/
│   └── context/
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

```text
91 passed
```

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
LLM
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
| Context Builder | Planned |
| API / CLI | Planned |

---

## Roadmap

### Next — MCP Integration

- Model Context Protocol support
- IDE integration
- External development tools
- AI-assisted workflows

### Future

- Multi-language parsing
- Incremental scanning
- Persistent project knowledge
- Retrieval-optimized chunking
- Cross-file context
- Distributed indexing
- MCP integration
- API and CLI interfaces
- LLM provider integration
- Prompt generation
- Context optimisation

---

## Documentation

- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/adr/`
- `docs/lessons/LESSONS_LEARNED.md`
- `CHANGELOG.md`
- `ROADMAP.md`

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
- retrieval becomes semantic project understanding.
- contexts become structured knowledge prepared for AI consumption.

The goal is not only to search code, but to build a **deterministic and evolvable understanding of a software project**.