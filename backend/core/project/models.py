"""
Domain models representing the central Project aggregate.

Every major module in Codelp communicates through these entities.

The Project acts as the single source of truth during repository
analysis.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

class ProjectMetadata(BaseModel):
    """
    Describes immutable and descriptive information about a software project.

    Responsibility
    --------------
    Stores the identity of the project independently of any analysis
    performed by Codelp.

    This model contains descriptive information only.

    Invariants
    ----------
    - Represents exactly one project.
    - Does not store analysis results.
    - Does not contain runtime state.

    Boundaries
    ----------
    This model must never contain scanner, parser or indexer data.

    Evolution
    ---------
    Future milestones may enrich this model with repository metadata
    such as Git information, license detection and supported languages.
    """

    name: str

    root_path: Path

    description: str | None = None

    version: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ProjectConfiguration(BaseModel):
    """
    Defines analysis configuration for a project.

    Responsibility
    --------------
    Stores configuration values that influence how Codelp modules
    analyse the project.

    Invariants
    ----------
    - Configuration is independent from analysis results.
    - Configuration may be persisted between runs.
    - Modules read configuration but do not own it.

    Boundaries
    ----------
    This model must not contain runtime statistics or analysis output.

    Evolution
    ---------
    Future milestones may extend this model with parser, embedding,
    retrieval and plugin-specific options.
    """

    follow_symlinks: bool = False

    ignore_hidden: bool = True

    max_file_size_bytes: int = 5 * 1024 * 1024

    ignored_directories: set[str] = Field(default_factory=set)

    ignored_extensions: set[str] = Field(default_factory=set)
    
    
class ProjectStatistics(BaseModel):
    """
    Stores quantitative information about a project analysis.

    Responsibility
    --------------
    Tracks metrics produced by Codelp during project analysis.

    Invariants
    ----------
    - Statistics represent analysis state, not project identity.
    - All counters are non-negative.
    - Duration values are expressed in seconds.

    Boundaries
    ----------
    This model must not contain trees, symbols, chunks or embeddings.

    Evolution
    ---------
    Future milestones may add parser, indexer, chunking and quality
    metrics such as classes, functions, imports, tokens and complexity.
    """

    directories: int = 0

    files: int = 0

    scan_duration_seconds: float = 0.0
    
    scanned_files: list[Path] = Field(default_factory=list)
    
    
class Project(BaseModel):
    """
    Aggregate Root of the Codelp domain.

    Responsibility
    --------------
    Represents a software project throughout the entire analysis
    pipeline.

    Every major module in Codelp communicates through this entity.

    The Project acts as the single source of truth for all knowledge
    produced during project analysis.

    Invariants
    ----------
    - A Project represents exactly one repository.
    - The Project owns all analysis state.
    - Modules communicate only through Project.
    - Project does not perform scanning, parsing or indexing itself.

    Boundaries
    ----------
    This model coordinates data but must not contain analysis logic.

    Scanner, Parser, Indexer and other modules update the Project;
    they are not owned by it.

    Evolution
    ---------
    Future milestones will extend this model with parser, index,
    chunking, embedding, retrieval, context, diagnostic and
    knowledge information.
    """

    metadata: ProjectMetadata

    configuration: ProjectConfiguration = Field(
        default_factory=ProjectConfiguration
    )

    statistics: ProjectStatistics = Field(
        default_factory=ProjectStatistics
    )

    root_tree: dict[str, object] | None = None

    parser_result: object | None = None

    index_result: object | None = None

    chunk_result: object | None = None

    embedding_result: object | None = None
    
    retrieval_result: object | None = None
    
    context_result: object | None = None

    diagnostics: list[str] = Field(default_factory=list)