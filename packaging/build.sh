#!/usr/bin/env bash
# Build a standalone `chinglish` executable on Linux or macOS.
#
# Usage:
#   ./packaging/build.sh
#
# Produces dist/chinglish. Run it with ./dist/chinglish --help
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install "pyinstaller>=6.0"

rm -rf build dist
pyinstaller packaging/chinglish.spec

echo
echo "Built: dist/chinglish"
echo "Try:   ./dist/chinglish --version"
