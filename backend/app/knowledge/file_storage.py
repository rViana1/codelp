import json
import os
from pathlib import Path

from pydantic import ValidationError

from .exceptions import (
    KnowledgeCorruptedError,
    KnowledgeWriteError,
)
from .interfaces import KnowledgeStorage
from .models import PersistentProjectKnowledge
from .normalizer import KnowledgeNormalizer


class FileKnowledgeStorage(KnowledgeStorage):
    """
    File-based implementation of persistent knowledge storage.

    Stores each project knowledge snapshot as a JSON file.
    """

    def __init__(
        self,
        base_path: str,
        normalizer: KnowledgeNormalizer | None = None,
    ) -> None:

        self.base_path = Path(base_path)

        self.normalizer = (
            normalizer
            or KnowledgeNormalizer()
        )

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )


    def _project_path(
        self,
        project_id: str,
    ) -> Path:

        return self.base_path / f"{project_id}.json"


    def save(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        normalized = self.normalizer.normalize(
            knowledge
        )

        path = self._project_path(
            normalized.metadata.project_id
        )

        temporary_path = path.with_suffix(
            ".json.tmp"
        )

        content = normalized.model_dump_json(
            indent=4
        )

        try:
            with temporary_path.open(
                "w",
                encoding="utf-8",
            ) as file:

                file.write(
                    content
                )

                file.flush()

                os.fsync(
                    file.fileno()
                )

            temporary_path.replace(
                path
            )

        except OSError as exc:

            if temporary_path.exists():
                temporary_path.unlink()

            raise KnowledgeWriteError(
                "Failed to persist knowledge safely"
            ) from exc


    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:

        path = self._project_path(
            project_id
        )

        if not path.exists():
            return None

        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            knowledge = PersistentProjectKnowledge(
                **data
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ) as exc:

            raise KnowledgeCorruptedError(
                "Stored knowledge is invalid"
            ) from exc

        return self.normalizer.normalize(
            knowledge
        )


    def exists(
        self,
        project_id: str,
    ) -> bool:

        return self._project_path(
            project_id
        ).exists()


    def delete(
        self,
        project_id: str,
    ) -> None:

        path = self._project_path(
            project_id
        )

        if path.exists():
            path.unlink()


    def contains(
        self,
        project_id: str,
    ) -> bool:
        """
        Checks if project knowledge exists.
        """

        return self._project_path(
            project_id
        ).exists()