from app.chunking.builders import (
    build_class_chunk,
    build_function_chunk,
    build_method_chunk,
)
from app.chunking.models import ChunkKind


def test_build_function_chunk() -> None:

    chunk = build_function_chunk(
        chunk_id="src/main.py::hello",
        file_path="src/main.py",
        content="def hello():\n    pass\n",
        start_line=1,
        end_line=2,
    )

    assert chunk.kind == ChunkKind.FUNCTION

    assert chunk.id == "src/main.py::hello"

    assert chunk.symbol_id == "src/main.py::hello"


def test_build_method_chunk() -> None:

    chunk = build_method_chunk(
        chunk_id="src/main.py::User.login",
        file_path="src/main.py",
        content="def login(self):\n    pass\n",
        start_line=3,
        end_line=4,
    )

    assert chunk.kind == ChunkKind.METHOD

    assert chunk.id == "src/main.py::User.login"


def test_build_class_chunk() -> None:

    chunk = build_class_chunk(
        chunk_id="src/main.py::User",
        file_path="src/main.py",
        content="class User:\n    pass\n",
        start_line=1,
        end_line=2,
    )

    assert chunk.kind == ChunkKind.CLASS

    assert chunk.id == "src/main.py::User"
