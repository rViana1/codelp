"""
Context builder responsible for transforming retrieval results
into structured LLM-ready context.
"""

from __future__ import annotations

import hashlib
import json

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
                    semantic_score=result.semantic_score,
                    structural_score=result.structural_score,
                    historical_score=result.historical_score,
                    selection_reasons=result.reasons,
                    relationship_ids=result.relationship_ids,
                    provenance_entity_ids=result.provenance_entity_ids,
                )
            )

        return PromptContext(
            query=retrieval.query.text,
            context_id=self._context_id(
                retrieval.query.text,
                context_chunks,
            ),
            chunks=context_chunks,
        )

    @staticmethod
    def _context_id(
        query: str,
        chunks: list[ContextChunk],
    ) -> str:
        payload = {
            "query": query,
            "chunks": [
                {
                    "chunk_id": item.chunk_id,
                    "content_hash": hashlib.sha256(
                        item.content.encode("utf-8")
                    ).hexdigest(),
                    "score": item.score,
                    "semantic_score": item.semantic_score,
                    "structural_score": item.structural_score,
                    "historical_score": item.historical_score,
                    "reasons": item.selection_reasons,
                    "relationships": item.relationship_ids,
                    "provenance": item.provenance_entity_ids,
                }
                for item in chunks
            ],
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
        
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
