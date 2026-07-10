"""Command-line interface for ChinglishConverter.

Subcommands:
    convert    Convert a file between English and Chinglish.
    tutorial   Print the Chinglish tutorial.
    login      Save an Anthropic API key.
    logout     Remove the saved API key.
    config     Show or set default preferences.

Run ``chinglish --help`` or ``chinglish <command> --help`` for details.
"""

from __future__ import annotations

import argparse
import getpass
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from chinglishconverter import __version__, config, prompts
from chinglishconverter.client import (
    AuthError,
    ChinglishClient,
    ConversionAPIError,
)
from chinglishconverter.converter import Converter, ConversionOptions
from chinglishconverter.parsers import (
    KIND_LATEX,
    UnsupportedInput,
    is_overleaf_zip,
    read_input,
)
from chinglishconverter.parsers import overleaf as overleaf_parser
from chinglishconverter.tutorial import tutorial_text

_BANNER = "chinglish"


def _eprint(*args) -> None:
    print(*args, file=sys.stderr)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=_BANNER,
        description="Convert PDF / LaTeX / Overleaf / text documents between "
                    "English and Chinglish, using the Claude API.",
        epilog="No output quality, accuracy, or safety guarantee is made. "
               "You must supply your own Anthropic API key.",
    )
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # convert
    c = sub.add_parser("convert", help="Convert a document.")
    c.add_argument("input", help="Path to a .pdf, .tex, .txt/.md file, an "
                                 "Overleaf .zip, or a project directory.")
    c.add_argument("-o", "--output",
                   help="Output path. Default: alongside input with a suffix. "
                        "For projects, an output directory.")
    c.add_argument("--to", choices=["chinglish", "english"], default="chinglish",
                   help="Conversion direction (default: chinglish).")
    c.add_argument("--intensity", choices=list(prompts.INTENSITY_GUIDES),
                   default=None,
                   help="Chinglish strength (default: your saved preference, "
                        "or 'medium'). Ignored for --to english.")
    c.add_argument("--model", default=None,
                   help="Claude model id (default: your saved preference, or "
                        "claude-opus-4-8).")
    c.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"],
                   default="medium", help="Reasoning effort (default: medium).")
    c.add_argument("--stdout", action="store_true",
                   help="Write the result to stdout instead of a file "
                        "(single files only).")

    # tutorial
    t = sub.add_parser("tutorial", help="Print the Chinglish tutorial.")
    t.add_argument("-o", "--output",
                   help="Write the tutorial to a file instead of stdout.")

    # login / logout
    li = sub.add_parser("login", help="Save your Anthropic API key.")
    li.add_argument("--api-key", default=None,
                    help="API key (omit to be prompted securely).")
    sub.add_parser("logout", help="Remove the saved API key.")

    # config
    cfg = sub.add_parser("config", help="Show or set default preferences.")
    cfg.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"),
                     help="Set a preference (keys: intensity, model).")

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _make_converter(model: Optional[str]) -> Converter:
    prefs = config.default_preferences()
    model = model or prefs["model"]
    client = ChinglishClient(model=model)
    return Converter(client)


def _output_suffix(direction: str) -> str:
    return ".chinglish" if direction == "chinglish" else ".english"


def _default_output_path(inp: Path, direction: str) -> Path:
    suffix = _output_suffix(direction)
    # PDF input becomes markdown output (we do not regenerate PDFs).
    out_ext = ".md" if inp.suffix.lower() == ".pdf" else inp.suffix
    return inp.with_name(inp.stem + suffix + out_ext)


def _progress(i: int, total: int) -> None:
    if total > 1:
        _eprint(f"  chunk {i}/{total} ...")


def _cmd_convert(args) -> int:
    inp = Path(args.input)
    prefs = config.default_preferences()
    intensity = args.intensity or prefs["intensity"]

    try:
        converter = _make_converter(args.model)
    except AuthError as exc:
        _eprint(f"error: {exc}")
        _eprint("Set a key with:  chinglish login")
        return 2

    # --- Overleaf project (directory or zip of many .tex files) ---
    if inp.is_dir() or is_overleaf_zip(inp):
        return _convert_project(inp, args, converter, intensity)

    # --- Single file ---
    try:
        text, kind = read_input(inp)
    except (FileNotFoundError, UnsupportedInput, RuntimeError) as exc:
        _eprint(f"error: {exc}")
        return 2

    options = ConversionOptions(
        direction=args.to,
        intensity=intensity,
        latex=(kind == KIND_LATEX),
        effort=args.effort,
    )

    _eprint(f"Converting {inp.name} -> {args.to} "
            f"({'latex' if options.latex else 'text'})...")
    try:
        result = converter.convert_text(text, options, progress=_progress)
    except (AuthError, ConversionAPIError) as exc:
        _eprint(f"error: {exc}")
        return 2

    if args.stdout:
        sys.stdout.write(result + "\n")
        return 0

    out_path = Path(args.output) if args.output else _default_output_path(inp, args.to)
    out_path.write_text(result, encoding="utf-8")
    _eprint(f"Wrote {out_path}")
    return 0


def _convert_project(inp: Path, args, converter: Converter, intensity: str) -> int:
    """Convert every .tex file in an Overleaf directory or zip."""
    if args.stdout:
        _eprint("error: --stdout is not supported for projects.")
        return 2

    cleanup_dir = None
    if is_overleaf_zip(inp):
        cleanup_dir = Path(tempfile.mkdtemp(prefix="chinglish_overleaf_"))
        root = overleaf_parser.extract_zip(inp, cleanup_dir)
        default_out = inp.with_name(inp.stem + _output_suffix(args.to))
    else:
        root = inp
        default_out = inp.with_name(inp.name + _output_suffix(args.to))

    out_root = Path(args.output) if args.output else default_out
    tex_files = overleaf_parser.list_tex_files(root)
    if not tex_files:
        _eprint(f"error: no .tex files found under {inp}")
        return 2

    _eprint(f"Converting Overleaf project: {len(tex_files)} .tex file(s) "
            f"-> {out_root}")

    # Copy the whole project first so images/.bib/.sty are preserved, then
    # overwrite the .tex files with converted versions.
    import shutil
    if out_root.exists() and out_root.is_dir():
        pass
    else:
        shutil.copytree(root, out_root, dirs_exist_ok=True)

    rc = 0
    for tf in tex_files:
        src = tf.path
        _eprint(f"  {tf.relpath} ...")
        text = src.read_text(encoding="utf-8")
        options = ConversionOptions(
            direction=args.to, intensity=intensity, latex=True, effort=args.effort,
        )
        try:
            result = converter.convert_text(text, options, progress=_progress)
        except (AuthError, ConversionAPIError) as exc:
            _eprint(f"  error on {tf.relpath}: {exc}")
            rc = 2
            continue
        (out_root / tf.relpath).write_text(result, encoding="utf-8")

    if cleanup_dir is not None:
        import shutil as _sh
        _sh.rmtree(cleanup_dir, ignore_errors=True)

    _eprint(f"Done. Output in {out_root}")
    return rc


def _cmd_tutorial(args) -> int:
    text = tutorial_text()
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        _eprint(f"Wrote {args.output}")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def _cmd_login(args) -> int:
    key = args.api_key
    if not key:
        _eprint("Paste your Anthropic API key (input hidden). "
                "Get one at https://console.anthropic.com/")
        try:
            key = getpass.getpass("API key: ")
        except (EOFError, KeyboardInterrupt):
            _eprint("\naborted.")
            return 1
    key = (key or "").strip()
    if not key:
        _eprint("error: no key entered.")
        return 2
    path = config.save_api_key(key)
    _eprint(f"Saved API key to {path}")
    return 0


def _cmd_logout(_args) -> int:
    if config.clear_api_key():
        _eprint("Removed saved API key.")
    else:
        _eprint("No saved API key to remove.")
    return 0


def _cmd_config(args) -> int:
    if args.set:
        key, value = args.set
        if key not in ("intensity", "model"):
            _eprint(f"error: unknown preference '{key}' (use: intensity, model)")
            return 2
        if key == "intensity" and value not in prompts.INTENSITY_GUIDES:
            _eprint(f"error: intensity must be one of "
                    f"{', '.join(prompts.INTENSITY_GUIDES)}")
            return 2
        config.save_preference(key, value)
        _eprint(f"Set {key} = {value}")
        return 0

    prefs = config.default_preferences()
    key = config.resolve_api_key()
    print("Preferences:")
    for k, v in prefs.items():
        print(f"  {k} = {v}")
    print(f"  api_key = {'(set)' if key else '(not set)'}")
    print(f"  config file = {config.config_path()}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_HANDLERS = {
    "convert": _cmd_convert,
    "tutorial": _cmd_tutorial,
    "login": _cmd_login,
    "logout": _cmd_logout,
    "config": _cmd_config,
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    handler = _HANDLERS[args.command]
    try:
        return handler(args)
    except KeyboardInterrupt:  # pragma: no cover
        _eprint("\naborted.")
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
