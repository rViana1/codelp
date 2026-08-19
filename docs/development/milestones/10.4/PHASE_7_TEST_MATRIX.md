# Milestone 10.4 — Phase 7 Test Matrix

## Purpose

This matrix records the executable acceptance coverage for persistent
identity, change detection and incremental analysis. Unit tests validate
individual policies; pipeline tests validate the complete lifecycle across
scanner discovery, pre-analysis planning, selective execution and persisted
knowledge update.

| Requirement | Primary executable coverage | Validation |
| --- | --- | --- |
| New file detection | `test_new_file_is_analyzed_without_reprocessing_known_files` | New file is reported before and after analysis; known files are reused. |
| Deleted file detection | `test_removal_drops_invalidated_artifacts_without_recomputing_survivors` | Removed file and derived artifacts disappear while surviving knowledge is reused. |
| Moved file detection | `test_move_reuses_analysis_and_relocates_runtime_results` | Pure move is reported and runtime paths are relocated without expensive stages. |
| Renamed file detection | `test_rename_reuses_analysis_and_preserves_all_identities` | Pure rename is distinguished from a move and skips expensive stages. |
| Modified file detection | `test_only_modified_file_and_invalidated_chunk_are_recomputed` | Only the modified file and changed chunk embedding are regenerated. |
| Unchanged file detection | `test_unchanged_execution_skips_every_expensive_stage` | All unchanged files are reported reusable; parser/index/chunk/embed calls remain zero. |
| Duplicate file detection | `test_duplicate_file_contents_are_reported_in_pre_analysis_plan` | Duplicate fingerprints are reported deterministically without merging file identities. |
| Identity after updates | `test_only_modified_file_and_invalidated_chunk_are_recomputed` | Modified file, symbol, chunk and embedding composite identities remain stable while hashes change. |
| Identity after moves | `test_move_preserves_file_symbol_chunk_and_embedding_identity` | File, symbol, chunk and embedding identities survive a persisted move/rename execution. |
| Identity after renames | `test_rename_reuses_analysis_and_preserves_all_identities` | All persistent identities survive a pure same-directory rename. |
| Incremental analysis | `test_unchanged_execution_skips_every_expensive_stage`, `test_only_modified_file_and_invalidated_chunk_are_recomputed` | Both complete reuse and selective invalidation paths are verified by call counts. |
| Persistence after incremental execution | `test_modified_incremental_snapshot_persists_across_processes` | A modified snapshot and cache survive new storage/analyzer instances and are reusable later. |
| Full/incremental consistency | `test_incremental_and_full_runtime_results_are_consistent` | Runtime outputs and authoritative identity/hash snapshots match a full analysis from the same baseline. |

## Supporting policy coverage

- `test_detects_every_file_change_using_stable_identity` validates every file
  change classification in one deterministic report.
- `test_resolution_result_is_independent_of_input_order` validates identity
  tracking determinism.
- `test_change_report_is_deterministic_for_shuffled_snapshots` validates
  change-report determinism.
- `test_merge_is_deterministic_for_reordered_inputs` validates update-order
  determinism.
- `test_ambiguous_duplicate_content_does_not_merge_identities` validates the
  conservative duplicate-content conflict policy.
- `test_failed_commit_rolls_back_snapshot_and_runtime_report` validates the
  transactional rollback boundary.

## Acceptance rule

Phase 7 is accepted only when the complete backend suite, Python module
compilation and whitespace validation all pass together.
