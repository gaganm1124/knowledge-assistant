from __future__ import annotations

import hashlib
from pathlib import Path


SUPPORTED_EXTENSIONS = {"md", "txt"}


def discover_files(
        source_dir: str,
        recursive: bool = True,
        file_types: list[str] | None = None,
) -> list[Path]:
    """
    Discover files under source_dir matching allowed extensions.
    """
    base = Path(source_dir)
    if not base.exists() or not base.is_dir():
        return []

    allowed = set(file_types or SUPPORTED_EXTENSIONS)
    allowed = {ext.lower().lstrip(".") for ext in allowed}

    pattern = "**/*" if recursive else "*"
    files = []

    for path in base.glob(pattern):
        if path.is_file():
            ext = path.suffix.lower().lstrip(".")
            if ext in allowed:
                files.append(path)

    return sorted(files)


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def infer_doc_type(path: Path) -> str:
    return path.suffix.lower().lstrip(".")
