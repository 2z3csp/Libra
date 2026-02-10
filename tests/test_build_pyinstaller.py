from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_pyinstaller.py"
SPEC = importlib.util.spec_from_file_location("build_pyinstaller", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
bp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bp)


def test_resolve_build_version_prefers_describe(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(bp, "run_git", lambda _root, *args: "v1.2.3-4-gabc123-dirty" if args[:1] == ("describe",) else "")
    assert bp.resolve_build_version(tmp_path) == "v1.2.3-4-gabc123-dirty"


def test_prepare_archive_tree_creates_versioned_root(tmp_path: Path):
    dist_dir = tmp_path / "dist" / "Libra"
    dist_dir.mkdir(parents=True)
    (dist_dir / "Libra.exe").write_text("binary", encoding="utf-8")

    package_dir = bp.prepare_archive_tree(dist_dir, "v1.0.0+abc")

    assert package_dir.name == "Libra-v1.0.0-abc"
    assert (package_dir / "Libra" / "Libra.exe").exists()


def test_build_pyinstaller_command_includes_contents_directory_when_supported(monkeypatch, tmp_path: Path):
    repo_root = tmp_path
    entry = repo_root / "src" / "pyinstaller_entry.py"
    add_data = "dummy;libra/resources"

    monkeypatch.setattr(bp, "supports_contents_directory_option", lambda _root: True)

    cmd = bp.build_pyinstaller_command(repo_root, entry, add_data)

    assert "--contents-directory" in cmd
    idx = cmd.index("--contents-directory")
    assert cmd[idx + 1] == "_internal"
    assert cmd[-1] == str(entry)


def test_build_pyinstaller_command_skips_contents_directory_when_unsupported(monkeypatch, tmp_path: Path):
    repo_root = tmp_path
    entry = repo_root / "src" / "pyinstaller_entry.py"
    add_data = "dummy;libra/resources"

    monkeypatch.setattr(bp, "supports_contents_directory_option", lambda _root: False)

    cmd = bp.build_pyinstaller_command(repo_root, entry, add_data)

    assert "--contents-directory" not in cmd
    assert cmd[-1] == str(entry)


def test_supports_contents_directory_option_detects_help_text(monkeypatch, tmp_path: Path):
    class R:
        def __init__(self, stdout: str, stderr: str = ""):
            self.stdout = stdout
            self.stderr = stderr

    monkeypatch.setattr(bp.subprocess, "run", lambda *a, **k: R("... --contents-directory DIR ..."))
    assert bp.supports_contents_directory_option(tmp_path) is True

    monkeypatch.setattr(bp.subprocess, "run", lambda *a, **k: R("usage: pyinstaller"))
    assert bp.supports_contents_directory_option(tmp_path) is False
