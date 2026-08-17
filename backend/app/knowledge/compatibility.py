from __future__ import annotations

from app.knowledge.schema import (
    COMPATIBLE_KNOWLEDGE_VERSIONS,
    KNOWLEDGE_SCHEMA_VERSION,
)


class KnowledgeSchemaCompatibility:
    """
    Defines compatibility rules for persistent knowledge schemas.

    Schema compatibility is independent from application version.

    This class does not perform migrations.
    It only determines whether a persisted schema
    can be consumed safely.
    """

    @staticmethod
    def is_compatible(
        version: str,
    ) -> bool:
        """
        Checks if a schema version can be loaded.
        """

        return (
            version
            in COMPATIBLE_KNOWLEDGE_VERSIONS
        )


    @staticmethod
    def is_current(
        version: str,
    ) -> bool:
        """
        Checks if the schema version is the latest available.
        """

        return (
            version
            == KNOWLEDGE_SCHEMA_VERSION
        )