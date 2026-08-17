import hashlib
from pathlib import Path


class FileContentHasher:

    @staticmethod
    def hash_file(
        path: Path,
    ) -> str:

        content = path.read_bytes()

        return hashlib.sha256(
            content
        ).hexdigest()
