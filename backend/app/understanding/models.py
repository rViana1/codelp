"""Storage-independent project understanding results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArchitecturalArea(BaseModel):
    area_id: str
    name: str
    path_prefix: str
    file_ids: tuple[str, ...] = ()
    symbol_ids: tuple[str, ...] = ()
    importance_score: float = 0.0


class ProjectComponent(BaseModel):
    component_id: str
    entity_id: str
    entity_kind: str
    label: str
    importance_score: float
    incoming_dependencies: int = 0
    outgoing_dependencies: int = 0
    related_entity_ids: tuple[str, ...] = ()


class DependencyFlow(BaseModel):
    flow_id: str
    source_file_id: str
    target_file_id: str
    module: str = ""


class RelatedCodeRegion(BaseModel):
    relationship_id: str
    source_chunk_id: str
    target_chunk_id: str
    relationship_kind: str
    score: float


class RefactoringOpportunity(BaseModel):
    opportunity_id: str
    pattern: str
    entity_ids: tuple[str, ...]
    reason: str
    confidence: float


class EvolutionPattern(BaseModel):
    pattern_id: str
    pattern: str
    entity_ids: tuple[str, ...]
    description: str


class ProjectInsight(BaseModel):
    insight_id: str
    category: str
    title: str
    description: str
    entity_ids: tuple[str, ...] = ()
    score: float = 0.0


class ProjectStructuralSummary(BaseModel):
    entity_counts: dict[str, int] = Field(default_factory=dict)
    relationship_counts: dict[str, int] = Field(default_factory=dict)
    current_entities: int = 0
    historical_entities: int = 0
    dependency_cycles: tuple[tuple[str, ...], ...] = ()


class ProjectUnderstanding(BaseModel):
    project_id: str
    areas: tuple[ArchitecturalArea, ...] = ()
    important_components: tuple[ProjectComponent, ...] = ()
    dependency_flows: tuple[DependencyFlow, ...] = ()
    related_code_regions: tuple[RelatedCodeRegion, ...] = ()
    refactoring_opportunities: tuple[RefactoringOpportunity, ...] = ()
    evolution_patterns: tuple[EvolutionPattern, ...] = ()
    insights: tuple[ProjectInsight, ...] = ()
    structural_summary: ProjectStructuralSummary = Field(
        default_factory=ProjectStructuralSummary
    )
