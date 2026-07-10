"""Input parsers: turn a file path into (text, kind) for conversion.

Each parser returns the extractable text plus a ``kind`` string that tells the
converter whether the payload is LaTeX (so markup is preserved) or free prose.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path
from typing import Tuple

from chinglishconverter.parsers import pdf as _pdf
from chinglishconverter.parsers import tex as _tex

KIND_TEXT = "text"
KIND_LATEX = "latex"

_TEX_SUFFIXES = {".tex", ".ltx", ".latex"}
_TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".rst", ".text", ""}


class UnsupportedInput(ValueError):
    """Raised for a file type the tool cannot read."""


def detect_kind(path: Path) -> str:
    """Return KIND_LATEX or KIND_TEXT based on the file extension."""
    suffix = path.suffix.lower()
    if suffix in _TEX_SUFFIXES:
        return KIND_LATEX
    return KIND_TEXT


def is_overleaf_zip(path: Path) -> bool:
    """A .zip that contains at least one .tex file (an Overleaf export)."""
    if path.suffix.lower() != ".zip":
        return False
    try:
        with zipfile.ZipFile(path) as zf:
            return any(n.lower().endswith(".tex") for n in zf.namelist())
    except (zipfile.BadZipFile, OSError):
        return False


def read_input(path: Path) -> Tuple[str, str]:
    """Read a single file into ``(text, kind)``.

    Supports PDF, LaTeX, and plain-text/markdown. For Overleaf projects use the
    ``overleaf`` module instead (a directory or zip of many files).
    """
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _pdf.extract_text(path), KIND_TEXT
    if suffix in _TEX_SUFFIXES:
        return _tex.read(path), KIND_LATEX
    if suffix in _TEXT_SUFFIXES or os.path.isfile(path):
        try:
            return path.read_text(encoding="utf-8"), KIND_TEXT
        except UnicodeDecodeError as exc:
            raise UnsupportedInput(
                f"Cannot read {path} as UTF-8 text. Supported: .pdf, .tex, .txt, .md"
            ) from exc

    raise UnsupportedInput(f"Unsupported input type: {path}")
