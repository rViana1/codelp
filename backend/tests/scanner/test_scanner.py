from pathlib import Path

import pytest

from app.scanner.scanner import ProjectScanner


def test_scan_empty_directory(tmp_path: Path) -> None:
    """
    The scanner should correctly scan an empty project.
    """

    scanner = ProjectScanner()

    result = scanner.scan(tmp_path)

    assert result.root == tmp_path

    assert result.files == []

    assert result.directories == []

    assert result.errors == []

    assert result.tree.name == tmp_path.name

    assert result.tree.is_directory is True

    assert result.tree.children == {}
    
def test_scan_single_file(tmp_path: Path) -> None:
    """
    The scanner should correctly scan a directory containing a single file.
    """

    # Arrange

    scanner = ProjectScanner()

    readme = tmp_path / "README.md"
    readme.touch()

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    assert len(result.files) == 1
    assert result.files[0] == readme

    assert result.directories == []

    assert result.errors == []

    assert len(result.tree.children) == 1

    child = result.tree.get_child("README.md")

    assert child is not None
    assert child.path == readme
    assert child.name == "README.md"
    assert child.is_directory is False
    assert child.parent == result.tree
    assert child.is_leaf is True
    
    
def test_scan_nested_directories(tmp_path: Path) -> None:
    """
    The scanner should correctly scan nested directories.
    """

    # Arrange

    scanner = ProjectScanner()

    src = tmp_path / "src"
    src.mkdir()

    main = src / "main.py"
    utils = src / "utils.py"
    readme = tmp_path / "README.md"

    main.touch()
    utils.touch()
    readme.touch()

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    assert len(result.directories) == 1
    assert result.directories == [src]

    assert len(result.files) == 3

    assert readme in result.files
    assert main in result.files
    assert utils in result.files

    root = result.tree

    assert len(root.children) == 2

    src_node = root.get_child("src")
    readme_node = root.get_child("README.md")

    assert src_node is not None
    assert readme_node is not None

    assert src_node.is_directory is True
    assert readme_node.is_directory is False

    assert src_node.parent == root
    assert readme_node.parent == root

    assert len(src_node.children) == 2

    main_node = src_node.get_child("main.py")
    utils_node = src_node.get_child("utils.py")

    assert main_node is not None
    assert utils_node is not None

    assert main_node.parent == src_node
    assert utils_node.parent == src_node

    assert main_node.is_leaf is True
    assert utils_node.is_leaf is True
    
    
def test_scan_complete_tree(tmp_path: Path) -> None:
    """
    The scanner should correctly build a complete project tree.
    """

    # Arrange

    scanner = ProjectScanner()

    src = tmp_path / "src"
    api = src / "api"
    models = src / "models"
    tests_dir = tmp_path / "tests"

    api.mkdir(parents=True)
    models.mkdir(parents=True)
    tests_dir.mkdir()

    routes = api / "routes.py"
    user = models / "user.py"
    utils = src / "utils.py"
    test_api = tests_dir / "test_api.py"
    readme = tmp_path / "README.md"
    pyproject = tmp_path / "pyproject.toml"

    routes.touch()
    user.touch()
    utils.touch()
    test_api.touch()
    readme.touch()
    pyproject.touch()

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    assert len(result.directories) == 4

    assert len(result.files) == 6

    root = result.tree

    assert root.get_child("src") is not None
    assert root.get_child("tests") is not None
    assert root.get_child("README.md") is not None
    assert root.get_child("pyproject.toml") is not None

    src_node = root.get_child("src")
    assert src_node is not None

    api_node = src_node.get_child("api")
    models_node = src_node.get_child("models")
    utils_node = src_node.get_child("utils.py")

    assert api_node is not None
    assert models_node is not None
    assert utils_node is not None

    assert api_node.get_child("routes.py") is not None
    assert models_node.get_child("user.py") is not None

    tests_node = root.get_child("tests")
    assert tests_node is not None

    assert tests_node.get_child("test_api.py") is not None
    

def test_scan_non_existing_directory(tmp_path: Path) -> None:
    """
    The scanner should raise FileNotFoundError
    when the directory does not exist.
    """

    # Arrange

    scanner = ProjectScanner()

    directory = tmp_path / "does_not_exist"

    # Act / Assert

    with pytest.raises(FileNotFoundError):
        scanner.scan(directory)
        
        
def test_scan_file_instead_of_directory(tmp_path: Path) -> None:
    """
    The scanner should raise NotADirectoryError
    when the given path is a file.
    """

    # Arrange

    scanner = ProjectScanner()

    file = tmp_path / "main.py"
    file.touch()

    # Act / Assert

    with pytest.raises(NotADirectoryError):
        scanner.scan(file)
        
        
def test_scan_ignores_default_directories(tmp_path: Path) -> None:
    """
    The scanner should ignore directories configured by the default filter.
    """

    # Arrange

    scanner = ProjectScanner()

    src = tmp_path / "src"
    src.mkdir()

    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()

    git = tmp_path / ".git"
    git.mkdir()

    app = src / "app.py"
    app.touch()

    ignored_file = node_modules / "library.js"
    ignored_file.touch()

    git_file = git / "config"
    git_file.touch()

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    assert len(result.directories) == 1
    assert result.directories == [src]

    assert len(result.files) == 1
    assert result.files == [app]

    root = result.tree

    assert root.get_child("src") is not None

    assert root.get_child("node_modules") is None
    assert root.get_child(".git") is None

    src_node = root.get_child("src")

    assert src_node is not None
    assert src_node.get_child("app.py") is not None
    
    
    
    
def test_scan_ignores_symbolic_links(tmp_path: Path) -> None:
    """
    The scanner should ignore symbolic links.
    """

    # Arrange

    scanner = ProjectScanner()

    real_file = tmp_path / "real.py"
    real_file.touch()

    symlink = tmp_path / "link.py"
    symlink.symlink_to(real_file)

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    assert len(result.files) == 1
    assert result.files == [real_file]

    assert result.tree.get_child("real.py") is not None
    assert result.tree.get_child("link.py") is None
    
    
    
def test_scan_returns_deterministic_tree_order(tmp_path: Path) -> None:
    """
    The scanner should always return children in a deterministic order:
    directories first, then files, both sorted alphabetically.
    """

    # Arrange

    scanner = ProjectScanner()

    (tmp_path / "zeta").mkdir()
    (tmp_path / "Alpha").mkdir()

    (tmp_path / "gamma.py").touch()
    (tmp_path / "Beta.py").touch()

    # Act

    result = scanner.scan(tmp_path)

    # Assert

    children = list(result.tree.children.keys())

    assert children == [
        "Alpha",
        "zeta",
        "Beta.py",
        "gamma.py",
    ]