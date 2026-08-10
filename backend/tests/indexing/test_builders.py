from pathlib import Path

from app.indexing.builders import (
    class_id,
    function_id,
    method_id,
    relative_file_path,
)
from app.parser.models import ClassSymbol, FunctionSymbol, MethodSymbol


def test_relative_file_path_uses_project_relative_posix_path() -> None:

    root = Path("/project")

    file_path = Path("/project/src/main.py")

    result = relative_file_path(root, file_path)

    assert result == "src/main.py"


def test_function_identifier() -> None:

    result = function_id(
        "src/main.py",
        FunctionSymbol(
            name="hello",
            start_line=1,
            end_line=2,
        ),
    )

    assert result == "src/main.py::hello"


def test_class_identifier() -> None:

    result = class_id(
        "src/models/user.py",
        ClassSymbol(
            name="User",
            start_line=1,
            end_line=2,
        ),
    )

    assert result == "src/models/user.py::User"


def test_method_identifier() -> None:

    result = method_id(
        "src/models/user.py",
        MethodSymbol(
            name="login",
            class_name="User",
            start_line=2,
            end_line=3,
        ),
    )

    assert result == "src/models/user.py::User.login"


def test_identifiers_are_deterministic() -> None:

    first = method_id(
        "src/models/user.py",
        MethodSymbol(
            name="login",
            class_name="User",
            start_line=2,
            end_line=3,
        ),
    )

    second = method_id(
        "src/models/user.py",
        MethodSymbol(
            name="login",
            class_name="User",
            start_line=2,
            end_line=3,
        ),
    )

    assert first == second