import inspect
from pathlib import Path

from core.project import Project, ProjectMetadata

from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.indexing.indexer import ProjectIndexer
from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.diff import ChangeDetectionEngine
from app.knowledge.lifecycle import KnowledgeLifecycleService
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.planning import KnowledgeExecutionPlanner
from app.knowledge.restorer import KnowledgeRestorer
from app.knowledge.storage import InMemoryKnowledgeStorage
from app.knowledge.tracking import IdentityTrackingEngine
from app.parser.parser import ProjectParser
from app.pipeline import PipelineAnalyzer
from app.pipeline.incremental import IncrementalAnalysisEngine
from app.scanner.scanner import ProjectScanner


class RecordingScanner(ProjectScanner):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def scan_project(self, project):
        self.events.append("scan")
        return super().scan_project(project)


class RecordingIdentityTracker(IdentityTrackingEngine):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def track_files(self, **kwargs):
        self.events.append("identity")
        return super().track_files(**kwargs)


class RecordingChangeDetector(ChangeDetectionEngine):
    def __init__(self, events):
        self.events = events

    def compare_files(self, previous_files, current_files):
        self.events.append("changes")
        return super().compare_files(previous_files, current_files)


class RecordingParser(ProjectParser):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def parse_file(self, path):
        self.events.append("parser")
        return super().parse_file(path)


def create_project(root: Path):
    return Project(
        metadata=ProjectMetadata(name="demo", root_path=root)
    )


def create_analyzer(storage, events):
    planner = KnowledgeExecutionPlanner(
        identity_tracker=RecordingIdentityTracker(events),
        change_detector=RecordingChangeDetector(events),
    )
    lifecycle = KnowledgeLifecycleService(
        KnowledgeLoader(storage),
        KnowledgeRestorer(),
        KnowledgePersistenceService(KnowledgeBuilder(), storage),
        planner=planner,
    )
    return PipelineAnalyzer(
        scanner=RecordingScanner(events),
        parser=RecordingParser(events),
        indexer=ProjectIndexer(),
        chunker=ProjectChunker(),
        embedding_engine=EmbeddingEngine(FakeEmbeddingProvider(5)),
        knowledge_lifecycle=lifecycle,
    )


def test_identity_and_change_planning_execute_before_analysis(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    source = root / "main.py"
    source.write_text("def hello():\n    return 1\n", encoding="utf-8")
    storage = InMemoryKnowledgeStorage()
    events = []
    analyzer = create_analyzer(storage, events)

    first = analyzer.analyze(create_project(root))

    assert events[:4] == ["scan", "identity", "changes", "parser"]
    assert first.knowledge_analysis_plan is not None
    assert len(first.knowledge_analysis_plan.file_changes.new_files) == 1
    assert {
        item.file_id
        for item in first.knowledge_analysis_plan.resolved_files
        if any(location.is_current for location in item.locations)
    } == {
        item.file_id
        for item in storage.load("project").files
        if any(location.is_current for location in item.locations)
    }

    source.write_text("def hello():\n    return 2\n", encoding="utf-8")
    events.clear()
    second = analyzer.analyze(create_project(root))

    assert events[:4] == ["scan", "identity", "changes", "parser"]
    plan = second.knowledge_analysis_plan
    assert plan.analyzed_paths == ("main.py",)
    assert plan.reused_paths == ()
    assert len(plan.file_changes.modified_files) == 1
    assert len(second.knowledge_change_result.modified_files) == 1


def test_analysis_modules_remain_unaware_of_knowledge_persistence():
    modules = (
        "app.parser.parser",
        "app.indexing.indexer",
        "app.chunking.chunker",
        "app.embeddings.engine",
    )
    for module_name in modules:
        module = __import__(module_name, fromlist=["*"])
        assert "app.knowledge" not in inspect.getsource(module)


def test_duplicate_file_contents_are_reported_in_pre_analysis_plan(
    tmp_path,
):
    root = tmp_path / "project"
    root.mkdir()
    content = "def duplicate():\n    return True\n"
    (root / "a.py").write_text(content, encoding="utf-8")
    (root / "b.py").write_text(content, encoding="utf-8")
    storage = InMemoryKnowledgeStorage()
    result = create_analyzer(storage, []).analyze(create_project(root))

    duplicates = result.knowledge_analysis_plan.duplicated_file_contents
    assert len(duplicates) == 1
    assert duplicates[0].paths == ("a.py", "b.py")
    current_ids = {
        item.file_id
        for item in storage.load("project").files
        if any(location.is_current for location in item.locations)
    }
    assert len(current_ids) == 2


def test_pipeline_consumes_plan_without_owning_identity_resolution():
    source = inspect.getsource(
        __import__("app.pipeline.incremental", fromlist=["*"])
    )

    assert "FileIdentityResolver" not in source
    assert "FileObservation" not in source
    assert "FileContentHasher" not in source
    assert "PersistentProjectKnowledge" not in source
    assert KnowledgeExecutionPlanner.__module__.startswith("app.knowledge")
    assert IncrementalAnalysisEngine.__module__.startswith("app.pipeline")
