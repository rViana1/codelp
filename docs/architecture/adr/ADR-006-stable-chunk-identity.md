# ADR-006 — Stable Chunk Identity Derived from Symbol Identity

**Status:** Accepted

**Date:** 2026-08-10

---

# Context

The Chunker transforms indexed project knowledge into semantic chunks that will later be used for embeddings, retrieval and context generation.

Each chunk must have a stable identifier so that future operations such as:

- embedding caching;
- incremental updates;
- vector store synchronization;
- chunk replacement;
- retrieval diagnostics;

can be performed deterministically.

An alternative considered was generating chunk identifiers independently from the Indexer, for example using sequential numbers or content hashes.

However, independent identifiers would create an additional identity layer and make synchronization between symbols and chunks more complex.

---

# Decision

Chunk identifiers are derived directly from symbol identifiers.

The relationship is:

```text
chunk.id == symbol.id
```

Examples:

- `src/main.py::hello`
- `src/models/user.py::User`
- `src/models/user.py::User.login`

The Indexer remains the single authority responsible for symbol identity.

The Chunker does not generate new semantic identifiers.

---

# Consequences

## Advantages

- Single source of truth for semantic identity.
- Deterministic chunk generation.
- Simpler embedding cache keys.
- Easier incremental updates.
- Easier synchronization with vector stores.
- Reduced architectural complexity.

---

## Disadvantages

- Chunk identity depends on Indexer stability.
- Renaming a symbol changes the chunk identifier.
- Future support for multiple chunks per symbol will require an additional strategy.

---

# Future Evolution

If large symbols need to be split into multiple chunks, the identifier may evolve to:

```text
<symbol_id>#<chunk_number>
```

Example:

```text
src/main.py::Service.run#1
src/main.py::Service.run#2
```

The base symbol identity will remain preserved.

---

# Notes

This ADR establishes a deterministic identity chain across the architecture:

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
    ↓
Retrieval Result
```

This decision is a foundation for future embedding, retrieval and persistent knowledge milestones.
