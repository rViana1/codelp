# ADR-016 — Persistent Knowledge Graph Projection

## Status

Accepted

## Date

2026-08-19

## Context

Milestone 10.4 gave Codelp stable persistent identities, historical file
tracking, deterministic change detection and incremental updates. Milestone
10.5 must connect those entities into a graph that can support project-level
understanding, structural retrieval and historical exploration.

Introducing a graph creates several architectural risks:

- replacing `Project` with a second aggregate root;
- inventing graph-local identities that diverge from persistent identities;
- coupling persistence to a graph database;
- losing removed entities and relationships during snapshot updates;
- exposing graph implementation details to analysis modules or consumers.

The foundation must resolve these boundaries before richer relationships or
inference are added.

## Decision

Codelp will represent the knowledge graph as a deterministic persistent
projection owned by the Knowledge layer.

### Aggregate boundary

`Project` remains the only runtime Aggregate Root. The persistent graph is
restored as a storage-independent value inside `ProjectKnowledgeState`; it
does not own scanning, parsing, lifecycle or analysis behavior.

### Identity strategy

Every graph node references an existing persistent source identity. A stable
`entity_id` is derived deterministically from:

- project identity;
- graph entity kind;
- persistent source identity or stable historical key.

Relationship identity is derived deterministically from:

- project identity;
- relationship kind;
- source graph entity identity;
- target graph entity identity.

The graph therefore projects the existing identity system instead of creating
a competing one.

### Foundational entities

The first graph schema represents:

- project;
- file;
- historical file location;
- historical file content state;
- symbol;
- chunk;
- embedding metadata;
- retrieval metadata.

### Foundational relationships

The first graph schema supports directed relationships for:

- project contains file;
- file has location;
- file has content state;
- file declares symbol;
- symbol has chunk;
- chunk has embedding;
- chunk has retrieval metadata.

Import, dependency, duplication, similarity and explicit evolution
relationships remain later Milestone 10.5 phases.

### Historical model

Entities and relationships have first/last observation timestamps and an
`is_current` marker. Items absent from a later authoritative projection are
retained with their stable identity and marked inactive. A later reappearance
reactivates the same deterministic identity and preserves its earliest
observation.

File locations and content fingerprints are projected as independent temporal
entities, so file evolution is representable without treating a path or hash
as the file identity.

### Persistence boundary

The graph is embedded in `PersistentProjectKnowledge` and remains independent
from storage technology. JSON file storage and in-memory storage persist the
same graph contract; no graph database is required.

Knowledge schema `3.0` introduces the graph projection. Schema `2.0` snapshots
remain readable and restore with no graph until the next authoritative update
projects one.

The `KnowledgeBuilder` creates the current projection. The
`KnowledgeUpdateEngine` rebuilds it after authoritative merge so cumulative
file history and inactive graph history remain consistent. Normalization,
validation, serialization and restoration treat the graph as part of the
knowledge snapshot.

### Dependency direction

Scanner, Parser, Indexer, Chunker and Embedding Engine do not depend on the
graph implementation. Graph construction does not access storage or pipeline
orchestration. External consumers must eventually use application services
rather than persistent graph models directly.

## Consequences

### Positive

- Existing persistent identities remain authoritative.
- Graph identity survives executions and input ordering.
- Historical entities remain traceable after removal and reappearance.
- Storage technology remains replaceable.
- The graph can evolve toward richer relationships without redesigning Core.
- Project remains the runtime source of truth.

### Negative

- The persistent snapshot becomes larger because inactive graph history is
  retained.
- Schema `3.0` requires an explicit compatibility window for `2.0` snapshots.
- Derived graph consistency must be validated alongside canonical knowledge.
- Relationship growth will require future retention and compaction policies.

## Alternatives considered

### Replace Project with a graph aggregate

Rejected. It would invert the existing domain architecture and make analysis
modules depend on a representation optimized for persistence and querying.

### Use file paths as graph node identities

Rejected. Paths are historical locations and would recreate the identity
problem solved by Milestone 10.4.

### Persist only graph database identifiers

Rejected. It would couple project knowledge to one storage technology and
make deterministic restoration harder.

### Rebuild the graph without retaining inactive nodes

Rejected. It would prevent historical traceability and relationship identity
preservation across project evolution.

## Validation

The decision is protected by model, deterministic projection, temporal
history, storage round-trip, restoration, validation and architecture
boundary tests introduced in Milestone 10.5 Phase 1.

## Related decisions

- ADR-001 — Project Model
- ADR-012 — Persistent Project Knowledge Boundary
- ADR-013 — Knowledge Lifecycle Integration Boundary
- ADR-014 — Persistent Entity Identity and Historical File Tracking
- ADR-015 — Deterministic Knowledge Updates and Rollback
