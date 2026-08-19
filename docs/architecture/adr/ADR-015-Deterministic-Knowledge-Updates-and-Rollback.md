# ADR-015 — Deterministic Knowledge Updates and Rollback

## Status

Accepted

## Context

Incremental analysis produces a mixture of regenerated and reused project
knowledge. Persisting that mixture directly from individual mappers leaves
important decisions implicit: which entries replace previous values, which
missing entries are obsolete, which histories must survive, and what happens
when validation or storage fails.

The authoritative snapshot must never contain a partially applied update.
Its result must also be independent from input collection order.

## Decision

Codelp will apply every candidate snapshot through a dedicated
`KnowledgeUpdateEngine` before validation and persistence.

The merge policy is:

- the candidate is authoritative for current symbols, chunks, embeddings and
  retrieval metadata;
- entries missing from those current collections are obsolete and removed;
- equal entries preserve their previous persisted value;
- modified and new entries use the candidate value;
- file identities are historical entities and are never removed;
- previous file locations and fingerprints are merged cumulatively;
- the earliest observation and latest sighting are preserved;
- a file absent from the current state remains as inactive history;
- every collection is returned in deterministic identity order;
- the merged snapshot must pass the complete knowledge validator before
  storage is touched.

## Transaction and rollback policy

The persistence service treats validation and storage as a commit boundary.
It calculates the merged snapshot and change report locally, validates the
snapshot, and then attempts one storage commit.

File storage commits through an atomic temporary-file replacement, so a
failed replacement leaves the previous snapshot intact. For storage
implementations that can fail after a partial write, the service makes a
best-effort restoration of the previous snapshot. A rollback failure never
hides the original commit exception.

Runtime state is published only after the storage commit succeeds. Therefore
`Project.knowledge_change_result` never describes an update that was rejected
or rolled back. The disposable incremental cache is written only after the
authoritative snapshot commits.

## Consequences

- Merge behavior is testable independently from analysis and storage.
- Historical file identity cannot be accidentally lost by a partial mapper.
- Obsolete derived knowledge is removed consistently.
- Failed validation performs no write.
- Failed commits retain or restore the prior authoritative state.
- Storage implementations are still expected to provide atomic writes where
  practical; best-effort rollback is a secondary safeguard.

## Related decisions

- ADR-012 — Persistent Project Knowledge Boundary
- ADR-013 — Pipeline Knowledge Integration
- ADR-014 — Persistent Entity Identity and Historical File Tracking
