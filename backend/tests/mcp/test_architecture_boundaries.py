from pathlib import Path


def test_mcp_does_not_depend_on_pipeline_execution():

    mcp_path = Path("backend/app/mcp")

    forbidden_imports = [
        "Indexer",
        "Scanner",
        "Parser",
        "Chunker",
        "EmbeddingGenerator",
        "VectorStoreManager",
    ]

    for file in mcp_path.glob("*.py"):
        content = file.read_text()

        for forbidden in forbidden_imports:
            assert forbidden not in content