from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

from app.runtime import create_configured_application

from .application import create_rest_api


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run the Codelp REST API")
    result.add_argument("--project-root", type=Path, default=Path.cwd())
    result.add_argument(
        "--host",
        default=os.environ.get("CODELP_API_HOST", "127.0.0.1"),
    )
    result.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("CODELP_API_PORT", "8000")),
    )
    result.add_argument(
        "--log-level",
        choices=("critical", "error", "warning", "info", "debug", "trace"),
        default=os.environ.get("CODELP_API_LOG_LEVEL", "info"),
    )
    return result


def main() -> None:
    arguments = parser().parse_args()
    runtime = create_configured_application(
        arguments.project_root,
        interface="rest",
    )
    uvicorn.run(
        create_rest_api(runtime),
        host=arguments.host,
        port=arguments.port,
        log_level=arguments.log_level,
    )


if __name__ == "__main__":
    main()
