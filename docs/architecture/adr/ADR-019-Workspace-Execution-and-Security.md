# ADR-019 — Workspace Execution, Isolation and Operational Safety

## Status

Accepted

## Date

2026-08-19

## Context

Long-running analysis exposed through public transports introduces concurrent
requests, cancellation, filesystem scope and diagnostic leakage risks.

## Decision

Workspace roots are canonicalized and authorized against an explicit
allowlist before a Project is created. Filesystem roots are invalid
allowlists, symlink escapes are rejected and workspace/query limits are
central runtime policy shared by every transport.

Analysis executions receive deterministic runtime identities. Only one
analysis may run for a workspace; different workspaces may run concurrently.
Cancellation is accepted only while an execution remains queued, because
interrupting a running pipeline cannot yet guarantee safe stage rollback.
Timeouts stop waiting, not the underlying atomic analysis.

Operational events contain correlation IDs, categories, durations and numeric
metrics. They never include source content, query text, credentials or raw
exception messages.

## Consequences

- Public interfaces cannot expand filesystem authority independently.
- Failed analysis retains the last committed knowledge snapshot.
- Running cancellation remains deliberately unsupported until cooperative
  stage cancellation exists.
- Diagnostics remain useful without leaking project content.

## Validation

Concurrency, queued cancellation, timeout, allowlist, symlink escape,
resource-limit, redaction and architecture tests protect this decision.
