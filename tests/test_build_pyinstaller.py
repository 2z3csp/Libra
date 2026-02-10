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


def test_pyinstaller_command_places_binaries_under_internal(monkeypatch, tmp_path: Path):
    repo_root = tmp_path
    (repo_root / "src" / "libra").mkdir(parents=True)
    (repo_root / "src" / "libra" / "__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    (repo_root / "src" / "pyinstaller_entry.py").write_text('print("entry")\n', encoding="utf-8")

    captured = {}

    def fake_call(cmd, cwd):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        dist = repo_root / "dist" / "Libra"
        dist.mkdir(parents=True, exist_ok=True)
        return 0

    monkeypatch.setattr(bp, "subprocess", type("S", (), {"call": staticmethod(fake_call)}))
    monkeypatch.setattr(bp, "resolve_build_version", lambda _root: "v0.1.0-1-gabc")

    old_file = bp.__file__
    bp.__file__ = str(repo_root / "scripts" / "build_pyinstaller.py")
    try:
        assert bp.main() == 0
    finally:
        bp.__file__ = old_file

    cmd = captured["cmd"]
    assert "--contents-directory" in cmd
    idx = cmd.index("--contents-directory")
    assert cmd[idx + 1] == "_internal"
