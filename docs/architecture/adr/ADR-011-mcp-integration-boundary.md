# ADR-011 — MCP Integration Boundary

## Status

Accepted

## Context

Codelp exposes a growing amount of project knowledge generated through its internal pipeline.

This knowledge includes:

- project metadata;
- project structure;
- indexed symbols;
- embeddings;
- retrieval results;
- generated context.

External consumers such as AI assistants, developer tools and IDE integrations require access to this knowledge.

Direct access from external integrations into domain implementations would create strong coupling between MCP and internal pipeline components, reducing maintainability and making future architectural evolution harder.

The Model Context Protocol (MCP) integration must therefore expose project knowledge while preserving existing domain boundaries.

## Decision

MCP will act as an external integration boundary and will not directly depend on internal pipeline implementations.

MCP access will happen exclusively through application-level services and exposed contracts.

The architecture follows these rules:

- MCP does not access scanner, parser, chunking, indexing, embeddings or vector storage implementations directly.
- MCP does not modify the Project aggregate state.
- Project remains the source of truth for generated knowledge.
- Application services translate domain information into external representations.
- MCP resources expose deterministic read-only project information.
- MCP tools delegate execution to existing application services.
- Retrieval and context generation remain independent from MCP.

The MCP layer is responsible only for:

- protocol-facing models;
- resource definitions;
- tool definitions;
- request/response handling;
- external serialization.

## Consequences

### Positive consequences

- External AI integrations can consume Codelp knowledge safely.
- Internal pipeline responsibilities remain unchanged.
- Domain logic remains independent from external protocols.
- MCP transport can evolve without changing core architecture.
- Future IDE integrations can reuse existing contracts.

### Negative consequences

- Additional application service layers are required.
- Some data transformation is necessary before external exposure.
- New MCP capabilities require explicit boundary design.

## Alternatives Considered

### Direct MCP access to domain objects

Rejected.

This would expose internal implementation details and create coupling between the protocol layer and domain internals.

### MCP calling pipeline components directly

Rejected.

Pipeline components have specific responsibilities and should not become external APIs.

### Embedding MCP inside the domain layer

Rejected.

MCP is an integration concern and does not belong to domain logic.

## Implementation Notes

Current MCP integration provides:

- project information resources;
- project structure resources;
- symbol resources;
- context resources;
- symbol lookup tool;
- semantic search tool;
- context retrieval tool.

All exposed functionality preserves deterministic behaviour and existing project knowledge identities.

## Validation

The architectural boundary is validated through automated tests ensuring:

- MCP does not import internal implementation modules;
- MCP communicates through application boundaries;
- exposed resources remain deterministic;
- tools preserve existing retrieval and context behaviour.

## Related Components

- MCP Server
- MCP Resources
- MCP Tools
- Application Services
- Retrieval Engine
- Context Builder
- Project Aggregate
