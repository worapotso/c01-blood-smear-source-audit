"""Offline regression tests for docs/EQUATIONS_EXPLAINED_{TH,EN}.md.

All samples are synthetic and generated locally. No source images/network access.
"""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples/equations_demo.py"
spec = importlib.util.spec_from_file_location("equations_demo", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Equation demonstration is missing")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
r = demo.run_demo()

assert r["execution_scope"] == "SYNTHETIC_OFFLINE_ONLY"
eq1 = r["equation_1"]
assert eq1 == {
    "transformed_scalar": 85.61,
    "historical_count": 3,
    "current_count": 2,
    "missing_count": 1,
    "added_count": 0,
    "missing_class": "rbc",
}, eq1
eq2 = r["equation_2"]
assert eq2["positive_extent"]["equation_2"] == 1
assert eq2["positive_extent"]["full_guard"] is True
assert eq2["zero_both"]["equation_2"] == 0
assert eq2["zero_both"]["full_guard"] is False
assert eq2["zero_width"]["equation_2"] == 0
assert eq2["outside_image"]["equation_2"] == 1
assert eq2["outside_image"]["full_guard"] is False
eq3 = r["equation_3"]
assert eq3["synthetic_resized_shape_rows_columns"] == [8, 9]
assert eq3["first_row_left_greater_right"] == "00101000"
assert eq3["first_row_right_greater_left"] == "10000010"
assert eq3["strict_ties_each"] == [32, 32]
assert eq3["toy_a"] == "10110010"
assert eq3["toy_b"] == "10010111"
assert eq3["toy_xor"] == "00100101"
assert eq3["toy_hamming_distance"] == 3
assert eq3["real_pair_historical_expected_ONLY"] == {
    "names": ["BloodImage_00037.jpg", "BloodImage_00038.jpg"],
    "left_gt_right": 3,
    "right_gt_left": 1,
    "source_dataset_loaded_in_demo": False,
}
for filename in ("EQUATIONS_EXPLAINED_TH.md", "EQUATIONS_EXPLAINED_EN.md"):
    p = ROOT / "docs" / filename
    doc = p.read_text(encoding="utf-8")
    for token in ("Equation (1)", "Equation (2)", "Equation (3)", "85.61", "00101000", "10000010"):
        assert token in doc, (filename, token)
print("C01 equation examples PASS (3 synthetic equations; no dataset, network, or clinical model)")
