from pathlib import Path


FORBIDDEN_DEPENDENCIES = [
    "knowledge.storage",
    "knowledge.file_storage",
    "database",
    "sqlalchemy",
]


PROTECTED_MODULES = [
    "backend/app/scanner",
    "backend/app/parser",
    "backend/app/indexing",
    "backend/app/chunking",
    "backend/app/embeddings",
    "backend/app/retrieval",
    "backend/app/context",
]


def test_protected_modules_have_no_architecture_violations():

    for module in PROTECTED_MODULES:

        for file in Path(module).rglob("*.py"):

            content = file.read_text(
                encoding="utf-8"
            )

            for dependency in FORBIDDEN_DEPENDENCIES:

                assert dependency not in content, (
                    f"{file} violates architecture boundary: {dependency}"
                )