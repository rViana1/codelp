from pathlib import Path


def test_domain_does_not_depend_on_mcp():

    forbidden_import = "app.mcp"

    paths = [
        Path("backend/core"),
        Path("backend/app"),
    ]

    for base_path in paths:
        if not base_path.exists():
            continue

        for file in base_path.rglob("*.py"):

            if "/mcp/" in str(file):
                continue

            content = file.read_text()

            assert forbidden_import not in content
