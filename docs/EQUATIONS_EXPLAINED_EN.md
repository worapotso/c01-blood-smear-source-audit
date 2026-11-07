# Equations (1)–(3): Worked explanations for the C-01 blood-smear source audit

> **Scope.** Educational companion to the C-01 manuscript under preparation, not a new observed run, clinical validation, or replay of the protected production pipeline.
> **Original implementation:** [`src/audit_sources_r2_frozen.py`](../src/audit_sources_r2_frozen.py). **Source protocol:** [`SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md`](SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md).
> **Thai detailed version:** [อ่านฉบับภาษาไทย](EQUATIONS_EXPLAINED_TH.md). **Offline demonstration:** [`examples/equations_demo.py`](../examples/equations_demo.py).

## Overview and evidence limits

| Equation | Operation | Reported finding | Not established |
|---|---|---|---|
| (1) | Compare historical and current BCDD record **multisets** after a declared coordinate transform | One historical annotation missing; no new current record | Cause of removal, biological class truth |
| (2) | Test positive width and height of a bounding box | 2 BCCD boxes have zero extent under the study-defined noninclusive rule | Whether all conventions treat these boxes as erroneous |
| (3) | Compute 64-bit horizontal dHash descriptors under two strict directions and compare them | One cross-split BCCD candidate pair at distances 3 (L>R) and 1 (R>L) | Exact image identity, same slide/patient or model leakage |

### Equation (1): Reconciliation across BCDD source revisions

$$
\begin{aligned}
T(u) &= \operatorname{round}(256u,5),\\
|A_{\mathrm h}\ominus T(A_{\mathrm c})| &= 1,\\
|T(A_{\mathrm c})\ominus A_{\mathrm h}| &= 0 .
\end{aligned}\tag{1}
$$

Here `A_h` is the multiset of *historical pixel-coordinate* BCDD annotation records; `A_c` is the multiset of *current normalized-coordinate* records. Each complete record key is `(image, label, xmin, ymin, xmax, ymax)`. The code lowercases the label and rounds each coordinate to 5 decimal places. `T` multiplies the four current coordinates by 256 and rounds to 5 decimal places, but it does not change the source image or class label. The multiset difference `A \ominus B` retains `max(A(k)-B(k),0)` copies of each record key `k`, so `|·|` sums counts **including multiplicity**.

For a sample normalized coordinate `u=0.3344140625`, `T(u)=round(256×0.3344140625,5)=85.61000`. Apply `T` to *all four coordinate fields* before comparing full records.

**Small illustrative example:** Let historical records contain `R1`, `W1` and `R2` (each once), while current transformed records contain only `W1` and `R2`. Then `A_h \ominus T(A_c)` has one copy of `R1`, and the reverse difference is empty. This illustrates **missing=1, added=0**. If a record occurred twice historically but once currently, ordinary set subtraction would miss the discrepancy, whereas multiset subtraction reports 1.

**Reported historical targets:** BCDD previously had 2,340 records (2,237 RBC and 103 WBC), while the current CSV has 2,339 (2,236 RBC and 103 WBC). One historical RBC record is absent; there are zero additional current records under this source-pinned five-decimal matching rule. Same-coordinate opposite-class source-label pairs change from four to three. These record-level observations do **not** identify why a row was removed or which label is biologically correct.

Implementation: `pixel_record_key`, `csv_record_multiset` and `audit_bccd_and_bcdd_history`. Example Python:

```python
old = csv_record_multiset(historical_rows, normalized=False)
new = csv_record_multiset(current_rows, normalized=True)
missing = sum((old - new).values())
added   = sum((new - old).values())
```

**Methodological distinction:** record equivalence after scaling/rounding is not source-file byte identity and does not establish the historical conversion program.

### Equation (2): Positive-extent bounding-box criterion

$$
V(b)=
\mathbf{1}(x_{\max}>x_{\min})
\mathbf{1}(y_{\max}>y_{\min}).
\tag{2}
$$

For a box `b=(xmin,ymin,xmax,ymax)`, the indicator `1[condition]` is 1 when its predicate is true and 0 otherwise. Thus `V=1` only if both width and height are strictly positive under a **noninclusive** coordinate interpretation.

| Synthetic box | Width × height | Eq. (2) | Full validator `valid_box(...,640,480)` |
|---|---|---|---|
| `(2,3,10,12)` | 8×9 | 1 | True |
| `(4,4,4,4)` | 0×0 | 0 | False |
| `(8,5,8,15)` | 0×10 | 0 | False |
| `(-2,3,10,12)` | 12×9 | **1** | **False:** x out of image bounds |

**Crucial qualification:** Equation (2) is only the positive-extent component. The actual function `valid_box` also checks finite coordinates and image bounds: `0≤xmin<xmax≤width` and `0≤ymin<ymax≤height`. Passing Eq. (2) alone therefore does not guarantee passing the implemented validator.

An inclusive Pascal VOC convention can interpret equal endpoints as a one-pixel box. Therefore, zero extent **under the declared noninclusive rule** should be treated as a representation/consumer-compatibility flag, not necessarily a universally erroneous or biologically invalid label.

Source-pinned totals: BCCD passes **4,886/4,888** and has **2** flagged equal-endpoint boxes; current BCDD passes **2,339/2,339**. The combined 7,225/7,227 count belongs to the stated *implemented guard*, not a clinical correctness score.

### Equation (3): Direction-sensitive horizontal dHash and Hamming distance

$$
h_{r,c}^{(s)}(I)=
\mathbf{1}\!\left[
G_{r,c}(I)\;s\;G_{r,c+1}(I)
\right],
\qquad r,c\in\{1,\dots,8\},\ s\in\{>,<\},
$$

$$
D_H^{(s)}(A,B)=
\sum_{r=1}^{8}\sum_{c=1}^{8}
\mathbf{1}\!\left[h_{r,c}^{(s)}(A)\ne h_{r,c}^{(s)}(B)\right].
\tag{3}
$$

For each image `I`, the implementation converts to Pillow grayscale `L` and resizes with **LANCZOS to 9 columns × 8 rows** (i.e., **8 rows × 9 columns**). Each row contains eight adjacent horizontal comparisons, yielding 64 bits. Bit traversal is row-major, first bit at the most significant position.

- `s=">"` corresponds to strict left > right, implemented as `left_gt_right`.
- `s="<"` corresponds to strict left < right (equivalently right > left), implemented as `right_gt_left`.
- **Ties return 0 in both directions**. The two descriptors therefore need not be complements.
- `D_H` counts positions where corresponding bits disagree; it equals the popcount of the XOR of the two 64-bit hashes.

**Worked nine-pixel-row example (synthetic):** `[120,150,150,100,100,90,90,110,110]`.

| Adjacent pair | L>R bit | R>L bit |
|---|---:|---:|
| 120 / 150 | 0 | 1 |
| 150 / 150 | 0 | 0 — tie |
| 150 / 100 | 1 | 0 |
| 100 / 100 | 0 | 0 — tie |
| 100 / 90 | 1 | 0 |
| 90 / 90 | 0 | 0 — tie |
| 90 / 110 | 0 | 1 |
| 110 / 110 | 0 | 0 — tie |

Row descriptors: **00101000** (L>R) and **10000010** (R>L). Repeating this row eight times creates 64-bit descriptors and 32 ties.

For a separate *toy* eight-bit comparison, `10110010 XOR 10010111 = 00100101`, with popcount **3**. Actual source screening uses 64 bits and `(hash_a ^ hash_b).bit_count()`, not toy descriptors.

**Reported real-source pair:** BCCD `BloodImage_00037.jpg` (validation) and `BloodImage_00038.jpg` (training), from pinned commit `d272fb14cdff6e473fafeeeba32aba5f560e9e43`. Their reported Hamming distances are **3 bits** (left > right) and **1 bit** (right > left), both under the screening threshold `≤5`. The values are *distances for one pair*, not the number of candidate pairs. An 8×8 XOR grid indexes **descriptor bits**, not spatial locations on the full microscopy photos.

These values flag an **unadjudicated visual-similarity candidate**. They do not prove identical slides, patients, image files, biological labels, or any measured evaluation bias.

## Reproducible offline walkthrough — no third-party data

```bash
python -m pip install -r requirements.txt
python examples/equations_demo.py
python tests/test_equation_examples.py
python tests/test_source_synthetic.py
```

These commands use only synthetic records, boxes and grayscale pixels. To repeat the source audit, consult the pinned upstream source repositories and [opt-in Colab notebook](../notebooks/C01_SourcePinned_Audit_Colab.ipynb). New executions must record **observed** values separately from the [32 historical expected values](../manifests/historical_expected_32_NOT_OBSERVED.json). No original source images or annotations are distributed by this repository.

**Source references:** [frozen Python audit](../src/audit_sources_r2_frozen.py), [source-audit protocol](SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md), [BCCD upstream](https://github.com/Shenggan/BCCD_Dataset) (`d272fb14cdff6e473fafeeeba32aba5f560e9e43`), [BCDD upstream](https://github.com/draaslan/blood-cell-detection-dataset) (`c15d0652b3eefd97ac1b3347d83a7e5646dcb97a`).

*Prepared 2026-11-07 for researcher and reviewer education. The companion manuscript has not been declared clinically or scientifically submission-approved by this documentation.*
