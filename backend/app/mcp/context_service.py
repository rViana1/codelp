from __future__ import annotations

from core.project.models import Project


class ContextInformationService:
    """
    Application service responsible for exposing
    project context information.

    This service does not build context itself.
    It exposes already generated context through
    an application boundary.
    """

    def get_context(
        self,
        project: Project,
    ) -> dict[str, object] | None:
        if project.context_result is None:
            return None

        context = project.context_result

        return {
            "query": context.query,
            "context_id": context.context_id,
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "score": chunk.score,
                }
                for chunk in context.chunks
            ],
            "max_tokens": context.max_tokens,
            "total_tokens": context.total_tokens,
        }
