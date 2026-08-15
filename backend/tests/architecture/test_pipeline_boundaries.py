from pathlib import Path


def test_pipeline_does_not_depend_on_storage_implementation():
    """
    Pipeline may orchestrate knowledge lifecycle,
    but must not depend on concrete storage implementations.
    """

    pipeline_path = Path(
        "backend/app/pipeline"
    )

    forbidden_dependencies = [
        "FileKnowledgeStorage",
        "InMemoryKnowledgeStorage",
    ]

    for file in pipeline_path.rglob("*.py"):

        content = file.read_text(
            encoding="utf-8"
        )

        for dependency in forbidden_dependencies:
            assert dependency not in content
