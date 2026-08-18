import ast
from pathlib import Path


LIFECYCLE_MODULES = [
    "backend/app/knowledge",
]


FORBIDDEN_IMPLEMENTATIONS = [
    "app.knowledge.file_storage",
    "app.embeddings.fake_provider",
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


def test_lifecycle_does_not_depend_on_concrete_implementations():

    for module in LIFECYCLE_MODULES:

        for file in Path(module).rglob("*.py"):

            imports = extract_imports(
                file
            )

            for imported in imports:

                for forbidden in FORBIDDEN_IMPLEMENTATIONS:

                    assert not imported.startswith(
                        forbidden
                    ), (
                        f"{file} depends on concrete implementation {imported}"
                    )