# Codelp Operational Deployment

## Supported deployment model

Codelp 0.11 runs as one local or host-scoped process over an explicitly
authorized project root. Workspaces, execution records, vector stores and
events are process-local; committed Knowledge and incremental caches are
persisted below the configured storage path.

Use one API process per storage scope. Multiple independent worker processes
must not share the same in-memory workspace contract. Horizontal or distributed
execution requires a future persistent execution coordinator.

## Installation

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install .
```

Run validation before deployment:

```bash
.venv/bin/pytest backend -q
.venv/bin/python -m compileall -q backend
```

## API startup

Loopback-only development or desktop operation:

```bash
codelp-api --project-root /srv/projects --host 127.0.0.1 --port 8000
```

The host, port and log level can also be supplied through
`CODELP_API_HOST`, `CODELP_API_PORT` and `CODELP_API_LOG_LEVEL`.

Binding to a non-loopback address expands network authority. Put the service
behind a trusted reverse proxy or application host that injects the REST
authorization callback, terminates TLS, limits request bodies and records
access logs. Do not expose the default unauthenticated executable directly to
an untrusted network.

## MCP startup

Configure the external MCP host to launch `codelp-mcp` with its working
directory set to the authorized project root. The stdio child receives only
the environment explicitly passed by the host. Authentication policy is
injected at the MCP transport boundary rather than placed in tool arguments.

## Filesystem policy

The service account needs read access to registered source trees and read/write
access only to configured `.codelp/knowledge` storage. Canonical allowlists,
symlink-escape rejection and project/request limits are enforced before
analysis. Never configure a filesystem root as an allowed project root.

Configuration and Knowledge contain no credential fields. Supply provider
credentials through a future provider/deployment boundary, not project files.

## Lifecycle and health

- `/health` confirms that the process is running.
- `/ready` confirms that the API composition completed.
- `/metrics` exposes aggregate content-safe counters.
- SIGINT or SIGTERM lets Uvicorn run the application lifespan and release
  workspaces and the execution pool.
- MCP closes its runtime when the stdio stream reaches EOF.

Running analysis is allowed to finish atomically during graceful shutdown.
Queued cancellation does not interrupt already-running stages.

## Persistence and recovery

Knowledge snapshots are written to temporary files, flushed, and atomically
replaced. Failed analysis does not publish partial Knowledge. Back up the
configured Knowledge directory if historical identity must survive host loss.
Incremental `analysis-cache` files are disposable and can be regenerated from
source and authoritative Knowledge.

Multi-project REST and MCP runtimes namespace storage by a SHA-256 identity of
the canonical root, so equal project directory names do not collide. CLI
project-local storage retains the readable project-name filenames.

## Operational limits

Review these settings for the deployment host:

- `security.max_open_workspaces`
- `security.max_request_bytes`
- `security.max_query_characters`
- `security.max_project_files`
- `security.max_project_bytes`
- `scanner.max_file_size_bytes`
- `execution.max_workers`
- `execution.default_wait_timeout_seconds`

Limits reject work deterministically; they do not truncate source or publish a
partial result.
