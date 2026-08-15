from pathlib import Path

from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.loader import KnowledgeLoader


def test_loader_handles_corrupted_knowledge(
    tmp_path,
):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    file = Path(tmp_path) / "project-a.json"

    file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    loader = KnowledgeLoader(
        storage
    )

    result = loader.load(
        "project-a"
    )

    assert result is None
