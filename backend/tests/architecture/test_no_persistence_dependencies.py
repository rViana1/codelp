import ast
from pathlib import Path


DOMAIN_MODULES = [
    "backend/app/scanner",
    "backend/app/parser",
    "backend/app/indexing",
    "backend/app/chunking",
    "backend/app/embeddings",
    "backend/app/retrieval",
    "backend/app/context",
    "backend/core",
]


FORBIDDEN_IMPORTS = [
    "app.knowledge.storage",
    "app.knowledge.file_storage",
    "app.persistence",
    "persistence",
    "database",
]


def extract_imports(
    file: Path,
) -> list[str]:

    content = file.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        content
    )

    imports = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:
                imports.append(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:
                imports.append(
                    node.module
                )

    return imports


def test_domain_has_no_persistence_dependencies():

    for module in DOMAIN_MODULES:

        for file in Path(module).rglob("*.py"):

            imports = extract_imports(
                file
            )

            for imported in imports:

                for forbidden in FORBIDDEN_IMPORTS:

                    assert not imported.startswith(
                        forbidden
                    ), (
                        f"{file} imports forbidden dependency {imported}"
                    )