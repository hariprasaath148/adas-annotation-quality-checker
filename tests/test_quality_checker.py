import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from quality_checker import validate_row, audit_rows


class TestQualityChecker(unittest.TestCase):
    def setUp(self):
        self.valid_row = {
            "image_name": "frame_001.jpg",
            "image_width": "640",
            "image_height": "480",
            "label": "car",
            "xmin": "20",
            "ymin": "30",
            "xmax": "150",
            "ymax": "180",
        }

    def test_valid_annotation_passes(self):
        self.assertEqual(validate_row(self.valid_row), [])

    def test_negative_coordinate_is_flagged(self):
        row = dict(self.valid_row, xmin="-1")
        self.assertIn("negative_coordinate", validate_row(row))

    def test_invalid_box_size_is_flagged(self):
        row = dict(self.valid_row, xmin="150", xmax="20")
        self.assertIn("invalid_box_size", validate_row(row))

    def test_box_outside_image_is_flagged(self):
        row = dict(self.valid_row, xmax="700")
        self.assertIn("box_outside_image", validate_row(row))

    def test_missing_label_is_flagged(self):
        row = dict(self.valid_row, label=" ")
        self.assertIn("missing_label", validate_row(row))

    def test_later_duplicate_is_flagged(self):
        report, summary = audit_rows([self.valid_row, dict(self.valid_row)])
        self.assertEqual(report[0]["status"], "PASS")
        self.assertEqual(report[1]["status"], "FAIL")
        self.assertIn("duplicate_annotation", report[1]["issues"])
        self.assertEqual(summary["total_rows"], 2)
        self.assertEqual(summary["failed_rows"], 1)


if __name__ == "__main__":
    unittest.main()
