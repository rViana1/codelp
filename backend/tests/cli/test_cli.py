import json

from typer.testing import CliRunner

from app.cli.main import cli


runner = CliRunner()


def project(tmp_path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text(
        "def hello(name):\n    return f'Hello {name}'\n",
        encoding="utf-8",
    )
    return root


def test_init_creates_secret_free_project_configuration(tmp_path):
    root = project(tmp_path)

    result = runner.invoke(cli, ["init", str(root)])

    assert result.exit_code == 0
    data = json.loads((root / ".codelp/config.json").read_text())
    assert data["embeddings"]["enabled"] is False
    assert data["llm_enabled"] is False
    assert "key" not in json.dumps(data).lower()


def test_analyze_returns_deterministic_json_status(tmp_path):
    root = project(tmp_path)

    first = runner.invoke(cli, ["analyze", str(root), "--json"])
    second = runner.invoke(cli, ["analyze", str(root), "--json"])

    assert first.exit_code == second.exit_code == 0
    first_data = json.loads(first.stdout)
    second_data = json.loads(second.stdout)
    assert first_data["workspace_id"] == second_data["workspace_id"]
    assert first_data["files"] == second_data["files"] == 1
    assert first_data["capabilities"]["llm"] is False


def test_explore_and_query_expose_json_contracts(tmp_path):
    root = project(tmp_path)

    explore = runner.invoke(
        cli, ["explore", "project", "--path", str(root), "--json"]
    )
    query = runner.invoke(
        cli, ["query", "hello", "--path", str(root), "--json"]
    )

    assert explore.exit_code == query.exit_code == 0
    assert json.loads(explore.stdout)["project_id"] == "demo"
    assert json.loads(query.stdout)["results"]


def test_unknown_exploration_view_has_stable_exit_code(tmp_path):
    result = runner.invoke(
        cli,
        ["explore", "unknown", "--path", str(project(tmp_path))],
    )

    assert result.exit_code == 2
    assert "Unsupported exploration view" in result.stderr


def test_missing_project_has_stable_invalid_request_exit_code(tmp_path):
    missing = tmp_path / "missing"

    result = runner.invoke(cli, ["analyze", str(missing)])

    assert result.exit_code == 2
    assert "missing" in result.stderr
    assert not missing.exists()
