"""Typer command-line interface over the Codelp application runtime."""

from __future__ import annotations

import json
from enum import IntEnum
from pathlib import Path

import typer

from app.configuration import CodelpSettings
from app.runtime import create_configured_application


class ExitCode(IntEnum):
    OK = 0
    INTERNAL_ERROR = 1
    INVALID_REQUEST = 2
    CAPABILITY_UNAVAILABLE = 3


cli = typer.Typer(
    name="codelp",
    help="Deterministic project knowledge and exploration.",
    no_args_is_help=True,
)


def _emit(value, json_output: bool) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    if json_output:
        typer.echo(json.dumps(value, sort_keys=True, separators=(",", ":")))
    elif isinstance(value, dict):
        for key, item in value.items():
            typer.echo(f"{key}: {item}")
    else:
        typer.echo(value)


def _runtime(path: Path, *, local_embeddings: bool = False):
    overrides = None
    if local_embeddings:
        overrides = {
            "embeddings": {"enabled": True, "provider": "local_hash"}
        }
    try:
        application = create_configured_application(path, overrides=overrides)
        workspace = application.open_project(path)
    except (
        FileNotFoundError,
        NotADirectoryError,
        PermissionError,
        ValueError,
    ) as exc:
        raise typer.BadParameter(str(exc)) from exc
    return application, workspace


@cli.command("init")
def initialize(path: Path = typer.Argument(Path("."))) -> None:
    """Create a project-local Codelp configuration."""
    root = path.expanduser().resolve()
    if not root.is_dir():
        raise typer.BadParameter(f"Not a project directory: {root}")
    target = root / ".codelp" / "config.json"
    if target.exists():
        typer.echo(f"Configuration already exists: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            CodelpSettings().secret_free_dump(),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    typer.echo(f"Created {target}")


@cli.command()
def analyze(
    path: Path = typer.Argument(Path(".")),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Analyse a project and publish persistent knowledge."""
    application, workspace = _runtime(path)
    application.analyze(workspace.workspace_id)
    _emit(application.status(workspace.workspace_id), json_output)


@cli.command()
def status(
    path: Path = typer.Argument(Path(".")),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show current project analysis status."""
    application, workspace = _runtime(path)
    application.analyze(workspace.workspace_id)
    _emit(application.status(workspace.workspace_id), json_output)


@cli.command()
def query(
    text: str,
    path: Path = typer.Option(Path("."), "--path"),
    limit: int = typer.Option(5, min=1),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Search project chunks using configured local embeddings and graph."""
    application, workspace = _runtime(path, local_embeddings=True)
    application.analyze(workspace.workspace_id)
    result = application.query(workspace.workspace_id, text, limit=limit)
    _emit(result, json_output)


@cli.command()
def explore(
    view: str,
    path: Path = typer.Option(Path("."), "--path"),
    entity_id: str | None = typer.Option(None, "--entity-id"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Explore project, symbol, dependency, history or related-code views."""
    application, workspace = _runtime(path)
    application.analyze(workspace.workspace_id)
    try:
        result = application.explore(workspace.workspace_id, view, entity_id)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(ExitCode.INVALID_REQUEST) from exc
    _emit(result, json_output)


@cli.command()
def context(
    text: str,
    path: Path = typer.Option(Path("."), "--path"),
    limit: int = typer.Option(5, min=1),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Generate provenance-rich project context for a query."""
    application, workspace = _runtime(path, local_embeddings=True)
    application.analyze(workspace.workspace_id)
    application.query(workspace.workspace_id, text, limit=limit)
    _emit(application.explore(workspace.workspace_id, "context"), json_output)


def main() -> None:
    cli()
