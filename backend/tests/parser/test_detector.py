from pathlib import Path

from app.parser.detector import LanguageDetector


def test_detect_python() -> None:

    detector = LanguageDetector()

    language = detector.detect(Path("main.py"))

    assert language == "python"


def test_detect_unknown_language() -> None:

    detector = LanguageDetector()

    language = detector.detect(Path("main.js"))

    assert language == "unknown"


def test_detect_file_without_extension() -> None:

    detector = LanguageDetector()

    language = detector.detect(Path("Dockerfile"))

    assert language == "unknown"
