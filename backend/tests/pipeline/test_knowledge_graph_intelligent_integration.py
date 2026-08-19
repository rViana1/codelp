"""Milestone 10.5 Phase 6 end-to-end acceptance tests."""

from pathlib import Path

from app.chunking.models import ChunkCollection, ChunkKind, CodeChunk
from app.context.builder import ContextBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.restorer import KnowledgeRestorer
from app.retrieval.intelligent import IntelligentRetrievalEngine
from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)
from app.understanding.engine import ProjectUnderstandingEngine
from app.understanding.service import ProjectKnowledgeService
from core.project import Project, ProjectMetadata
from tests.knowledge.test_knowledge_graph_relationships import (
    relationship_knowledge,
)


def test_graph_persistence_restoration_understanding_retrieval_and_context(
    tmp_path,
):
    knowledge = relationship_knowledge()
    knowledge.graph = KnowledgeGraphBuilder().build(knowledge)
    storage = FileKnowledgeStorage(str(tmp_path / "knowledge"))
    storage.save(knowledge)

    loaded = KnowledgeLoader(storage).load("demo")
    assert loaded is not None
    assert loaded.graph == knowledge.graph

    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=Path("/tmp/demo"))
    )
    KnowledgeRestorer().restore(project, loaded)
    ProjectUnderstandingEngine().understand_project(project)

    assert project.knowledge_state is not None
    assert project.knowledge_state.graph is not None
    assert project.understanding_result.related_code_regions
    assert ProjectKnowledgeService().explore_related_code(project)

    semantic = RetrievalCollection(
        query=RetrievalQuery(text="shared implementation", limit=3),
        results=[RetrievalResult(chunk_id="chunk-a", score=0.9)],
    )
    enriched = IntelligentRetrievalEngine().enrich(
        semantic,
        project.knowledge_state.graph,
    )
    assert {item.chunk_id for item in enriched.results} >= {
        "chunk-a",
        "chunk-b",
    }

    chunks = ChunkCollection(
        chunks=[
            CodeChunk(
                id=chunk_id,
                symbol_id=f"symbol-{suffix}",
                file_path=f"{suffix}.py",
                kind=ChunkKind.FUNCTION,
                content=f"def {suffix}(): pass",
                start_line=1,
                end_line=1,
            )
            for chunk_id, suffix in (
                ("chunk-a", "a"),
                ("chunk-b", "b"),
                ("chunk-c", "c"),
            )
        ]
    )
    context = ContextBuilder().build(enriched, chunks)

    assert context.chunks
    assert any(item.relationship_ids for item in context.chunks)


def test_graph_relationship_and_entity_identities_survive_json_round_trip(
    tmp_path,
):
    knowledge = relationship_knowledge()
    knowledge.graph = KnowledgeGraphBuilder().build(knowledge)
    storage = FileKnowledgeStorage(str(tmp_path))
    storage.save(knowledge)

    restored = storage.load("demo")

    assert restored is not None and restored.graph is not None
    assert [item.entity_id for item in restored.graph.entities] == [
        item.entity_id for item in knowledge.graph.entities
    ]
    assert [item.relationship_id for item in restored.graph.relationships] == [
        item.relationship_id for item in knowledge.graph.relationships
    ]
