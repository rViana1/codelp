from datetime import datetime, timezone

import pytest

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.identity import deterministic_identity
from app.knowledge.models import (
    KnowledgeGraphEntityKind,
    KnowledgeGraphRelationshipKind,
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentKnowledgeGraphRelationship,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentRetrievalMetadata,
    PersistentSymbolIdentity,
)
from app.knowledge.validator import KnowledgeValidator
from app.knowledge.normalizer import KnowledgeNormalizer
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.update import KnowledgeUpdateEngine


T1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T2 = datetime(2026, 2, 1, tzinfo=timezone.utc)
T3 = datetime(2026, 3, 1, tzinfo=timezone.utc)


def create_knowledge(
    *,
    observed_at: datetime = T2,
    include_derived: bool = True,
) -> PersistentProjectKnowledge:
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo",
            created_at=T1,
            updated_at=observed_at,
        ),
        files=[
            PersistentFileIdentity(
                file_id="file-1",
                locations=[
                    PersistentFileLocation(
                        path="old/main.py",
                        first_seen=T1,
                        last_seen=T1,
                        is_current=False,
                    ),
                    PersistentFileLocation(
                        path="src/main.py",
                        first_seen=T2,
                        last_seen=observed_at,
                        is_current=True,
                    ),
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-old",
                        size_bytes=10,
                        generated_at=T1,
                        last_seen=T1,
                        is_current=False,
                    ),
                    PersistentFileFingerprint(
                        content_hash="hash-current",
                        size_bytes=20,
                        generated_at=T2,
                        last_seen=observed_at,
                        is_current=True,
                    ),
                ],
            )
        ],
        symbols=(
            [
                PersistentSymbolIdentity(
                    symbol_id="symbol-1",
                    file_id="file-1",
                    name="main",
                    symbol_type="function",
                )
            ]
            if include_derived
            else []
        ),
        chunks=(
            [
                PersistentChunkIdentity(
                    chunk_id="chunk-1",
                    symbol_id="symbol-1",
                    content_hash="chunk-hash",
                )
            ]
            if include_derived
            else []
        ),
        embeddings=(
            [
                PersistentEmbeddingMetadata(
                    chunk_id="chunk-1",
                    provider="fake:model",
                    embedding_hash="embedding-hash",
                )
            ]
            if include_derived
            else []
        ),
        retrieval=(
            [
                PersistentRetrievalMetadata(
                    chunk_id="chunk-1",
                    query_hash="query-hash",
                    score=0.75,
                )
            ]
            if include_derived
            else []
        ),
    )


def test_graph_projects_all_foundational_entities_and_relationships():
    graph = KnowledgeGraphBuilder().build(create_knowledge())

    assert graph.project_id == "demo"
    assert {entity.kind for entity in graph.entities} == {
        KnowledgeGraphEntityKind.PROJECT,
        KnowledgeGraphEntityKind.FILE,
        KnowledgeGraphEntityKind.FILE_LOCATION,
        KnowledgeGraphEntityKind.FILE_CONTENT_STATE,
        KnowledgeGraphEntityKind.SYMBOL,
        KnowledgeGraphEntityKind.CHUNK,
        KnowledgeGraphEntityKind.EMBEDDING,
        KnowledgeGraphEntityKind.RETRIEVAL,
    }
    assert {relationship.kind for relationship in graph.relationships} == {
        KnowledgeGraphRelationshipKind.PROJECT_CONTAINS_FILE,
        KnowledgeGraphRelationshipKind.FILE_HAS_LOCATION,
        KnowledgeGraphRelationshipKind.FILE_HAS_CONTENT_STATE,
        KnowledgeGraphRelationshipKind.FILE_DECLARES_SYMBOL,
        KnowledgeGraphRelationshipKind.SYMBOL_HAS_CHUNK,
        KnowledgeGraphRelationshipKind.CHUNK_HAS_EMBEDDING,
        KnowledgeGraphRelationshipKind.CHUNK_HAS_RETRIEVAL,
        KnowledgeGraphRelationshipKind.LOCATION_MOVED_TO,
        KnowledgeGraphRelationshipKind.CONTENT_STATE_EVOLVED_TO,
    }
    entity_ids = {entity.entity_id for entity in graph.entities}
    assert all(
        relationship.source_entity_id in entity_ids
        and relationship.target_entity_id in entity_ids
        for relationship in graph.relationships
    )


def test_graph_uses_persistent_identity_and_is_deterministic():
    knowledge = create_knowledge()
    first = KnowledgeGraphBuilder().build(knowledge)
    reordered = knowledge.model_copy(
        update={
            "files": list(reversed(knowledge.files)),
            "symbols": list(reversed(knowledge.symbols)),
            "chunks": list(reversed(knowledge.chunks)),
            "embeddings": list(reversed(knowledge.embeddings)),
            "retrieval": list(reversed(knowledge.retrieval)),
        },
        deep=True,
    )
    second = KnowledgeGraphBuilder().build(reordered)

    assert first == second
    file_entity = next(
        entity
        for entity in first.entities
        if entity.kind == KnowledgeGraphEntityKind.FILE
    )
    assert file_entity.source_identity == "file-1"


def test_graph_represents_historical_locations_and_content_states():
    graph = KnowledgeGraphBuilder().build(create_knowledge())
    locations = [
        entity
        for entity in graph.entities
        if entity.kind == KnowledgeGraphEntityKind.FILE_LOCATION
    ]
    content_states = [
        entity
        for entity in graph.entities
        if entity.kind == KnowledgeGraphEntityKind.FILE_CONTENT_STATE
    ]

    assert {entity.properties["path"] for entity in locations} == {
        "old/main.py",
        "src/main.py",
    }
    assert sum(entity.is_current for entity in locations) == 1
    assert sum(entity.is_current for entity in content_states) == 1


def test_graph_preserves_removed_and_reappearing_entity_identity():
    builder = KnowledgeGraphBuilder()
    first = builder.build(create_knowledge(observed_at=T2))
    removed = builder.build(
        create_knowledge(observed_at=T3, include_derived=False),
        previous=first,
    )
    restored = builder.build(
        create_knowledge(observed_at=T3, include_derived=True),
        previous=removed,
    )

    first_symbol = next(
        entity
        for entity in first.entities
        if entity.kind == KnowledgeGraphEntityKind.SYMBOL
    )
    removed_symbol = next(
        entity
        for entity in removed.entities
        if entity.kind == KnowledgeGraphEntityKind.SYMBOL
    )
    restored_symbol = next(
        entity
        for entity in restored.entities
        if entity.kind == KnowledgeGraphEntityKind.SYMBOL
    )
    first_relationship = next(
        relationship
        for relationship in first.relationships
        if relationship.kind
        == KnowledgeGraphRelationshipKind.FILE_DECLARES_SYMBOL
    )
    removed_relationship = next(
        relationship
        for relationship in removed.relationships
        if relationship.kind
        == KnowledgeGraphRelationshipKind.FILE_DECLARES_SYMBOL
    )
    restored_relationship = next(
        relationship
        for relationship in restored.relationships
        if relationship.kind
        == KnowledgeGraphRelationshipKind.FILE_DECLARES_SYMBOL
    )

    assert first_symbol.entity_id == removed_symbol.entity_id
    assert removed_symbol.is_current is False
    assert restored_symbol.entity_id == first_symbol.entity_id
    assert restored_symbol.is_current is True
    assert restored_symbol.first_observed_at == T2
    assert restored_symbol.last_observed_at == T3
    assert (
        removed_relationship.relationship_id
        == first_relationship.relationship_id
    )
    assert removed_relationship.is_current is False
    assert (
        restored_relationship.relationship_id
        == first_relationship.relationship_id
    )
    assert restored_relationship.is_current is True


def test_graph_round_trips_through_storage(tmp_path):
    knowledge = create_knowledge()
    knowledge.graph = KnowledgeGraphBuilder().build(knowledge)
    storage = FileKnowledgeStorage(str(tmp_path))

    storage.save(knowledge)
    restored = storage.load("demo")

    assert restored is not None
    assert restored.graph == knowledge.graph


def test_graph_validator_rejects_unknown_relationship_endpoint():
    knowledge = create_knowledge()
    graph = KnowledgeGraphBuilder().build(knowledge)
    relationship = graph.relationships[0]
    graph.relationships[0] = PersistentKnowledgeGraphRelationship(
        relationship_id=deterministic_identity(
            "demo",
            "graph_relationship",
            relationship.kind.value,
            "missing",
            relationship.target_entity_id,
        ),
        kind=relationship.kind,
        source_entity_id="missing",
        target_entity_id=relationship.target_entity_id,
    )
    knowledge.graph = graph

    with pytest.raises(ValueError, match="unknown source"):
        KnowledgeValidator().validate(knowledge)


def test_graph_validator_rejects_duplicate_entity_identity():
    knowledge = create_knowledge()
    graph = KnowledgeGraphBuilder().build(knowledge)
    graph.entities.append(graph.entities[0].model_copy(deep=True))
    knowledge.graph = graph

    with pytest.raises(ValueError, match="Duplicate graph entity"):
        KnowledgeValidator().validate(knowledge)


def test_graph_validator_rejects_nondeterministic_entity_identity():
    knowledge = create_knowledge()
    graph = KnowledgeGraphBuilder().build(knowledge)
    graph.entities[0].entity_id = "random-id"
    knowledge.graph = graph

    with pytest.raises(ValueError, match="identity is not deterministic"):
        KnowledgeValidator().validate(knowledge)


def test_knowledge_builder_integrates_graph_with_persistent_file_identity(
    tmp_path,
):
    project_root = tmp_path / "demo"
    project_root.mkdir()
    source = project_root / "main.py"
    source.write_text("def main():\n    return 1\n")
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=project_root)
    )
    project.statistics.scanned_files = [source]

    knowledge = KnowledgeBuilder().build(project)

    assert knowledge.graph is not None
    file_identity = knowledge.files[0].file_id
    file_entity = next(
        entity
        for entity in knowledge.graph.entities
        if entity.kind == KnowledgeGraphEntityKind.FILE
    )
    assert file_entity.source_identity == file_identity


def test_update_engine_preserves_historical_graph_entities():
    previous = create_knowledge(observed_at=T2)
    previous.graph = KnowledgeGraphBuilder().build(previous)
    current = create_knowledge(observed_at=T3, include_derived=False)

    merged = KnowledgeUpdateEngine().merge(previous, current)

    assert merged.graph is not None
    symbol = next(
        entity
        for entity in merged.graph.entities
        if entity.kind == KnowledgeGraphEntityKind.SYMBOL
    )
    assert symbol.is_current is False


def test_schema_two_snapshot_is_projected_before_first_graph_update():
    previous = create_knowledge(observed_at=T2)
    previous.metadata.version = "2.0"
    assert previous.graph is None
    current = create_knowledge(observed_at=T3, include_derived=False)

    merged = KnowledgeUpdateEngine().merge(previous, current)

    assert merged.graph is not None
    historical_symbol = next(
        entity
        for entity in merged.graph.entities
        if entity.kind == KnowledgeGraphEntityKind.SYMBOL
    )
    assert historical_symbol.source_identity == "symbol-1"
    assert historical_symbol.is_current is False


def test_normalizer_orders_graph_without_mutating_input():
    knowledge = create_knowledge()
    graph = KnowledgeGraphBuilder().build(knowledge)
    graph.entities.reverse()
    graph.relationships.reverse()
    knowledge.graph = graph
    original_entities = [entity.entity_id for entity in graph.entities]

    normalized = KnowledgeNormalizer().normalize(knowledge)

    assert normalized.graph is not None
    assert [entity.entity_id for entity in normalized.graph.entities] == sorted(
        original_entities
    )
    assert [entity.entity_id for entity in graph.entities] == original_entities


def test_restorer_exposes_storage_independent_graph_on_project(tmp_path):
    knowledge = create_knowledge()
    knowledge.graph = KnowledgeGraphBuilder().build(knowledge)
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=tmp_path)
    )

    KnowledgeRestorer().restore(project, knowledge)

    assert project.knowledge_state is not None
    assert project.knowledge_state.graph is not None
    assert project.knowledge_state.graph.graph_id == knowledge.graph.graph_id
    assert len(project.knowledge_state.graph.entities) == len(
        knowledge.graph.entities
    )
