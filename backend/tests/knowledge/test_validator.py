import pytest

from app.knowledge.models import (
    PersistentEmbeddingMetadata,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
    PersistentRetrievalMetadata,
)

from app.knowledge.validator import KnowledgeValidator


def test_validator_accepts_valid_knowledge():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="file-1",
                path="main.py",
                content_hash="hash",
            )
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
            PersistentFileIdentity(
                file_id="file-1",
                path="a.py",
                content_hash="hash",
            ),
            PersistentFileIdentity(
                file_id="file-1",
                path="b.py",
                content_hash="hash",
            ),
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
            PersistentFileIdentity(
                file_id="file-1",
                path="",
                content_hash="hash",
            )
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )


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
            PersistentFileIdentity(
                file_id="file-1",
                path="main.py",
                content_hash="",
            )
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