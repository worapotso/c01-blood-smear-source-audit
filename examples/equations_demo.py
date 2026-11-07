"""Offline demonstration of C-01 equations with SYNTHETIC data only.

Imports the frozen source-audit implementation; does not download, inspect,
or redistribute blood-smear images, perform training, or run Google Colab.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "audit_sources_r2_frozen.py"
spec = importlib.util.spec_from_file_location("c01_source_audit", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Source audit module unavailable")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def row(image: str, label: str, coords: tuple[float, ...], normalized: bool = False) -> dict[str, str]:
    """Synthetic BCDD CSV-style record with complete source identity."""
    values = [float(v) / 256 if normalized else float(v) for v in coords]
    return {
        "image": image,
        "label": label,
        **dict(zip(("xmin", "ymin", "xmax", "ymax"), map(str, values))),
    }


def eq1_demo() -> dict[str, object]:
    # Illustrative values, not exact BCDD record contents.
    box_a = (85.61, 2.33, 187.74, 120.07)
    box_b = (2.0, 3.0, 10.0, 12.0)
    historical = [
        row("image-1.png", "rbc", box_a),
        row("image-1.png", "wbc", box_a),
        row("image-2.png", "rbc", box_b),
    ]
    current = [
        row("image-1.png", "wbc", box_a, normalized=True),
        row("image-2.png", "rbc", box_b, normalized=True),
    ]
    old = audit.csv_record_multiset(historical, normalized=False)
    new = audit.csv_record_multiset(current, normalized=True)
    missing, added = old - new, new - old
    assert missing == audit.csv_record_multiset(historical[:1], normalized=False)
    return {
        "transformed_scalar": round(256 * 0.3344140625, 5),
        "historical_count": sum(old.values()),
        "current_count": sum(new.values()),
        "missing_count": sum(missing.values()),
        "added_count": sum(added.values()),
        "missing_class": next(iter(missing))[1],
    }


def eq2_demo() -> dict[str, object]:
    boxes = {
        "positive_extent": (2, 3, 10, 12),
        "zero_both": (4, 4, 4, 4),
        "zero_width": (8, 5, 8, 15),
        "outside_image": (-2, 3, 10, 12),
    }
    results = {}
    for label, (x1, y1, x2, y2) in boxes.items():
        results[label] = {
            "width": x2 - x1,
            "height": y2 - y1,
            "equation_2": int(x2 > x1) * int(y2 > y1),
            "full_guard": audit.valid_box(x1, y1, x2, y2, 640, 480),
        }
    return results


def eq3_demo() -> dict[str, object]:
    gray_row = [120, 150, 150, 100, 100, 90, 90, 110, 110]
    image = Image.new("L", (9, 8))
    image.putdata(gray_row * 8)
    left, lt = audit.dhash_strict(image, "left_gt_right")
    right, rt = audit.dhash_strict(image, "right_gt_left")
    # Separate 8-bit toy XOR comparison (real dHash is 64 bits).
    toy_a, toy_b = 0b10110010, 0b10010111
    xor = toy_a ^ toy_b
    return {
        "synthetic_resized_shape_rows_columns": [8, 9],
        "first_row_left_greater_right": f"{left:064b}"[:8],
        "first_row_right_greater_left": f"{right:064b}"[:8],
        "strict_ties_each": [lt, rt],
        "toy_a": f"{toy_a:08b}",
        "toy_b": f"{toy_b:08b}",
        "toy_xor": f"{xor:08b}",
        "toy_hamming_distance": xor.bit_count(),
        "real_pair_historical_expected_ONLY": {
            "names": ["BloodImage_00037.jpg", "BloodImage_00038.jpg"],
            "left_gt_right": 3,
            "right_gt_left": 1,
            "source_dataset_loaded_in_demo": False,
        },
    }


def run_demo() -> dict[str, object]:
    return {
        "execution_scope": "SYNTHETIC_OFFLINE_ONLY",
        "equation_1": eq1_demo(),
        "equation_2": eq2_demo(),
        "equation_3": eq3_demo(),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
