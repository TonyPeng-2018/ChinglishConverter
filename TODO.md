# TODO — ChinglishConverter

## Now / next
- [ ] Run one live end-to-end conversion with a real API key and eyeball quality
      at each intensity (light / medium / heavy).
- [ ] Build the PyInstaller binary on Linux, macOS, and Windows; smoke-test
      `chinglish --version`, `tutorial`, and `convert` from the frozen exe.
- [ ] Verify LaTeX round-trip: converted `.tex` still compiles (spot-check a real
      Overleaf paper).

## Soon
- [ ] Add a GitHub Actions workflow: run offline tests on push; build + attach
      per-OS binaries on tag/release.
- [ ] `--dry-run` flag that prints token estimate + cost estimate before calling
      the API (use `messages.count_tokens`).
- [ ] Optional PDF *output* (reportlab) so PDF-in can produce PDF-out.
- [ ] Glossary / do-not-translate list flag (`--keep-terms`).

## Ideas / later
- [ ] More source dialects of Chinglish (Cantonese-influenced, etc.).
- [ ] Side-by-side diff view (original vs. converted).
- [ ] Batch mode for a folder of mixed files.
- [ ] Streaming progress to stdout token-by-token in `--stdout` mode.

## Done
- [x] Scaffold package, CLI, packaging, docs.
- [x] Chinglish rulebook + intensity presets (the "skill").
- [x] EN↔Chinglish conversion via Claude API (streaming, adaptive thinking).
- [x] PDF / LaTeX / text / Overleaf parsers.
- [x] Tutorial content + `chinglish tutorial`.
- [x] API-key login/logout/config + credential resolution.
- [x] Offline test suite.
- [x] DISCLAIMER (no quality/safety guarantee; bring-your-own key).
