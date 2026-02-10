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


VERSION_RE = re.compile(r"^__version__\s*=\s*['\"](?P<version>[^'\"]+)['\"]")


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
    desc = run_git(repo_root, "describe", "--tags", "--dirty", "--always")
    if desc:
        return desc

    short_sha = run_git(repo_root, "rev-parse", "--short", "HEAD") or "nogit"
    today = dt.datetime.now().strftime("%Y%m%d")
    return f"{today}+{short_sha}"


def resolve_product_version(repo_root: pathlib.Path) -> str:
    init_path = repo_root / "src" / "libra" / "__init__.py"
    try:
        for line in init_path.read_text(encoding="utf-8").splitlines():
            m = VERSION_RE.match(line.strip())
            if m:
                return m.group("version")
    except OSError:
        pass
    return "0.0.0"


def sanitize_for_filename(version: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", version)


def compose_runtime_version(product_version: str, build_id: str) -> str:
    normalized_build = build_id.lstrip("v")
    if normalized_build.startswith(product_version):
        return normalized_build
    return f"{product_version}+{sanitize_for_filename(build_id)}"


def write_version_file(dist_dir: pathlib.Path, version: str) -> pathlib.Path:
    version_file = dist_dir / "VERSION.txt"
    version_file.write_text(version + "\n", encoding="utf-8")
    return version_file


def prepare_archive_tree(dist_dir: pathlib.Path, product_version: str) -> pathlib.Path:
    safe_version = sanitize_for_filename(product_version)
    package_root = dist_dir.parent / "_package"
    package_dir = package_root / f"Libra-{safe_version}"
    bundled_dist = package_dir / dist_dir.name

    if package_root.exists():
        shutil.rmtree(package_root)
    bundled_dist.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dist_dir, bundled_dist)
    return package_dir


def create_archive(dist_dir: pathlib.Path, product_version: str) -> pathlib.Path:
    package_dir = prepare_archive_tree(dist_dir, product_version)
    archive_base = package_dir.parent / package_dir.name
    archive_path = shutil.make_archive(
        str(archive_base),
        "zip",
        root_dir=package_dir.parent,
        base_dir=package_dir.name,
    )
    return pathlib.Path(archive_path)




def supports_contents_directory_option(repo_root: pathlib.Path) -> bool:
    """Return True when installed PyInstaller supports --contents-directory."""
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--help"],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    help_text = (result.stdout or "") + "\n" + (result.stderr or "")
    return "--contents-directory" in help_text


def build_pyinstaller_command(repo_root: pathlib.Path, entry: pathlib.Path, add_data: str) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
    ]

    if not supports_contents_directory_option(repo_root):
        print("[build] ERROR: installed PyInstaller does not support --contents-directory.")
        print("[build]        Please upgrade PyInstaller (recommended >= 6.0) to build onedir with _internal layout.")
        raise RuntimeError("PyInstaller --contents-directory is required")

    cmd.extend(["--contents-directory", "_internal"])

    cmd.extend(
        [
            "--name",
            "Libra",
            "--paths",
            str(repo_root / "src"),
            "--add-data",
            add_data,
            str(entry),
        ]
    )
    return cmd

def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    entry = repo_root / "src" / "pyinstaller_entry.py"
    resources_src = repo_root / "src" / "libra" / "resources"
    add_data = f"{resources_src}{os.pathsep}libra/resources"
    build_id = resolve_build_version(repo_root)
    product_version = resolve_product_version(repo_root)
    runtime_version = compose_runtime_version(product_version, build_id)

    cmd = build_pyinstaller_command(repo_root, entry, add_data)

    print("[build] repo_root:", repo_root)
    print("[build] entry:", entry)
    print("[build] product_version:", product_version)
    print("[build] build_id:", build_id)
    print("[build] runtime_version:", runtime_version)
    print("[build] command:", " ".join(cmd))

    result = subprocess.call(cmd, cwd=repo_root)
    if result != 0:
        return result

    dist_dir = repo_root / "dist" / "Libra"
    if not dist_dir.exists():
        print("[build] ERROR: dist directory not found:", dist_dir)
        return 1

    version_file = write_version_file(dist_dir, runtime_version)
    archive_path = create_archive(dist_dir, product_version)

    print("[build] wrote:", version_file)
    print("[build] archive:", archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
