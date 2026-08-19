import pytest

from app.knowledge.models import (
    PersistentEmbeddingMetadata,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
    PersistentFileFingerprint,
    PersistentFileLocation,
    PersistentRetrievalMetadata,
)

from app.knowledge.validator import KnowledgeValidator


def create_file(
    *,
    file_id: str = "file-1",
    path: str = "main.py",
    content_hash: str = "hash",
) -> PersistentFileIdentity:
    return PersistentFileIdentity(
        file_id=file_id,
        locations=[
            PersistentFileLocation(
                path=path,
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-01-01T00:00:00Z",
            )
        ],
        fingerprints=[
            PersistentFileFingerprint(
                content_hash=content_hash,
                size_bytes=1,
                generated_at="2026-01-01T00:00:00Z",
                last_seen="2026-01-01T00:00:00Z",
            )
        ],
    )

def test_validator_accepts_valid_knowledge():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            create_file()
        ],
    )

    KnowledgeValidator().validate(
        knowledge
    )


def test_validator_rejects_duplicate_file_identity():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            create_file(path="a.py"),
            create_file(path="b.py"),
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
        
        
def test_validator_rejects_unknown_embedding_chunk():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="missing",
                provider="fake",
                embedding_hash="hash",
            )
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
        
def test_validator_rejects_unknown_retrieval_chunk():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="missing",
                query_hash="hash",
                score=0.9,
            )
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
        
def test_validator_rejects_different_project_identity():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="project-a"
        )
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate_project_identity(
            "project-b",
            knowledge,
        )
        
def test_validator_accepts_matching_project_identity():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="project-a"
        )
    )

    KnowledgeValidator().validate_project_identity(
        "project-a",
        knowledge,
    )
    
def test_validator_rejects_file_without_path():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            create_file(path="")
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )


def test_validator_rejects_noncanonical_file_path():
    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            create_file(path="/absolute/main.py")
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(knowledge)


def test_validator_rejects_symbol_without_identity():

    from app.knowledge.models import PersistentSymbolIdentity

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="",
                file_id="file-1",
                name="hello",
                symbol_type="function",
            )
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
        
def test_validator_rejects_file_without_hash():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            create_file(content_hash="")
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )


def test_validator_rejects_invalid_retrieval_score():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        chunks=[],
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="chunk-1",
                query_hash="hash",
                score=-1,
            )
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
