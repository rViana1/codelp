# Knowledge Persistence Architecture

## Purpose

The knowledge layer represents the persistent memory of a project between Codelp executions.

Persistent knowledge is independent from storage technology and contains only stable project information.

---

# Persistent State

The following information is eligible for persistence:

## Project Metadata

Contains:

- project identity
- schema version
- lifecycle timestamps

---

## File Identity

Represents analysed files through stable identities.

Contains:

- file identifier
- path
- content hash

---

## Symbol Identity

Represents parsed symbols through stable identities.

Contains:

- symbol identifier
- owning file identifier
- symbol name
- symbol type

---

## Chunk Identity

Represents semantic chunks through stable identities.

Contains:

- chunk identifier
- source symbol identifier
- content hash

---

## Embedding Metadata

Contains metadata about generated embeddings.

The embedding vector storage is external.

---

## Retrieval Metadata

Contains retrieval-related persistent information.

---

# Runtime State

The following information must never be persisted:

- Scanner instances
- Parser instances
- Indexer instances
- Chunker instances
- Embedding engines
- Storage implementations
- Temporary caches
- Runtime object references
- Parent-child runtime navigation references

---

# Design Rules

- Persistent knowledge must not depend on storage implementation.
- Persistent models must be serializable.
- Persistent identities must remain stable across executions.
- Runtime services must consume knowledge, not own it.
