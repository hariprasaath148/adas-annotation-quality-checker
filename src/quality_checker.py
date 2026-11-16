#!/usr/bin/env python3
"""Validate object-detection annotation rows and export a quality report."""

import argparse
import csv
from pathlib import Path
from collections import Counter

REQUIRED_COLUMNS = [
    "image_name", "image_width", "image_height", "label",
    "xmin", "ymin", "xmax", "ymax",
]


def parse_number(value, field_name):
    """Convert a CSV value to a float or raise a readable error."""
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be numeric; got {value!r}")


def validate_row(row, duplicate_keys=None):
    """Return a list of quality issues for one annotation row."""
    issues = []
    duplicate_keys = duplicate_keys or set()

    image_name = (row.get("image_name") or "").strip()
    label = (row.get("label") or "").strip()

    if not image_name:
        issues.append("missing_image_name")
    if not label:
        issues.append("missing_label")

    try:
        width = parse_number(row.get("image_width"), "image_width")
        height = parse_number(row.get("image_height"), "image_height")
        xmin = parse_number(row.get("xmin"), "xmin")
        ymin = parse_number(row.get("ymin"), "ymin")
        xmax = parse_number(row.get("xmax"), "xmax")
        ymax = parse_number(row.get("ymax"), "ymax")
    except ValueError as exc:
        issues.append(f"invalid_numeric_value: {exc}")
        return issues

    if width <= 0 or height <= 0:
        issues.append("invalid_image_dimensions")

    if xmin < 0 or ymin < 0:
        issues.append("negative_coordinate")

    if xmin >= xmax or ymin >= ymax:
        issues.append("invalid_box_size")

    if xmax > width or ymax > height:
        issues.append("box_outside_image")

    key = (
        image_name, label,
        xmin, ymin, xmax, ymax,
    )
    if key in duplicate_keys:
        issues.append("duplicate_annotation")

    return issues


def read_annotations(input_path):
    """Read annotations from CSV and verify the required columns."""
    with open(input_path, "r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty or has no header row.")

        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError("Missing required CSV columns: " + ", ".join(missing))

        return list(reader)


def make_duplicate_keys(rows):
    """Identify duplicate annotation keys; the later occurrence is flagged."""
    seen = set()
    duplicate_keys_by_index = set()

    for index, row in enumerate(rows):
        try:
            key = (
                (row.get("image_name") or "").strip(),
                (row.get("label") or "").strip(),
                parse_number(row.get("xmin"), "xmin"),
                parse_number(row.get("ymin"), "ymin"),
                parse_number(row.get("xmax"), "xmax"),
                parse_number(row.get("ymax"), "ymax"),
            )
        except ValueError:
            continue

        if key in seen:
            duplicate_keys_by_index.add(index)
        else:
            seen.add(key)

    return duplicate_keys_by_index


def audit_rows(rows):
    """Return report rows and summary counts."""
    duplicate_indices = make_duplicate_keys(rows)
    report_rows = []

    for index, row in enumerate(rows):
        issues = validate_row(row)
        if index in duplicate_indices:
            issues.append("duplicate_annotation")
        report_row = dict(row)
        report_row["issues"] = "|".join(issues) if issues else "None"
        report_row["status"] = "FAIL" if issues else "PASS"
        report_rows.append(report_row)

    total = len(report_rows)
    passed = sum(1 for row in report_rows if row["status"] == "PASS")
    failed = total - passed
    pass_rate = (passed / total * 100) if total else 0.0

    summary = {
        "total_rows": total,
        "passed_rows": passed,
        "failed_rows": failed,
        "pass_rate_percent": round(pass_rate, 2),
    }
    return report_rows, summary


def write_report(report_rows, output_path):
    """Write report rows to CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not report_rows:
        # Write a useful header even if the input has no data rows.
        fieldnames = REQUIRED_COLUMNS + ["issues", "status"]
    else:
        fieldnames = list(report_rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Check object-detection annotations and export a CSV QA report."
    )
    parser.add_argument("--input", required=True, help="Path to the annotation CSV.")
    parser.add_argument("--output", required=True, help="Path for the quality report CSV.")
    args = parser.parse_args()

    try:
        rows = read_annotations(args.input)
        report_rows, summary = audit_rows(rows)
        write_report(report_rows, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print("Annotation Quality Summary")
    print("--------------------------")
    print(f"Total rows : {summary['total_rows']}")
    print(f"Passed     : {summary['passed_rows']}")
    print(f"Failed     : {summary['failed_rows']}")
    print(f"Pass rate  : {summary['pass_rate_percent']}%")
    print(f"Report     : {args.output}")


if __name__ == "__main__":
    main()
