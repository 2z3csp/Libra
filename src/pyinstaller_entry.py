"""PyInstaller entry point for Libra.

Uses absolute imports so it works when executed as a top-level script.
"""

from libra.app import main


if __name__ == "__main__":
    raise SystemExit(main())
