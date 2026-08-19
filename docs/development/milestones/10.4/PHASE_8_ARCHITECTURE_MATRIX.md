# Milestone 10.4 — Phase 8 Architecture Matrix

## Purpose

This matrix records the executable architecture rules for persistent identity
and incremental analysis. Carrying runtime state on `Project` is distinct from
owning application logic: the Aggregate Root may expose opaque result slots,
while identity resolution, change detection, incremental planning and
persistence remain application-layer responsibilities.

| Requirement | Executable rule | Validation |
| --- | --- | --- |
| Identity tracking does not leak into domain models | `test_identity_tracking_and_incremental_logic_do_not_leak_into_core` | Core imports no application module and contains no tracking engines, decisions or identity-resolution methods. |
| Incremental logic does not leak into domain models | `test_identity_tracking_and_incremental_logic_do_not_leak_into_core` | Incremental plan, result and change-report slots remain typed as opaque runtime state; no planning or execution logic exists in Core. |
| Scanner owns only discovery | `test_analysis_facades_keep_their_single_responsibility[backend/app/scanner/scanner.py]` | Public API is limited to scanning and the facade imports no later analysis stage. |
| Parser owns only parsing | `test_analysis_facades_keep_their_single_responsibility[backend/app/parser/parser.py]` | Public API is limited to file/project parsing and imports no persistence or later analysis stage. |
| Indexer owns only indexing | `test_analysis_facades_keep_their_single_responsibility[backend/app/indexing/indexer.py]` | Public API is limited to index building and Project enrichment. |
| Chunker owns only chunk generation | `test_analysis_facades_keep_their_single_responsibility[backend/app/chunking/chunker.py]` | Public API is limited to chunk building and Project enrichment. |
| Embedding Engine owns only embeddings | `test_analysis_facades_keep_their_single_responsibility[backend/app/embeddings/engine.py]` | Public API is limited to embedding generation and Project enrichment. |
| Knowledge owns persistence intelligence | `test_knowledge_layer_owns_persistence_and_identity_intelligence` | Tracking, change detection, planning, merging, persistence and lifecycle classes remain in `app.knowledge`; pipeline cannot import their internals directly. |
| Project remains Aggregate Root | `test_project_is_the_analysis_aggregate_root` | Every analysis facade receives and returns the same domain `Project` contract. |
| Deterministic identities are preserved | `test_persistent_identity_generation_uses_deterministic_primitives` | Persistent identity sources reject random generators, `uuid4` and process-randomized `hash()`; deterministic inputs are behaviorally verified. |
| Architecture boundary tests added | `test_phase8_architecture_validation.py` | Thirteen Phase 8 acceptance tests protect dependency direction, responsibilities, ownership and determinism. |

## Boundary interpretation

- `ProjectKnowledgeState` is a storage-independent domain representation, not
  an identity tracking engine.
- `Project.knowledge_analysis_plan`, `knowledge_change_result` and
  `incremental_analysis_result` are non-persistent, opaque runtime slots.
- `KnowledgeLifecycleService` may populate those slots; Core cannot construct,
  interpret or execute their application-layer types.
- The pipeline may consume the lifecycle plan and disposable cache contracts,
  but cannot load snapshots, resolve identities, detect changes, merge
  knowledge or address a concrete storage implementation.

## Acceptance rule

Phase 8 is accepted only when the dedicated Phase 8 tests, the complete
architecture suite, the complete backend suite, module compilation and diff
validation all pass.
