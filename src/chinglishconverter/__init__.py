"""ChinglishConverter — convert documents between English and Chinglish.

A command-line tool and installable plugin that rewrites English text into
Chinglish (English shaped by Chinese grammar and idiom) or restores Chinglish
back to standard English. It handles plain text, LaTeX/Overleaf sources, and
PDFs, and ships a tutorial that explains the structural differences between the
two.

The rewriting is performed by the Claude API. You must supply your own API
credentials (see ``chinglish login`` or the README). No output quality, accuracy,
or safety guarantees are made — see DISCLAIMER.md.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
