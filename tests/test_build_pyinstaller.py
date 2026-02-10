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
