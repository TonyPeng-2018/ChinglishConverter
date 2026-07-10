"""LaTeX source reading.

We hand the raw LaTeX to the model with an explicit instruction to preserve all
markup and touch only prose (see ``prompts._LATEX_GUARD``). This keeps the
document compilable while letting the model use full context to decide what is
prose and what is markup — more robust than a brittle regex tokenizer.
"""

from __future__ import annotations

from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")
