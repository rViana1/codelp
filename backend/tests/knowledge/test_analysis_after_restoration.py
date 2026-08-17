from pathlib import Path

from core.project import (
    Project,
    ProjectMetadata,
)

from app.knowledge.builder import (
    KnowledgeBuilder,
)

from app.knowledge.file_storage import (
    FileKnowledgeStorage,
)

from app.knowledge.restorer import (
    KnowledgeRestorer,
)


def create_project(
    path: Path,
):
    return Project(
        metadata=ProjectMetadata(
            name="analysis-after-restore",
            root_path=path,
        )
    )


def test_analysis_after_restoration(
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


    builder = KnowledgeBuilder()

    first_knowledge = builder.build(
        first_project
    )


    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )

    storage.save(
        first_knowledge
    )


    # Second execution

    second_project = create_project(
        project_path
    )


    loaded = storage.load(
        first_knowledge.metadata.project_id
    )


    assert loaded is not None


    KnowledgeRestorer().restore(
        second_project,
        loaded,
    )


    assert (
        second_project.knowledge_state
        is not None
    )


    # Analyse after restoration

    second_project.statistics.scanned_files = [
        source_file
    ]


    second_knowledge = builder.build(
        second_project
    )


    assert (
        second_knowledge.metadata.project_id
        ==
        first_knowledge.metadata.project_id
    )


    assert (
        len(second_knowledge.files)
        ==
        len(first_knowledge.files)
    )