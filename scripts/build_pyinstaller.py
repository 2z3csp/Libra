#!/usr/bin/env python3
"""Build Libra desktop app with a fixed PyInstaller entry point.

Usage:
    python scripts/build_pyinstaller.py
"""

from __future__ import annotations

import datetime as dt
import os
import pathlib
import re
import shutil
import subprocess
import sys


def run_git(repo_root: pathlib.Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def resolve_build_version(repo_root: pathlib.Path) -> str:
    tag = run_git(repo_root, "describe", "--tags", "--exact-match")
    if tag:
        return tag

    short_sha = run_git(repo_root, "rev-parse", "--short", "HEAD") or "nogit"
    today = dt.datetime.now().strftime("%Y%m%d")
    return f"{today}+{short_sha}"


def sanitize_for_filename(version: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", version)


def write_version_file(dist_dir: pathlib.Path, version: str) -> pathlib.Path:
    version_file = dist_dir / "VERSION.txt"
    version_file.write_text(version + "\n", encoding="utf-8")
    return version_file


def create_archive(dist_dir: pathlib.Path, version: str) -> pathlib.Path:
    safe_version = sanitize_for_filename(version)
    archive_base = dist_dir.parent / f"Libra-{safe_version}"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=dist_dir.parent, base_dir=dist_dir.name)
    return pathlib.Path(archive_path)


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    entry = repo_root / "src" / "libra" / "app.py"
    resources_src = repo_root / "src" / "libra" / "resources"
    add_data = f"{resources_src}{os.pathsep}libra/resources"
    build_version = resolve_build_version(repo_root)

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
    print("[build] version:", build_version)
    print("[build] command:", " ".join(cmd))

    result = subprocess.call(cmd, cwd=repo_root)
    if result != 0:
        return result

    dist_dir = repo_root / "dist" / "Libra"
    if not dist_dir.exists():
        print("[build] ERROR: dist directory not found:", dist_dir)
        return 1

    version_file = write_version_file(dist_dir, build_version)
    archive_path = create_archive(dist_dir, build_version)

    print("[build] wrote:", version_file)
    print("[build] archive:", archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
