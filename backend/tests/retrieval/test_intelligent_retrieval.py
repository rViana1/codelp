from core.project import (
    ProjectKnowledgeGraph,
    ProjectKnowledgeGraphEntity,
    ProjectKnowledgeGraphRelationship,
)

from app.retrieval.intelligent import IntelligentRetrievalEngine
from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)


def graph() -> ProjectKnowledgeGraph:
    return ProjectKnowledgeGraph(
        graph_id="graph",
        project_id="project",
        entities=[
            ProjectKnowledgeGraphEntity(
                entity_id="chunk-a-entity",
                kind="chunk",
                source_identity="chunk-a",
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="chunk-b-entity",
                kind="chunk",
                source_identity="chunk-b",
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="symbol-a", kind="symbol", source_identity="sym-a"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="old-file",
                kind="file_location",
                source_identity="old.py",
                is_current=False,
            ),
        ],
        relationships=[
            ProjectKnowledgeGraphRelationship(
                relationship_id="similarity-evidence",
                kind="chunk_similar_to_chunk",
                source_entity_id="chunk-a-entity",
                target_entity_id="chunk-b-entity",
                properties={"score": "0.8"},
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="chunk-owner",
                kind="symbol_has_chunk",
                source_entity_id="symbol-a",
                target_entity_id="chunk-a-entity",
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="historical-evidence",
                kind="location_moved_to",
                source_entity_id="old-file",
                target_entity_id="symbol-a",
                is_current=False,
            ),
        ],
    )


def retrieval() -> RetrievalCollection:
    return RetrievalCollection(
        query=RetrievalQuery(text="authentication", limit=5),
        results=[RetrievalResult(chunk_id="chunk-a", score=0.9)],
    )


def test_combines_semantic_structural_and_historical_graph_evidence():
    result = IntelligentRetrievalEngine().enrich(retrieval(), graph())
    by_chunk = {item.chunk_id: item for item in result.results}

    assert set(by_chunk) == {"chunk-a", "chunk-b"}
    assert by_chunk["chunk-a"].semantic_score == 0.9
    assert by_chunk["chunk-a"].historical_score > 0
    assert by_chunk["chunk-b"].structural_score > 0
    assert by_chunk["chunk-b"].relationship_ids == (
        "similarity-evidence",
    )
    assert any(
        "chunk_similar_to_chunk" in reason
        for reason in by_chunk["chunk-b"].reasons
    )


def test_graph_enrichment_is_deterministic_for_reordered_graph():
    source = graph()
    reordered = source.model_copy(
        update={
            "entities": list(reversed(source.entities)),
            "relationships": list(reversed(source.relationships)),
        },
        deep=True,
    )

    first = IntelligentRetrievalEngine().enrich(retrieval(), source)
    second = IntelligentRetrievalEngine().enrich(retrieval(), reordered)

    assert first == second


def test_graph_enrichment_discovers_chunks_through_file_dependencies():
    source = graph()
    source.entities.extend(
        [
            ProjectKnowledgeGraphEntity(
                entity_id="file-a", kind="file", source_identity="file-a"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="file-b", kind="file", source_identity="file-b"
            ),
            ProjectKnowledgeGraphEntity(
                entity_id="symbol-b", kind="symbol", source_identity="sym-b"
            ),
        ]
    )
    source.relationships.extend(
        [
            ProjectKnowledgeGraphRelationship(
                relationship_id="file-symbol-a",
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
                relationship_id="file-symbol-b",
                kind="file_declares_symbol",
                source_entity_id="file-b",
                target_entity_id="symbol-b",
            ),
            ProjectKnowledgeGraphRelationship(
                relationship_id="chunk-owner-b",
                kind="symbol_has_chunk",
                source_entity_id="symbol-b",
                target_entity_id="chunk-b-entity",
            ),
        ]
    )
    source.relationships = [
        item
        for item in source.relationships
        if item.relationship_id != "similarity-evidence"
    ]

    result = IntelligentRetrievalEngine().enrich(retrieval(), source)
    related = next(item for item in result.results if item.chunk_id == "chunk-b")

    assert related.structural_score > 0
    assert "dependency" in related.relationship_ids
