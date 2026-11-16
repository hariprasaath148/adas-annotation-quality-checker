# ADAS Annotation Quality Checker

A beginner-friendly Python project that audits object-detection annotations for common quality issues.

## What it checks

- Missing or blank labels
- Invalid bounding boxes (`xmin >= xmax` or `ymin >= ymax`)
- Negative coordinates
- Bounding boxes outside image dimensions
- Duplicate annotations (same image, label, and coordinates)
- Summary metrics and a CSV quality report

> This is an educational portfolio project. It is not an official TELUS Digital tool and should only be used with public, synthetic, or personally created sample data. Never upload confidential employer data.

## Requirements

- Python 3.10 or newer
- No third-party packages are required for the core checker

## Run on macOS

Open Terminal and move into this project folder:

```bash
cd adas-annotation-quality-checker
python3 --version
python3 src/quality_checker.py --input sample_data/annotations.csv --output reports/quality_report.csv
```

The report is written to `reports/quality_report.csv`. The terminal also prints a summary.

## Input CSV format

Required columns:

| Column | Meaning | Example |
|---|---|---|
| `image_name` | Image file name | `frame_001.jpg` |
| `image_width` | Image width in pixels | `640` |
| `image_height` | Image height in pixels | `480` |
| `label` | Object category | `car` |
| `xmin` | Left x-coordinate | `20` |
| `ymin` | Top y-coordinate | `30` |
| `xmax` | Right x-coordinate | `150` |
| `ymax` | Bottom y-coordinate | `180` |

Coordinates are expected to be absolute pixel coordinates.

## Example output

The report contains the original annotation fields plus:
- `issues`: pipe-separated validation issues, or `None`
- `status`: `PASS` or `FAIL`

The summary reports total rows, passed rows, failed rows, and row-level pass rate. This pass rate is **not** a model accuracy metric; it only measures the share of annotation rows that pass these checks.

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Suggested improvements

1. Add class-name validation against an approved label list.
2. Add image-file existence checks.
3. Add a small dashboard using Streamlit.
4. Add JSON/COCO annotation support.
5. Add configurable image dimensions and validation rules.

## Portfolio description

Built a Python-based annotation QA utility to validate object-detection bounding boxes, flag malformed or out-of-frame coordinates, detect duplicate rows, and export a CSV quality report. Added unit tests and documented input/output formats.
