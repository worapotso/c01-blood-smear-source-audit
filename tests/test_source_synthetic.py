# Offline-only smoke tests: NO dataset, network, GitHub, Colab or clinical model.
from pathlib import Path
from PIL import Image
import importlib.util, sys, json, ast
root=Path(__file__).resolve().parents[1]
code=root/"src/audit_sources_r2_frozen.py"
ast.parse(code.read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("source_audit",code)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# Original R1 test confirms these names from frozen source implementation.
assert mod.valid_box(2,3,10,12,640,480)
assert not mod.valid_box(4,4,4,4,640,480)
blank=Image.new("RGB",(15,15),(127,127,127))
for comparator in ("left_gt_right","right_gt_left"):
    hashed,ties=mod.dhash_strict(blank,comparator)
    assert hashed==0 and ties==64
m=json.loads((root/"manifests/historical_expected_32_NOT_OBSERVED.json").read_text(encoding="utf-8"))
assert len(m["claims"])==32
assert all(c["status"]=="NOT_TESTED_UNTIL_AUTHORIZED_COLAB" for c in m["claims"])
notebook=json.loads((root/"notebooks/C01_SourcePinned_Audit_Colab.ipynb").read_text(encoding="utf-8"))
assert len(notebook["cells"])==10
assert all(c["execution_count"] is None and not c["outputs"] for c in notebook["cells"] if c["cell_type"]=="code")
flags="".join(notebook["cells"][1]["source"])
for label in ("USER_ACCEPTS_SOURCE_TERMS","ALLOW_EXTERNAL_SOURCE_FETCH","RUN_SOURCE_AUDIT","RUN_PAIRWISE_DHASH"):
    assert label+" = False" in flags
print("G5 OFFLINE smoke tests PASS (synthetic only, zero source dataset and zero remote calls)")
