import json
import logging

from app.configuration import CodelpSettings
from app.runtime import create_codelp_application


def test_runtime_records_analysis_and_retrieval_metrics_without_content(
    tmp_path, caplog
):
    root = tmp_path / "demo"
    root.mkdir()
    secret_source = "def secret(): return 'DO_NOT_LOG_SOURCE'\n"
    (root / "main.py").write_text(secret_source, encoding="utf-8")
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(
            embeddings={"enabled": True, "provider": "local_hash"}
        ),
    )
    workspace = runtime.open_project(root)

    with caplog.at_level(logging.INFO, logger="codelp.runtime"):
        runtime.analyze(workspace.workspace_id)
        runtime.query(workspace.workspace_id, "DO_NOT_LOG_QUERY")

    events = runtime.observability.events()
    analysis = next(item for item in events if item.operation == "analysis")
    retrieval = next(item for item in events if item.operation == "retrieval")

    assert analysis.metrics["files"] == 1
    assert analysis.metrics["graph_entities"] > 0
    assert retrieval.metrics["results"] > 0
    assert len(analysis.correlation_id) == 64
    serialized = json.dumps(
        [item.model_dump(mode="json") for item in events]
    ) + caplog.text
    assert "DO_NOT_LOG_SOURCE" not in serialized
    assert "DO_NOT_LOG_QUERY" not in serialized


def test_observability_records_sanitized_failure_category(tmp_path):
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
    )
    root = tmp_path / "demo"
    root.mkdir()
    workspace = runtime.open_project(root)
    runtime.analyzer.scanner.scan_project = lambda _project: (_ for _ in ()).throw(
        ValueError("sensitive failure detail")
    )

    try:
        runtime.analyze(workspace.workspace_id)
    except ValueError:
        pass

    event = runtime.observability.events()[-1]
    assert event.status == "failed"
    assert event.error_category == "ValueError"
    assert "sensitive failure detail" not in event.model_dump_json()


def test_disabled_retrieval_records_failure_without_query_text(tmp_path):
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
    )
    root = tmp_path / "demo"
    root.mkdir()
    workspace = runtime.open_project(root)

    try:
        runtime.query(workspace.workspace_id, "DO_NOT_RECORD_THIS_QUERY")
    except RuntimeError:
        pass

    event = runtime.observability.events()[-1]
    assert event.operation == "retrieval"
    assert event.status == "failed"
    assert event.error_category == "RuntimeError"
    assert "DO_NOT_RECORD_THIS_QUERY" not in event.model_dump_json()
