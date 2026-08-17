from pathlib import Path

from core.project import (
    Project,
    ProjectMetadata,
)


def test_project_exports_only_persistent_state():

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path("/tmp/demo"),
        )
    )

    project.parser_result = "runtime-parser"
    project.index_result = "runtime-index"

    state = project.export_persistent_state()

    assert state.metadata.name == "demo"
    assert state.configuration is not None

    assert not hasattr(
        state,
        "parser_result",
    )

    assert not hasattr(
        state,
        "index_result",
    )

