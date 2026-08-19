# ADR-018 — Application Runtime and Public Transport Boundary

## Status

Accepted

## Date

2026-08-19

## Context

CLI, MCP and REST need the same project capabilities. Allowing each transport
to assemble Scanner, Pipeline, Knowledge, Retrieval and storage independently
would duplicate policy and make externally visible behaviour diverge.

## Decision

`CodelpApplication` is the single transport-neutral application facade. It
owns workspace sessions and coordinates analysis, understanding, retrieval,
context and exploration through existing application services. `Project`
remains the Aggregate Root.

CLI, MCP and REST may depend on the runtime facade and external DTOs. They may
not instantiate the pipeline, access persistent knowledge models or select a
storage implementation.

The runtime is useful without an LLM. Embeddings are disabled by default;
deterministic analysis, graph construction, understanding and structural
exploration remain available. Local hash vectors are an optional model-free
fallback and are not described as learned semantic embeddings.

## Consequences

- All public interfaces share lifecycle, identity and error policy.
- New transports can be added without changing Core or Knowledge.
- The runtime becomes a significant application component requiring explicit
  architecture tests.
- Generative model providers remain optional consumers in a future milestone.

## Validation

Runtime, CLI, MCP, REST, no-model and public-interface consistency tests
protect this decision.
