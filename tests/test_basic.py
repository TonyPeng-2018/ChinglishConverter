"""Offline tests — no network or API key required.

Run with:  python -m pytest   (or)   python tests/test_basic.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chinglishconverter import prompts  # noqa: E402
from chinglishconverter.converter import _split_into_chunks  # noqa: E402
from chinglishconverter.tutorial import tutorial_text  # noqa: E402


def test_prompt_directions():
    p = prompts.build_system_prompt("chinglish", "medium")
    assert "Chinglish" in p
    assert "topic" in p.lower()
    e = prompts.build_system_prompt("english")
    assert "standard English" in e


def test_prompt_intensities():
    for level in prompts.INTENSITY_GUIDES:
        p = prompts.build_system_prompt("chinglish", level)
        assert level.upper() in p


def test_latex_guard_appended():
    p = prompts.build_system_prompt("chinglish", "medium", latex=True)
    assert "LaTeX SOURCE" in p
    p2 = prompts.build_system_prompt("chinglish", "medium", latex=False)
    assert "LaTeX SOURCE" not in p2


def test_unknown_direction_raises():
    try:
        prompts.build_system_prompt("klingon")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_chunking_small_text_single_chunk():
    text = "hello world"
    assert _split_into_chunks(text, 9000) == [text]


def test_chunking_respects_paragraphs():
    paras = ["A" * 100, "B" * 100, "C" * 100]
    text = "\n\n".join(paras)
    chunks = _split_into_chunks(text, 150)
    # No chunk should exceed the limit unless a single paragraph is bigger.
    for c in chunks:
        assert len(c) <= 150 or "\n\n" not in c
    # Round-trips back to the same content.
    assert "\n\n".join(chunks).replace("\n\n", "") == text.replace("\n\n", "")


def test_chunking_oversized_paragraph_kept_whole():
    big = "X" * 500
    chunks = _split_into_chunks(big, 100)
    assert chunks == [big]


def test_tutorial_loads():
    t = tutorial_text()
    assert "Chinglish" in t
    assert "topic-comment" in t.lower()


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
