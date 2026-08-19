from pathlib import Path

from core.project import (
    Project,
    ProjectKnowledgeGraph,
    ProjectKnowledgeGraphEntity,
    ProjectKnowledgeGraphRelationship,
    ProjectKnowledgeState,
    ProjectMetadata,
)

from app.understanding.service import ProjectKnowledgeService


def project() -> Project:
    graph = ProjectKnowledgeGraph(
        graph_id="graph",
        project_id="demo",
        entities=[
            ProjectKnowledgeGraphEntity(
                entity_id="file-a", kind="file", source_identity="file-a"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="file-b", kind="file", source_identity="file-b"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="symbol-a",
                kind="symbol",
                source_identity="symbol-a",
                properties={"name": "alpha"},
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="chunk-a", kind="chunk", source_identity="chunk-a"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="chunk-b", kind="chunk", source_identity="chunk-b"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="old-path",
                kind="file_location",
                source_identity="old.py",
                is_current=False,
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="new-path",
                kind="file_location",
                source_identity="new.py",
            ),
        ],
        relationships=[
            ProjectKnowledgeGraphRelationship(
                relationship_id="symbol-owner",
                kind="file_declares_symbol",
                source_entity_id="file-a",
                target_entity_id="symbol-a",
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="dependency",
                kind="file_depends_on_file",
                source_entity_id="file-a",
                target_entity_id="file-b",
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="similarity",
                kind="chunk_similar_to_chunk",
                source_entity_id="chunk-a",
                target_entity_id="chunk-b",
                properties={"score": "0.8"},
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="history",
                kind="file_has_location",
                source_entity_id="file-a",
                target_entity_id="old-path",
                is_current=False,
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="current-location",
                kind="file_has_location",
                source_entity_id="file-a",
                target_entity_id="new-path",
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="move-history",
                kind="location_moved_to",
                source_entity_id="old-path",
                target_entity_id="new-path",
                is_current=False,
            ),
        ],
    )
    return Project(
        metadata=ProjectMetadata(name="demo", root_path=Path("/tmp/demo")),
        knowledge_state=ProjectKnowledgeState(graph=graph),
    )


def test_service_exposes_project_symbol_dependency_history_and_similarity():
    service = ProjectKnowledgeService()
    aggregate = project()

    assert service.explore_project(aggregate)["project_id"] == "demo"
    assert service.explore_symbol(aggregate, "symbol-a")["properties"] == {
        "name": "alpha"
    }
    assert service.explore_dependencies(aggregate, "file-a")[0]["target"] == (
        "file-b"
    )
    history = service.explore_history(aggregate, "file-a")
    assert {item["kind"] for item in history} == {
        "file_has_location",
        "location_moved_to",
    }
    assert service.explore_related_code(aggregate)[0]["properties"] == {
        "score": "0.8"
    }
    assert service.explore_duplicates(aggregate) == []
    assert service.explore_similarity(aggregate)[0]["kind"] == (
        "chunk_similar_to_chunk"
    )


def test_service_returns_external_safe_data_without_graph_models():
    result = ProjectKnowledgeService().contextual_knowledge(project())

    assert isinstance(result, dict)
    assert isinstance(result["project"], dict)
    assert result["understanding"] is None
    assert result["context"] is None
