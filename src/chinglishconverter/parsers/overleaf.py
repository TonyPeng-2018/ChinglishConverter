"""Overleaf-project handling.

An Overleaf project is just a bundle of files. You can get one by:
  * "Menu -> Download -> Source" in Overleaf (a .zip), or
  * cloning the project's git remote (a directory).

This module walks a directory or a .zip and yields the ``.tex`` files to
convert. Other files (images, .bib, .sty) are left untouched. When the source is
a zip, we extract it to a working directory so results can be written back.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

_TEX_SUFFIXES = {".tex", ".ltx", ".latex"}


@dataclass
class TexFile:
    """A single .tex file inside a project, with its path relative to the root."""
    root: Path
    relpath: Path

    @property
    def path(self) -> Path:
        return self.root / self.relpath


def extract_zip(zip_path: Path, dest: Path) -> Path:
    """Extract an Overleaf .zip into ``dest`` and return the extraction root."""
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        # Guard against path traversal (zip slip).
        for member in zf.namelist():
            target = (dest / member).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise ValueError(f"Unsafe path in zip: {member}")
        zf.extractall(dest)
    return dest


def iter_tex_files(root: Path) -> Iterator[TexFile]:
    """Yield every .tex file under ``root`` (recursively)."""
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in _TEX_SUFFIXES:
            yield TexFile(root=root, relpath=path.relative_to(root))


def list_tex_files(root: Path) -> List[TexFile]:
    return list(iter_tex_files(root))
