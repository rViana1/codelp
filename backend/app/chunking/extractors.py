from pathlib import Path


def extract_source(
    file_path: Path,
    start_line: int,
    end_line: int,
) -> str:
    """
    Extracts the exact source text between the given line numbers.

    Lines are 1-based and inclusive.
    """

    lines = file_path.read_text(encoding="utf-8").splitlines(
        keepends=True
    )

    return "".join(lines[start_line - 1 : end_line])
