# ADR-013 — Knowledge Lifecycle Integration Boundary

## Status

Accepted

## Date

2026-08-15

---

# Context

Codelp requires persistent project knowledge between analysis executions.

The platform must be able to:

- load previously persisted project knowledge;
- restore compatible project state;
- execute the existing analysis pipeline;
- generate updated knowledge snapshots;
- persist the updated knowledge.

However, existing analysis modules must remain independent from persistence concerns.

The following modules must not know about storage or persistence lifecycle:

- Scanner
- Parser
- Indexer
- Chunker
- Embedding Engine
- Retriever
- Context Builder

Directly adding persistence responsibilities to these modules would violate existing architectural boundaries and reduce future extensibility.

---

# Decision

Introduce a dedicated knowledge lifecycle orchestration layer responsible for coordinating persistent project knowledge.

The `KnowledgeLifecycleService` becomes responsible for:

- loading existing project knowledge;
- restoring compatible project state;
- coordinating knowledge persistence after analysis;
- maintaining separation between persistence lifecycle and storage implementation.

The `PipelineAnalyzer` coordinates lifecycle execution by:

1. Preparing project knowledge before analysis.
2. Executing the existing analysis pipeline unchanged.
3. Persisting updated knowledge after analysis.

Existing pipeline modules remain unaware that persistence exists.

---

# Architecture

The lifecycle flow becomes:

Persistent Knowledge Storage
            │
            ▼
KnowledgeLifecycleService
            │
            ▼
PipelineAnalyzer
            │
            ├── Scanner
            ├── Parser
            ├── Indexer
            ├── Chunker
            ├── Embedding Engine
            ├── Retriever
            └── Context Builder


The lifecycle layer acts as an application boundary between persistence and analysis execution.

---

# Consequences

## Positive

- Existing analysis modules remain independent.
- Persistence implementation can change without affecting analysis modules.
- Storage technology remains replaceable.
- Future incremental analysis can reuse persisted knowledge.
- Project remains the single source of truth during execution.
- Pipeline responsibilities remain clearly separated.

## Negative

- Pipeline orchestration becomes responsible for lifecycle coordination.
- Additional application-layer abstraction must be maintained.
- Lifecycle behaviour requires dedicated integration tests.

---

# Validation

The decision was validated through:

- Knowledge lifecycle tests.
- Pipeline persistence integration tests.
- Project identity restoration tests.
- Architecture boundary tests.
- Full regression suite.

Validation results:

- Persistent knowledge restoration validated.
- Pipeline integration validated.
- Storage independence validated.
- Existing module boundaries preserved.
- 225 automated tests passing.