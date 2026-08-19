"""Deterministic configuration loading with explicit precedence."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

from .models import CodelpSettings


class ConfigurationLoader:
    """Merge defaults, user, project, environment and explicit overrides."""

    ENVIRONMENT_PATHS = {
        "CODELP_EMBEDDINGS_ENABLED": ("embeddings", "enabled", "bool"),
        "CODELP_EMBEDDINGS_PROVIDER": ("embeddings", "provider", "str"),
        "CODELP_EMBEDDINGS_DIMENSIONS": ("embeddings", "dimensions", "int"),
        "CODELP_PERSISTENCE_PATH": ("persistence", "path", "str"),
        "CODELP_RETRIEVAL_LIMIT": ("retrieval", "default_limit", "int"),
        "CODELP_LLM_ENABLED": ("llm_enabled", "bool"),
    }

    def load(
        self,
        *,
        project_root: str | Path | None = None,
        user_config: str | Path | None = None,
        environment: dict[str, str] | None = None,
        overrides: dict[str, object] | None = None,
    ) -> CodelpSettings:
        merged = CodelpSettings().model_dump(mode="python")
        if user_config is not None:
            merged = self._merge(merged, self._read(Path(user_config)))
        if project_root is not None:
            project_file = Path(project_root) / ".codelp" / "config.json"
            if project_file.exists():
                merged = self._merge(merged, self._read(project_file))
        merged = self._merge(
            merged,
            self._environment(environment if environment is not None else os.environ),
        )
        if overrides:
            merged = self._merge(merged, overrides)
        return CodelpSettings.model_validate(merged)

    @staticmethod
    def _read(path: Path) -> dict[str, object]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Configuration root must be an object: {path}")
        return data

    @classmethod
    def _environment(cls, values) -> dict[str, object]:
        result: dict[str, object] = {}
        for variable, path in cls.ENVIRONMENT_PATHS.items():
            raw = values.get(variable)
            if raw is None:
                continue
            *keys, value_type = path
            value = cls._convert(raw, value_type)
            target = result
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = value
        return result

    @staticmethod
    def _convert(value: str, value_type: str):
        if value_type == "bool":
            normalized = value.strip().lower()
            if normalized not in {"true", "false", "1", "0", "yes", "no"}:
                raise ValueError(f"Invalid boolean configuration value: {value}")
            return normalized in {"true", "1", "yes"}
        if value_type == "int":
            return int(value)
        return value

    @classmethod
    def _merge(cls, base, overlay):
        result = deepcopy(base)
        for key, value in overlay.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = cls._merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        return result
