import json
from pathlib import Path

from .interfaces import KnowledgeStorage
from .models import PersistentProjectKnowledge


class FileKnowledgeStorage(KnowledgeStorage):
    """
    File-based implementation of persistent knowledge storage.

    Stores each project knowledge snapshot as a JSON file.
    """

    def __init__(
        self,
        base_path: str,
    ) -> None:

        self.base_path = Path(base_path)

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

        path = self._project_path(
            knowledge.metadata.project_id
        )

        path.write_text(
            knowledge.model_dump_json(
                indent=4
            ),
            encoding="utf-8",
        )


    def load(
        self,
        project_id: str,
    ) -> PersistentProjectKnowledge | None:

        path = self._project_path(
            project_id
        )

        if not path.exists():
            return None

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return PersistentProjectKnowledge(
            **data
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
        project_id: str
    ) -> bool:
        """
        Checks if project knowledge exists.
        """

        return self._project_path(
            project_id
        ).exists()