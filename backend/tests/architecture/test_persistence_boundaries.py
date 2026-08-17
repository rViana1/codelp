def test_project_persistent_state_does_not_contain_runtime_objects():
    """
    Persistent project state must not expose runtime analysis objects.
    """

    from core.project.persistence import ProjectPersistentState

    persistent_fields = set(
        ProjectPersistentState.model_fields.keys()
    )

    forbidden_fields = {
        "parser_result",
        "index_result",
        "chunk_result",
        "embedding_result",
        "retrieval_result",
        "context_result",
        "knowledge_state",
        "diagnostics",
    }

    assert forbidden_fields.isdisjoint(
        persistent_fields
    )