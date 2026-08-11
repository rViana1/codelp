"""
Context builder responsible for transforming retrieval results
into structured LLM-ready context.
"""

from __future__ import annotations

from uuid import uuid4

from app.chunking.models import ChunkCollection
from app.context.models import (
    ContextChunk,
    PromptContext,
)
from app.retrieval.models import RetrievalCollection

from core.project import Project

class ContextBuilder:
    """
    Builds structured context from retrieval results.

    The ContextBuilder does not perform retrieval,
    ranking or embedding generation.

    It only resolves retrieved chunk identities
    and prepares structured context.
    """

    def build(
        self,
        retrieval: RetrievalCollection,
        chunks: ChunkCollection,
    ) -> PromptContext:
        """
        Convert retrieval results into PromptContext.
        """

        chunk_map = {
            chunk.id: chunk
            for chunk in chunks.chunks
        }

        context_chunks: list[ContextChunk] = []

        for result in retrieval.results:

            chunk = chunk_map.get(
                result.chunk_id
            )

            if chunk is None:
                continue

            context_chunks.append(
                ContextChunk(
                    chunk_id=chunk.id,
                    content=chunk.content,
                    score=result.score,
                )
            )

        return PromptContext(
            query=retrieval.query.text,
            context_id=str(uuid4()),
            chunks=context_chunks,
        )
        
    def build_project(
        self,
        project: Project,
    ) -> Project:
        """
        Builds project context from retrieval results.

        The Project aggregate is enriched with the generated context.
        """

        if project.retrieval_result is None:
            project.diagnostics.append(
                "Project has no retrieval_result"
            )
            return project

        if project.chunk_result is None:
            project.diagnostics.append(
                "Project has no chunk_result"
            )
            return project

        project.context_result = self.build(
            project.retrieval_result,
            project.chunk_result,
        )

        return project
