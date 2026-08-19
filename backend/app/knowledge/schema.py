"""
Knowledge schema compatibility definitions.

The knowledge schema version is independent
from the Codelp application version.
"""


from __future__ import annotations


KNOWLEDGE_SCHEMA_VERSION = "3.0"


COMPATIBLE_KNOWLEDGE_VERSIONS = {
    "2.0",
    "3.0",
}


def is_supported_version(
    version: str,
) -> bool:
    """
    Checks if a knowledge schema version
    can be loaded directly.
    """

    return version in COMPATIBLE_KNOWLEDGE_VERSIONS


def is_current_version(
    version: str,
) -> bool:
    """
    Checks if the knowledge schema version
    is the latest available version.
    """

    return version == KNOWLEDGE_SCHEMA_VERSION
