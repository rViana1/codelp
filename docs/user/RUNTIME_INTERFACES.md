# Runtime and Public Interfaces

Codelp 0.11 introduces one application runtime shared by the command-line,
MCP and REST interfaces. All interfaces open the same project workspace and
delegate analysis, retrieval and exploration to `CodelpApplication`; they do
not assemble the pipeline or access knowledge storage directly.

## Installation

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

This installs three commands:

- `codelp` — command-line project analysis and exploration;
- `codelp-mcp` — JSON-RPC MCP server over standard input/output;
- `codelp-api` — local REST server bound to `127.0.0.1:8000`.

## Model-free operation

The default configuration does not load an LLM, contact a model service or
generate embeddings. Scanning, parsing, indexing, chunking, persistent
identity, incremental updates, graph construction, structural project
understanding and graph exploration remain available.

Set the embedding provider to `local_hash` to enable deterministic signed
feature-hash vectors without a model or network. These vectors preserve
reproducible lexical overlap; they are not learned semantic embeddings. An
external embedding provider can be added behind the existing provider boundary
when deeper semantic retrieval is required.

## Configuration

Run `codelp init PATH` to create `.codelp/config.json`. Configuration precedence
is deterministic:

1. built-in defaults;
2. an explicitly supplied user configuration file;
3. project `.codelp/config.json`;
4. allowlisted `CODELP_` environment settings;
5. explicit application overrides.

Unknown fields are rejected. Credentials are deliberately absent from the
configuration model and must be supplied by the deployment or provider
integration. Symbolic-link traversal is disabled until bounded traversal can
be guaranteed. Setting `llm_enabled` to true is also rejected in 0.11 because
no generative LLM integration is shipped; capability reporting therefore
cannot claim support that is not present.

## Command line

```bash
codelp analyze PATH --json
codelp status PATH --json
codelp query "where is configuration loaded?" --path PATH --json
codelp context "how is identity preserved?" --path PATH --json
codelp explore project --path PATH --json
```

JSON output is canonically ordered. `query` and `context` explicitly enable the
local hash embedding fallback; all other commands retain model-free defaults.

## MCP

Start the stdio transport with `codelp-mcp`. It supports the stateless
`server/discover` handshake and the compatibility `initialize` handshake, then
exposes workspace open, analysis, query, exploration and close tools. Dynamic
workspace resources expose status, knowledge and generated context.

MCP handlers use the same runtime as the CLI. Authentication or authorization
is injected by the host through the transport authorization callback; secrets
are never part of tool arguments or persisted knowledge.

## REST

Start the local API with `codelp-api`. The generated OpenAPI document is
available at `/docs`. The API provides health and readiness checks, workspace
lifecycle, synchronous and queued analysis, execution status and cancellation,
query, context, knowledge and exploration endpoints.

The default executable binds only to loopback. A production host should inject
authorization at the API boundary and choose its network exposure explicitly.
Health and readiness endpoints remain available without authorization.

## Workspace and execution safety

Every workspace root is canonicalized and must be inside an allowed root.
Filesystem-root allowlists, path escapes and symbolic-link escapes are
rejected. Query size and open-workspace limits are enforced centrally.

Only one analysis execution may be active for a workspace. Different
workspaces may execute concurrently. Queued work can be cancelled safely;
running analysis completes atomically so failed execution cannot replace the
last committed knowledge snapshot.

## Observability

Runtime operations generate structured events with correlation identifiers,
durations, result categories and numeric metrics. Source code, query text,
credentials and raw exception details are excluded. REST `/metrics` exposes
aggregate counters rather than sensitive event payloads.
