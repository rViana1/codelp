from pathlib import Path


def test_storage_does_not_depend_on_project_domain():
    """
    Storage implementations must work with
    persistent knowledge models only.

    They must not depend directly on Project aggregate.
    """

    storage_files = [
        Path(
            "backend/app/knowledge/storage.py"
        ),
        Path(
            "backend/app/knowledge/file_storage.py"
        ),
    ]

    for file in storage_files:

        content = file.read_text(
            encoding="utf-8"
        )

        assert "core.project" not in content
