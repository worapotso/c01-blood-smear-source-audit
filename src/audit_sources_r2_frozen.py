"""C01 paper-only educational source audit. No clinical validation or training.
Independent example reimplementation; NOT the historical production pipeline.
Original repositories are read only. Outputs contain aggregate numeric results only.
"""
from __future__ import annotations
import csv, hashlib, json, math, subprocess
from collections import Counter
from itertools import combinations
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

PINNED = {
    "BCCD": "d272fb14cdff6e473fafeeeba32aba5f560e9e43",
    "BCDD": "c15d0652b3eefd97ac1b3347d83a7e5646dcb97a",
}
EXPECTED = {
    "BCCD": {"images":364, "objects":4888, "valid":4886, "rbc":4155,"wbc":372,"platelets":361},
    "BCDD": {"images":100, "objects":2339, "valid":2339, "rbc":2236,"wbc":103,"platelets":0},
}
def git_revision(root: Path) -> str:
    return subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True,check=True).stdout.strip()

def verify_revision(root: Path, expected: str):
    actual=git_revision(root)
    if actual != expected:
        raise ValueError(f"Source revision mismatch: expected {expected}, received {actual}")
    return actual

def sha256_file(path: Path):
    sha=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1<<20), b""):
            sha.update(chunk)
    return sha.hexdigest()

def difference_hash(img: Image.Image) -> int:
    # Exactly follows source audit.py: 9x8 LANCZOS grayscale and left>right.
    pix=list(img.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    bits=0
    for y in range(8):
        for x in range(8):
            bits=(bits<<1)|int(pix[y*9+x]>pix[y*9+x+1])
    return bits

def valid_box(x1,y1,x2,y2,w,h):
    vals=(x1,y1,x2,y2)
    return (all(math.isfinite(v) for v in vals) and
            0<=x1<x2<=w and 0<=y1<y2<=h)

def examine_images(files, want_hash=False):
    modes=Counter()
    alpha_opaque=0
    hashes={}
    bad=[]
    for p in files:
        try:
            with Image.open(p) as img:
                img.load()
                modes[img.mode]+=1
                if img.mode=="RGBA" and img.getchannel("A").getextrema()==(255,255):
                    alpha_opaque+=1
                if want_hash:hashes[p.name]=sha256_file(p)
        except Exception as e:
            bad.append({"filename":p.name,"issue_type":type(e).__name__})
    return {"count":len(files),"decoded":len(files)-len(bad),
            "modes":dict(modes),"opaque_rgba":alpha_opaque,
            "sha256":hashes,"decode_failures":bad}

def audit_bccd(repo: Path):
    images=sorted((repo/"BCCD"/"JPEGImages").glob("*.jpg"))
    xmlfiles=sorted((repo/"BCCD"/"Annotations").glob("*.xml"))
    image_names={p.stem for p in images}
    count=Counter();valid=0;degenerate=[];objects=0
    size={"width":640,"height":480}
    for f in xmlfiles:
        doc=ET.parse(f).getroot()
        if f.stem not in image_names:
            raise ValueError("Unexpected orphan XML "+f.name)
        for o in doc.findall("object"):
            b=o.find("bndbox")
            if b is None:raise ValueError("Missing bounding box in "+f.name)
            raw=(o.findtext("name") or "").strip().lower()
            lab="platelets" if raw in ("platelet","platelets") else raw
            count[lab]+=1;objects+=1
            vals=[float(b.findtext(k)) for k in ("xmin","ymin","xmax","ymax")]
            if valid_box(*vals,size["width"],size["height"]):valid+=1
            else:degenerate.append({"file":f.name,"label":lab,"coordinates":vals})
    info=examine_images(images)
    return {"source":"BCCD","annotation_containers":len(xmlfiles),"records":objects,
            "valid_boxes":valid,"invalid_boxes":objects-valid,
            "labels":dict(count),"image":info,"degenerate_records":degenerate}

def audit_bcdd(repo: Path):
    images=sorted((repo/"images").glob("*.png"))
    found={p.name for p in images}
    count=Counter();valid=0;records=0
    with (repo/"annotations.csv").open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        for row in reader:
            records+=1
            name=Path(row["image"]).name
            if name not in found: raise ValueError("Source image missing: "+name)
            lab=(row["label"] or "").strip().lower()
            count[lab]+=1
            coords=[float(row[k]) for k in ("xmin","ymin","xmax","ymax")]
            # Original BCDD CSV is normalized to [0,1].
            if valid_box(coords[0]*256,coords[1]*256,coords[2]*256,coords[3]*256,256,256):
                valid+=1
    info=examine_images(images)
    return {"source":"BCDD","annotation_containers":1,"records":records,
            "valid_boxes":valid,"invalid_boxes":records-valid,
            "labels":dict(count),"image":info}

def screen_candidate_pairs(paths,threshold=5):
    """Heuristic candidates only. Do not assert duplicate biological origin."""
    digests=[]
    for p in paths:
        with Image.open(p) as img:digests.append((p.name,difference_hash(img)))
    flags=[]
    for (a,h1),(b,h2) in combinations(digests,2):
        dist=(h1^h2).bit_count()
        if dist<=threshold:flags.append({"left":a,"right":b,"dhash_distance":dist,
                                         "status":"UNADJUDICATED"})
    return sorted(flags,key=lambda x:(x["dhash_distance"],x["left"],x["right"]))

def run_local_read_only(bccd_root: Path,bcdd_root: Path,hashes=False,candidates=False):
    bccd_root=Path(bccd_root);bcdd_root=Path(bcdd_root)
    revisions={"BCCD":verify_revision(bccd_root,PINNED["BCCD"]),
               "BCDD":verify_revision(bcdd_root,PINNED["BCDD"])}
    bccd=audit_bccd(bccd_root);bcdd=audit_bcdd(bcdd_root)
    result={"code_status":"INDEPENDENT_DEMONSTRATOR_NOT_HISTORICAL_RUN",
            "revisions":revisions,"datasets":{"BCCD":bccd,"BCDD":bcdd}}
    if hashes:
        files=list((bccd_root/"BCCD"/"JPEGImages").glob("*.jpg"))+list((bcdd_root/"images").glob("*.png"))
        digests=[sha256_file(p) for p in files]
        digest_counts=Counter(digests)
        result["exact_duplicate_pairs"]=sum(n*(n-1)//2 for n in digest_counts.values())
    if candidates:
        images=sorted((bccd_root/"BCCD"/"JPEGImages").glob("*.jpg"))
        result["candidate_screening_BCCD"]=screen_candidate_pairs(images,threshold=5)
    return result

def compare_to_historical(result):
    """Descriptive result comparison, NOT proof of independent provenance equivalence."""
    tests={}
    for key in ("BCCD","BCDD"):
        x=result["datasets"][key];e=EXPECTED[key]
        tests[key]={"images":x["image"]["count"]==e["images"],
                    "records":x["records"]==e["objects"],
                    "geometry":x["valid_boxes"]==e["valid"],
                    "RBC":x["labels"].get("rbc",0)==e["rbc"],
                    "WBC":x["labels"].get("wbc",0)==e["wbc"],
                    "platelets":x["labels"].get("platelets",0)==e["platelets"]}
    return tests


# ==== S12B-R1 controlled extension: source history, alternative streams, and E1/E2/E3 ====
# Base functions above are copies of the 2026-11-01 candidate (untouched).
# No downloader, source mutation, training or public upload is implemented here.
import io
from collections import defaultdict

HISTORICAL_REVISIONS = {
    "2020_pixel_CSV": "4635fd9",
    "2022_pre_normalization_CSV": "9280ce8",
    "2023_ratio_CSV": "721d642",
}
def historical_guard(repo):
    receipts = {}
    for key, commit in HISTORICAL_REVISIONS.items():
        try:
            p = subprocess.run(["git","-C",str(repo),"rev-parse","--verify",commit+"^{commit}"],
                               capture_output=True,text=True,check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("FAIL_CLOSED_MISSING_HISTORICAL_COMMIT: "+commit+
                               " ; use a full-history authorized source clone") from exc
        receipts[key] = p.stdout.strip()
    return receipts

def source_csv_at_commit(repo, revision):
    p = subprocess.run(["git","-C",str(repo),"show",revision+":annotations.csv"],
                       capture_output=True,check=True)
    return list(csv.DictReader(io.StringIO(p.stdout.decode("utf-8-sig"))))

def pixel_record_key(image, cls, coords):
    # Explicit five-decimal pixel-space equivalence; not exact byte identity.
    return (str(image),str(cls).lower(),*[round(float(v),5) for v in coords])

def csv_record_multiset(rows, normalized):
    m = 256.0 if normalized else 1.0
    return Counter(pixel_record_key(r["image"],r["label"],
                  [float(r[k])*m for k in ("xmin","ymin","xmax","ymax")]) for r in rows)

def kitti_record_multiset(repo):
    out=Counter()
    files=sorted((Path(repo)/"labels").glob("*.txt"))
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            x=line.split()
            if len(x)<8:raise ValueError("Short KITTI line in "+f.name)
            out[pixel_record_key(f.stem+".png",x[0],x[4:8])]+=1
    return out,len(files)

def class_counts(multiset):
    out=Counter()
    for key,n in multiset.items():out[key[1]]+=n
    return dict(out)

def cross_class_same_box_count(multiset):
    groups=defaultdict(set)
    for key,n in multiset.items():
        if n:groups[(key[0],*key[2:])].add(key[1])
    return sum({"rbc","wbc"}.issubset(classes) for classes in groups.values())

def check_bccd_test_csv(repo):
    root=Path(repo)
    xs=Counter()
    for f in sorted((root/"BCCD/Annotations").glob("*.xml")):
        doc=ET.parse(f).getroot()
        for obj in doc.findall("object"):
            b=obj.find("bndbox")
            label=(obj.findtext("name") or "").strip().lower()
            label="platelets" if label in ("platelet","platelets") else label
            coords=[b.findtext(k) for k in ("xmin","ymin","xmax","ymax")]
            xs[pixel_record_key(f.stem+".jpg",label,coords)]+=1
    with (root/"test.csv").open(encoding="utf-8-sig",newline="") as f:
        test=list(csv.DictReader(f))
    ts=Counter(pixel_record_key(r["filename"],
               "platelets" if r["cell_type"].lower() in ("platelet","platelets") else r["cell_type"],
               [r[k] for k in ("xmin","ymin","xmax","ymax")]) for r in test)
    return {"source_rows":sum(ts.values()),"xml_objects":sum(xs.values()),
            "record_multisets_equal":ts==xs}

def audit_bccd_and_bcdd_history(bccd_repo,bcdd_repo):
    archived=historical_guard(bcdd_repo)
    before2020=csv_record_multiset(source_csv_at_commit(bcdd_repo,"4635fd9"),False)
    before2022=csv_record_multiset(source_csv_at_commit(bcdd_repo,"9280ce8"),False)
    normalized2023=csv_record_multiset(source_csv_at_commit(bcdd_repo,"721d642"),True)
    current=csv_record_multiset(list(csv.DictReader(
        (Path(bcdd_repo)/"annotations.csv").open(encoding="utf-8-sig",newline=""))),True)
    kitti,nlabels=kitti_record_multiset(bcdd_repo)
    missing=list((before2022-normalized2023).elements())
    added=sum((normalized2023-before2022).values())
    modes=_image_channels_contract(bcdd_repo)
    return {
      "historical_git_commits":archived,
      "bccd_duplicate_test_csv":check_bccd_test_csv(bccd_repo),
      "2020_pixel_csv": {"records":sum(before2020.values()),"class_counts":class_counts(before2020),
                         "opposite_class_same_box_pairs":cross_class_same_box_count(before2020)},
      "2022_pixel_csv_records":sum(before2022.values()),
      "2022_equal_to_2020":before2022==before2020,
      "2023_normalized_csv_records":sum(normalized2023.values()),
      "2023_normalized_equal_to_pinned_current":normalized2023==current,
      "current_csv": {"records":sum(current.values()),"class_counts":class_counts(current),
                      "opposite_class_same_box_pairs":cross_class_same_box_count(current)},
      "kitti": {"files":nlabels,"records":sum(kitti.values()),
                "class_counts":class_counts(kitti),
                "equivalent_to_2020_pixel_csv_5dp":kitti==before2020,
                "opposite_class_same_box_pairs":cross_class_same_box_count(kitti)},
      "record_difference": {"historical_missing_in_2023":len(missing),
                            "2023_new_entries":added,
                            "only_missing_image_name":missing[0][0] if len(missing)==1 else None},
      "bcdd_strict_consumer":modes}

def _image_channels_contract(bcdd_repo):
    images=sorted((Path(bcdd_repo)/"images").glob("*.png"))
    original3,converted3,opaque=0,0,0
    for path in images:
        with Image.open(path) as im:
            im.load()
            original3+=int(len(im.getbands())==3)
            converted3+=int(len(im.convert("RGB").getbands())==3)
            opaque+=int(im.mode=="RGBA" and im.getchannel("A").getextrema()==(255,255))
    return {"files":len(images),"native_exact_3_channels":original3,
            "after_explicit_rgb_conversion":converted3,"fully_opaque_rgba":opaque}

def dhash_strict(img,direction):
    if direction not in ("left_gt_right","right_gt_left"):
        raise ValueError("Unrecognized strict comparator")
    pix=list(img.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    h=0;ties=0
    for row in range(8):
        for col in range(8):
            left,right=pix[row*9+col],pix[row*9+col+1]
            ties+=int(left==right)
            bit=left>right if direction=="left_gt_right" else right>left
            h=(h<<1)|int(bit)
    return h,ties

def pairwise_screen(bccd_repo,bcdd_repo, enabled=False):
    images=sorted((Path(bccd_repo)/"BCCD/JPEGImages").glob("*.jpg"))+sorted(
              (Path(bcdd_repo)/"images").glob("*.png"))
    n=len(images);digests=Counter(sha256_file(f) for f in images)
    result={"images":n,"unordered_pairs":n*(n-1)//2,
            "exact_sha256_duplicate_pairs":sum(c*(c-1)//2 for c in digests.values()),
            "dhash_status":"NOT_TESTED"}
    if not enabled:return result
    pairs=[]
    for f in images:
        with Image.open(f) as im:
            pairs.append((f.name,dhash_strict(im,"left_gt_right"),
                          dhash_strict(im,"right_gt_left")))
    hist={d:Counter() for d in ("left_gt_right","right_gt_left")}
    check_pair={}
    for a,b in combinations(pairs,2):
        left_dist=(a[1][0]^b[1][0]).bit_count()
        right_dist=(a[2][0]^b[2][0]).bit_count()
        hist["left_gt_right"][left_dist]+=1
        hist["right_gt_left"][right_dist]+=1
        if {a[0],b[0]}=={"BloodImage_00037.jpg","BloodImage_00038.jpg"}:
            check_pair={"images":["BloodImage_00037.jpg","BloodImage_00038.jpg"],
                        "left_gt_right":left_dist,"right_gt_left":right_dist,
                        "ties_each":[a[1][1],b[1][1]]}
    result.update({"dhash_status":"COMPUTED",
        "candidate_pairs_le5":{direction:sum(hist[direction][i] for i in range(6))
                               for direction in hist},
        "threshold_sweep_0_to_8":{direction:[sum(hist[direction][j] for j in range(i+1))
                                            for i in range(9)] for direction in hist},
        "check_pair":check_pair,
        "method":"grayscale Pillow LANCZOS 9x8, row-major MSB, strict directions, ties=0"})
    return result

def run_r1(bccd_repo,bcdd_repo,run_pairwise=False):
    revisions={"BCCD":verify_revision(Path(bccd_repo),PINNED["BCCD"]),
               "BCDD":verify_revision(Path(bcdd_repo),PINNED["BCDD"])}
    # Guard full historical availability before touching audit calculations.
    hist=historical_guard(bcdd_repo)
    bccd=audit_bccd(Path(bccd_repo));bcdd=audit_bcdd(Path(bcdd_repo))
    history=audit_bccd_and_bcdd_history(bccd_repo,bcdd_repo)
    similarity=pairwise_screen(bccd_repo,bcdd_repo,enabled=run_pairwise)
    return {"run_status":"OBSERVED_IN_THIS_RUNTIME_NO_HISTORICAL_RESULT_SUBSTITUTION",
            "code_role":"INDEPENDENT_SOURCE_REIMPLEMENTATION_NOT_PRODUCTION",
            "revisions":revisions,"historical_commits":hist,
            "primary":{"BCCD":bccd,"BCDD":bcdd},"history_and_alternates":history,
            "similarity":similarity,
            "E3_not_established":["biological_class_truth","patient_slide_identity",
                                  "trained_model_accuracy_or_leakage_effect"]}

def expected_comparison(report,expected):
    """Explicit PASS/MISMATCH/NOT_TESTED. Never overwrite observed data."""
    checks=[]
    for item in expected["claims"]:
        val=report
        try:
            for k in item["observed_path"]:val=val[k]
        except (KeyError,IndexError,TypeError):
            checks.append({"id":item["id"],"status":"NOT_TESTED","expected":item["expected"]})
            continue
        checks.append({"id":item["id"],"evidence_tier":item["tier"],
                       "expected":item["expected"],"observed":val,
                       "status":"PASS" if val==item["expected"] else "MISMATCH"})
    return checks

