"""Deterministic higher-level understanding derived from a project graph."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import PurePosixPath

from core.project import Project, ProjectKnowledgeGraph

from .models import (
    ArchitecturalArea,
    DependencyFlow,
    EvolutionPattern,
    ProjectComponent,
    ProjectInsight,
    ProjectStructuralSummary,
    ProjectUnderstanding,
    RefactoringOpportunity,
    RelatedCodeRegion,
)


class ProjectUnderstandingEngine:
    """Transform graph facts into deterministic project-level insights."""

    def understand(self, graph: ProjectKnowledgeGraph) -> ProjectUnderstanding:
        entities = {entity.entity_id: entity for entity in graph.entities}
        current = {
            entity_id: entity
            for entity_id, entity in entities.items()
            if entity.is_current
        }
        current_relationships = [
            relationship
            for relationship in graph.relationships
            if relationship.is_current
        ]

        dependency_flows = self._dependency_flows(
            current_relationships,
            entities,
        )
        cycles = self._dependency_cycles(dependency_flows)
        components = self._components(
            current,
            current_relationships,
            dependency_flows,
        )
        areas = self._areas(current, current_relationships, components)
        related = self._related_code(current_relationships, entities)
        refactoring = self._refactoring_opportunities(
            current_relationships,
            entities,
            cycles,
        )
        evolution = self._evolution_patterns(graph.relationships, entities)
        summary = ProjectStructuralSummary(
            entity_counts=dict(
                sorted(Counter(item.kind for item in graph.entities).items())
            ),
            relationship_counts=dict(
                sorted(
                    Counter(item.kind for item in graph.relationships).items()
                )
            ),
            current_entities=len(current),
            historical_entities=len(graph.entities) - len(current),
            dependency_cycles=cycles,
        )
        insights = self._insights(
            graph.project_id,
            areas,
            components,
            related,
            refactoring,
            evolution,
            cycles,
        )
        return ProjectUnderstanding(
            project_id=graph.project_id,
            areas=areas,
            important_components=components,
            dependency_flows=dependency_flows,
            related_code_regions=related,
            refactoring_opportunities=refactoring,
            evolution_patterns=evolution,
            insights=insights,
            structural_summary=summary,
        )

    def understand_project(self, project: Project) -> Project:
        graph = (
            project.knowledge_state.graph
            if project.knowledge_state is not None
            else None
        )
        if graph is None:
            project.diagnostics.append("Project has no knowledge graph")
            return project
        project.understanding_result = self.understand(graph)
        return project

    def _dependency_flows(self, relationships, entities):
        flows = []
        for relationship in relationships:
            if relationship.kind != "file_depends_on_file":
                continue
            source = entities[relationship.source_entity_id]
            target = entities[relationship.target_entity_id]
            flows.append(
                DependencyFlow(
                    flow_id=relationship.relationship_id,
                    source_file_id=source.source_identity,
                    target_file_id=target.source_identity,
                    module=relationship.properties.get("module", ""),
                )
            )
        return tuple(
            sorted(
                flows,
                key=lambda item: (
                    item.source_file_id,
                    item.target_file_id,
                    item.flow_id,
                ),
            )
        )

    def _components(self, entities, relationships, flows):
        incoming = Counter(flow.target_file_id for flow in flows)
        outgoing = Counter(flow.source_file_id for flow in flows)
        related_by_entity = defaultdict(set)
        symbol_count = Counter()
        chunk_count = Counter()

        source_identity_by_id = {
            entity_id: entity.source_identity
            for entity_id, entity in entities.items()
        }
        for relationship in relationships:
            source_identity = source_identity_by_id.get(
                relationship.source_entity_id
            )
            target_identity = source_identity_by_id.get(
                relationship.target_entity_id
            )
            if source_identity is None or target_identity is None:
                continue
            related_by_entity[source_identity].add(target_identity)
            related_by_entity[target_identity].add(source_identity)
            if relationship.kind == "file_declares_symbol":
                symbol_count[source_identity] += 1
            if relationship.kind == "symbol_has_chunk":
                chunk_count[source_identity] += 1

        components = []
        for entity in entities.values():
            if entity.kind not in {"file", "symbol"}:
                continue
            identity = entity.source_identity
            if entity.kind == "file":
                label = entity.properties.get("current_path", identity)
                score = (
                    incoming[identity] * 2.0
                    + outgoing[identity]
                    + symbol_count[identity]
                )
            else:
                label = entity.properties.get("name", identity)
                score = 1.0 + chunk_count[identity]
            components.append(
                ProjectComponent(
                    component_id=self._id("component", entity.entity_id),
                    entity_id=identity,
                    entity_kind=entity.kind,
                    label=label,
                    importance_score=score,
                    incoming_dependencies=incoming[identity],
                    outgoing_dependencies=outgoing[identity],
                    related_entity_ids=tuple(
                        sorted(related_by_entity[identity])
                    ),
                )
            )
        return tuple(
            sorted(
                components,
                key=lambda item: (
                    -item.importance_score,
                    item.entity_kind,
                    item.entity_id,
                ),
            )
        )

    def _areas(self, entities, relationships, components):
        files_by_area = defaultdict(list)
        for entity in entities.values():
            if entity.kind != "file":
                continue
            path = entity.properties.get("current_path", "")
            parts = PurePosixPath(path).parts
            area = parts[0] if len(parts) > 1 else "(root)"
            files_by_area[area].append(entity.source_identity)

        symbols_by_file = defaultdict(list)
        entity_by_id = entities
        for relationship in relationships:
            if relationship.kind != "file_declares_symbol":
                continue
            source = entity_by_id[relationship.source_entity_id]
            target = entity_by_id[relationship.target_entity_id]
            symbols_by_file[source.source_identity].append(
                target.source_identity
            )

        component_score = {
            item.entity_id: item.importance_score
            for item in components
        }
        areas = []
        for name, file_ids in sorted(files_by_area.items()):
            ordered_files = tuple(sorted(file_ids))
            symbols = tuple(
                sorted(
                    symbol
                    for file_id in ordered_files
                    for symbol in symbols_by_file[file_id]
                )
            )
            areas.append(
                ArchitecturalArea(
                    area_id=self._id("area", name),
                    name=name,
                    path_prefix="" if name == "(root)" else name,
                    file_ids=ordered_files,
                    symbol_ids=symbols,
                    importance_score=sum(
                        component_score.get(file_id, 0.0)
                        for file_id in ordered_files
                    ),
                )
            )
        return tuple(
            sorted(
                areas,
                key=lambda item: (-item.importance_score, item.name),
            )
        )

    def _related_code(self, relationships, entities):
        result = []
        for relationship in relationships:
            if relationship.kind not in {
                "chunk_duplicates_chunk",
                "chunk_similar_to_chunk",
            }:
                continue
            source = entities[relationship.source_entity_id]
            target = entities[relationship.target_entity_id]
            result.append(
                RelatedCodeRegion(
                    relationship_id=relationship.relationship_id,
                    source_chunk_id=source.source_identity,
                    target_chunk_id=target.source_identity,
                    relationship_kind=relationship.kind,
                    score=float(relationship.properties.get("score", "1")),
                )
            )
        return tuple(
            sorted(
                result,
                key=lambda item: (
                    -item.score,
                    item.source_chunk_id,
                    item.target_chunk_id,
                ),
            )
        )

    def _refactoring_opportunities(self, relationships, entities, cycles):
        opportunities = []
        patterns = {
            "file_duplicates_file": ("duplicate_file", 1.0),
            "symbol_duplicates_symbol": ("duplicate_symbol", 0.9),
            "chunk_duplicates_chunk": ("duplicate_code", 1.0),
            "chunk_similar_to_chunk": ("similar_code", 0.75),
        }
        for relationship in relationships:
            policy = patterns.get(relationship.kind)
            if policy is None:
                continue
            source = entities[relationship.source_entity_id].source_identity
            target = entities[relationship.target_entity_id].source_identity
            pattern, confidence = policy
            if relationship.kind == "chunk_similar_to_chunk":
                confidence = float(
                    relationship.properties.get("score", confidence)
                )
            entity_ids = tuple(sorted((source, target)))
            opportunities.append(
                RefactoringOpportunity(
                    opportunity_id=self._id(pattern, *entity_ids),
                    pattern=pattern,
                    entity_ids=entity_ids,
                    reason=relationship.kind.replace("_", " "),
                    confidence=confidence,
                )
            )
        for cycle in cycles:
            opportunities.append(
                RefactoringOpportunity(
                    opportunity_id=self._id("dependency_cycle", *cycle),
                    pattern="dependency_cycle",
                    entity_ids=cycle,
                    reason="Files participate in a circular dependency flow",
                    confidence=1.0,
                )
            )
        return tuple(
            sorted(
                opportunities,
                key=lambda item: (
                    item.pattern,
                    item.entity_ids,
                    item.opportunity_id,
                ),
            )
        )

    def _evolution_patterns(self, relationships, entities):
        supported = {
            "location_moved_to",
            "location_renamed_to",
            "location_moved_and_renamed_to",
            "content_state_evolved_to",
        }
        patterns = []
        for relationship in relationships:
            if relationship.kind not in supported:
                continue
            source = entities[relationship.source_entity_id].source_identity
            target = entities[relationship.target_entity_id].source_identity
            patterns.append(
                EvolutionPattern(
                    pattern_id=relationship.relationship_id,
                    pattern=relationship.kind,
                    entity_ids=(source, target),
                    description=relationship.kind.replace("_", " "),
                )
            )
        return tuple(
            sorted(patterns, key=lambda item: item.pattern_id)
        )

    def _insights(
        self,
        project_id,
        areas,
        components,
        related,
        opportunities,
        evolution,
        cycles,
    ):
        insights = []
        if areas:
            lead = areas[0]
            insights.append(
                ProjectInsight(
                    insight_id=self._id(project_id, "primary_area", lead.area_id),
                    category="architecture",
                    title="Primary architectural area",
                    description=(
                        f"{lead.name} has the highest structural importance"
                    ),
                    entity_ids=lead.file_ids,
                    score=lead.importance_score,
                )
            )
        if components:
            lead = components[0]
            insights.append(
                ProjectInsight(
                    insight_id=self._id(
                        project_id,
                        "important_component",
                        lead.entity_id,
                    ),
                    category="component",
                    title="Important project component",
                    description=f"{lead.label} is highly connected",
                    entity_ids=(lead.entity_id,),
                    score=lead.importance_score,
                )
            )
        if related:
            insights.append(
                ProjectInsight(
                    insight_id=self._id(project_id, "related_code"),
                    category="similarity",
                    title="Related code regions detected",
                    description=f"{len(related)} related chunk pairs detected",
                    entity_ids=tuple(
                        sorted(
                            {
                                identity
                                for item in related
                                for identity in (
                                    item.source_chunk_id,
                                    item.target_chunk_id,
                                )
                            }
                        )
                    ),
                    score=float(len(related)),
                )
            )
        if opportunities:
            insights.append(
                ProjectInsight(
                    insight_id=self._id(project_id, "refactoring"),
                    category="refactoring",
                    title="Refactoring opportunities detected",
                    description=(
                        f"{len(opportunities)} structural opportunities found"
                    ),
                    score=float(len(opportunities)),
                )
            )
        if evolution:
            insights.append(
                ProjectInsight(
                    insight_id=self._id(project_id, "evolution"),
                    category="evolution",
                    title="Project evolution is traceable",
                    description=f"{len(evolution)} evolution transitions found",
                    score=float(len(evolution)),
                )
            )
        if cycles:
            insights.append(
                ProjectInsight(
                    insight_id=self._id(project_id, "cycles"),
                    category="dependency",
                    title="Circular dependencies detected",
                    description=f"{len(cycles)} dependency cycles found",
                    entity_ids=tuple(
                        sorted({item for cycle in cycles for item in cycle})
                    ),
                    score=float(len(cycles)),
                )
            )
        return tuple(sorted(insights, key=lambda item: item.insight_id))

    @staticmethod
    def _dependency_cycles(flows):
        adjacency = defaultdict(set)
        nodes = set()
        for flow in flows:
            adjacency[flow.source_file_id].add(flow.target_file_id)
            nodes.update((flow.source_file_id, flow.target_file_id))

        index = 0
        indexes = {}
        lowlinks = {}
        stack = []
        on_stack = set()
        components = []

        def visit(node):
            nonlocal index
            indexes[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            for target in sorted(adjacency[node]):
                if target not in indexes:
                    visit(target)
                    lowlinks[node] = min(lowlinks[node], lowlinks[target])
                elif target in on_stack:
                    lowlinks[node] = min(lowlinks[node], indexes[target])
            if lowlinks[node] != indexes[node]:
                return
            component = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            if len(component) > 1:
                components.append(tuple(sorted(component)))

        for node in sorted(nodes):
            if node not in indexes:
                visit(node)
        return tuple(sorted(components))

    @staticmethod
    def _id(*parts: str) -> str:
        value = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
