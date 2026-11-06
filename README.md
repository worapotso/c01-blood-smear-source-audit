# C-01 Blood-Smear Source Integrity Audit

**Status: Public research-code repository.** The manuscript is under preparation for Ubi-Media 2027. This independent source-audit implementation is not an original production-pipeline replay. Historical expected values are not results from a new notebook execution.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/worapotso/c01-blood-smear-source-audit/blob/main/notebooks/C01_SourcePinned_Audit_Colab.ipynb)

Repository: https://github.com/worapotso/c01-blood-smear-source-audit .
This independently authored, read-only source audit accompanies the research
manuscript **Tracing Data Integrity and Interoperability Across Public Blood-Smear
Image Repositories: A Cross-Format Case Study** (under manuscript review; not yet
an accepted or published conference paper).

## Scope and files
- \`src/audit_sources_r2_frozen.py\`: frozen Python implementation of the independent
  source/annotation audit; **not** the original M3 production workflow.
- \`notebooks/C01_SourcePinned_Audit_Colab.ipynb\`: Colab notebook with source-acquisition
  and pairwise-screening switches **OFF by default** and no execution outputs.
- \`tests/test_source_synthetic.py\`: no-dataset, offline synthetic tests.
- \`manifests/historical_expected_32_NOT_OBSERVED.json\`: 32 reference measurements
  from archived evidence, **not actual observations from this notebook**.
- \`docs/\`: source revisions, scientific evidence limits, original-data rights and protocol.

## Data (third-party; not redistributed)
- BCCD: https://github.com/Shenggan/BCCD_Dataset
  at \`d272fb14cdff6e473fafeeeba32aba5f560e9e43\`
- BCDD: https://github.com/draaslan/blood-cell-detection-dataset
  at \`c15d0652b3eefd97ac1b3347d83a7e5646dcb97a\`.
  Historical BCDD objects are \`4635fd9\`, \`9280ce8\`, and \`721d642\`.
Fetch data from original repositories under their own terms. We do not publish
their photographs, annotations, patient/source metadata, or dataset clones here.

## Getting started
1. With Python 3.11+ and an isolated environment, install \`pip install -r requirements.txt\`.
2. Run synthetic-only checks: \`python tests/test_source_synthetic.py\`.
3. To reproduce source-audit measurements, open
   \`notebooks/C01_SourcePinned_Audit_Colab.ipynb\` in Google Colab from a copy of this
   repository. Carefully inspect network and code cells, then explicitly opt in to
   external source access and the audit flags.
4. Record actual pinned source SHA/git revisions, Python/Pillow versions and all
   32 PASS/MISMATCH/NOT_TESTED statuses. No automatic upload of source images or raw
   annotations is intended.
5. Verify the linked Git commit and use the Open in Colab badge above. The
   code and expected values alone are not a historical Windows/Colab receipt.

## Evidence boundaries
The earlier G3 independent Windows/Colab audit is separately archived. A fresh
public notebook run is not automatically equivalent to that historical execution.
dHash yields an *unverified visual similarity candidate*, not proven specimen
identity or model-data leakage; conflicting RBC/WBC annotations are source-label
inconsistencies, not adjudicated biological truth. M3 and M4 are out of scope.

## License and citation
Code and this candidate notebook are prepared under the **MIT License** (see
\`LICENSE\`). The software copyright attribution and institutional release authority
must be respected by downstream users. Open-source permission applies to the independently authored code only, not to images or annotations from the source repositories. This license **does not require
academic paper citation as a legal condition**; however, scientific attribution
is requested. Use GitHub's **Cite this repository** button backed by
\`CITATION.cff\`. Once the manuscript is accepted, add its accurate proceedings
metadata and DOI to \`CITATION.cff\` without inventing publication details.

If the paper is relevant to your work, please cite:
W. Sommool and coauthors, *Tracing Data Integrity and Interoperability Across
Public Blood-Smear Image Repositories: A Cross-Format Case Study*,
manuscript under preparation for Ubi-Media 2027 (publication metadata pending).

Please also cite the upstream dataset creators and follow their licenses.
