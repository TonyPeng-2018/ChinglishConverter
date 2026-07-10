# PROGRESS — ChinglishConverter

Status of the main workstreams. Sourced from the code and manual smoke tests.

| Date | Workstream | Status | Notes / headline result |
|------|-----------|--------|-------------------------|
| 2026-07-10 | Project scaffolding | ✅ Done | `src/` layout, `pyproject.toml`, `chinglish` console entry point, MIT license. |
| 2026-07-10 | Chinglish "skill" (prompt harness) | ✅ Done | `prompts.py`: explicit 14-rule rulebook (topic-comment, article drop, lexical tense, existential *have*, doubled connectives, idiom calques) + 3 intensity presets. Default = medium. |
| 2026-07-10 | Conversion engine | ✅ Done | `converter.py` chunks on paragraph boundaries; `client.py` streams from Claude (`claude-opus-4-8`, adaptive thinking). Both directions (EN↔Chinglish). |
| 2026-07-10 | Input parsers | ✅ Done | PDF (pypdf text extraction), LaTeX (markup-preserving), text/Markdown, Overleaf (zip or directory of `.tex`). |
| 2026-07-10 | CLI | ✅ Done | `convert`, `tutorial`, `login`, `logout`, `config`. Credential resolution: env → saved key → SDK profile. |
| 2026-07-10 | Tutorial | ✅ Done | `data/tutorial.md` — structural differences between English and Chinglish; printed by `chinglish tutorial`. |
| 2026-07-10 | Packaging (exe/binary) | ✅ Done | PyInstaller spec + `build.sh` / `build.ps1` produce a one-file `chinglish` / `chinglish.exe`. Not yet built/verified on each OS in CI. |
| 2026-07-10 | Docs | ✅ Done | README (canonical) — now **bilingual**: each section has an inline `> **Chinglish:**` echo. DISCLAIMER (no quality/safety guarantee, bring-your-own key). |
| 2026-07-10 | Offline tests | ✅ Done | `tests/` cover chunking, prompt building, config; run without network/API. |

## Not yet done / verified
- End-to-end conversion against the live Claude API (needs a key; not run in this environment).
- PyInstaller binaries not yet built and smoke-tested per OS.
- No CI workflow yet.
