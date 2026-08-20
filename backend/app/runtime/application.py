"""Top-level application facade for Codelp project operations."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

from core.project import Project, ProjectMetadata
from core.project import ProjectConfiguration

from app.context.builder import ContextBuilder
from app.chunking.models import ChunkKind, CodeChunk
from app.pipeline.analyzer import PipelineAnalyzer
from app.retrieval.models import RetrievalCollection, RetrievalQuery
from app.retrieval.service import RetrievalService
from app.understanding.engine import ProjectUnderstandingEngine
from app.understanding.service import ProjectKnowledgeService
from app.vectorstore.manager import VectorStoreManager
from app.configuration.models import CodelpSettings

from .exceptions import (
    CapabilityUnavailableError,
    InvalidRequestError,
    WorkspaceClosedError,
    WorkspaceNotFoundError,
)
from .models import ProjectWorkspace, WorkspaceState, WorkspaceStatus
from .execution import AnalysisExecutionManager, ExecutionConflictError
from .security import WorkspaceSecurityPolicy
from .observability import RuntimeObservability
from .diagnostics import categorize_exception, safe_diagnostic_message


class CodelpApplication:
    """Coordinate Codelp capabilities behind one transport-neutral facade."""

    def __init__(
        self,
        analyzer: PipelineAnalyzer,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilder | None = None,
        understanding_engine: ProjectUnderstandingEngine | None = None,
        knowledge_service: ProjectKnowledgeService | None = None,
        vector_store_manager: VectorStoreManager | None = None,
        settings: CodelpSettings | None = None,
        security_policy: WorkspaceSecurityPolicy | None = None,
        observability: RuntimeObservability | None = None,
    ) -> None:
        self.analyzer = analyzer
        self.retrieval_service = retrieval_service
        self.context_builder = context_builder or ContextBuilder()
        self.understanding_engine = (
            understanding_engine or ProjectUnderstandingEngine()
        )
        self.knowledge_service = knowledge_service or ProjectKnowledgeService()
        self.vector_store_manager = (
            vector_store_manager or retrieval_service.store_manager
        )
        self.settings = settings or CodelpSettings()
        self.security_policy = security_policy or WorkspaceSecurityPolicy(
            (Path.cwd(),),
            max_open_workspaces=self.settings.security.max_open_workspaces,
            max_query_characters=self.settings.security.max_query_characters,
            max_project_files=self.settings.security.max_project_files,
            max_project_bytes=self.settings.security.max_project_bytes,
        )
        self.observability = observability or RuntimeObservability()
        self._workspaces: dict[str, ProjectWorkspace] = {}
        self.execution_manager = AnalysisExecutionManager(
            self.analyze,
            max_workers=self.settings.execution.max_workers,
            categorize_error=lambda exc: categorize_exception(exc).value,
            safe_error_message=safe_diagnostic_message,
        )

    def open_project(
        self,
        root_path: str | Path,
        *,
        name: str | None = None,
    ) -> ProjectWorkspace:
        root = self.security_policy.validate_project_root(Path(root_path))
        if not root.exists():
            raise FileNotFoundError(root)
        if not root.is_dir():
            raise NotADirectoryError(root)
        self.security_policy.validate_project_budget(root)
        workspace_id = self._workspace_id(root)
        existing = self._workspaces.get(workspace_id)
        if existing is not None and existing.state != WorkspaceState.CLOSED:
            return existing
        self.security_policy.validate_workspace_count(len(self._workspaces))
        workspace = ProjectWorkspace(
            workspace_id=workspace_id,
            project=Project(
                metadata=ProjectMetadata(name=name or root.name, root_path=root),
                configuration=ProjectConfiguration(
                    follow_symlinks=self.settings.scanner.follow_symlinks,
                    ignore_hidden=self.settings.scanner.ignore_hidden,
                    max_file_size_bytes=(
                        self.settings.scanner.max_file_size_bytes
                    ),
                    ignored_directories=set(
                        self.settings.scanner.ignored_directories
                    ),
                    ignored_extensions=set(
                        self.settings.scanner.ignored_extensions
                    ),
                ),
            ),
            opened_at=datetime.now(timezone.utc),
        )
        self._workspaces[workspace_id] = workspace
        return workspace

    def analyze(self, workspace_id: str) -> Project:
        workspace = self._workspace(workspace_id)
        correlation_id = self.observability.correlation_id(
            "analysis", workspace_id
        )
        started = time.perf_counter()
        try:
            self.analyzer.analyze(workspace.project)
            self.understanding_engine.understand_project(workspace.project)
        except Exception as exc:
            self.observability.record(
                correlation_id=correlation_id,
                operation="analysis",
                status="failed",
                workspace_id=workspace_id,
                duration_seconds=time.perf_counter() - started,
                error_category=categorize_exception(exc).value,
            )
            raise
        workspace.state = WorkspaceState.ANALYZED
        workspace.analyzed_at = datetime.now(timezone.utc)
        graph = workspace.project.knowledge_state.graph
        incremental = workspace.project.incremental_analysis_result
        self.observability.record(
            correlation_id=correlation_id,
            operation="analysis",
            status="completed",
            workspace_id=workspace_id,
            duration_seconds=time.perf_counter() - started,
            metrics={
                "files": workspace.project.statistics.files,
                "reused_files": len(incremental.reused_files),
                "graph_entities": len(graph.entities),
                "graph_relationships": len(graph.relationships),
            },
        )
        return workspace.project

    def retrieve(
        self,
        workspace_id: str,
        query: RetrievalQuery,
        query_vector: list[float],
    ) -> RetrievalCollection:
        workspace = self._workspace(workspace_id)
        result = self.retrieval_service.retrieve_project(
            workspace.project,
            query,
            query_vector,
        )
        workspace.project.retrieval_result = result
        self.context_builder.build_project(workspace.project)
        return result

    def query(
        self,
        workspace_id: str,
        text: str,
        *,
        limit: int | None = None,
    ) -> RetrievalCollection:
        workspace = self._workspace(workspace_id)
        self.security_policy.validate_query(text)
        correlation_id = self.observability.correlation_id(
            "retrieval", workspace_id
        )
        started = time.perf_counter()
        try:
            provider = self.analyzer.embedding_engine.provider
            if provider.info.name == "disabled":
                raise CapabilityUnavailableError(
                    "Embedding retrieval is disabled"
                )
            query_embedding = provider.generate_embedding(
                CodeChunk(
                    id="__query__",
                    file_path="",
                    kind=ChunkKind.FUNCTION,
                    content=text,
                    start_line=1,
                    end_line=1,
                )
            )
            result = self.retrieve(
                workspace_id,
                RetrievalQuery(
                    text=text,
                    limit=limit or self.settings.retrieval.default_limit,
                ),
                query_embedding.vector,
            )
        except Exception as exc:
            self.observability.record(
                correlation_id=correlation_id,
                operation="retrieval",
                status="failed",
                workspace_id=workspace_id,
                duration_seconds=time.perf_counter() - started,
                error_category=categorize_exception(exc).value,
            )
            raise
        self.observability.record(
            correlation_id=correlation_id,
            operation="retrieval",
            status="completed",
            workspace_id=workspace_id,
            duration_seconds=time.perf_counter() - started,
            metrics={
                "results": len(result.results),
                "provenance_relationships": sum(
                    len(item.relationship_ids) for item in result.results
                ),
            },
        )
        return result

    def understand(self, workspace_id: str):
        workspace = self._workspace(workspace_id)
        self.understanding_engine.understand_project(workspace.project)
        return workspace.project.understanding_result

    def explore(
        self,
        workspace_id: str,
        view: str = "project",
        entity_id: str | None = None,
    ) -> object:
        project = self._workspace(workspace_id).project
        if view == "project":
            return self.knowledge_service.explore_project(project)
        if view == "symbol":
            return self.knowledge_service.explore_symbol(
                project, entity_id or ""
            )
        if view == "dependencies":
            return self.knowledge_service.explore_dependencies(
                project, entity_id
            )
        if view == "history":
            return self.knowledge_service.explore_history(project, entity_id)
        if view == "duplicates":
            return self.knowledge_service.explore_duplicates(project, entity_id)
        if view == "similarity":
            return self.knowledge_service.explore_similarity(project, entity_id)
        if view == "related_code":
            return self.knowledge_service.explore_related_code(project, entity_id)
        if view == "context":
            return self.knowledge_service.contextual_knowledge(project)
        raise InvalidRequestError(f"Unsupported exploration view: {view}")

    def status(self, workspace_id: str) -> WorkspaceStatus:
        workspace = self._workspace(workspace_id)
        project = workspace.project
        graph = (
            project.knowledge_state.graph
            if project.knowledge_state is not None
            else None
        )
        incremental = project.incremental_analysis_result
        return WorkspaceStatus(
            workspace_id=workspace.workspace_id,
            project_name=project.metadata.name,
            root_path=str(project.metadata.root_path),
            state=workspace.state,
            files=project.statistics.files,
            directories=project.statistics.directories,
            symbols=(
                len(project.index_result.symbols)
                if project.index_result is not None
                else 0
            ),
            chunks=(
                len(project.chunk_result.chunks)
                if project.chunk_result is not None
                else 0
            ),
            embeddings=(
                len(project.embedding_result.embeddings)
                if project.embedding_result is not None
                else 0
            ),
            graph_entities=len(graph.entities) if graph is not None else 0,
            graph_relationships=(
                len(graph.relationships) if graph is not None else 0
            ),
            analysis_mode=(
                "full"
                if incremental is not None and incremental.full_analysis
                else "incremental"
                if incremental is not None
                else None
            ),
            analyzed_files=(
                incremental.analyzed_files if incremental is not None else ()
            ),
            reused_files=(
                incremental.reused_files if incremental is not None else ()
            ),
            diagnostics=tuple(project.diagnostics),
            capabilities={
                "analysis": True,
                "graph": graph is not None,
                "understanding": project.understanding_result is not None,
                "retrieval": bool(
                    project.embedding_result is not None
                    and project.embedding_result.embeddings
                ),
                "llm": self.settings.llm_enabled,
            },
        )

    def list_workspaces(self) -> tuple[WorkspaceStatus, ...]:
        return tuple(
            self.status(workspace_id)
            for workspace_id in sorted(self._workspaces)
            if self._workspaces[workspace_id].state != WorkspaceState.CLOSED
        )

    def close_project(self, workspace_id: str) -> ProjectWorkspace:
        workspace = self._workspace(workspace_id)
        if self.execution_manager.is_workspace_active(workspace_id):
            raise ExecutionConflictError(
                "Cannot close a workspace during analysis"
            )
        workspace.state = WorkspaceState.CLOSED
        self.vector_store_manager.remove_project(
            workspace.project.metadata.root_path
        )
        self._workspaces.pop(workspace_id, None)
        return workspace

    def submit_analysis(self, workspace_id: str):
        self._workspace(workspace_id)
        return self.execution_manager.submit(workspace_id)

    def execution_status(self, execution_id: str):
        return self.execution_manager.get(execution_id)

    def cancel_execution(self, execution_id: str) -> bool:
        return self.execution_manager.cancel(execution_id)

    def wait_for_execution(
        self, execution_id: str, timeout: float | None = None
    ):
        return self.execution_manager.wait(execution_id, timeout)

    def shutdown(self, *, wait: bool = True) -> None:
        for workspace_id in tuple(sorted(self._workspaces)):
            if not self.execution_manager.is_workspace_active(workspace_id):
                self.close_project(workspace_id)
        self.execution_manager.shutdown(wait=wait)

    def _workspace(self, workspace_id: str) -> ProjectWorkspace:
        workspace = self._workspaces.get(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(workspace_id)
        if workspace.state == WorkspaceState.CLOSED:
            raise WorkspaceClosedError(workspace_id)
        return workspace

    @staticmethod
    def _workspace_id(root_path: Path) -> str:
        return hashlib.sha256(
            root_path.as_posix().encode("utf-8")
        ).hexdigest()
