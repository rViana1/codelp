from app.knowledge.models import PersistentKnowledgeMetadata


def test_default_knowledge_version():

    metadata = PersistentKnowledgeMetadata(
        project_id="project-a"
    )

    assert metadata.version == "1.0"
