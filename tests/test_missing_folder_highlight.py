from __future__ import annotations

import os

import pytest

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from libra.app import MainWindow


@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    return app


def test_set_item_missing_folder_style_applies_background(qapp):
    window = MainWindow()
    item = QTableWidgetItem("folder")

    window.set_item_missing_folder_style(item, True)
    assert item.background().color() == window.missing_folder_bg_color()

    window.set_item_missing_folder_style(item, False)
    assert item.background().style() == 0

    window.close()
