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
            name="multi-execution-project",
            root_path=path,
        )
    )


def test_multiple_execution_identity_preservation(
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


    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )


    builder = KnowledgeBuilder()


    # Execution 1

    project_1 = create_project(
        project_path
    )

    project_1.statistics.scanned_files = [
        source_file
    ]


    knowledge_1 = builder.build(
        project_1
    )


    storage.save(
        knowledge_1
    )


    file_ids_1 = [
        item.file_id
        for item in knowledge_1.files
    ]

    symbol_ids_1 = [
        item.symbol_id
        for item in knowledge_1.symbols
    ]

    chunk_ids_1 = [
        item.chunk_id
        for item in knowledge_1.chunks
    ]


    # Execution 2

    project_2 = create_project(
        project_path
    )


    loaded_1 = storage.load(
        knowledge_1.metadata.project_id
    )


    assert loaded_1 is not None


    KnowledgeRestorer().restore(
        project_2,
        loaded_1,
    )


    project_2.statistics.scanned_files = [
        source_file
    ]


    knowledge_2 = builder.build(
        project_2
    )


    storage.save(
        knowledge_2
    )


    # Execution 3

    project_3 = create_project(
        project_path
    )


    loaded_2 = storage.load(
        knowledge_2.metadata.project_id
    )


    assert loaded_2 is not None


    KnowledgeRestorer().restore(
        project_3,
        loaded_2,
    )


    project_3.statistics.scanned_files = [
        source_file
    ]


    knowledge_3 = builder.build(
        project_3
    )


    file_ids_3 = [
        item.file_id
        for item in knowledge_3.files
    ]

    symbol_ids_3 = [
        item.symbol_id
        for item in knowledge_3.symbols
    ]

    chunk_ids_3 = [
        item.chunk_id
        for item in knowledge_3.chunks
    ]


    assert file_ids_1 == file_ids_3

    assert symbol_ids_1 == symbol_ids_3

    assert chunk_ids_1 == chunk_ids_3