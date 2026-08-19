# ADR-017 — Explainable Graph-Aware Retrieval and External Knowledge Access

## Status

Accepted

## Date

2026-08-19

## Context

Semantic vector similarity identifies textually relevant chunks but does not
explain architectural relevance, related implementations or historical
continuity. Milestone 10.5 also needs external consumers to explore graph
knowledge without coupling MCP to persistent models or storage technology.

Combining these capabilities creates two risks: hiding unlike evidence inside
one opaque score, and allowing external adapters to become an alternative
application layer that bypasses project policies.

## Decision

Codelp will implement graph-aware retrieval as a deterministic enrichment
stage after semantic retrieval.

Semantic, structural and historical scores remain separate. The initial
combination weights are `0.70`, `0.25` and `0.05`. Each result retains
selection reasons, supporting relationship identities and provenance entity
identities. Final context propagates this evidence without performing graph
traversal itself.

Retrieval consumes `ProjectKnowledgeGraph` from the storage-independent Core
runtime contract. It does not depend on `KnowledgeGraphBuilder`, persistent
graph models or a storage adapter.

External graph access is mediated by `ProjectKnowledgeService`. MCP resources
and tools are adapters over that application service and may not directly
import Knowledge persistence or storage modules.

## Consequences

### Positive

- Context selection is auditable rather than represented by one opaque score.
- Structural and historical evidence can evolve independently.
- Semantic retrieval, graph projection and context construction remain
  replaceable.
- MCP and future consumers share the same application policy boundary.
- Persistent identities provide end-to-end traceability.

### Negative

- Weight changes become explicit retrieval policy changes requiring tests.
- Graph expansion increases the number of candidate results.
- External response contracts require deliberate evolution as new graph
  relationships are introduced.

## Alternatives considered

### Replace semantic ranking with graph ranking

Rejected. The graph augments semantic relevance; it does not contain enough
query meaning to replace embeddings.

### Collapse all evidence into a single undocumented score

Rejected. Consumers could not explain why context was selected or distinguish
current structural evidence from historical observations.

### Let MCP query persistent graph models directly

Rejected. It would bypass application services and couple external contracts
to storage-oriented representation details.

## Validation

Retrieval, context, external exploration, end-to-end and architecture tests
protect deterministic fusion, provenance propagation and dependency
boundaries.

## Related decisions

- ADR-008 — Retrieval Engine Abstraction
- ADR-009 — Context Builder Abstraction
- ADR-011 — MCP Integration Boundary
- ADR-012 — Persistent Project Knowledge Boundary
- ADR-016 — Persistent Knowledge Graph Projection
