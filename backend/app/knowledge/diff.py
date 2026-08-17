from __future__ import annotations

from pydantic import BaseModel, Field

from app.knowledge.models import PersistentFileIdentity


class KnowledgeDiffResult(BaseModel):
    """
    Represents the difference between previous and current
    project file knowledge.
    """

    added_files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )

    modified_files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )

    removed_files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )

    unchanged_files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )


class KnowledgeDiff:
    """
    Compares previous project knowledge with current files.

    This component only detects changes.

    It does not:
    - modify knowledge;
    - persist data;
    - execute analysis.
    """

    def compare(
        self,
        previous_files: list[PersistentFileIdentity],
        current_files: list[PersistentFileIdentity],
    ) -> KnowledgeDiffResult:
        """
        Calculates file changes between executions.
        """

        previous_by_path = {
            file.path: file
            for file in previous_files
        }

        current_by_path = {
            file.path: file
            for file in current_files
        }

        added = []
        modified = []
        unchanged = []
        removed = []

        for path, current in current_by_path.items():

            previous = previous_by_path.get(
                path
            )

            if previous is None:
                added.append(
                    current
                )

            elif previous.content_hash != current.content_hash:
                modified.append(
                    current
                )

            else:
                unchanged.append(
                    current
                )

        for path, previous in previous_by_path.items():

            if path not in current_by_path:
                removed.append(
                    previous
                )

        return KnowledgeDiffResult(
            added_files=added,
            modified_files=modified,
            removed_files=removed,
            unchanged_files=unchanged,
        )
