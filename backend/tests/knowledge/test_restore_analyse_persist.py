from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.restorer import KnowledgeRestorer


def create_project(
    path: Path,
):
    return Project(
        metadata=ProjectMetadata(
            name="restore-cycle-project",
            root_path=path,
        )
    )


def test_restore_analyse_persist_cycle(
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


    project = create_project(
        project_path
    )

    project.statistics.scanned_files = [
        source_file
    ]


    builder = KnowledgeBuilder()

    first_knowledge = builder.build(
        project
    )


    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )


    storage.save(
        first_knowledge
    )


    loaded = storage.load(
        first_knowledge.metadata.project_id
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


    restored_project.statistics.scanned_files = [
        source_file
    ]


    second_knowledge = builder.build(
        restored_project,
        previous=loaded,
    )


    storage.save(
        second_knowledge
    )


    reloaded = storage.load(
        second_knowledge.metadata.project_id
    )


    assert reloaded is not None


    assert (
        first_knowledge.metadata.project_id
        ==
        second_knowledge.metadata.project_id
    )

    assert len(first_knowledge.files) == len(
        second_knowledge.files
    )

    first_file = first_knowledge.files[0]
    second_file = second_knowledge.files[0]

    assert first_file.file_id == second_file.file_id

    assert (
        first_file.locations[0].path
        ==
        second_file.locations[0].path
    )

    assert (
        first_file.locations[0].first_seen
        ==
        second_file.locations[0].first_seen
    )

    assert len(first_file.fingerprints) == len(
        second_file.fingerprints
    )

    first_fingerprint = first_file.fingerprints[0]
    second_fingerprint = second_file.fingerprints[0]

    assert (
        first_fingerprint.content_hash
        == second_fingerprint.content_hash
    )
    assert (
        first_fingerprint.generated_at
        == second_fingerprint.generated_at
    )
    assert (
        second_fingerprint.last_seen
        >= first_fingerprint.last_seen
    )

    assert (
        second_file.locations[0].last_seen
        >=
        first_file.locations[0].last_seen
    )
