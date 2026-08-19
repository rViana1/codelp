# Persistent Knowledge Graph and Project Understanding

## Purpose

The Codelp knowledge graph is a deterministic, historical projection of the
authoritative persistent project knowledge. It connects stable project
entities so the application can explain structure, evolution and context
selection without replacing the `Project` Aggregate Root.

## Ownership and Persistence

`PersistentProjectKnowledge` owns the persisted graph contract. The graph is
serialized through `KnowledgeStorage` exactly like the rest of the canonical
snapshot, so neither the model nor its consumers depend on a graph database.
Knowledge schema `3.0` contains the graph; schema `2.0` remains readable and is
projected during the next successful knowledge update.

At runtime, `KnowledgeRestorer` translates the persistent graph into
`ProjectKnowledgeState.graph`. Understanding, Retrieval and external
exploration consume only this storage-independent runtime form.

## Entity Model

The graph represents:

- project;
- file;
- module;
- historical file location;
- historical file content state;
- symbol;
- chunk;
- embedding metadata;
- retrieval metadata.

Every graph entity points back to an existing persistent source identity.
Entity identity derives from project, entity kind and source identity. It is
therefore stable across ordering, persistence round-trips and executions.

## Relationship Model

Directed relationships describe:

- project ownership of files;
- file locations and content states;
- file-to-symbol and symbol-to-chunk ownership;
- chunk-to-embedding and chunk-to-retrieval metadata;
- imports and internal file dependencies;
- duplicate files, symbols and chunks;
- structurally similar chunks;
- moved, renamed and moved-and-renamed locations;
- content-state evolution.

Relationship identity derives from project, relationship kind and stable
endpoint identities. The validator rejects duplicate relationships, unknown
endpoints and current relationships whose endpoints are historical.

## Historical Entity Model

Entities and relationships carry first and last observation timestamps and an
`is_current` marker. Missing observations remain as inactive history; a later
reappearance reactivates the same deterministic identity.

Locations are not file identities. Content fingerprints are not file
identities. Both are temporal observations connected to a stable file entity.
Explicit evolution edges retain move, rename and content transitions,
including a return to a previously observed state.

## Duplicate and Similarity Model

Exact duplicate relationships use canonical persistent evidence:

- current file content fingerprint for files;
- symbol name and kind across distinct files for probable symbol duplicates;
- content hash for chunks.

Structural chunk fingerprints use normalized Python token shingles. Names and
literal values are normalized before shingles are generated, allowing similar
structure to be recognized even when identifiers differ. Similarity is the
deterministic Jaccard score of the two fingerprint sets; an edge is produced at
or above the configured `0.6` threshold and stores its score as evidence.

Ambiguity is handled conservatively. Internal import targets are linked to a
file only when module resolution has exactly one candidate.

## Project Understanding Model

The Understanding layer derives, without persistence side effects:

- architectural areas from current file locations;
- important components from dependency and ownership connectivity;
- dependency flows and circular dependency components;
- related code regions and refactoring opportunities;
- move, rename and content evolution patterns;
- project-level insights and structural summaries.

These values are reproducible projections held as opaque runtime state on the
Project. Persistent graph facts remain authoritative.

## Intelligent Retrieval and Provenance

Intelligent Retrieval enriches semantic results with current graph evidence
and separately identified historical evidence. Its deterministic policy gives
semantic, structural and historical contributions weights of `0.70`, `0.25`
and `0.05` respectively.

Results retain the component scores, human-readable selection reasons,
relationship identifiers and provenance entity identifiers. The Context
Builder propagates that trace unchanged and derives context identity from the
query and selected evidence.

## External Consumers

External consumers use `ProjectKnowledgeService`. MCP exposes the
`project://knowledge` resource and `project_exploration` tool over that
service. Consumers cannot import storage adapters or query persistent graph
models directly.

## Determinism and Validation

Graph collections, relationship properties, derived understanding and
retrieval results use canonical ordering and stable tie-breakers. Tests cover
input reordering, persistence and restoration, identity continuity,
relationship consistency, historical traceability, retrieval provenance and
external-service boundaries.
