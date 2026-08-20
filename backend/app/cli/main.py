"""Typer command-line interface over the Codelp application runtime."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import IntEnum
from functools import wraps
from pathlib import Path

import click
import typer

from app.configuration import CodelpSettings
from app.runtime import (
    DiagnosticCategory,
    categorize_exception,
    create_configured_application,
    safe_diagnostic_message,
)
from app.runtime.exceptions import InvalidRequestError


class ExitCode(IntEnum):
    OK = 0
    INTERNAL_ERROR = 1
    INVALID_REQUEST = 2
    CAPABILITY_UNAVAILABLE = 3


@dataclass(frozen=True)
class CLIOptions:
    user_config: Path | None = None
    knowledge_path: Path | None = None
    embedding_provider: str | None = None
    retrieval_limit: int | None = None


cli = typer.Typer(
    name="codelp",
    help="Deterministic project knowledge and exploration.",
    no_args_is_help=True,
)
explore_cli = typer.Typer(help="Explore persisted project knowledge.")
cli.add_typer(explore_cli, name="explore")


@cli.callback()
def configure_cli(
    ctx: typer.Context,
    user_config: Path | None = typer.Option(None, "--config"),
    knowledge_path: Path | None = typer.Option(None, "--knowledge-path"),
    embedding_provider: str | None = typer.Option(
        None, "--embedding-provider"
    ),
    retrieval_limit: int | None = typer.Option(
        None, "--retrieval-limit", min=1
    ),
) -> None:
    """Apply command-line overrides after file and environment settings."""
    ctx.obj = CLIOptions(
        user_config=user_config,
        knowledge_path=knowledge_path,
        embedding_provider=embedding_provider,
        retrieval_limit=retrieval_limit,
    )


def _guarded(command):
    @wraps(command)
    def wrapper(*args, **kwargs):
        try:
            return command(*args, **kwargs)
        except (typer.Exit, click.ClickException):
            raise
        except Exception as exc:
            category = categorize_exception(exc)
            typer.echo(
                f"{category.value}: {safe_diagnostic_message(exc)}",
                err=True,
            )
            exit_code = (
                ExitCode.INTERNAL_ERROR
                if category == DiagnosticCategory.INTERNAL
                else ExitCode.CAPABILITY_UNAVAILABLE
                if category == DiagnosticCategory.CAPABILITY
                else ExitCode.INVALID_REQUEST
            )
            raise typer.Exit(exit_code) from None

    return wrapper


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


def _runtime(
    ctx: typer.Context,
    path: Path,
    *,
    local_embeddings: bool = False,
):
    options = ctx.ensure_object(CLIOptions)
    overrides: dict[str, object] = {}
    provider = options.embedding_provider or (
        "local_hash" if local_embeddings else None
    )
    if provider is not None:
        if provider not in {"disabled", "local_hash"}:
            raise InvalidRequestError(
                f"Unsupported embedding provider: {provider}"
            )
        overrides["embeddings"] = {
            "enabled": provider != "disabled",
            "provider": provider,
        }
    if options.knowledge_path is not None:
        overrides["persistence"] = {"path": options.knowledge_path}
    if options.retrieval_limit is not None:
        overrides["retrieval"] = {
            "default_limit": options.retrieval_limit
        }
    application = create_configured_application(
        path,
        user_config=options.user_config,
        overrides=overrides or None,
        interface="cli",
    )
    workspace = application.open_project(path)
    return application, workspace


@cli.command("init")
@_guarded
def initialize(
    ctx: typer.Context,
    path: Path = typer.Argument(Path(".")),
) -> None:
    """Create a project-local Codelp configuration."""
    root = path.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a project directory: {root}")
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


def _analyze(ctx: typer.Context, path: Path, json_output: bool) -> None:
    application, workspace = _runtime(ctx, path)
    application.analyze(workspace.workspace_id)
    _emit(application.status(workspace.workspace_id), json_output)


@cli.command("analyze")
@_guarded
def analyze(
    ctx: typer.Context,
    path: Path = typer.Argument(Path(".")),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Analyze a project and publish persistent knowledge."""
    _analyze(ctx, path, json_output)


@cli.command("analyse")
@_guarded
def analyse(
    ctx: typer.Context,
    path: Path = typer.Argument(Path(".")),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """British-English alias for analyze."""
    _analyze(ctx, path, json_output)


@cli.command()
@_guarded
def status(
    ctx: typer.Context,
    path: Path = typer.Argument(Path(".")),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show current project analysis status."""
    application, workspace = _runtime(ctx, path)
    application.analyze(workspace.workspace_id)
    _emit(application.status(workspace.workspace_id), json_output)


@cli.command()
@_guarded
def query(
    ctx: typer.Context,
    text: str,
    path: Path = typer.Option(Path("."), "--path"),
    limit: int | None = typer.Option(None, min=1),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Search project chunks using local lexical vectors and graph evidence."""
    application, workspace = _runtime(ctx, path, local_embeddings=True)
    application.analyze(workspace.workspace_id)
    result = application.query(workspace.workspace_id, text, limit=limit)
    _emit(result, json_output)


@cli.command()
@_guarded
def context(
    ctx: typer.Context,
    text: str,
    path: Path = typer.Option(Path("."), "--path"),
    limit: int | None = typer.Option(None, min=1),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Generate provenance-rich project context for a query."""
    application, workspace = _runtime(ctx, path, local_embeddings=True)
    application.analyze(workspace.workspace_id)
    application.query(workspace.workspace_id, text, limit=limit)
    _emit(application.explore(workspace.workspace_id, "context"), json_output)


def _explore(
    ctx: typer.Context,
    view: str,
    path: Path,
    entity_id: str | None,
    json_output: bool,
) -> None:
    application, workspace = _runtime(ctx, path)
    application.analyze(workspace.workspace_id)
    result = application.explore(workspace.workspace_id, view, entity_id)
    _emit(result, json_output)


@explore_cli.command("project")
@_guarded
def explore_project(
    ctx: typer.Context,
    path: Path = typer.Option(Path("."), "--path"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    _explore(ctx, "project", path, None, json_output)


@explore_cli.command("symbol")
@_guarded
def explore_symbol(
    ctx: typer.Context,
    symbol_id: str,
    path: Path = typer.Option(Path("."), "--path"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    _explore(ctx, "symbol", path, symbol_id, json_output)


def _relation_command(view: str):
    def command(
        ctx: typer.Context,
        path: Path = typer.Option(Path("."), "--path"),
        entity_id: str | None = typer.Option(None, "--entity-id"),
        json_output: bool = typer.Option(False, "--json"),
    ) -> None:
        _explore(ctx, view, path, entity_id, json_output)

    command.__name__ = f"explore_{view}"
    command.__doc__ = f"Explore project {view.replace('_', ' ')}."
    return _guarded(command)


for _view in (
    "dependencies",
    "history",
    "duplicates",
    "similarity",
    "related_code",
):
    explore_cli.command(_view.replace("_", "-"))(_relation_command(_view))


def main() -> None:
    cli()
