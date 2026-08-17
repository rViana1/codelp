from pathlib import Path

from core.project import Project, ProjectMetadata

from app.pipeline import PipelineAnalyzer

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer


def create_project(
    path: Path,
) -> Project:

    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=path,
        )
    )


def create_analyzer(
    storage,
):

    lifecycle = KnowledgeLifecycleService(
        KnowledgeLoader(
            storage
        ),
        KnowledgeRestorer(),
        KnowledgePersistenceService(
            KnowledgeBuilder(),
            storage,
        ),
    )

    return PipelineAnalyzer(
        scanner=ProjectScanner(),
        parser=ProjectParser(),
        indexer=ProjectIndexer(),
        chunker=ProjectChunker(),
        embedding_engine=EmbeddingEngine(
            FakeEmbeddingProvider(
                dimensions=5
            )
        ),
        knowledge_lifecycle=lifecycle,
    )


def extract_identity_snapshot(
    knowledge,
):
    return {
        "files": [
            (
                item.file_id,
                item.content_hash,
            )
            for item in knowledge.files
        ],
        "symbols": [
            (
                item.symbol_id,
            )
            for item in knowledge.symbols
        ],
        "chunks": [
            (
                item.chunk_id,
                item.content_hash,
            )
            for item in knowledge.chunks
        ],
        "embeddings": [
            (
                item.chunk_id,
                item.provider,
                item.embedding_hash,
            )
            for item in knowledge.embeddings
        ],
        "retrieval": [
            (
                item.chunk_id,
                item.query_hash,
                item.score,
            )
            for item in knowledge.retrieval
        ],
    }


def test_identical_project_states_produce_identical_identities(
    tmp_path: Path,
):

    project_path = tmp_path / "project"

    project_path.mkdir()

    (project_path / "main.py").write_text(
        "def hello():\n"
        "    return 42\n"
    )

    storage = FileKnowledgeStorage(
        str(
            tmp_path / "knowledge"
        )
    )

    analyzer = create_analyzer(
        storage
    )

    first_project = create_project(
        project_path
    )

    analyzer.analyze(
        first_project
    )

    first_knowledge = storage.load(
        "project"
    )

    assert first_knowledge is not None

    first_snapshot = extract_identity_snapshot(
        first_knowledge
    )


    second_project = create_project(
        project_path
    )

    analyzer.analyze(
        second_project
    )

    second_knowledge = storage.load(
        "project"
    )

    assert second_knowledge is not None

    second_snapshot = extract_identity_snapshot(
        second_knowledge
    )


    assert first_snapshot == second_snapshot