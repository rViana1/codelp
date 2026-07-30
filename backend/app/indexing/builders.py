from pathlib import Path

from app.parser.models import ClassSymbol, FunctionSymbol, MethodSymbol


def relative_file_path(
    project_root: Path,
    file_path: Path,
) -> str:
    """
    Returns a project-relative file path using POSIX separators.
    """

    return file_path.relative_to(project_root).as_posix()


def function_id(
    relative_path: str,
    function: FunctionSymbol,
) -> str:
    """
    Builds a stable identifier for a function.
    """

    return f"{relative_path}::{function.name}"


def class_id(
    relative_path: str,
    cls: ClassSymbol,
) -> str:
    """
    Builds a stable identifier for a class.
    """

    return f"{relative_path}::{cls.name}"


def method_id(
    relative_path: str,
    method: MethodSymbol,
) -> str:
    """
    Builds a stable identifier for a method.
    """

    return f"{relative_path}::{method.class_name}.{method.name}"