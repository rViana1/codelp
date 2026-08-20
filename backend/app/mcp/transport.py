"""Protocol-compatible MCP JSON-RPC transport over CodelpApplication."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TextIO
from collections.abc import Callable
from urllib.parse import urlparse

from app.runtime import CodelpApplication
from app.runtime import categorize_exception, safe_diagnostic_message
from app.runtime.exceptions import InterfaceDisabledError


class MCPProtocolError(Exception):
    def __init__(self, code: int, message: str, data=None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class CodelpMCPTransport:
    """Serve current stateless MCP and legacy initialize clients."""

    CURRENT_PROTOCOL_VERSION = "2026-07-28"
    LEGACY_PROTOCOL_VERSION = "2025-11-25"

    TOOL_DEFINITIONS = (
        {
            "name": "workspace_open",
            "description": "Open a project workspace and return its handle.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "properties": {"workspace_id": {"type": "string"}},
                "required": ["workspace_id"],
                "additionalProperties": False,
            },
        },
        {
            "name": "workspace_analyze",
            "description": "Analyse an open workspace deterministically.",
            "inputSchema": {
                "type": "object",
                "properties": {"workspace_id": {"type": "string"}},
                "required": ["workspace_id"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "required": ["workspace_id", "state", "capabilities"],
                "additionalProperties": True,
            },
        },
        {
            "name": "project_explore",
            "description": "Explore project graph knowledge and history.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "view": {"type": "string"},
                    "entity_id": {"type": ["string", "null"]},
                },
                "required": ["workspace_id", "view"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "view": {"type": "string"},
                    "data": {},
                },
                "required": ["view", "data"],
                "additionalProperties": False,
            },
        },
        {
            "name": "project_query",
            "description": "Retrieve graph-aware project context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "text": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1},
                },
                "required": ["workspace_id", "text"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "required": ["query", "results"],
                "additionalProperties": True,
            },
        },
        {
            "name": "project_context",
            "description": "Generate provenance-rich context for a query.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "text": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1},
                },
                "required": ["workspace_id", "text"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "required": ["project", "understanding", "context"],
                "additionalProperties": False,
            },
        },
        {
            "name": "workspace_close",
            "description": "Close a workspace and release runtime resources.",
            "inputSchema": {
                "type": "object",
                "properties": {"workspace_id": {"type": "string"}},
                "required": ["workspace_id"],
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "state": {"const": "closed"},
                },
                "required": ["workspace_id", "state"],
                "additionalProperties": False,
            },
        },
    )

    def __init__(
        self,
        application: CodelpApplication,
        *,
        authorize: Callable[[dict[str, object]], bool] | None = None,
    ) -> None:
        if not application.settings.interfaces.mcp_enabled:
            raise InterfaceDisabledError("mcp")
        self.application = application
        self.authorize = authorize

    def handle(self, request: dict[str, object]) -> dict[str, object] | None:
        request_id = request.get("id")
        try:
            if request.get("jsonrpc") != "2.0":
                raise MCPProtocolError(-32600, "Invalid JSON-RPC version")
            if self.authorize is not None and not self.authorize(request):
                raise MCPProtocolError(-32001, "Request is not authorized")
            method = request.get("method")
            if not isinstance(method, str):
                raise MCPProtocolError(-32600, "Request method is required")
            if request_id is None:
                return None
            params = request.get("params") or {}
            if not isinstance(params, dict):
                raise MCPProtocolError(-32602, "Parameters must be an object")
            result = self._dispatch(method, params)
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except MCPProtocolError as exc:
            error = {"code": exc.code, "message": exc.message}
            if exc.data is not None:
                error["data"] = exc.data
            return {"jsonrpc": "2.0", "id": request_id, "error": error}
        except Exception as exc:
            category = categorize_exception(exc)
            error_code = {
                "user_error": -32602,
                "project_error": -32004,
                "configuration_error": -32002,
                "capability_unavailable": -32003,
                "security_error": -32001,
                "execution_conflict": -32009,
                "execution_timeout": -32008,
                "internal_error": -32603,
            }[category.value]
            return self._error(
                request_id,
                error_code,
                safe_diagnostic_message(exc),
                data={"category": category.value},
            )

    def _dispatch(self, method: str, params: dict[str, object]):
        if method == "server/discover":
            return self._server_info(self.CURRENT_PROTOCOL_VERSION)
        if method == "initialize":
            requested = str(params.get("protocolVersion", ""))
            version = (
                requested
                if requested in {
                    self.CURRENT_PROTOCOL_VERSION,
                    self.LEGACY_PROTOCOL_VERSION,
                }
                else self.LEGACY_PROTOCOL_VERSION
            )
            return self._server_info(version)
        if method == "ping":
            return {}
        if method == "tools/list":
            return {
                "tools": list(self.TOOL_DEFINITIONS),
                "ttlMs": 60000,
                "cacheScope": "public",
            }
        if method == "tools/call":
            return self._call_tool(params)
        if method == "resources/list":
            return {
                "resources": self._resources(),
                "ttlMs": 0,
                "cacheScope": "private",
            }
        if method == "resources/read":
            return self._read_resource(str(params.get("uri", "")))
        raise MCPProtocolError(-32601, f"Method not found: {method}")

    def _call_tool(self, params):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            raise MCPProtocolError(-32602, "Tool arguments must be an object")
        definition = next(
            (item for item in self.TOOL_DEFINITIONS if item["name"] == name),
            None,
        )
        if definition is None:
            raise MCPProtocolError(-32602, f"Unknown tool: {name}")
        schema = definition["inputSchema"]
        missing = [
            key for key in schema.get("required", []) if key not in arguments
        ]
        unknown = sorted(set(arguments) - set(schema["properties"]))
        if missing:
            raise MCPProtocolError(
                -32602, f"Missing tool arguments: {', '.join(missing)}"
            )
        if unknown:
            raise MCPProtocolError(
                -32602, f"Unknown tool arguments: {', '.join(unknown)}"
            )
        if name == "workspace_open" and len(str(arguments.get("path", ""))) > 4096:
            raise MCPProtocolError(-32602, "Workspace path exceeds size limit")
        if len(str(arguments.get("entity_id", ""))) > 4096:
            raise MCPProtocolError(-32602, "Entity identity exceeds size limit")
        if name == "workspace_open":
            workspace = self.application.open_project(arguments["path"])
            data = {"workspace_id": workspace.workspace_id}
        elif name == "workspace_analyze":
            workspace_id = str(arguments["workspace_id"])
            self.application.analyze(workspace_id)
            data = self.application.status(workspace_id).model_dump(mode="json")
        elif name == "project_explore":
            view = str(arguments["view"])
            data = {
                "view": view,
                "data": self.application.explore(
                    str(arguments["workspace_id"]),
                    view,
                    arguments.get("entity_id"),
                ),
            }
        elif name == "project_query":
            result = self.application.query(
                str(arguments["workspace_id"]),
                str(arguments["text"]),
                limit=arguments.get("limit"),
            )
            data = result.model_dump(mode="json")
        elif name == "project_context":
            workspace_id = str(arguments["workspace_id"])
            self.application.query(
                workspace_id,
                str(arguments["text"]),
                limit=arguments.get("limit"),
            )
            data = self.application.explore(workspace_id, "context")
        elif name == "workspace_close":
            closed = self.application.close_project(
                str(arguments["workspace_id"])
            )
            data = {"workspace_id": closed.workspace_id, "state": "closed"}
        else:
            raise MCPProtocolError(-32602, f"Unknown tool: {name}")
        text = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return {
            "content": [{"type": "text", "text": text}],
            "structuredContent": data,
            "isError": False,
        }

    def _resources(self):
        result = []
        for status in self.application.list_workspaces():
            base = f"codelp://workspace/{status.workspace_id}"
            for name in ("status", "knowledge", "context"):
                result.append(
                    {
                        "uri": f"{base}/{name}",
                        "name": f"{status.project_name} {name}",
                        "description": f"Codelp project {name}",
                        "mimeType": "application/json",
                    }
                )
        return sorted(result, key=lambda item: item["uri"])

    def _read_resource(self, uri: str):
        parsed = urlparse(uri)
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.scheme != "codelp" or parsed.netloc != "workspace" or len(parts) != 2:
            raise MCPProtocolError(-32602, f"Invalid Codelp resource URI: {uri}")
        workspace_id, resource = parts
        if resource == "status":
            data = self.application.status(workspace_id).model_dump(mode="json")
        elif resource == "knowledge":
            data = self.application.explore(workspace_id, "project")
        elif resource == "context":
            data = self.application.explore(workspace_id, "context")
        else:
            raise MCPProtocolError(-32602, f"Unknown resource: {resource}")
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(data, sort_keys=True, separators=(",", ":")),
                }
            ],
            "ttlMs": 0,
            "cacheScope": "private",
        }

    @staticmethod
    def _server_info(protocol_version: str):
        return {
            "protocolVersion": protocol_version,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": True},
            },
            "serverInfo": {
                "name": "codelp",
                "title": "Codelp Project Knowledge",
                "version": "0.11.0",
            },
            "instructions": (
                "Open a workspace handle before analysis or exploration. "
                "Codelp operates without a generative LLM."
            ),
        }

    @staticmethod
    def _error(request_id, code, message, data=None):
        error = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error,
        }

    def run_stdio(
        self,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        source = input_stream or sys.stdin
        target = output_stream or sys.stdout
        try:
            for line in source:
                if not line.strip():
                    continue
                if len(line.encode("utf-8")) > (
                    self.application.settings.security.max_request_bytes
                ):
                    response = self._error(
                        None,
                        -32600,
                        "Request exceeds configured size limit",
                        data={"category": "security_error"},
                    )
                else:
                    try:
                        request = json.loads(line)
                        response = self.handle(request)
                    except json.JSONDecodeError:
                        response = self._error(None, -32700, "Parse error")
                if response is not None:
                    target.write(
                        json.dumps(response, separators=(",", ":")) + "\n"
                    )
                    target.flush()
        finally:
            self.application.shutdown()
