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
            name="persistent-project",
            root_path=path,
        )
    )


def test_restore_after_previous_execution(
    tmp_path,
):

    project_path = (
        tmp_path / "project"
    )

    project_path.mkdir()

    source_file = (
        project_path / "main.py"
    )

    source_file.write_text(
        "def hello():\n"
        "    return 42\n"
    )


    # First execution

    first_project = create_project(
        project_path
    )

    first_project.statistics.scanned_files = [
        source_file
    ]


    knowledge = KnowledgeBuilder().build(
        first_project
    )


    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )

    storage.save(
        knowledge
    )


    # Second execution

    second_project = create_project(
        project_path
    )


    loaded = storage.load(
        knowledge.metadata.project_id
    )


    assert loaded is not None


    restored = KnowledgeRestorer().restore(
        second_project,
        loaded,
    )


    assert restored.knowledge_state is not None


    assert (
        len(restored.knowledge_state.files)
        ==
        len(knowledge.files)
    )

    assert (
        len(restored.knowledge_state.symbols)
        ==
        len(knowledge.symbols)
    )

    assert (
        len(restored.knowledge_state.chunks)
        ==
        len(knowledge.chunks)
    )