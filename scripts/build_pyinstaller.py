#!/usr/bin/env python3
"""Build Libra desktop app with a fixed PyInstaller entry point.

Usage:
    python scripts/build_pyinstaller.py
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    entry = repo_root / "src" / "libra" / "app.py"
    resources_src = repo_root / "src" / "libra" / "resources"
    add_data = f"{resources_src}{os.pathsep}libra/resources"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "Libra",
        "--paths",
        str(repo_root / "src"),
        "--add-data",
        add_data,
        str(entry),
    ]

    print("[build] repo_root:", repo_root)
    print("[build] entry:", entry)
    print("[build] command:", " ".join(cmd))
    return subprocess.call(cmd, cwd=repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
