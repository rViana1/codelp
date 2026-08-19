from pathlib import Path


def test_security_policy_is_transport_and_storage_independent():
    content = Path("backend/app/runtime/security.py").read_text(encoding="utf-8")

    assert "app.api" not in content
    assert "app.mcp" not in content
    assert "app.cli" not in content
    assert "app.knowledge" not in content
    assert "storage" not in content.lower()
