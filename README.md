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
Embeddings (planned)
    ↓
Retriever (planned)
    ↓
LLM Context (planned)
```

The project is designed around **determinism, modularity and testability**, providing a strong foundation for future semantic search, retrieval-augmented generation (RAG) and persistent project knowledge.

---

## Current Status

**Version:** `v0.5.0`

Implemented:

- Repository Scanner
- Python AST Parser
- Stable Symbol Index
- Deterministic Semantic Chunker
- Full pipeline integration
- Architecture documentation
- ADRs (Architecture Decision Records)

Validation:

- **55 automated tests passing**
- Deterministic outputs across executions
- Stable symbol and chunk identifiers

---

## Implemented Features

### Scanner

- Recursive repository discovery
- Ignore rules
- Deterministic tree ordering
- Symbolic link protection
- Project integration

### Parser

- Python AST parsing
- Import extraction
- Function extraction
- Class extraction
- Method extraction
- Source location metadata

### Indexer

- Stable symbol identifiers
- O(1) file lookup
- O(1) symbol lookup
- Dependency indexing
- Deterministic ordering

### Chunker

- Function chunks
- Class chunks
- Method chunks
- Exact source extraction
- Stable chunk identifiers
- Deterministic ordering

---

## Stable Symbol & Chunk Identity

Codelp uses deterministic identifiers throughout the pipeline.

Examples:

```text
src/main.py::hello
src/models/user.py::User
src/models/user.py::User.login
```

Chunk identifiers are derived directly from symbol identifiers:

```text
chunk.id == symbol.id
```

This strategy simplifies embeddings, caching, persistence and incremental updates.

---

## Project Structure

```text
backend/
├── app/
│   ├── scanner/
│   ├── parser/
│   ├── indexing/
│   └── chunking/
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
git clone https://github.com/<your-username>/codelp.git
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
55 passed
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
└── diagnostics
```

Each application module enriches the same `Project` instance.

---

## Milestones

| Milestone | Status |
|---|---|
| Project Domain | Completed |
| Scanner | Completed |
| Parser | Completed |
| Indexer | Completed |
| Chunker | Completed |
| Embedding Engine | Planned |
| Retriever | Planned |
| Context Builder | Planned |
| API / CLI | Planned |

---

## Roadmap

### Next — Embedding Engine

- Provider abstraction
- Batch generation
- Embedding cache
- In-memory vector store
- Persistence
- Project integration

### Future

- Multi-language parsing
- Incremental scanning
- Persistent project knowledge
- Retrieval-optimized chunking
- Cross-file context
- Distributed indexing

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

MIT

---

## Why Codelp?

Most code-assistant systems treat repositories as collections of text files.

Codelp treats a repository as **structured knowledge**:

- files become indexed artifacts;
- symbols become stable entities;
- chunks become semantic retrieval units;
- embeddings become reusable knowledge vectors.

The goal is not only to search code, but to build a **deterministic and evolvable understanding of a software project**.