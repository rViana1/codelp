from app.knowledge.schema import (
    KNOWLEDGE_SCHEMA_VERSION,
    is_supported_version,
    is_current_version,
)


def test_current_schema_version_is_supported():

    assert is_supported_version(
        KNOWLEDGE_SCHEMA_VERSION
    )


def test_current_schema_version_is_current():

    assert is_current_version(
        KNOWLEDGE_SCHEMA_VERSION
    )


def test_unknown_schema_version_is_not_supported():

    assert not is_supported_version(
        "99.0"
    )


def test_unknown_schema_version_is_not_current():

    assert not is_current_version(
        "99.0"
    )
