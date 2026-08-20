"""Typed, secret-free configuration for the Codelp runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConfigurationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScannerSettings(ConfigurationModel):
    follow_symlinks: bool = False
    ignore_hidden: bool = True
    max_file_size_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    ignored_directories: set[str] = Field(default_factory=set)
    ignored_extensions: set[str] = Field(default_factory=set)

    @model_validator(mode="after")
    def validate_symlink_policy(self):
        if self.follow_symlinks:
            raise ValueError(
                "Following symlinks is disabled until bounded traversal is available"
            )
        return self


class PersistenceSettings(ConfigurationModel):
    path: Path = Path(".codelp/knowledge")


class EmbeddingSettings(ConfigurationModel):
    enabled: bool = False
    provider: Literal["disabled", "local_hash"] = "disabled"
    dimensions: int = Field(default=8, gt=0, le=4096)

    @model_validator(mode="after")
    def validate_provider_state(self):
        expected = "local_hash" if self.enabled else "disabled"
        if self.provider != expected:
            raise ValueError(
                f"Embedding provider must be '{expected}' when enabled is "
                f"{self.enabled}"
            )
        return self


class RetrievalSettings(ConfigurationModel):
    default_limit: int = Field(default=5, gt=0)
    semantic_weight: float = Field(default=0.70, ge=0, le=1)
    structural_weight: float = Field(default=0.25, ge=0, le=1)
    historical_weight: float = Field(default=0.05, ge=0, le=1)
    similarity_threshold: float = Field(default=0.60, ge=0, le=1)

    @model_validator(mode="after")
    def validate_weights(self):
        total = (
            self.semantic_weight
            + self.structural_weight
            + self.historical_weight
        )
        if abs(total - 1.0) > 1e-9:
            raise ValueError("Retrieval weights must total 1.0")
        return self


class InterfaceSettings(ConfigurationModel):
    cli_enabled: bool = True
    mcp_enabled: bool = True
    rest_enabled: bool = True


class ExecutionSettings(ConfigurationModel):
    max_workers: int = Field(default=4, gt=0, le=64)
    default_wait_timeout_seconds: float = Field(default=30.0, gt=0, le=300)


class SecuritySettings(ConfigurationModel):
    allowed_project_roots: tuple[Path, ...] = ()
    max_open_workspaces: int = Field(default=16, gt=0, le=1024)
    max_query_characters: int = Field(default=10000, gt=0)
    max_request_bytes: int = Field(default=1024 * 1024, gt=0)
    max_project_files: int = Field(default=100000, gt=0)
    max_project_bytes: int = Field(default=2 * 1024 * 1024 * 1024, gt=0)


class CodelpSettings(ConfigurationModel):
    scanner: ScannerSettings = Field(default_factory=ScannerSettings)
    persistence: PersistenceSettings = Field(
        default_factory=PersistenceSettings
    )
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    interfaces: InterfaceSettings = Field(default_factory=InterfaceSettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    llm_enabled: bool = False

    @model_validator(mode="after")
    def validate_llm_availability(self):
        if self.llm_enabled:
            raise ValueError(
                "Generative LLM integration is not available in Codelp 0.11"
            )
        return self

    def secret_free_dump(self) -> dict[str, object]:
        """Return the complete public configuration; no secret field exists."""
        return self.model_dump(mode="json")
