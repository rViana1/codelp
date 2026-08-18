import ast
from pathlib import Path


DOMAIN_COMPONENTS = [
    "backend/app/scanner",
    "backend/app/parser",
    "backend/app/indexing",
    "backend/app/chunking",
    "backend/app/embeddings",
    "backend/app/retrieval",
    "backend/app/context",
]


FORBIDDEN_STORAGE_USAGE = [
    "KnowledgeStorage",
    "FileKnowledgeStorage",
    "InMemoryKnowledgeStorage",
    ".save(",
    ".load(",
]


def test_domain_does_not_bypass_application_services():

    for component in DOMAIN_COMPONENTS:

        for file in Path(component).rglob("*.py"):

            content = file.read_text(
                encoding="utf-8"
            )

            for forbidden in FORBIDDEN_STORAGE_USAGE:

                assert forbidden not in content, (
                    f"{file} bypasses application boundary using {forbidden}"
                )