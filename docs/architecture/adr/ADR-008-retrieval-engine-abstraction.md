# ADR-008 — Retrieval Engine Abstraction

## Status

Accepted

## Date

2026-08-11

---

# Context

Codelp requires a retrieval layer capable of searching previously generated project knowledge.

Previous milestones introduced:

- stable symbol identifiers;
- semantic chunks;
- deterministic embeddings;
- embedding storage abstraction.

The Retrieval Engine must consume this knowledge and return relevant project information without creating direct dependencies between processing stages.

The architecture must support future evolution, including:

- different vector storage implementations;
- hybrid retrieval strategies;
- metadata filtering;
- ranking improvements;
- persistent knowledge stores.

A concrete retrieval implementation should not dictate the architecture of the entire platform.

---

# Decision

Introduce a dedicated Retrieval Engine responsible for semantic search over project embeddings.

The Retrieval Engine will:

- receive an already encoded query vector;
- retrieve stored embeddings through a storage contract;
- calculate similarity scores;
- rank results deterministically;
- limit returned results according to query configuration;
- update the Project aggregate when operating through project integration APIs.

Retrieval will depend on an abstract vector storage contract instead of concrete storage implementations.

The initial implementation uses:

- cosine similarity for vector comparison;
- in-memory vector storage for validation;
- deterministic ordering rules for stable results.

---

# Architecture

The retrieval flow becomes:

```text
Query
  |
  v
Query Vector
  |
  v
Retriever
  |
  v
VectorStore
  |
  v
EmbeddingCollection
  |
  v
RetrievalResult
```

The complete knowledge identity flow remains:

```text
Source File
    |
    v
Parser Symbol
    |
    v
Symbol ID
    |
    v
Chunk ID
    |
    v
Embedding.chunk_id
    |
    v
RetrievalResult.chunk_id
```

Retrieval does not introduce a new identity system.

---

# Consequences

## Positive

- Retrieval logic is isolated from embedding generation.
- Vector storage can be replaced without changing retrieval behaviour.
- Future vector databases can be introduced through the storage contract.
- Retrieval behaviour is deterministic and testable.
- Existing project knowledge identity is preserved.

## Negative

- Additional abstractions increase the number of components.
- Future retrieval optimizations may require extending current contracts.
- Advanced ranking strategies are intentionally deferred.

---

# Alternatives Considered

## Direct Retrieval Over EmbeddingCollection

Rejected.

The Retriever would become coupled to the current embedding representation and make future storage changes harder.

---

## Coupling Retrieval With Embedding Generation

Rejected.

Query encoding and retrieval are separate responsibilities.

Combining them would reduce provider flexibility and violate the Single Responsibility Principle.

---

## Introducing a Vector Database Immediately

Rejected.

The current goal is architectural validation.

A persistent vector database should only be introduced when retrieval requirements justify the additional complexity.

---

# Future Evolution

Possible future extensions:

- hybrid semantic and structural retrieval;
- metadata filtering;
- persistent vector stores;
- retrieval scoring strategies;
- query rewriting;
- context-aware ranking;
- incremental vector synchronization.

---

# Validation

The decision was validated through:

- retrieval unit tests;
- similarity tests;
- vector store contract tests;
- project retrieval integration tests;
- deterministic retrieval tests.

Validation result:

```text
23 retrieval tests passing
```