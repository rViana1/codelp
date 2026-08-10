# ADR-006 — Embedding Provider Abstraction

**Status:** Accepted

**Date:** 2026-08-10

---

# Context

After introducing deterministic semantic chunking, Codelp required a mechanism for transforming chunks into vector embeddings.

The embedding subsystem needed to support:

- multiple embedding providers;
- deterministic testing;
- provider replacement without changing orchestration logic;
- future batching;
- future caching;
- future persistence;
- future retrieval and ranking.

A key architectural decision was defining how embedding generation would be abstracted from the rest of the system.

---

# Decision

Codelp will introduce an **EmbeddingProvider abstraction** implemented as a Python `Protocol`.

The embedding engine depends only on this abstraction and not on any concrete provider.

---

# Provider Contract

Every provider must expose:

INÍCIO DO BLOCO PYTHON
```python
@property
def info(self) -> EmbeddingProviderInfo: ...

def generate_embedding(
    self,
    chunk: CodeChunk,
) -> Embedding: ...

def generate_embeddings(
    self,
    chunks: list[CodeChunk],
) -> EmbeddingCollection: ...
```
FIM DO BLOCO PYTHON

The provider is responsible for:

- vector generation;
- vector dimensions;
- provider metadata.

The engine is responsible for:

- orchestration;
- deterministic ordering;
- project integration.

---

# Domain Model

Embeddings are represented by:

INÍCIO DO BLOCO TEXT

Embedding
├── chunk_id
└── vector

FIM DO BLOCO TEXT

Provider metadata is stored separately:

INÍCIO DO BLOCO TEXT

EmbeddingProviderInfo
├── name
├── model
└── dimensions

FIM DO BLOCO TEXT

Embeddings are grouped in:

INÍCIO DO BLOCO TEXT

EmbeddingCollection
├── provider
└── embeddings

FIM DO BLOCO TEXT

---

# Identity Strategy

Embeddings do not define a new identifier.

Identity is inherited from the chunk:

INÍCIO DO BLOCO TEXT

Symbol ID
   ↓
Chunk ID
   ↓
Embedding.chunk_id

FIM DO BLOCO TEXT

This preserves a stable navigation chain:

INÍCIO DO BLOCO TEXT

Embedding → Chunk → Symbol → File

FIM DO BLOCO TEXT

---

# Variable Vector Dimensions

The domain does not assume a fixed embedding size.

Vector dimensions are defined by the provider and exposed through `EmbeddingProviderInfo`.

This allows future use of models with different dimensionalities without changing the domain.

---

# Deterministic Testing

The first implementation introduces a `FakeEmbeddingProvider`.

Characteristics:

- deterministic;
- dependency-free;
- reproducible;
- stable for identical content.

It is used for unit tests, integration tests and pipeline validation.

---

# Storage Strategy

The initial implementation uses an `InMemoryVectorStore`.

Characteristics:

- O(1) lookup by `chunk_id`;
- insertion order preservation;
- no persistence.

Persistent storage is intentionally deferred to future milestones.

---

# Dependency Direction

The architecture preserves the dependency flow:

INÍCIO DO BLOCO TEXT

Chunker → Embeddings → Retrieval

FIM DO BLOCO TEXT

Forbidden dependencies:

INÍCIO DO BLOCO TEXT

Embeddings ↛ Scanner
Embeddings ↛ Parser
Embeddings ↛ Indexer
Embeddings ↛ Retrieval
Core ↛ Embeddings

FIM DO BLOCO TEXT

The domain remains independent from embedding providers.

---

# Public APIs

Technical API:

INÍCIO DO BLOCO PYTHON

embed(chunks: ChunkCollection) -> EmbeddingCollection

FIM DO BLOCO PYTHON

Domain API:

INÍCIO DO BLOCO PYTHON

embed_project(project: Project) -> Project

FIM DO BLOCO PYTHON

This remains consistent with the Scanner, Parser, Indexer and Chunker architecture.

---

# Consequences

## Advantages

- provider independence;
- deterministic tests;
- easy future integrations;
- low coupling;
- clear orchestration boundaries;
- retrieval-ready identity chain.

## Disadvantages

- additional abstraction layer;
- provider metadata duplicated across collections;
- no batching optimization yet;
- no persistence yet.

---

# Alternatives Considered

## Direct OpenAI integration

Rejected because it would couple the architecture to a single provider and make testing expensive and non-deterministic.

---

## Fixed vector dimension in the domain

Rejected because different embedding models use different dimensions.

---

## Embedding IDs independent from chunks

Rejected because chunk identity already provides a stable and navigable identifier.

---

# Future Evolution

Future milestones may add:

- OpenAI provider;
- local embedding providers;
- batching;
- caching;
- persistent vector stores;
- similarity search;
- asynchronous providers;
- provider registry;
- incremental embedding updates.

The current abstraction is considered sufficient for these future extensions.

---

# Validation

The decision is validated by automated tests covering:

- provider protocol;
- single embedding generation;
- multiple embedding generation;
- deterministic vectors;
- different content vectors;
- variable dimensions;
- in-memory store;
- project integration;
- full Scanner → Parser → Indexer → Chunker → Embeddings pipeline.

Current project validation:

- 72 passing automated tests.