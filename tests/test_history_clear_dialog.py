import os
import sys
import unittest

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover
    Qt = None
    QApplication = None

TESTS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from libra.main import HistoryClearDialog, should_select_minor, should_select_patch


def build_history_items(revs):
    return [{"rev": rev, "file": f"{rev}.docx"} for rev in revs]


@unittest.skipIf(QApplication is None, "PySide6 is not available")
class HistoryClearDialogSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_should_select_patch_includes_older_same_minor(self):
        latest = (1, 2, 3)
        self.assertTrue(should_select_patch(latest, (1, 2, 2)))
        self.assertTrue(should_select_patch(latest, (1, 2, 0)))
        self.assertFalse(should_select_patch(latest, (1, 2, 3)))
        self.assertFalse(should_select_patch(latest, (1, 1, 9)))

    def test_should_select_minor_includes_older_same_major(self):
        latest = (2, 1, 0)
        self.assertTrue(should_select_minor(latest, (2, 0, 5)))
        self.assertFalse(should_select_minor(latest, (2, 1, 0)))
        self.assertFalse(should_select_minor(latest, (1, 9, 9)))

    def test_select_patch_versions_checks_same_minor_only(self):
        history_items = build_history_items([
            "rev1.2.1_20240101",
            "rev1.2.2_20240102",
            "rev1.1.9_20231231",
            "rev2.0.0_20240201",
        ])
        dialog = HistoryClearDialog(history_items, "rev1.2.3_20240210")
        dialog.select_patch_versions()

        checked = []
        for row in range(dialog.table.rowCount()):
            item = dialog.table.item(row, 0)
            data = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                checked.append(data["rev"])

        self.assertEqual(sorted(checked), ["rev1.2.1_20240101", "rev1.2.2_20240102"])

    def test_select_minor_versions_checks_older_minor_same_major(self):
        history_items = build_history_items([
            "rev1.2.1_20240101",
            "rev1.1.9_20231231",
            "rev1.0.0_20231010",
            "rev2.0.0_20240201",
        ])
        dialog = HistoryClearDialog(history_items, "rev1.2.3_20240210")
        dialog.select_minor_versions()

        checked = []
        for row in range(dialog.table.rowCount()):
            item = dialog.table.item(row, 0)
            data = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                checked.append(data["rev"])

        self.assertEqual(sorted(checked), ["rev1.0.0_20231010", "rev1.1.9_20231231"])
