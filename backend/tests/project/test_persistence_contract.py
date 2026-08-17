from core.project.models import Project
from core.project.persistence import (
    PERSISTABLE_PROJECT_FIELDS,
    NON_PERSISTABLE_PROJECT_FIELDS,
    ProjectPersistentState,
)


def test_persistable_project_fields_exist():
    """
    Persistable fields must exist in the Project aggregate.
    """

    project_fields = set(
        Project.model_fields.keys()
    )

    for field in PERSISTABLE_PROJECT_FIELDS:
        assert field in project_fields


def test_non_persistable_project_fields_exist():
    """
    Runtime-only fields must exist in the Project aggregate.
    """

    project_fields = set(
        Project.model_fields.keys()
    )

    for field in NON_PERSISTABLE_PROJECT_FIELDS:
        assert field in project_fields


def test_persistent_state_contains_only_persistable_fields():
    """
    Persistent state must only expose explicitly
    allowed fields.
    """

    persistent_fields = set(
        ProjectPersistentState.model_fields.keys()
    )

    assert persistent_fields == PERSISTABLE_PROJECT_FIELDS
