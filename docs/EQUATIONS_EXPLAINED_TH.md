# คู่มือสมการ (1)–(3): C-01 Blood-Smear Source Integrity Audit

> **สถานะ:** คำอธิบายประกอบเชิงการศึกษา (*companion documentation*) สำหรับงานวิจัย C-01 ฉบับเตรียมเผยแพร่ ไม่ใช่ผลทดลองใหม่ ไม่ใช่คำแนะนำทางคลินิก และไม่ใช่การรัน original production pipeline ซ้ำ
> **อ้างอิงโค้ด:** [`src/audit_sources_r2_frozen.py`](../src/audit_sources_r2_frozen.py) และ [`docs/SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md`](SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md)
> **ภาษาอังกฤษ:** [English companion](EQUATIONS_EXPLAINED_EN.md)
> **สาธิตโดยไม่ใช้ dataset:** [`examples/equations_demo.py`](../examples/equations_demo.py) (ใช้ข้อมูลสมมติเท่านั้น)

## ภาพรวมและขอบเขตหลักฐาน

| สมการ | คำถามที่ต้องการตอบ | สิ่งที่ตรวจวัด | สิ่งที่ *ไม่ได้* พิสูจน์ |
|---|---|---|---|
| (1) Annotation reconciliation | Annotation records ข้าม source revisions ต่างกันอย่างไร | Multiset difference ระหว่าง BCDD historical กับ current | เหตุผลที่ผู้สร้างข้อมูลลบรายการหรือ biological truth |
| (2) Bounding-box criterion | Bounding box มีพื้นที่แบบ positive extent หรือไม่ | `xmax > xmin` และ `ymax > ymin` | ว่า annotation ถูกต้องทางชีววิทยาหรือผิดตาม VOC ทุก convention |
| (3) Directional dHash | ภาพสองภาพมี descriptor คล้ายกันเพียงใด | 64-bit binary descriptor และ Hamming distance | ว่าภาพเป็น specimen/patient เดียวกัน หรือมี model leakage |

**ค่าที่พบในงานวิจัยเดิม (historical, source-pinned):** BCCD 364 ภาพ JPEG / 4,888 VOC objects; BCDD 100 ภาพ PNG / 2,339 current CSV records; รวม 464 ภาพ / 7,227 primary records. ค่าที่ปรากฏใน [expected-value manifest](../manifests/historical_expected_32_NOT_OBSERVED.json) เป็น **historical expected targets** ไม่ใช่หลักฐานว่าผู้ใช้ GitHub รัน notebook แล้วได้ผลเดียวกัน

## 1. Equation (1): Reconciliation ของ BCDD annotation ข้าม revisions

### 1.1 รูปสมการ

$$
\begin{aligned}
T(u) &= \operatorname{round}(256u,5),\\
\left|A_{\mathrm h}\ominus T(A_{\mathrm c})\right| &= 1,\\
\left|T(A_{\mathrm c})\ominus A_{\mathrm h}\right| &= 0.
\end{aligned} \tag{1}
$$

- `A_h` คือ **multiset** ของ *complete annotation records* จาก historical pixel-coordinate CSV; `A_c` คือ multiset ของ current normalized-coordinate CSV
- Annotation record หนึ่งรายการประกอบด้วย `(image, class, xmin, ymin, xmax, ymax)`; class label ถูกแปลงเป็น lower case และพิกัดทั้งสี่ถูกปัดทศนิยม 5 ตำแหน่ง
- `T` แปลง **เฉพาะพิกัดสี่ช่อง** ของ current records โดยคูณ 256 แล้ว `round(..., 5)` ไม่เปลี่ยนชื่อภาพหรือ class
- `\ominus` หมายถึง **multiset subtraction** ซึ่งนับ multiplicity ของ record เหมือนกัน; สำหรับ record `k` นิยาม `(A \ominus B)(k)=\max(A(k)-B(k),0)`
- `|A|` ในบริบทนี้คือ **ผลรวม multiplicity** ของรายการ ไม่ใช่จำนวนชนิดของ keys ที่ไม่ซ้ำ
- ค่าสองบรรทัดหลังหมายถึง historical มีหนึ่ง record ที่ไม่อยู่ใน current และ current ไม่มี record ใหม่เพิ่มกลับมาเมื่อเทียบกับ historical ใน precision ที่ระบุ

> **หมายเหตุด้าน precision:** การแปลงแล้วปัด 5 decimal places เป็นวิธีเปรียบเทียบ *record equivalence* ที่กำหนดไว้ล่วงหน้า ไม่ใช่การพิสูจน์ว่าไฟล์ต้นฉบับเหมือนกันในระดับ bytes หรือที่มาของ conversion pipeline เหมือนกัน

### 1.2 ตัวอย่างคำนวณพิกัดหนึ่งค่า (สมมติแต่สอดคล้องกับสูตร)

หาก `u = 0.3344140625` (normalized coordinate):

$$
T(u)=\operatorname{round}(256\times0.3344140625,5)=85.61000.
$$

ต้องทำขั้นตอนเดียวกันกับ `xmin, ymin, xmax, ymax` ทุกค่า ก่อนสร้าง record key แล้วเปรียบเทียบ multisets

### 1.3 ตัวอย่าง multiset สั้น ๆ (ข้อมูลสมมติ ไม่ใช่ผล dataset)

กำหนด record แบบย่อสามรายการ คือ `R1` = (image-1.png, rbc, *box-A*), `W1` = (image-1.png, wbc, *box-A*) และ `R2` = (image-2.png, rbc, *box-B*)

| Dataset | R1 | W1 | R2 | จำนวนรวม |
|---|---:|---:|---:|---:|
| Historical `A_h` | 1 | 1 | 1 | 3 |
| Current หลังแปลง `T(A_c)` | 0 | 1 | 1 | 2 |
| `A_h \ominus T(A_c)` | 1 | 0 | 0 | **1** |
| `T(A_c) \ominus A_h` | 0 | 0 | 0 | **0** |

**ผล:** record `R1` หายไปหนึ่งรายการ แต่การปรากฏพร้อมกันของ label `rbc` กับ `wbc` สำหรับ box เดียวกันนั้นเป็น **source-label inconsistency**; เราไม่สามารถบอกว่า label ใดเป็นเซลล์ประเภทที่ถูกต้องจากสมการนี้

**ทำไมต้อง multiset?** หาก historical มี record เดียวกัน 2 ครั้ง แต่ current มี 1 ครั้ง การลบแบบ set ปกติจะมองว่ารายการยังอยู่และมองข้าม multiplicity แต่ multiset subtraction จะพบ missing count เท่ากับ 1

### 1.4 การเชื่อมกับโค้ดจริงและผลในบทความ

โค้ดจริงใช้ `csv_record_multiset(rows, normalized)` สร้าง `collections.Counter` ของ record keys และใช้การลบสองทิศทางภายใน `audit_bccd_and_bcdd_history`:

```python
historical = csv_record_multiset(historical_rows, normalized=False)
current = csv_record_multiset(current_rows, normalized=True)
missing = historical - current       # records absent from current
added = current - historical         # records newly present in current
missing_count = sum(missing.values())
added_count = sum(added.values())
```

ผล source-pinned ที่รายงาน: historical BCDD **2,340** records (2,237 RBC / 103 WBC) เทียบ current **2,339** records (2,236 RBC / 103 WBC), missing **1 RBC**, added **0**; จำนวน opposite-class same-coordinate pairs จาก **4** เหลือ **3** ตามวิธีนับใน code. ตัวเลขนี้ไม่ยืนยันเหตุผลการเปลี่ยนแปลงหรือความถูกต้องของ cell class

## 2. Equation (2): Geometry criterion สำหรับ bounding boxes

### 2.1 รูปสมการ

$$
V(b)=\mathbf{1}(x_{\max}>x_{\min})\,\mathbf{1}(y_{\max}>y_{\min}).
\tag{2}
$$

โดย `b=(xmin,ymin,xmax,ymax)` และ `\mathbf{1}(condition)` คือ indicator ที่มีค่า **1 ถ้าเงื่อนไขเป็นจริง** มิฉะนั้น **0**

สมการจะให้ `V(b)=1` ก็ต่อเมื่อ **ความกว้างมากกว่า 0 และความสูงมากกว่า 0** ภายใต้เกณฑ์ *non-inclusive positive extent* ที่ระบุในบทความ

### 2.2 ตัวอย่างคำนวณ

| พิกัดตัวอย่าง (xmin, ymin, xmax, ymax) | ความกว้าง | ความสูง | `V(b)` | ความหมาย |
|---|---:|---:|---:|---|
| `(2, 3, 10, 12)` | 8 | 9 | **1** | ผ่าน positive extent |
| `(4, 4, 4, 4)` | 0 | 0 | **0** | zero-width / zero-height |
| `(8, 5, 8, 15)` | 0 | 10 | **0** | zero-width |
| `(-2, 3, 10, 12)` | 12 | 9 | **1** | ผ่าน *เฉพาะ* Eq. (2), แต่พิกัดออกนอกภาพ |

**ข้อควรระวังสำคัญ:** ฟังก์ชันโค้ด `valid_box(x1,y1,x2,y2,w,h)` มีเงื่อนไข **มากกว่าสมการ (2)** ได้แก่ทุกพิกัดเป็น finite number และ `0 ≤ xmin < xmax ≤ width` กับ `0 ≤ ymin < ymax ≤ height` ดังนั้น Eq. (2) เป็นเพียง **positive-extent subcriterion**, ไม่ใช่คำจำกัดความครบทุกเงื่อนไขของฟังก์ชัน `valid_box`

### 2.3 Inclusive VOC convention กับการตีความ

สำหรับ coordinate convention ที่ถือ endpoints **inclusive** พิกัด `xmin=xmax` อาจแทนพื้นที่ 1 pixel ได้ ไม่ใช่ annotation ที่ผิดแน่นอน ในทางตรงกันข้าม ภายใต้ non-inclusive positive extent จะมี width = 0 และไม่ผ่าน Eq. (2)

ผล source-pinned: BCCD **4,886 / 4,888** records ผ่าน implemented geometry guard และ **2** source boxes ไม่ผ่านเพราะ zero extent; BCDD current **2,339 / 2,339** records ผ่าน; รวม **7,225 / 7,227** records ผ่านเกณฑ์ที่ประกาศ โดยไม่ตัดสิน biological correctness

```python
valid_box(2, 3, 10, 12, 640, 480)    # True
valid_box(4, 4, 4, 4, 640, 480)      # False
valid_box(-2, 3, 10, 12, 640, 480)   # False: out of bounds
```

## 3. Equation (3): Horizontal dHash แบบสองทิศทาง และ Hamming distance

### 3.1 การสร้าง descriptor จากภาพ

สำหรับภาพ `I`, โค้ดทำตามลำดับ:

1. เปิดภาพและแปลงเป็น grayscale ด้วย Pillow `convert("L")`
2. ย่อภาพด้วย `resize((9,8), Image.Resampling.LANCZOS)` ให้ได้ **8 rows × 9 columns**
3. ในแต่ละแถวเปรียบเทียบ pixels ข้างกัน 8 คู่ ได้ **8 × 8 = 64 bits** เรียง row-major; บิตแรกอยู่ตำแหน่ง most significant bit (MSB)
4. ใช้ comparator สองแบบ ได้แก่ `s = L>R` (pixel ซ้าย > pixel ขวา) หรือ `s = R>L` (pixel ขวา > pixel ซ้าย ซึ่งเท่ากับซ้าย < ขวา)
5. หากค่าพิกเซล **เท่ากัน** ทั้งสองกฎให้บิต **0** ดังนั้น descriptor สองทิศทาง *ไม่จำเป็นต้องเป็น bitwise complement* โดยเฉพาะตำแหน่ง ties

### 3.2 รูปสมการ

$$
h_{r,c}^{(s)}(I)=
\mathbf{1}\!\left[G_{r,c}(I)\;s\;G_{r,c+1}(I)\right],
\quad r,c\in\{1,\dots,8\},\quad s\in\{>,<\}.
$$

$$
D_H^{(s)}(A,B)=
\sum_{r=1}^{8}\sum_{c=1}^{8}
\mathbf{1}\!\left[h_{r,c}^{(s)}(A)\neq h_{r,c}^{(s)}(B)\right].
\tag{3}
$$

- `G` คือค่าความเข้ม grayscale ขนาด 8 × 9 ที่ resize แล้ว
- `h` คือ binary comparison ที่ตำแหน่ง (row, column)
- `D_H` คือจำนวนตำแหน่งบิตที่ต่างกันระหว่าง descriptor สองภาพในกฎเปรียบเทียบเดียวกัน; ช่วงค่า 0–64
- เกณฑ์ในงานนี้ใช้ `D_H ≤ 5` เพื่อ **คัดกรอง candidate** เท่านั้น ไม่ใช่เกณฑ์ยืนยัน biological identity

### 3.3 ตัวอย่างหนึ่งแถว (ข้อมูลสมมติ)

สมมติ grayscale pixels **9 ค่า** ในหนึ่งแถวเป็น:

`[120, 150, 150, 100, 100, 90, 90, 110, 110]`

เปรียบเทียบ 8 คู่จากซ้ายไปขวา:

| คู่ตำแหน่ง | ค่าซ้าย | ค่าขวา | L>R | R>L |
|---|---:|---:|---:|---:|
| 1 | 120 | 150 | 0 | 1 |
| 2 | 150 | 150 | 0 | 0 (tie) |
| 3 | 150 | 100 | 1 | 0 |
| 4 | 100 | 100 | 0 | 0 (tie) |
| 5 | 100 | 90 | 1 | 0 |
| 6 | 90 | 90 | 0 | 0 (tie) |
| 7 | 90 | 110 | 0 | 1 |
| 8 | 110 | 110 | 0 | 0 (tie) |

จึงได้ descriptor แถวนี้เป็น `00101000` สำหรับ L>R และ `10000010` สำหรับ R>L หากทั้ง 8 แถวมีค่าเหมือนกันจะได้ 64-bit descriptor ที่เป็นสตริง 8 บิตดังกล่าวซ้ำ 8 รอบ และมี **32 ties** ในแต่ละทิศทาง

### 3.4 ตัวอย่าง Hamming distance (8-bit toy example)

กำหนด descriptor สมมติ `A = 10110010`, `B = 10010111`:

```text
A          10110010
B          10010111
A XOR B    00100101
bit count         3
```

จึงได้ Hamming distance = **3** ในตัวอย่าง 8-bit นี้ ส่วนการตรวจจริงใช้ 64 บิตและ `(hash_A ^ hash_B).bit_count()`

### 3.5 ผล source-pinned ของคู่ภาพจริงและข้อจำกัด

คู่ภาพจริงที่ตรวจแยกจากเอกสารนี้คือ `BloodImage_00037.jpg` (validation) กับ `BloodImage_00038.jpg` (training) ใน BCCD pinned commit `d272fb14cdff6e473fafeeeba32aba5f560e9e43`

| Comparator | Reported 64-bit Hamming distance | Threshold `≤ 5` |
|---|---:|---|
| L>R | **3** | Candidate |
| R>L | **1** | Candidate |

คำว่า **candidate** มีความหมายเพียงว่า descriptor คล้ายกันภายใต้วิธีและ threshold ที่กำหนด ไม่ใช่ข้อพิสูจน์ว่าเป็น exact duplicate, ภาพผู้ป่วย/สไลด์เดียวกัน, true label เดียวกัน หรือเกิด performance leakage จริง

> **ห้ามตีความ 3 และ 1 ว่าเป็นจำนวน candidate pairs:** เป็นจำนวนบิตที่ต่างกันของ **ภาพคู่เดียวกัน** ภายใต้ comparator คนละกฎ ส่วนตำแหน่งใน 8×8 XOR grid เป็น **ตำแหน่งใน descriptor**, ไม่ใช่ตำแหน่งเซลล์บนภาพ microscopy

## 4. วิธีรันตัวอย่างและตรวจซ้ำ (offline, no dataset)

จาก root ของ repository:

```bash
python -m pip install -r requirements.txt
python examples/equations_demo.py
python tests/test_equation_examples.py
python tests/test_source_synthetic.py
```

- Demo ใช้เฉพาะ synthetic record keys, synthetic bounding boxes และ synthetic 9×8 grayscale data ไม่มีการ clone dataset ไม่มี network และไม่มีการประมวลผล image ของคนไข้
- หากต้องการทำ source-level audit ของจริง ให้เปิด [Colab notebook](../notebooks/C01_SourcePinned_Audit_Colab.ipynb) แล้วตรวจ upstream dataset terms, pinned commits และ switches ที่เริ่มต้นเป็น `False`; ค่าที่ได้ต้องรายงานเป็น **observed** ใหม่ ไม่ใช้ historical expectations แทนผลการรัน
- โค้ดและคำอธิบายนี้อยู่ภายใต้ MIT software license ของ repository แต่ **ไม่ใช่การอนุญาตให้นำภาพหรือ annotations ของ dataset ต้นทางมาแจกจ่ายต่อ**

## 5. เอกสารอ้างอิงเชิงปฏิบัติ

- Frozen implementation: [`src/audit_sources_r2_frozen.py`](../src/audit_sources_r2_frozen.py) (ดู `pixel_record_key`, `csv_record_multiset`, `valid_box`, `dhash_strict` และ `pairwise_screen`)
- Source protocol: [`docs/SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md`](SUPPLEMENTARY_PROTOCOL_SOURCE_AUDIT.md)
- Source expectations (not observed results): [`manifests/historical_expected_32_NOT_OBSERVED.json`](../manifests/historical_expected_32_NOT_OBSERVED.json)
- BCCD upstream: https://github.com/Shenggan/BCCD_Dataset (commit `d272fb14cdff6e473fafeeeba32aba5f560e9e43`)
- BCDD upstream: https://github.com/draaslan/blood-cell-detection-dataset (commit `c15d0652b3eefd97ac1b3347d83a7e5646dcb97a`)

*Prepared 2026-11-07 for C-01 researcher/coauthor review; equations describe bounded computational source audits, not clinical inference.*
