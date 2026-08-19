from pathlib import Path

from core.project import Project, ProjectMetadata

from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.indexing.indexer import ProjectIndexer
from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.storage import InMemoryKnowledgeStorage
from app.parser.parser import ProjectParser
from app.pipeline import PipelineAnalyzer
from app.scanner.scanner import ProjectScanner


class CountingParser(ProjectParser):
    def __init__(self):
        super().__init__()
        self.files_parsed = 0

    def parse_file(self, path):
        self.files_parsed += 1
        return super().parse_file(path)


class CountingIndexer(ProjectIndexer):
    def __init__(self):
        self.build_calls = 0
        self.files_indexed = 0

    def build(self, project_root, parsed_project):
        self.build_calls += 1
        self.files_indexed += len(parsed_project.files)
        return super().build(project_root, parsed_project)


class CountingChunker(ProjectChunker):
    def __init__(self):
        self.build_calls = 0
        self.files_chunked = 0

    def build(self, project_root, parsed_project, index_result):
        self.build_calls += 1
        self.files_chunked += len(parsed_project.files)
        return super().build(project_root, parsed_project, index_result)


class CountingProvider(FakeEmbeddingProvider):
    def __init__(self, dimensions=5):
        super().__init__(dimensions=dimensions)
        self.chunks_embedded = 0

    def generate_embedding(self, chunk):
        self.chunks_embedded += 1
        return super().generate_embedding(chunk)


def project(root: Path):
    return Project(
        metadata=ProjectMetadata(name="demo", root_path=root)
    )


def analyzer(storage, dimensions=5):
    parser = CountingParser()
    indexer = CountingIndexer()
    chunker = CountingChunker()
    provider = CountingProvider(dimensions=dimensions)
    lifecycle = KnowledgeLifecycleService(
        KnowledgeLoader(storage),
        KnowledgeRestorer(),
        KnowledgePersistenceService(KnowledgeBuilder(), storage),
    )
    pipeline = PipelineAnalyzer(
        scanner=ProjectScanner(),
        parser=parser,
        indexer=indexer,
        chunker=chunker,
        embedding_engine=EmbeddingEngine(provider),
        knowledge_lifecycle=lifecycle,
    )
    return pipeline, parser, indexer, chunker, provider


def write_project(root):
    root.mkdir()
    (root / "a.py").write_text(
        "def alpha():\n    return 1\n",
        encoding="utf-8",
    )
    (root / "b.py").write_text(
        "def beta():\n    return 2\n",
        encoding="utf-8",
    )


def identity_snapshot(knowledge):
    return {
        "files": tuple(
            (
                item.file_id,
                tuple(
                    (location.path, location.is_current)
                    for location in item.locations
                ),
                tuple(
                    (fingerprint.content_hash, fingerprint.is_current)
                    for fingerprint in item.fingerprints
                ),
            )
            for item in knowledge.files
        ),
        "symbols": tuple(item.symbol_id for item in knowledge.symbols),
        "chunks": tuple(
            (item.chunk_id, item.content_hash)
            for item in knowledge.chunks
        ),
        "embeddings": tuple(
            (item.chunk_id, item.provider, item.embedding_hash)
            for item in knowledge.embeddings
        ),
    }


def runtime_snapshot(value, root):
    return {
        "parsed": tuple(
            (
                item.path.relative_to(root).as_posix(),
                item.model_dump(exclude={"path"}),
            )
            for item in value.parser_result.files
        ),
        "index": value.index_result.model_dump(),
        "chunks": value.chunk_result.model_dump(),
        "embeddings": value.embedding_result.model_dump(),
    }


def test_unchanged_execution_skips_every_expensive_stage(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first = first_analyzer.analyze(project(root))
    first_identity = identity_snapshot(storage.load("project"))

    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert second.incremental_analysis_result.reused_files == (
        "a.py",
        "b.py",
    )
    assert second.incremental_analysis_result.analyzed_files == ()
    assert len(
        second.knowledge_analysis_plan.file_changes.unchanged_files
    ) == 2
    assert runtime_snapshot(second, root) == runtime_snapshot(first, root)
    assert identity_snapshot(storage.load("project")) == first_identity


def test_incremental_reuse_survives_new_file_storage_instance(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage_path = tmp_path / "knowledge"
    first_storage = FileKnowledgeStorage(str(storage_path))
    first_analyzer, *_ = analyzer(first_storage)
    first_analyzer.analyze(project(root))

    second_storage = FileKnowledgeStorage(str(storage_path))
    second_analyzer, parser, indexer, chunker, provider = analyzer(
        second_storage
    )
    result = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert result.incremental_analysis_result.reused_files == (
        "a.py",
        "b.py",
    )


def test_only_modified_file_and_invalidated_chunk_are_recomputed(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    first = storage.load("project")
    stable_file_id = next(
        file.file_id
        for file in first.files
        if any(location.path == "b.py" for location in file.locations)
    )
    alpha_file_id = next(
        file.file_id
        for file in first.files
        if any(location.path == "a.py" for location in file.locations)
    )
    alpha_symbol_id = next(
        item.symbol_id for item in first.symbols if item.name == "alpha"
    )
    alpha_chunk = next(
        item for item in first.chunks
        if item.symbol_id == alpha_symbol_id
    )
    alpha_embedding = next(
        item for item in first.embeddings
        if item.chunk_id == alpha_chunk.chunk_id
    )

    (root / "a.py").write_text(
        "def alpha():\n    return 100\n",
        encoding="utf-8",
    )
    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 1
    assert indexer.files_indexed == 1
    assert chunker.files_chunked == 1
    assert provider.chunks_embedded == 1
    assert second.incremental_analysis_result.analyzed_files == ("a.py",)
    assert second.incremental_analysis_result.reused_files == ("b.py",)
    assert second.knowledge_analysis_plan.analyzed_paths == ("a.py",)
    assert second.knowledge_analysis_plan.reused_paths == ("b.py",)
    assert len(
        second.knowledge_analysis_plan.file_changes.modified_files
    ) == 1
    current = storage.load("project")
    assert any(file.file_id == stable_file_id for file in current.files)
    assert any(file.file_id == alpha_file_id for file in current.files)
    assert any(
        item.symbol_id == alpha_symbol_id for item in current.symbols
    )
    current_chunk = next(
        item for item in current.chunks
        if item.symbol_id == alpha_symbol_id
    )
    current_embedding = next(
        item for item in current.embeddings
        if item.chunk_id == current_chunk.chunk_id
    )
    assert current_chunk.chunk_id == alpha_chunk.chunk_id
    assert current_chunk.content_hash != alpha_chunk.content_hash
    assert (
        current_embedding.chunk_id,
        current_embedding.provider,
    ) == (
        alpha_embedding.chunk_id,
        alpha_embedding.provider,
    )
    assert current_embedding.embedding_hash != alpha_embedding.embedding_hash
    assert len(second.knowledge_change_result.modified_files) == 1
    assert len(second.knowledge_change_result.unchanged_files) == 1


def test_new_file_is_analyzed_without_reprocessing_known_files(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    (root / "c.py").write_text(
        "def gamma():\n    return 3\n",
        encoding="utf-8",
    )

    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 1
    assert indexer.files_indexed == 1
    assert chunker.files_chunked == 1
    assert provider.chunks_embedded == 1
    assert second.incremental_analysis_result.analyzed_files == ("c.py",)
    assert second.incremental_analysis_result.reused_files == (
        "a.py",
        "b.py",
    )
    assert len(second.knowledge_change_result.new_files) == 1
    assert len(second.knowledge_analysis_plan.file_changes.new_files) == 1


def test_move_reuses_analysis_and_relocates_runtime_results(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    first = storage.load("project")
    beta_symbol_id = next(
        item.symbol_id for item in first.symbols if item.name == "beta"
    )

    (root / "src").mkdir()
    (root / "b.py").rename(root / "src" / "b.py")
    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert second.incremental_analysis_result.reused_files == (
        "a.py",
        "src/b.py",
    )
    assert "src/b.py" in second.index_result.files
    assert any(
        chunk.file_path == "src/b.py"
        for chunk in second.chunk_result.chunks
    )
    current = storage.load("project")
    assert any(item.symbol_id == beta_symbol_id for item in current.symbols)
    assert len(second.knowledge_change_result.moved_files) == 1
    assert len(second.knowledge_analysis_plan.file_changes.moved_files) == 1


def test_rename_reuses_analysis_and_preserves_all_identities(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    first = storage.load("project")
    file_id = next(
        item.file_id
        for item in first.files
        if any(location.path == "b.py" for location in item.locations)
    )
    symbol_id = next(
        item.symbol_id for item in first.symbols if item.name == "beta"
    )
    chunk_id = next(
        item.chunk_id
        for item in first.chunks
        if item.symbol_id == symbol_id
    )

    (root / "b.py").rename(root / "renamed.py")
    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))
    current = storage.load("project")

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert len(second.knowledge_analysis_plan.file_changes.renamed_files) == 1
    assert len(second.knowledge_change_result.renamed_files) == 1
    assert any(item.file_id == file_id for item in current.files)
    assert any(item.symbol_id == symbol_id for item in current.symbols)
    assert any(item.chunk_id == chunk_id for item in current.chunks)
    assert any(
        item.chunk_id == chunk_id for item in current.embeddings
    )
    assert "renamed.py" in second.index_result.files


def test_provider_change_only_regenerates_embeddings(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage, dimensions=5)
    first_analyzer.analyze(project(root))

    second_analyzer, parser, indexer, chunker, provider = analyzer(
        storage,
        dimensions=7,
    )
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 2
    assert second.incremental_analysis_result.embedded_chunks == 2
    assert all(
        len(item.vector) == 7
        for item in second.embedding_result.embeddings
    )


def test_removal_drops_invalidated_artifacts_without_recomputing_survivors(
    tmp_path,
):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    first = storage.load("project")
    beta_ids = {
        "symbol": next(
            item.symbol_id for item in first.symbols if item.name == "beta"
        ),
        "chunk": next(
            item.chunk_id
            for item in first.chunks
            if item.symbol_id
            == next(
                symbol.symbol_id
                for symbol in first.symbols
                if symbol.name == "beta"
            )
        ),
    }
    (root / "a.py").unlink()

    second_analyzer, parser, indexer, chunker, provider = analyzer(storage)
    second = second_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert set(second.index_result.files) == {"b.py"}
    assert len(second.knowledge_change_result.removed_files) == 1
    assert len(second.knowledge_analysis_plan.file_changes.removed_files) == 1
    current = storage.load("project")
    assert any(
        item.symbol_id == beta_ids["symbol"] for item in current.symbols
    )
    assert any(item.chunk_id == beta_ids["chunk"] for item in current.chunks)


def test_incremental_and_full_runtime_results_are_consistent(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage = InMemoryKnowledgeStorage()
    first_analyzer, *_ = analyzer(storage)
    first_analyzer.analyze(project(root))
    baseline = storage.load("project").model_copy(deep=True)
    (root / "a.py").write_text(
        "def alpha():\n    return 99\n",
        encoding="utf-8",
    )
    incremental_analyzer, *_ = analyzer(storage)
    incremental = incremental_analyzer.analyze(project(root))

    full_storage = InMemoryKnowledgeStorage()
    full_storage.save(baseline)
    full_analyzer, *_ = analyzer(full_storage)
    full = full_analyzer.analyze(project(root))

    assert runtime_snapshot(incremental, root) == runtime_snapshot(full, root)
    assert identity_snapshot(storage.load("project")) == identity_snapshot(
        full_storage.load("project")
    )


def test_modified_incremental_snapshot_persists_across_processes(tmp_path):
    root = tmp_path / "project"
    write_project(root)
    storage_path = tmp_path / "knowledge"
    first_storage = FileKnowledgeStorage(str(storage_path))
    first_analyzer, *_ = analyzer(first_storage)
    first_analyzer.analyze(project(root))
    (root / "a.py").write_text(
        "def alpha():\n    return 500\n",
        encoding="utf-8",
    )

    second_storage = FileKnowledgeStorage(str(storage_path))
    second_analyzer, parser, indexer, chunker, provider = analyzer(
        second_storage
    )
    second_analyzer.analyze(project(root))
    persisted = identity_snapshot(second_storage.load("project"))

    assert parser.files_parsed == 1
    assert indexer.files_indexed == 1
    assert chunker.files_chunked == 1
    assert provider.chunks_embedded == 1
    assert second_storage.load_analysis_cache("project") is not None

    third_storage = FileKnowledgeStorage(str(storage_path))
    third_analyzer, parser, indexer, chunker, provider = analyzer(third_storage)
    third_analyzer.analyze(project(root))

    assert parser.files_parsed == 0
    assert indexer.build_calls == 0
    assert chunker.build_calls == 0
    assert provider.chunks_embedded == 0
    assert identity_snapshot(third_storage.load("project")) == persisted
