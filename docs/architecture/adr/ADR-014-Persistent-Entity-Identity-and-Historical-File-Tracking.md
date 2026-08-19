# ADR-014 — Persistent Entity Identity and Historical File Tracking

## Status

Accepted

## Context

Codelp is evolving from a repository analysis tool into a persistent code intelligence system.

The current persistent knowledge implementation stores analysed files using a `file_id` associated with the analysed file. However, this approach still couples the identity of a file with its current physical representation, namely its path.

This creates limitations when a project evolves:

- Files can be moved to different directories.
- Files can be renamed.
- Files can temporarily disappear and return.
- Multiple files can contain identical content.
- Historical knowledge about a file should survive changes in its location.

For incremental analysis and long-term project understanding, Codelp needs to distinguish between:

- the identity of an entity that exists through time;
- the current representation and location of that entity.

A file should therefore be treated as a persistent historical entity rather than only as a path discovered during scanning.

This decision also creates a foundation for future capabilities:

- duplicate file detection;
- duplicated code detection;
- redundant implementation detection;
- historical project evolution analysis;
- smarter incremental analysis;
- knowledge graph relationships.

## Decision

Codelp will adopt a persistent identity model where analysed entities have stable identities independent from their current physical location.

### File identity model

A file entity will be represented by:

- a stable persistent identity;
- one or more historical locations;
- content fingerprints;
- metadata describing changes over time.

The file path will no longer be considered the identity of the file.

Instead:

- paths represent locations where an entity existed;
- identities represent the entity itself.

### Historical tracking

Codelp will preserve historical information about entities.

The system will maintain:

- previous file locations;
- identity associations across executions;
- historical content fingerprints;
- detected moves;
- detected renames;
- detected removals and reappearances.

A moved or renamed file should preserve its identity whenever Codelp can deterministically resolve that it represents the same entity.

### Fingerprint-based resolution

Codelp will use content-based fingerprinting as part of identity resolution.

Fingerprinting will support:

- detecting unchanged files;
- detecting moved files;
- detecting renamed files;
- detecting duplicated content.

The exact fingerprint strategy may evolve, but the architecture must allow identity resolution to use multiple signals.

Possible future signals include:

- content fingerprints;
- structural similarity;
- symbol information;
- repository metadata;
- Git history.

### Scope separation

The identity tracking mechanism belongs to the Knowledge layer.

The following boundaries are maintained:

- Scanner discovers current filesystem state.
- Parser extracts source structure.
- Indexer creates navigable representations.
- Chunker creates semantic chunks.
- Embedding engine generates embeddings.
- Knowledge layer manages persistence, identity and historical understanding.

The Project aggregate remains the runtime source of truth during analysis.

## Consequences

### Positive consequences

- File identities survive moves and renames.
- Incremental analysis becomes more reliable.
- Historical project understanding becomes possible.
- Duplicate detection becomes easier to implement.
- Future knowledge graph relationships become more meaningful.
- Embeddings and chunks can be reused more efficiently.

### Negative consequences

- Persistent knowledge becomes more complex.
- Additional storage is required for historical information.
- Identity resolution introduces new algorithms and edge cases.
- Conflict resolution strategies are required when multiple possible matches exist.

### Neutral consequences

The first implementation does not need to provide intelligent project understanding.

This ADR only defines the identity and tracking foundation.

Higher-level analysis such as:

- architectural understanding;
- redundant code analysis;
- intelligent retrieval;
- project insights;

will be implemented in future milestones, particularly Milestone 10.5.

## Alternatives Considered

### Alternative A — Use file path as permanent identity

Rejected.

A path identifies a location, not an entity.

This approach fails when files are moved or renamed.

### Alternative B — Generate a new identity every execution

Rejected.

This prevents historical continuity and makes incremental analysis inefficient.

### Alternative C — Use only content hash as identity

Rejected.

Content alone cannot fully represent an entity.

Two different files may contain identical content while representing different concepts in a project.

Content fingerprints are useful signals, but not sufficient as the only identity mechanism.

### Alternative D — Use complex machine learning similarity immediately

Rejected for now.

Although intelligent similarity matching may improve future resolution, introducing it at this stage would increase complexity before the foundation exists.

The architecture will allow future intelligent resolution strategies without requiring redesign.

## Implementation Impact

The implementation will be introduced through Milestone 10.4:

- Persistent identity model.
- Identity tracking layer.
- Historical location tracking.
- Fingerprint-based resolution.
- Change detection.
- Incremental analysis.

Milestone 10.5 will build on this foundation to provide:

- knowledge graph relationships;
- intelligent project understanding;
- improved retrieval;
- higher-level code intelligence.

## Implementation Status — Milestone 10.4 Phase 1

Implemented with the following concrete policy:

- new file identifiers are deterministic and scoped to a project;
- persisted file identifiers are independent from subsequent locations;
- paths are canonical project-relative POSIX locations;
- a current-path match preserves identity across content changes;
- a unique fingerprint match for an unobserved previous file detects an
  unchanged move or rename;
- ambiguous fingerprint matches never merge identities;
- removed identities and their histories remain persisted;
- reappearing files preserve identity when resolution is unambiguous;
- symbol identities are based on persistent file identity, name and kind;
- chunk identities are based on persistent symbol identity and chunk kind;
- embedding identity is the composite of persistent chunk identity and
  provider.

Move or rename combined with simultaneous content modification remains
conservatively unresolved in this phase and creates a new identity. Structural
similarity, Git-aware matching and selective incremental execution remain
future work.

### Phase 2 — Identity Tracking Engine

The identity policies are executed through a dedicated tracking layer. Each
execution produces deterministic decisions describing new, existing,
modified, moved, renamed, reappeared, removed and conflict-created files.

The engine also reports:

- known persistent entities;
- duplicate current content fingerprints;
- duplicate symbol names and types across distinct files;
- ambiguous current-path or fingerprint candidates;
- the conservative resolution applied to each conflict.

Exact current-path matches take precedence over fingerprint resolution.
Unique unobserved fingerprint matches are probable moves or renames.
Ambiguous candidates always result in a new identity and an explicit conflict
record.

### Phase 3 — Change Detection Engine

Resolved snapshots are compared by persistent entity identity. Physical paths
participate only in the classification of moves and renames. The resulting
immutable report deterministically identifies file changes and partitions
project elements into changed, unchanged, invalidated and reusable sets.

Chunk content changes invalidate dependent embedding and retrieval metadata.
Location-only file changes preserve identity and keep unchanged derived
knowledge reusable. The report is runtime Project state and is deliberately
excluded from the persistent schema.

### Phase 4 — Incremental Analysis Pipeline

Persistent identities and the change model now drive selective pipeline
execution. A separate disposable cache stores reconstructable runtime
artifacts by stable file identity. It does not alter the authoritative
knowledge schema and may be discarded at any time.

Unchanged files skip parser, indexer, chunker and embedding generation. New
or modified files are analyzed selectively, while embeddings are regenerated
only for changed chunks or a changed provider. Cached artifacts for unchanged
moves and renames are deterministically relocated. The merged runtime result
is required to match a complete analysis of the same current project state.

## Related Decisions

- ADR-001 — Persistent Project Knowledge
- ADR-002 — Knowledge Layer Architecture
- ADR-003 — Persistence Boundary
- ADR-004 — Persistent Project Understanding

## Status Review

This ADR should be revisited if future implementations introduce:

- Git-aware identity resolution;
- advanced similarity matching;
- distributed knowledge storage;
- cross-project knowledge sharing.
