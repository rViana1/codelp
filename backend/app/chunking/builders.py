from app.chunking.models import (
    ChunkKind,
    CodeChunk,
)


def build_function_chunk(
    *,
    chunk_id: str,
    file_path: str,
    content: str,
    start_line: int,
    end_line: int,
) -> CodeChunk:
    """
    Builds a function chunk.
    """

    return CodeChunk(
        id=chunk_id,
        file_path=file_path,
        symbol_id=chunk_id,
        kind=ChunkKind.FUNCTION,
        content=content,
        start_line=start_line,
        end_line=end_line,
    )


def build_method_chunk(
    *,
    chunk_id: str,
    file_path: str,
    content: str,
    start_line: int,
    end_line: int,
) -> CodeChunk:
    """
    Builds a method chunk.
    """

    return CodeChunk(
        id=chunk_id,
        file_path=file_path,
        symbol_id=chunk_id,
        kind=ChunkKind.METHOD,
        content=content,
        start_line=start_line,
        end_line=end_line,
    )


def build_class_chunk(
    *,
    chunk_id: str,
    file_path: str,
    content: str,
    start_line: int,
    end_line: int,
) -> CodeChunk:
    """
    Builds a class chunk.
    """

    return CodeChunk(
        id=chunk_id,
        file_path=file_path,
        symbol_id=chunk_id,
        kind=ChunkKind.CLASS,
        content=content,
        start_line=start_line,
        end_line=end_line,
    )
