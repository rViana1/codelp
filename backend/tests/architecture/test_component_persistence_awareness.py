import ast
from pathlib import Path


COMPONENTS = [
    "backend/app/scanner",
    "backend/app/parser",
    "backend/app/indexing",
    "backend/app/chunking",
    "backend/app/embeddings",
    "backend/app/retrieval",
    "backend/app/context",
]


FORBIDDEN_IMPORTS = [
    "app.knowledge",
    "app.persistence",
    "app.storage",
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


def test_components_are_persistence_unaware():

    for component in COMPONENTS:

        for file in Path(component).rglob("*.py"):

            imports = extract_imports(
                file
            )

            for imported in imports:

                for forbidden in FORBIDDEN_IMPORTS:

                    assert not imported.startswith(
                        forbidden
                    ), (
                        f"{file} depends on {imported}"
                    )