from app.chunking.models import (
    ChunkCollection,
    ChunkKind,
    CodeChunk,
)


def test_code_chunk_creation() -> None:

    chunk = CodeChunk(
        id="src/main.py::hello",
        file_path="src/main.py",
        symbol_id="src/main.py::hello",
        kind=ChunkKind.FUNCTION,
        content="def hello():\n    pass\n",
        start_line=1,
        end_line=2,
    )

    assert chunk.id == "src/main.py::hello"

    assert chunk.kind == ChunkKind.FUNCTION

    assert chunk.start_line == 1

    assert chunk.end_line == 2


def test_chunk_collection_defaults() -> None:

    collection = ChunkCollection()

    assert collection.chunks == []

    assert collection.diagnostics == []
