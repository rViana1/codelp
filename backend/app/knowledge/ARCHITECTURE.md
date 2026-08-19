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

- deterministic persistent file identifier
- historical project-relative POSIX locations
- historical content fingerprints and sizes
- current location and fingerprint markers

The first identity is generated from the project scope, initial canonical
location and initial content fingerprint. Once persisted, the identifier is
preserved independently from later locations and content changes.

Resolution uses the following deterministic order:

1. exactly matching current location;
2. a unique fingerprint belonging to an unobserved previous file;
3. a new deterministic identity.

Ambiguous duplicate fingerprints are never merged. An unchanged file moved
or renamed preserves its identity and adds a new historical location.
Removed entities remain in persistent history with no current location.

## Identity Tracking Engine

`IdentityTrackingEngine` is the application layer responsible for resolving
execution-local observations against known persistent entities. It produces
an auditable `IdentityTrackingResult` containing:

- known file, symbol, chunk and embedding identities;
- resolved files and symbols;
- current-path associations;
- typed file decisions with confidence;
- duplicate content and symbol groups;
- deterministic conflict records.

Current-path matches have confidence `1.0`. A unique fingerprint belonging
to an unobserved previous file is classified as a probable move or rename
with confidence `0.9`. Multiple candidates are never selected arbitrarily:
the engine records the conflict and creates a new deterministic identity.

---

## Pre-Analysis Knowledge Planning

After scanner discovery, `KnowledgeLifecycleService.plan_analysis()` invokes
`KnowledgeExecutionPlanner` before parser execution. The planner:

1. fingerprints current scanned files;
2. resolves their persistent identities through `IdentityTrackingEngine`;
3. compares resolved files with the prepared snapshot;
4. verifies which cached artifacts are reusable;
5. emits deterministic per-file `analyze` or `reuse` instructions.

The resulting `KnowledgeAnalysisPlan` is stored on `Project` as runtime state.
`PipelineAnalyzer` only chooses full or selective execution and passes the
plan to its execution helper. It does not interpret snapshots, fingerprints,
identity candidates or change rules.

The resolved file identities in the plan are authoritative for the complete
execution. Final knowledge mapping consumes those identities and resolves
only post-analysis symbols against them. Cache construction and storage also
belong to lifecycle finalization.

Duplicate current content fingerprints are also exposed on the plan. They are
diagnostic information only: distinct files retain distinct identities and
ambiguous historical matches are never merged automatically.

---

## Change Detection Engine

`ChangeDetectionEngine` compares the resolved current snapshot with the
previous persisted snapshot. File comparison is keyed by persistent
`file_id`; paths are compared only to classify location changes.

The immutable report classifies files as new, removed, moved, renamed,
moved-and-renamed, modified or unchanged. It also defines changed and
unchanged project elements plus invalidated and reusable knowledge for
files, symbols, chunks, embeddings and retrieval metadata.

Unchanged chunks allow their embeddings and retrieval metadata to be reused.
A modified or removed chunk invalidates dependent embedding and retrieval
knowledge even when that dependent metadata happens to have the same value.
Pure file moves and renames preserve reusable identity and derived knowledge.

The persistence service stores the report in `Project` runtime state after
building the current snapshot. The report itself is never serialized as
persistent project knowledge.

---

## Incremental Analysis Cache

The incremental cache is not persistent knowledge. It is a disposable
optimization containing reconstructable parser, index, chunk and embedding
runtime artifacts grouped by stable file identity.

Every execution still scans the repository. Current observations are
resolved against persistent file identities before expensive stages run.
Unchanged files reuse cached artifacts; new or modified files execute parser,
indexer and chunker selectively. Embeddings are reused per chunk and are
regenerated only when chunk content or provider metadata changes.

Moved and renamed unchanged files preserve their persistent identities. Their
cached runtime paths and execution-local symbol/chunk identifiers are
deterministically relocated without invoking expensive analysis stages.

The authoritative knowledge snapshot is saved before the cache. A missing,
stale, corrupted or unwritable cache never invalidates persisted knowledge;
it only causes a later execution to recompute the affected artifacts.

---

## Knowledge Update Strategy

`KnowledgeUpdateEngine` is the single merge boundary between an analyzed
candidate and the next authoritative snapshot. The candidate is authoritative
for symbols, chunks, embeddings and retrieval metadata: new and modified
entries replace by identity, equal entries preserve their previous values,
and missing entries are removed as obsolete.

Files follow a historical policy instead. Their identities, locations and
fingerprints are merged cumulatively. Removed files remain with inactive
locations and fingerprints. For repeated observations, the earliest creation
time and latest sighting are retained.

The update engine returns deterministic collection order and does not mutate
either input. The persistence service validates the merged result before
attempting storage. It publishes the runtime change report only after the
commit succeeds.

Atomic file replacement is the primary rollback guarantee. Stores capable of
partial writes receive a best-effort restoration of the previous snapshot.
Validation failures never touch storage, and commit failures never publish a
new runtime update result.

---

## Symbol Identity

Represents parsed symbols through stable identities.

Contains:

- symbol identifier
- owning file identifier
- symbol name
- symbol type

Symbol identity is generated from the persistent owning file identity,
symbol type and symbol name. It therefore survives file moves and renames.
A symbol rename represents a new symbol identity in this phase.

---

## Chunk Identity

Represents semantic chunks through stable identities.

Contains:

- chunk identifier
- source symbol identifier
- content hash

One semantic chunk is currently produced per symbol. Chunk identity is
derived from the persistent symbol identity and chunk kind, so body changes
do not replace the chunk identity.

---

## Embedding Metadata

Contains metadata about generated embeddings.

The embedding vector storage is external.

Embedding identity is the composite `(chunk_id, provider)`. The embedding
hash represents the current generated vector and is not itself the identity.

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
- Persistent paths must be project-relative and use POSIX separators.
- Identity resolution must be deterministic and conservative.
- Ambiguous matches must create a new identity rather than merge entities.
- Runtime services must consume knowledge, not own it.

## Executable Architecture Boundary

The domain may carry storage-independent knowledge and opaque runtime result
slots, but it must never import application modules or implement identity
tracking, change detection, incremental planning or persistence behavior.

Scanner, Parser, Indexer, Chunker and Embedding Engine enrich the shared
`Project` Aggregate Root only within their declared responsibilities. They do
not import Knowledge, pipeline or persistence modules.

Identity tracking, change detection, execution planning, deterministic update
merging, lifecycle coordination and persistence are owned by `app.knowledge`.
The pipeline may consume lifecycle plan and disposable cache contracts, but it
must not interpret persisted snapshots, resolve identity candidates, detect
changes, merge knowledge or depend on concrete storage.

These rules are enforced by
`backend/tests/architecture/test_phase8_architecture_validation.py` and mapped
to Milestone 10.4 acceptance requirements in
`docs/development/milestones/10.4/PHASE_8_ARCHITECTURE_MATRIX.md`.
