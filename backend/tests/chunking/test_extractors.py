from pathlib import Path

from app.chunking.extractors import extract_source


def test_extract_exact_source(tmp_path: Path) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "import os\n\n"
        "def hello():\n"
        "    print('hi')\n\n"
        "class User:\n"
        "    pass\n"
    )

    result = extract_source(path, 3, 4)

    assert result == (
        "def hello():\n"
        "    print('hi')\n"
    )


def test_extract_class_source(tmp_path: Path) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "class User:\n"
        "    pass\n"
    )

    result = extract_source(path, 1, 2)

    assert result == (
        "class User:\n"
        "    pass\n"
    )
