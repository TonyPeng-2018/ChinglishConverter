"""Loader for the bundled Chinglish tutorial."""

from __future__ import annotations

from pathlib import Path

_DATA = Path(__file__).resolve().parent / "data" / "tutorial.md"


def tutorial_text() -> str:
    """Return the full Chinglish tutorial as Markdown text.

    Works both from a source checkout and from a PyInstaller bundle, since the
    data file is shipped alongside the package.
    """
    return _DATA.read_text(encoding="utf-8")
