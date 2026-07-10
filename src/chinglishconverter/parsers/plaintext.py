"""Plain-text / Markdown reading (kept as a module for symmetry)."""

from __future__ import annotations

from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")
