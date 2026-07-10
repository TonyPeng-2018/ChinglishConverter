# ChinglishConverter

Convert **PDF**, **LaTeX**, **Overleaf**, and **plain-text/Markdown** documents
between **English** and **Chinglish** — and back — from the command line. The
rewriting is done by Anthropic's Claude API using an explicit, rule-based
"Chinglish skill", so results are consistent rather than ad-hoc.

It also ships a **tutorial** that explains what Chinglish is and how its sentence
structure differs from standard English (topic-comment order, dropped articles,
lexical tense, doubled connectives, literal idiom calques, …).

> ⚠️ **No guarantees.** This is a fun/creative tool. It makes **no guarantee** of
> output quality, accuracy, faithfulness, or safety, and it is **not** a
> professional translation or localization tool. See [DISCLAIMER.md](DISCLAIMER.md).
> You must bring your **own** Anthropic API key — usage is billed to your account.

---

## What is Chinglish here?

Chinglish = English *words* arranged by Mandarin Chinese *grammar and idiom*. It
is systematic, not random. Example:

> **English:** Although it was raining yesterday, I still went to the library,
> because there were three books I had to return.
>
> **Chinglish:** Yesterday although rain, but I still go library, because have
> three book I must return.

Run `chinglish tutorial` for the full explanation.

---

## Install

### Option A — from source (any OS with Python 3.9+)

```bash
git clone https://github.com/tintin/ChinglishConverter.git
cd ChinglishConverter
pip install -e .
```

This installs the `chinglish` command.

### Option B — standalone executable (no Python needed to run)

Build a self-contained binary with [PyInstaller](https://pyinstaller.org/):

| OS | Command | Output |
|---|---|---|
| Linux / macOS | `./packaging/build.sh` | `dist/chinglish` |
| Windows | `./packaging/build.ps1` | `dist/chinglish.exe` |

Copy the resulting file anywhere on your `PATH` and run it like any other
program (`chinglish --help`). This is the "install like an .exe" / plugin-style
distribution — one file, no Python install required on the target machine.

---

## Set up your API key

You need an Anthropic API key from <https://console.anthropic.com/>. Any of these
work (checked in this order):

1. Environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`
2. Saved credential: `chinglish login` (prompts for the key, stores it in your
   user config directory with owner-only permissions).
3. An `ant auth login` profile, if you use the Anthropic CLI.

```bash
chinglish login          # paste your key when prompted (hidden input)
chinglish logout         # remove the saved key
chinglish config         # show current settings + where the config lives
```

---

## Usage

```bash
# English -> Chinglish (default direction), medium intensity
chinglish convert paper.tex

# Chinglish -> English
chinglish convert notes.chinglish.tex --to english

# Control the "accent" strength
chinglish convert essay.txt --intensity heavy      # light | medium | heavy

# A PDF (text is extracted; output is Markdown)
chinglish convert report.pdf -o report.chinglish.md

# Preview to the terminal instead of writing a file
chinglish convert essay.txt --stdout

# A whole Overleaf project: point at the downloaded .zip or the project folder.
# Every .tex file is converted; images/.bib/.sty are copied through untouched.
chinglish convert my-overleaf-export.zip -o my-overleaf-chinglish
chinglish convert ./my-project-dir       -o ./my-project-chinglish

# Read the tutorial
chinglish tutorial
chinglish tutorial -o chinglish-tutorial.md
```

### Defaults / preferences

The **default** direction is English → Chinglish at **medium** intensity with the
`claude-opus-4-8` model. Change the defaults:

```bash
chinglish config --set intensity heavy
chinglish config --set model claude-sonnet-5
```

### What is preserved

- **LaTeX**: all commands, environments, math (`$...$`, `\[...\]`, `equation`,
  `align`, …), comments, and the preamble are kept byte-for-byte. Only prose is
  restyled, so the document still compiles.
- **Everywhere**: proper nouns, numbers, code, URLs, and citations are left
  unchanged; only natural-language text is converted.
- PDFs are **input only** — output is written as Markdown (the tool does not
  regenerate a laid-out PDF), and scanned PDFs without a text layer are not
  supported (no OCR).

---

## How it works

`src/chinglishconverter/prompts.py` contains an explicit, enumerated **rulebook**
(topic-comment structure, article dropping, lexical tense, existential *have*,
doubled connectives, idiom calques, …) plus three intensity presets. The
converter chunks the document on paragraph boundaries, sends each chunk to Claude
with the appropriate system prompt (adding a LaTeX-preservation guard for `.tex`
sources), and reassembles the result.

```
input file ─▶ parser (pdf/tex/text/overleaf) ─▶ chunker ─▶ Claude API ─▶ output
                                                     ▲
                                       prompts.py (the "Chinglish skill")
```

---

## Project layout

```
src/chinglishconverter/
  cli.py            # argparse CLI (convert, tutorial, login, logout, config)
  prompts.py        # the Chinglish rulebook + intensity presets  (the "skill")
  converter.py      # chunking + orchestration
  client.py         # Anthropic API wrapper (streaming, adaptive thinking)
  config.py         # API-key storage + preferences
  tutorial.py       # loads data/tutorial.md
  data/tutorial.md  # the Chinglish tutorial (also shown by `chinglish tutorial`)
  parsers/          # pdf.py, tex.py, plaintext.py, overleaf.py
packaging/          # PyInstaller spec + build scripts (build.sh / build.ps1)
```

---

## License & disclaimer

MIT (see [LICENSE](LICENSE)). No warranty of any kind — read
[DISCLAIMER.md](DISCLAIMER.md) before using the output for anything that matters.
