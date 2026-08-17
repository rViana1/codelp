from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.file_storage import FileKnowledgeStorage


def create_project(
    path: Path,
):
    return Project(
        metadata=ProjectMetadata(
            name="roundtrip-project",
            root_path=path,
        )
    )


def test_complete_knowledge_roundtrip(
    tmp_path,
):

    project_path = tmp_path / "project"

    project_path.mkdir()

    source_file = (
        project_path / "main.py"
    )

    source_file.write_text(
        "def hello():\n"
        "    return 42\n"
    )


    project = create_project(
        project_path
    )

    project.statistics.scanned_files = [
        source_file
    ]


    builder = KnowledgeBuilder()

    knowledge = builder.build(
        project
    )


    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )


    storage.save(
        knowledge
    )


    loaded = storage.load(
        knowledge.metadata.project_id
    )


    assert loaded is not None


    restored_project = create_project(
        project_path
    )


    KnowledgeRestorer().restore(
        restored_project,
        loaded,
    )


    assert (
        restored_project.knowledge_state
        is not None
    )


    state = (
        restored_project
        .knowledge_state
    )


    assert len(state.files) == len(
        knowledge.files
    )

    assert len(state.symbols) == len(
        knowledge.symbols
    )

    assert len(state.chunks) == len(
        knowledge.chunks
    )