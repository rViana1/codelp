from pathlib import Path

from app.knowledge.file_storage import (
    FileKnowledgeStorage,
)


def test_corrupted_knowledge_recovery(
    tmp_path,
):

    storage_path = (
        tmp_path / "knowledge"
    )


    storage = FileKnowledgeStorage(
        str(storage_path)
    )


    project_id = "broken-project"


    # Create corrupted knowledge file

    storage_path.mkdir(
        parents=True,
        exist_ok=True,
    )


    corrupted_file = (
        storage_path / f"{project_id}.json"
    )


    corrupted_file.write_text(
        "{ invalid json"
    )


    result = storage.load(
        project_id
    )


    assert result is None