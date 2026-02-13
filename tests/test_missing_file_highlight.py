from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")
from libra import app as app_mod


def test_scan_folder_keeps_missing_doc_and_marks_missing(monkeypatch, tmp_path: Path):
    folder_path = str(tmp_path)
    meta = {
        "documents": {
            "sample.docx": {
                "current_file": "sample_rev1.0.0_20260210.docx",
                "current_rev": "rev1.0.0_20260210",
                "updated_at": "",
                "updated_by": "",
                "last_memo": "",
                "history": [],
            }
        }
    }

    monkeypatch.setattr(app_mod, "load_meta", lambda _folder: meta)
    monkeypatch.setattr(app_mod, "safe_list_files", lambda _folder, _ignore=None: [])

    save_meta_called = {"value": False}

    def _save_meta(_folder, _meta):
        save_meta_called["value"] = True

    monkeypatch.setattr(app_mod, "save_meta", _save_meta)

    scanned_meta, rows = app_mod.scan_folder(folder_path)

    assert "sample.docx" in scanned_meta["documents"]
    assert len(rows) == 1
    assert rows[0].filename == "sample_rev1.0.0_20260210.docx"
    assert rows[0].missing is True
    # Missing file only state should not trigger metadata rewrite.
    assert save_meta_called["value"] is False


def test_scan_folder_removes_doc_without_current_file(monkeypatch, tmp_path: Path):
    folder_path = str(tmp_path)
    meta = {
        "documents": {
            "empty.docx": {
                "current_file": "",
                "current_rev": "",
                "updated_at": "",
                "updated_by": "",
                "last_memo": "",
                "history": [],
            }
        }
    }

    monkeypatch.setattr(app_mod, "load_meta", lambda _folder: meta)
    monkeypatch.setattr(app_mod, "safe_list_files", lambda _folder, _ignore=None: [])

    save_meta_called = {"value": False}

    def _save_meta(_folder, _meta):
        save_meta_called["value"] = True

    monkeypatch.setattr(app_mod, "save_meta", _save_meta)

    scanned_meta, rows = app_mod.scan_folder(folder_path)

    assert scanned_meta["documents"] == {}
    assert rows == []
    assert save_meta_called["value"] is True
