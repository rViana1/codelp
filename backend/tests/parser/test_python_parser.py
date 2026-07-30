from pathlib import Path

import pytest

from app.parser.exceptions import PythonSyntaxError
from app.parser.python_parser import PythonParser


def test_parse_empty_file(tmp_path: Path) -> None:

    path = tmp_path / "empty.py"

    path.write_text("")

    parser = PythonParser()

    result = parser.parse(path)

    assert result.language == "python"

    assert result.imports == []

    assert result.functions == []

    assert result.classes == []

    assert result.diagnostics == []


def test_parse_imports(tmp_path: Path) -> None:

    path = tmp_path / "imports.py"

    path.write_text(
        "import os\n"
        "from pathlib import Path\n"
    )

    parser = PythonParser()

    result = parser.parse(path)

    assert len(result.imports) == 2

    assert result.imports[0].module == "os"

    assert result.imports[0].name is None

    assert result.imports[1].module == "pathlib"

    assert result.imports[1].name == "Path"


def test_parse_functions(tmp_path: Path) -> None:

    path = tmp_path / "functions.py"

    path.write_text(
        "def a():\n"
        "    pass\n\n"
        "def b():\n"
        "    pass\n"
    )

    parser = PythonParser()

    result = parser.parse(path)

    names = [function.name for function in result.functions]

    assert names == ["a", "b"]


def test_parse_classes_and_methods(tmp_path: Path) -> None:

    path = tmp_path / "classes.py"

    path.write_text(
        "class User:\n"
        "    def login(self):\n"
        "        pass\n\n"
        "    def logout(self):\n"
        "        pass\n"
    )

    parser = PythonParser()

    result = parser.parse(path)

    assert len(result.classes) == 1

    cls = result.classes[0]

    assert cls.name == "User"

    methods = [method.name for method in cls.methods]

    assert methods == ["login", "logout"]
    
    assert cls.methods[0].class_name == "User"
    
    assert cls.methods[1].class_name == "User"


def test_methods_are_not_top_level_functions(tmp_path: Path) -> None:

    path = tmp_path / "no_duplicate.py"

    path.write_text(
        "class A:\n"
        "    def m(self):\n"
        "        pass\n"
    )

    parser = PythonParser()

    result = parser.parse(path)

    assert result.functions == []

    assert len(result.classes) == 1

    assert result.classes[0].methods[0].name == "m"
    
    assert result.classes[0].methods[0].class_name == "A"


def test_parse_multiple_symbols(tmp_path: Path) -> None:

    path = tmp_path / "mixed.py"

    path.write_text(
        "import os\n\n"
        "def helper():\n"
        "    pass\n\n"
        "class Service:\n"
        "    def run(self):\n"
        "        pass\n"
    )

    parser = PythonParser()

    result = parser.parse(path)

    assert len(result.imports) == 1

    assert len(result.functions) == 1

    assert len(result.classes) == 1

    assert result.functions[0].name == "helper"

    assert result.classes[0].name == "Service"

    assert result.classes[0].methods[0].name == "run"
    
    assert result.classes[0].methods[0].class_name == "Service"


def test_syntax_error_raises_exception(tmp_path: Path) -> None:

    path = tmp_path / "broken.py"

    path.write_text(
        "def broken(\n"
    )

    parser = PythonParser()

    with pytest.raises(PythonSyntaxError):
        parser.parse(path)
