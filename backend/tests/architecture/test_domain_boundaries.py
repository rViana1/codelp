from pathlib import Path


def test_core_does_not_depend_on_knowledge():
    """
    Domain layer must not depend on persistence knowledge layer.

    Core represents domain concepts and must remain independent.
    """

    core_path = Path(
        "backend/core"
    )

    for file in core_path.rglob("*.py"):

        content = file.read_text(
            encoding="utf-8"
        )

        assert "app.knowledge" not in content
