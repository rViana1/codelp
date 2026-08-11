# ADR-009 — Context Builder Abstraction

## Status

Accepted

## Date

2026-08-11

---

# Context

As the Codelp pipeline evolved, retrieval became responsible for finding relevant project knowledge through semantic similarity.

However, retrieval results are not directly suitable for consumption by downstream systems such as LLMs or developer tools.

A dedicated processing stage was required to transform retrieved knowledge into a structured context representation.

Without a separate abstraction, retrieval would become responsible for:

- selecting relevant knowledge;
- formatting context;
- managing prompt preparation;
- handling future token constraints;
- adapting data for external consumers.

This would create excessive coupling between retrieval and future LLM integrations.

---

# Decision

Introduce a dedicated **Context Builder** component responsible for transforming retrieval results into structured project context.

The Context Builder will:

- consume `RetrievalCollection`;
- resolve retrieved chunk identities;
- recover chunk content from project knowledge;
- preserve retrieval ranking;
- maintain deterministic ordering;
- generate `PromptContext`;
- propagate diagnostics when knowledge cannot be resolved.

The Context Builder will remain independent from:

- LLM providers;
- prompt templates;
- retrieval implementations;
- vector storage systems.

The output of this component is a structured context representation that can be consumed by future systems.

---

# Architecture

The pipeline becomes:

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

PromptContext

↓

LLM / External Consumer

The Context Builder operates on existing project knowledge and does not create a new identity system.

The identity chain remains:

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

---

# Rationale

## Separation of Responsibilities

Retrieval answers:

> "Which knowledge is relevant?"

Context Builder answers:

> "How should that knowledge be structured for consumption?"

Keeping these responsibilities separate prevents retrieval from becoming aware of external consumers.

---

## LLM Independence

The Context Builder prepares structured information but does not generate prompts or call AI providers.

This allows future support for:

- multiple LLM providers;
- non-LLM consumers;
- IDE integrations;
- developer tooling.

---

## Deterministic Behaviour

The Context Builder preserves deterministic ordering from retrieval results.

Given identical project knowledge and retrieval results, the generated context must remain identical.

This enables:

- reproducible tests;
- caching;
- persistence;
- predictable AI behaviour.

---

## Future Extensibility

The abstraction provides a foundation for future capabilities:

- token budget management;
- context compression;
- prompt templates;
- context ranking;
- context caching;
- multi-context generation.

These features can evolve without changing retrieval responsibilities.

---

# Consequences

## Positive

- Retrieval remains focused on semantic search.
- LLM integration remains isolated.
- Context generation becomes independently testable.
- Future AI integrations require fewer architectural changes.
- Project knowledge can be consumed by multiple external systems.

---

## Negative

- Introduces an additional processing stage.
- Requires explicit mapping between retrieval results and stored knowledge.
- Future token optimisation requires additional design decisions.

---

# Alternatives Considered

## 1. Let Retriever Generate Final Context

Rejected.

The Retriever should only locate relevant knowledge.

Combining retrieval and context generation would tightly couple semantic search with consumer-specific formatting.

---

## 2. Let LLM Integration Handle Context Construction

Rejected.

The architecture should not require an LLM provider to understand project knowledge.

Structured context should exist before any AI interaction.

---

## 3. Store Prompt Information Directly in Chunks

Rejected.

Chunks represent reusable project knowledge.

Prompt-specific information belongs to the context generation layer.

---

# Validation

The Context Builder implementation validates this decision through:

- deterministic context generation;
- chunk identity preservation;
- retrieval-to-context integration;
- diagnostics propagation;
- independence from LLM providers.

Validation:

- 8 Context Builder tests passing.
- 103 total automated tests passing.

---

# Future Considerations

Future ADRs may define:

- token management strategy;
- prompt generation strategy;
- context compression;
- context caching;
- multi-agent context handling.
