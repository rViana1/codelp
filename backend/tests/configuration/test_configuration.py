import json

import pytest
from pydantic import ValidationError

from app.configuration import (
    CodelpSettings,
    ConfigurationLoader,
    ConfiguredScanFilter,
)
from app.runtime import create_configured_application
from app.runtime.exceptions import InterfaceDisabledError


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_configuration_precedence_is_explicit_and_deterministic(tmp_path):
    user = tmp_path / "user.json"
    root = tmp_path / "project"
    root.mkdir()
    write_json(user, {"retrieval": {"default_limit": 10}})
    write_json(
        root / ".codelp/config.json",
        {"retrieval": {"default_limit": 8}},
    )

    settings = ConfigurationLoader().load(
        project_root=root,
        user_config=user,
        environment={"CODELP_RETRIEVAL_LIMIT": "6"},
        overrides={"retrieval": {"default_limit": 4}},
    )

    assert settings.retrieval.default_limit == 4


def test_user_configuration_is_discovered_automatically(tmp_path):
    home = tmp_path / "configuration-home"
    write_json(
        home / "codelp/config.json",
        {"retrieval": {"default_limit": 17}},
    )

    settings = ConfigurationLoader(user_config_home=home).load(environment={})

    assert settings.retrieval.default_limit == 17


def test_environment_can_enable_embeddings_but_not_inject_unknown_secrets():
    settings = ConfigurationLoader().load(
        environment={
            "CODELP_EMBEDDINGS_ENABLED": "true",
            "CODELP_EMBEDDINGS_PROVIDER": "local_hash",
            "CODELP_API_KEY": "must-not-be-loaded",
        }
    )

    assert settings.embeddings.enabled is True
    assert settings.embeddings.provider == "local_hash"
    assert "API_KEY" not in str(settings.secret_free_dump())


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValidationError):
        CodelpSettings(retrieval={"semantic_weight": 0.9})
    with pytest.raises(ValueError):
        ConfigurationLoader().load(
            environment={"CODELP_EMBEDDINGS_ENABLED": "sometimes"}
        )
    with pytest.raises(ValidationError, match="Following symlinks"):
        CodelpSettings(scanner={"follow_symlinks": True})
    with pytest.raises(ValidationError, match="Embedding provider"):
        CodelpSettings(embeddings={"enabled": True, "provider": "disabled"})
    with pytest.raises(ValidationError, match="less than or equal to 4096"):
        CodelpSettings(
            embeddings={
                "enabled": True,
                "provider": "local_hash",
                "dimensions": 4097,
            }
        )
    with pytest.raises(ValidationError, match="LLM integration is not available"):
        CodelpSettings(llm_enabled=True)


def test_configured_scanner_filter_applies_hidden_extension_and_size_rules(
    tmp_path,
):
    hidden = tmp_path / ".secret.py"
    binary = tmp_path / "image.png"
    large = tmp_path / "large.py"
    hidden.write_text("pass", encoding="utf-8")
    binary.write_bytes(b"x")
    large.write_text("12345", encoding="utf-8")
    filter_ = ConfiguredScanFilter(
        CodelpSettings(
            scanner={"max_file_size_bytes": 4}
        ).scanner
    )

    assert filter_.should_ignore_file(hidden)
    assert filter_.should_ignore_file(binary)
    assert filter_.should_ignore_file(large)


def test_configured_application_resolves_project_local_persistence(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    write_json(
        root / ".codelp/config.json",
        {
            "persistence": {"path": ".state/knowledge"},
            "embeddings": {"enabled": False},
        },
    )

    application = create_configured_application(root, environment={})
    workspace = application.open_project(root)
    application.analyze(workspace.workspace_id)

    assert (root / ".state/knowledge/project.json").exists()
    assert application.status(workspace.workspace_id).capabilities == {
        "analysis": True,
        "graph": True,
        "understanding": True,
        "retrieval": False,
        "llm": False,
    }


def test_configured_application_does_not_create_a_missing_project(tmp_path):
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        create_configured_application(missing, environment={})

    assert not missing.exists()


def test_disabled_external_interface_is_enforced(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    write_json(
        root / ".codelp/config.json",
        {"interfaces": {"cli_enabled": False}},
    )

    with pytest.raises(InterfaceDisabledError, match="cli interface"):
        create_configured_application(root, environment={}, interface="cli")
