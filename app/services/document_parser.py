from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedDocument:
    title: str
    source_path: str
    doc_type: str
    raw_text: str
    normalized_text: str


class DocumentParser:
    """
    Week 2 parser:
    - supports .md and .txt
    - extracts title from first markdown H1 if present
    - otherwise falls back to filename stem
    """

    def parse(self, file_path: Path) -> ParsedDocument:
        suffix = file_path.suffix.lower()

        if suffix not in {".md", ".txt"}:
            raise ValueError(f"Unsupported file type: {suffix}")

        raw_text = file_path.read_text(encoding="utf-8")
        normalized_text = self._normalize_text(raw_text)

        title = self._extract_title(file_path, raw_text)

        return ParsedDocument(
            title=title,
            source_path=str(file_path),
            doc_type=suffix.lstrip("."),
            raw_text=raw_text,
            normalized_text=normalized_text,
        )

    def _extract_title(self, file_path: Path, raw_text: str) -> str:
        # Markdown H1 title
        for line in raw_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()

        # Fallback: filename stem
        return file_path.stem.replace("_", " ").replace("-", " ").title()

    def _normalize_text(self, text: str) -> str:
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Trim trailing spaces on lines
        text = "\n".join(line.rstrip() for line in text.splitlines())

        return text.strip()
