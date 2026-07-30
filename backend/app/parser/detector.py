from pathlib import Path


class LanguageDetector:
    """
    Detects the programming language of a source file.
    """

    def detect(self, path: Path) -> str:
        """
        Returns the detected language.

        Unknown or unsupported files return "unknown".
        """

        suffix = path.suffix.lower()

        if suffix == ".py":
            return "python"

        return "unknown"