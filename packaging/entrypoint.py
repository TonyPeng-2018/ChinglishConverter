"""PyInstaller entry point — a plain script that PyInstaller can freeze.

Building the standalone executable points at this file (see chinglish.spec).
"""

import sys

from chinglishconverter.cli import main

if __name__ == "__main__":
    sys.exit(main())
