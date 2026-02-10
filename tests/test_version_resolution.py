from __future__ import annotations

from pathlib import Path

from libra.core import version as version_mod


def test_resolve_app_version_prefers_version_file(monkeypatch, tmp_path: Path):
    version_file = tmp_path / "VERSION.txt"
    version_file.write_text("20260210+abc123\n", encoding="utf-8")

    monkeypatch.setattr(version_mod, "version_file_candidates", lambda: [version_file])
    monkeypatch.setattr(version_mod, "__version__", "0.1.0")

    assert version_mod.resolve_app_version() == "20260210+abc123"


def test_resolve_app_version_falls_back_to_package_version(monkeypatch):
    monkeypatch.setattr(version_mod, "version_file_candidates", lambda: [])
    monkeypatch.setattr(version_mod, "__version__", "0.1.0")

    assert version_mod.resolve_app_version() == "0.1.0"
