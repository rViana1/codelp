"""Default composition root for the Codelp application runtime."""

from __future__ import annotations

from pathlib import Path

from app.chunking.chunker import ProjectChunker
from app.context.builder import ContextBuilder
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.disabled_provider import DisabledEmbeddingProvider
from app.embeddings.local_hash_provider import LocalHashEmbeddingProvider
from app.embeddings.providers import EmbeddingProvider
from app.indexing.indexer import ProjectIndexer
from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.update import KnowledgeUpdateEngine
from app.parser.parser import ProjectParser
from app.pipeline.analyzer import PipelineAnalyzer
from app.retrieval.retriever import Retriever
from app.retrieval.intelligent import IntelligentRetrievalEngine
from app.retrieval.service import RetrievalService
from app.scanner.scanner import ProjectScanner
from app.understanding.engine import ProjectUnderstandingEngine
from app.understanding.service import ProjectKnowledgeService
from app.vectorstore.manager import VectorStoreManager
from app.configuration import (
    CodelpSettings,
    ConfigurationLoader,
    ConfiguredScanFilter,
)

from .application import CodelpApplication
from .security import WorkspaceSecurityPolicy


def create_codelp_application(
    knowledge_path: str | Path | None = None,
    *,
    embedding_provider: EmbeddingProvider | None = None,
    settings: CodelpSettings | None = None,
    allowed_roots: tuple[str | Path, ...] | None = None,
) -> CodelpApplication:
    """Build the default local, LLM-independent Codelp runtime."""

    settings = settings or CodelpSettings()
    storage_path = (
        Path(knowledge_path)
        if knowledge_path is not None
        else settings.persistence.path
    )
    storage = FileKnowledgeStorage(str(storage_path))
    configured_roots = tuple(
        Path(item) for item in (allowed_roots or settings.security.allowed_project_roots)
    )
    if not configured_roots:
        configured_roots = (storage_path.expanduser().resolve().parent,)
    security_policy = WorkspaceSecurityPolicy(
        configured_roots,
        max_open_workspaces=settings.security.max_open_workspaces,
        max_query_characters=settings.security.max_query_characters,
    )
    graph_builder = KnowledgeGraphBuilder(
        settings.retrieval.similarity_threshold
    )
    lifecycle = KnowledgeLifecycleService(
        loader=KnowledgeLoader(storage),
        restorer=KnowledgeRestorer(),
        persistence=KnowledgePersistenceService(
            KnowledgeBuilder(graph_builder),
            storage,
            update_engine=KnowledgeUpdateEngine(graph_builder),
        ),
    )
    provider = embedding_provider or (
        LocalHashEmbeddingProvider(settings.embeddings.dimensions)
        if settings.embeddings.enabled
        else DisabledEmbeddingProvider()
    )
    vector_stores = VectorStoreManager()
    retrieval = RetrievalService(
        Retriever(),
        vector_stores,
        IntelligentRetrievalEngine(
            semantic_weight=settings.retrieval.semantic_weight,
            structural_weight=settings.retrieval.structural_weight,
            historical_weight=settings.retrieval.historical_weight,
        ),
    )
    analyzer = PipelineAnalyzer(
        scanner=ProjectScanner(ConfiguredScanFilter(settings.scanner)),
        parser=ProjectParser(),
        indexer=ProjectIndexer(),
        chunker=ProjectChunker(),
        embedding_engine=EmbeddingEngine(provider),
        knowledge_lifecycle=lifecycle,
    )
    return CodelpApplication(
        analyzer=analyzer,
        retrieval_service=retrieval,
        context_builder=ContextBuilder(),
        understanding_engine=ProjectUnderstandingEngine(),
        knowledge_service=ProjectKnowledgeService(),
        vector_store_manager=vector_stores,
        settings=settings,
        security_policy=security_policy,
    )


def create_configured_application(
    project_root: str | Path,
    *,
    user_config: str | Path | None = None,
    environment: dict[str, str] | None = None,
    overrides: dict[str, object] | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> CodelpApplication:
    """Resolve all configuration layers and build a project-local runtime."""

    root = Path(project_root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)
    settings = ConfigurationLoader().load(
        project_root=root,
        user_config=user_config,
        environment=environment,
        overrides=overrides,
    )
    knowledge_path = settings.persistence.path
    if not knowledge_path.is_absolute():
        knowledge_path = root / knowledge_path
    return create_codelp_application(
        knowledge_path,
        embedding_provider=embedding_provider,
        settings=settings,
        allowed_roots=(root,),
    )
