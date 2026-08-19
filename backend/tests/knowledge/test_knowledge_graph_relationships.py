from datetime import datetime, timezone

from app.indexing.models import DependencyEntry, ProjectIndex
from app.chunking.models import ChunkCollection, ChunkKind, CodeChunk
from app.knowledge.chunk_mapper import ChunkKnowledgeMapper
from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.identity import deterministic_identity
from app.knowledge.index_mapper import IndexKnowledgeMapper
from app.knowledge.models import (
    KnowledgeGraphEntityKind,
    KnowledgeGraphRelationshipKind,
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentImportReference,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentRetrievalMetadata,
    PersistentSymbolIdentity,
)
from app.knowledge.validator import KnowledgeValidator


T1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T2 = datetime(2026, 2, 1, tzinfo=timezone.utc)
T3 = datetime(2026, 3, 1, tzinfo=timezone.utc)


def file_identity(
    file_id: str,
    locations: list[tuple[str, datetime, bool]],
    content_hash: str,
) -> PersistentFileIdentity:
    return PersistentFileIdentity(
        file_id=file_id,
        locations=[
            PersistentFileLocation(
                path=path,
                first_seen=observed_at,
                last_seen=observed_at,
                is_current=is_current,
            )
            for path, observed_at, is_current in locations
        ],
        fingerprints=[
            PersistentFileFingerprint(
                content_hash=content_hash,
                size_bytes=10,
                generated_at=T1,
                last_seen=T3,
                is_current=True,
            )
        ],
    )


def relationship_knowledge() -> PersistentProjectKnowledge:
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo",
            created_at=T1,
            updated_at=T3,
        ),
        files=[
            file_identity(
                "file-a",
                [("src/a.py", T1, False), ("lib/a.py", T2, True)],
                "duplicate-file-hash",
            ),
            file_identity(
                "file-b",
                [("src/b.py", T1, False), ("src/renamed.py", T2, True)],
                "duplicate-file-hash",
            ),
            file_identity(
                "file-c",
                [("old/c.py", T1, False), ("new/d.py", T2, True)],
                "unique-file-hash",
            ),
        ],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="symbol-a",
                file_id="file-a",
                name="shared",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="symbol-b",
                file_id="file-b",
                name="shared",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="symbol-c",
                file_id="file-c",
                name="other",
                symbol_type="function",
            ),
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-a",
                symbol_id="symbol-a",
                content_hash="duplicate-chunk-hash",
                structural_fingerprint=("a", "b", "c"),
            ),
            PersistentChunkIdentity(
                chunk_id="chunk-b",
                symbol_id="symbol-b",
                content_hash="different-chunk-hash",
                structural_fingerprint=("a", "b", "c", "d"),
            ),
            PersistentChunkIdentity(
                chunk_id="chunk-c",
                symbol_id="symbol-c",
                content_hash="duplicate-chunk-hash",
                structural_fingerprint=("x", "y"),
            ),
        ],
        embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="chunk-a",
                provider="fake:model",
                embedding_hash="embedding-hash",
            )
        ],
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="chunk-a",
                query_hash="query-hash",
                score=0.9,
            )
        ],
        imports=[
            PersistentImportReference(
                import_id=deterministic_identity(
                    "demo", "import", "file-a", "src.renamed"
                ),
                source_file_id="file-a",
                imported_module="src.renamed",
                target_file_id="file-b",
            ),
            PersistentImportReference(
                import_id=deterministic_identity(
                    "demo", "import", "file-a", "os"
                ),
                source_file_id="file-a",
                imported_module="os",
            ),
        ],
    )


def test_graph_represents_all_phase_two_relationship_categories():
    knowledge = relationship_knowledge()
    graph = KnowledgeGraphBuilder().build(knowledge)
    kinds = {relationship.kind for relationship in graph.relationships}

    assert KnowledgeGraphRelationshipKind.FILE_IMPORTS_MODULE in kinds
    assert KnowledgeGraphRelationshipKind.FILE_DEPENDS_ON_FILE in kinds
    assert KnowledgeGraphRelationshipKind.FILE_DUPLICATES_FILE in kinds
    assert KnowledgeGraphRelationshipKind.SYMBOL_DUPLICATES_SYMBOL in kinds
    assert KnowledgeGraphRelationshipKind.CHUNK_DUPLICATES_CHUNK in kinds
    assert KnowledgeGraphRelationshipKind.CHUNK_SIMILAR_TO_CHUNK in kinds
    assert KnowledgeGraphRelationshipKind.LOCATION_MOVED_TO in kinds
    assert KnowledgeGraphRelationshipKind.LOCATION_RENAMED_TO in kinds
    assert (
        KnowledgeGraphRelationshipKind.LOCATION_MOVED_AND_RENAMED_TO
        in kinds
    )
    assert KnowledgeGraphRelationshipKind.CONTENT_STATE_EVOLVED_TO not in kinds
    assert KnowledgeGraphRelationshipKind.CHUNK_HAS_EMBEDDING in kinds
    assert KnowledgeGraphRelationshipKind.CHUNK_HAS_RETRIEVAL in kinds
    assert any(
        entity.kind == KnowledgeGraphEntityKind.MODULE
        and entity.source_identity == "os"
        for entity in graph.entities
    )
    KnowledgeValidator().validate(
        knowledge.model_copy(update={"graph": graph}, deep=True)
    )


def test_similarity_relationship_contains_deterministic_score():
    graph = KnowledgeGraphBuilder().build(relationship_knowledge())
    similarities = [
        relationship
        for relationship in graph.relationships
        if relationship.kind
        == KnowledgeGraphRelationshipKind.CHUNK_SIMILAR_TO_CHUNK
    ]

    assert len(similarities) == 1
    assert similarities[0].properties["score"] == "0.75"


def test_relationship_identity_is_independent_of_collection_order():
    knowledge = relationship_knowledge()
    first = KnowledgeGraphBuilder().build(knowledge)
    reordered = knowledge.model_copy(
        update={
            "files": list(reversed(knowledge.files)),
            "symbols": list(reversed(knowledge.symbols)),
            "chunks": list(reversed(knowledge.chunks)),
            "imports": list(reversed(knowledge.imports)),
        },
        deep=True,
    )
    second = KnowledgeGraphBuilder().build(reordered)

    assert first == second


def test_import_mapper_resolves_only_unique_internal_modules():
    index = ProjectIndex(
        dependencies=[
            DependencyEntry(
                source_file="app/main.py",
                imported_module="pkg.service",
            ),
            DependencyEntry(
                source_file="app/main.py",
                imported_module="external.library",
            ),
        ]
    )
    references = IndexKnowledgeMapper.imports_from_index(
        index,
        {
            "app/main.py": "file-main",
            "pkg/service.py": "file-service",
        },
        "demo",
    )

    by_module = {item.imported_module: item for item in references}
    assert by_module["pkg.service"].target_file_id == "file-service"
    assert by_module["external.library"].target_file_id is None


def test_import_mapper_does_not_guess_ambiguous_suffix_target():
    index = ProjectIndex(
        dependencies=[
            DependencyEntry(
                source_file="main.py",
                imported_module="pkg.service",
            )
        ]
    )

    references = IndexKnowledgeMapper.imports_from_index(
        index,
        {
            "main.py": "file-main",
            "one/pkg/service.py": "file-one",
            "two/pkg/service.py": "file-two",
        },
        "demo",
    )

    assert references[0].target_file_id is None


def test_structural_fingerprint_ignores_identifier_and_literal_names():
    chunks = ChunkCollection(
        chunks=[
            CodeChunk(
                id="source-a",
                file_path="a.py",
                symbol_id="source-a",
                kind=ChunkKind.FUNCTION,
                content="def alpha(value):\n    return value + 1\n",
                start_line=1,
                end_line=2,
            ),
            CodeChunk(
                id="source-b",
                file_path="b.py",
                symbol_id="source-b",
                kind=ChunkKind.FUNCTION,
                content="def beta(item):\n    return item + 99\n",
                start_line=1,
                end_line=2,
            ),
        ]
    )

    mapped = ChunkKnowledgeMapper.from_chunks(
        chunks,
        {"source-a": "symbol-a", "source-b": "symbol-b"},
        project_id="demo",
    )

    assert mapped[0].content_hash != mapped[1].content_hash
    assert mapped[0].structural_fingerprint
    assert (
        mapped[0].structural_fingerprint
        == mapped[1].structural_fingerprint
    )
