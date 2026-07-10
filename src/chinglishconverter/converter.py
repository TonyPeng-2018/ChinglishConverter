"""Core conversion orchestration: chunk text, call the model, reassemble."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from chinglishconverter import prompts
from chinglishconverter.client import ChinglishClient

# Chunk on paragraph boundaries so each request stays coherent and outputs are
# not truncated. ~9000 characters keeps well clear of the output-token ceiling
# while preserving enough context for consistent style.
DEFAULT_CHUNK_CHARS = 9000

ProgressFn = Callable[[int, int], None]


@dataclass
class ConversionOptions:
    direction: str = prompts.DIRECTION_TO_CHINGLISH
    intensity: str = prompts.DEFAULT_INTENSITY
    latex: bool = False
    effort: str = "medium"
    chunk_chars: int = DEFAULT_CHUNK_CHARS


def _split_into_chunks(text: str, limit: int) -> List[str]:
    """Split text into <=limit-char chunks on blank-line (paragraph) breaks.

    A paragraph longer than the limit is emitted whole rather than cut mid-line,
    so LaTeX blocks and long sentences are never sliced.
    """
    if len(text) <= limit:
        return [text]

    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        piece = para if not current else current + "\n\n" + para
        if len(piece) <= limit or not current:
            current = piece
        else:
            chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


class Converter:
    """High-level converter tying the prompt harness to the API client."""

    def __init__(self, client: ChinglishClient):
        self._client = client

    def convert_text(self, text: str, options: ConversionOptions,
                     progress: Optional[ProgressFn] = None) -> str:
        """Convert a whole document string according to ``options``."""
        if not text.strip():
            return text

        system_prompt = prompts.build_system_prompt(
            direction=options.direction,
            intensity=options.intensity,
            latex=options.latex,
        )
        chunks = _split_into_chunks(text, options.chunk_chars)
        total = len(chunks)
        out: List[str] = []
        for i, chunk in enumerate(chunks, start=1):
            if progress:
                progress(i, total)
            rewritten = self._client.rewrite(
                system_prompt, chunk, effort=options.effort
            )
            out.append(rewritten)
        return "\n\n".join(out)
