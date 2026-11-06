# Supplementary Protocol S1 — S12B-R1 source-audit preparation revision

## Purpose and authority
Controlled, separately authored, read-only **paper-only** demonstration of the existing scientific claims in S16R4D. It does NOT reproduce the original protected M3 pipeline byte-for-byte; existing S01 repeatability and actual future Colab outputs remain distinct provenance layers.

## Inputs and versions
- BCCD: `https://github.com/Shenggan/BCCD_Dataset` at full commit `d272fb14cdff6e473fafeeeba32aba5f560e9e43`. Pascal VOC XML and 364 original JPEGs (640×480); `test.csv` is an alternate representation of the 4,888 XML objects.
- BCDD: `https://github.com/draaslan/blood-cell-detection-dataset` at `c15d0652b3eefd97ac1b3347d83a7e5646dcb97a`. 100 original PNG files (256×256), current 2,339 normalized CSV records, 100 KITTI label files. Historical git objects `4635fd9`, `9280ce8`, `721d642` needed for original pixel CSV, unchanged pre-normalized state and normalized conversion.
- **No conversion pipeline from historical CSV to KITTI is inferred from matching values.** Equivalence is conditional on specified 5-decimal pixel-space record comparison.

## Calculations
- BCCD source VOC count, label types and box width/height under declared *noninclusive detector criterion*: finite, `xmax>xmin`, `ymax>ymin`, within [0,width]/[0,height]. Two equal-endpoint objects are source points; inclusive VOC conventions can treat them as one pixel. Do not call all universally invalid.
- BCDD current normalized coordinates are multiplied by 256 to reconstruct pixel-space; compare source fields at 5 decimal places to historical pixel CSV and KITTI, **never** combine parallel annotation streams into one denominator.
- Record-level class conflict: group by image name and exact matched source coordinates and flag both `rbc` and `wbc` within the group. Four pairs in original CSV/KITTI and three in latest CSV are source-level inconsistencies, not expert-confirmed cell-class errors.
- RGB consumer guard: Pillow image native band count versus exactly-three-channel requirement and after explicit `convert('RGB')`; README says *contains RGB channels*, not exactly three encoded bands.
- Exact image-byte SHA-256: one pass over the 464 source image files, **107,416** unordered image pairs. Perceptual screening is opt-in: convert to grayscale, 9×8 LANCZOS; compute two strict horizontal predicates (L>R, R>L) with tie=0; row-major bits and top-left MSB; report descriptive thresholds 0–8 and BCCD 00037/00038 distances. A candidate is not patient/slide identity.
- Optional auxiliary inventory includes BCCD `test.csv` equivalence; no TFRecord semantic equality or CRC validation claimed by R1.

## Evidence levels
- **E1 direct source:** committed record totals, class fields, source-history versions, format content and image mode under specified decoder.
- **E2 implementation-conditioned:** positive span rule, consumer exactly-three bands, two dHash hash directions/screening, possible split similarity.
- **E3 not established:** biological labels, slide/patient origin, veterinary clinical relevance, performance inflation, independent full original-pipeline parity.

## Expected vs actual
`S12B_R1_EXPECTED_CLAIM_MATRIX.json` is a historical evidence target with 32 independently named claims and no observed R1 data. Only an executed independent Colab environment may produce observed results. Comparator must report `PASS/MISMATCH/NOT_TESTED` individually; never silently convert failures to a pass. If dHash optional screening is disabled, its two expected distances are `NOT_TESTED`.

## Reproducibility limitations
The demonstration is independently authored, not an archived original M3 execution. Standalone Colab runs with external source clone are subject to PI authorization, dependency/network availability, rights and original source-byte availability. Actual run notebook, Python/Pillow/git versions, source commit receipts, environment, safe JSON, actual comparison output and SHA256 are required after G3. No new run or GitHub action occurs in R1 preparation.
