from pathlib import Path

from core.project import (
    Project,
    ProjectKnowledgeGraph,
    ProjectKnowledgeGraphEntity,
    ProjectKnowledgeGraphRelationship,
    ProjectKnowledgeState,
    ProjectMetadata,
)

from app.understanding.engine import ProjectUnderstandingEngine


def entity(
    entity_id: str,
    kind: str,
    source_identity: str,
    **properties: str,
) -> ProjectKnowledgeGraphEntity:
    return ProjectKnowledgeGraphEntity(
        entity_id=entity_id,
        kind=kind,
        source_identity=source_identity,
        properties=properties,
    )


def relationship(
    relationship_id: str,
    kind: str,
    source: str,
    target: str,
    *,
    is_current: bool = True,
    **properties: str,
) -> ProjectKnowledgeGraphRelationship:
    return ProjectKnowledgeGraphRelationship(
        relationship_id=relationship_id,
        kind=kind,
        source_entity_id=source,
        target_entity_id=target,
        is_current=is_current,
        properties=properties,
    )


def project_graph() -> ProjectKnowledgeGraph:
    return ProjectKnowledgeGraph(
        graph_id="graph",
        project_id="demo",
        entities=[
            entity("project", "project", "demo"),
            entity("file-a", "file", "persistent-a", current_path="app/a.py"),
            entity("file-b", "file", "persistent-b", current_path="app/b.py"),
            entity("file-c", "file", "persistent-c", current_path="lib/c.py"),
            entity("symbol-a", "symbol", "symbol-a", name="alpha"),
            entity("symbol-b", "symbol", "symbol-b", name="beta"),
            entity("chunk-a", "chunk", "chunk-a"),
            entity("chunk-b", "chunk", "chunk-b"),
            ProjectKnowledgeGraphEntity(
                entity_id="old-location",
                kind="file_location",
                source_identity="old/a.py",
                is_current=False,
                properties={"path": "old/a.py"},
            ),
            entity(
                "new-location",
                "file_location",
                "app/a.py",
                path="app/a.py",
            ),
        ],
        relationships=[
            relationship(
                "dependency-ab",
                "file_depends_on_file",
                "file-a",
                "file-b",
                module="app.b",
            ),
            relationship(
                "dependency-ba",
                "file_depends_on_file",
                "file-b",
                "file-a",
                module="app.a",
            ),
            relationship(
                "declare-a",
                "file_declares_symbol",
                "file-a",
                "symbol-a",
            ),
            relationship(
                "declare-b",
                "file_declares_symbol",
                "file-b",
                "symbol-b",
            ),
            relationship(
                "chunk-link-a", "symbol_has_chunk", "symbol-a", "chunk-a"
            ),
            relationship(
                "chunk-link-b", "symbol_has_chunk", "symbol-b", "chunk-b"
            ),
            relationship(
                "similar",
                "chunk_similar_to_chunk",
                "chunk-a",
                "chunk-b",
                score="0.8",
            ),
            relationship(
                "duplicate",
                "chunk_duplicates_chunk",
                "chunk-a",
                "chunk-b",
            ),
            relationship(
                "move",
                "location_moved_and_renamed_to",
                "old-location",
                "new-location",
                is_current=False,
            ),
        ],
    )


def test_understanding_identifies_areas_components_and_dependency_flows():
    result = ProjectUnderstandingEngine().understand(project_graph())

    assert {area.name for area in result.areas} == {"app", "lib"}
    assert len(result.dependency_flows) == 2
    assert result.structural_summary.dependency_cycles == (
        ("persistent-a", "persistent-b"),
    )
    assert result.important_components[0].entity_id in {
        "persistent-a",
        "persistent-b",
    }


def test_understanding_identifies_related_code_and_refactoring_patterns():
    result = ProjectUnderstandingEngine().understand(project_graph())

    assert {item.relationship_kind for item in result.related_code_regions} == {
        "chunk_duplicates_chunk",
        "chunk_similar_to_chunk",
    }
    assert {item.pattern for item in result.refactoring_opportunities} == {
        "dependency_cycle",
        "duplicate_code",
        "similar_code",
    }


def test_understanding_identifies_evolution_and_generates_insights():
    result = ProjectUnderstandingEngine().understand(project_graph())

    assert len(result.evolution_patterns) == 1
    assert result.evolution_patterns[0].pattern == (
        "location_moved_and_renamed_to"
    )
    assert {
        insight.category for insight in result.insights
    } >= {"architecture", "component", "dependency", "evolution"}
    assert result.structural_summary.current_entities == 9
    assert result.structural_summary.historical_entities == 1


def test_understanding_is_deterministic_for_reordered_graph():
    graph = project_graph()
    reordered = graph.model_copy(
        update={
            "entities": list(reversed(graph.entities)),
            "relationships": list(reversed(graph.relationships)),
        },
        deep=True,
    )

    first = ProjectUnderstandingEngine().understand(graph)
    second = ProjectUnderstandingEngine().understand(reordered)

    assert first == second


def test_understand_project_enriches_aggregate_root():
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=Path("/tmp/demo")),
        knowledge_state=ProjectKnowledgeState(graph=project_graph()),
    )

    result = ProjectUnderstandingEngine().understand_project(project)

    assert result is project
    assert project.understanding_result is not None
    assert project.understanding_result.project_id == "demo"


def test_understand_project_reports_missing_graph():
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=Path("/tmp/demo"))
    )

    ProjectUnderstandingEngine().understand_project(project)

    assert project.understanding_result is None
    assert project.diagnostics == ["Project has no knowledge graph"]
