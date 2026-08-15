from pathlib import Path

from core.project import Project, ProjectMetadata

from app.pipeline import PipelineAnalyzer

from app.scanner.scanner import ProjectScanner
from app.parser.parser import ProjectParser
from app.indexing.indexer import ProjectIndexer
from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider


def test_pipeline_analyzer_executes_complete_pipeline(
    tmp_path: Path,
) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text(
        "def hello():\n"
        "    return 42\n\n"
        "class User:\n"
        "    def login(self):\n"
        "        return True\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    analyzer = PipelineAnalyzer(
        scanner=ProjectScanner(),
        parser=ProjectParser(),
        indexer=ProjectIndexer(),
        chunker=ProjectChunker(),
        embedding_engine=EmbeddingEngine(
            FakeEmbeddingProvider(
                dimensions=5
            )
        ),
    )

    result = analyzer.analyze(
        project
    )

    assert result is project

    assert project.statistics.files == 1

    assert project.parser_result is not None

    assert project.index_result is not None

    assert project.chunk_result is not None

    assert project.embedding_result is not None
