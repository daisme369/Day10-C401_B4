# Quality report — Lab Day 10 (nhom C401_B4)

**run_id (inject):** sprint3-inject-bad  
**run_id (fixed):** sprint3-fixed  
**Ngay:** 15/04/2026

---

## 1. Tom tat so lieu

| Chi so | Truoc fix (inject bad) | Sau fix (run chuan) | Ghi chu |
|--------|-------------------------|---------------------|---------|
| raw_records | 10 | 10 | Tu logs run_sprint3-*.log |
| cleaned_records | 6 | 6 | Khong doi do corruption o noi dung policy refund |
| quarantine_records | 4 | 4 | Cung bo raw mau va cung rule quarantine |
| Expectation halt? | Co (refund_no_stale_14d_window FAIL) | Khong (tat ca halt OK) | Inject dung y do Sprint 3 |

---

## 2. Before / after retrieval (bat buoc)

Evidence files:

- artifacts/eval/after_inject_bad.csv
- artifacts/eval/after_fix.csv

**Cau hoi then chot:** refund window (`q_refund_window`)

- Truoc fix (inject bad): contains_expected=yes, hits_forbidden=yes
- Sau fix: contains_expected=yes, hits_forbidden=no

Dien giai: truoc khi fix, top-k retrieval van con chunk stale co cum tu "14 ngay lam viec" nen bi danh dau `hits_forbidden=yes`. Sau khi rerun pipeline chuan, chunk stale bi thay bang noi dung 7 ngay va `hits_forbidden` ve no.

**Merit (khuyen nghi):** versioning HR — `q_leave_version`

- Truoc fix: contains_expected=yes, hits_forbidden=no, top1_doc_expected=yes
- Sau fix: contains_expected=yes, hits_forbidden=no, top1_doc_expected=yes

Dien giai: rule quarantine HR stale (effective_date < 2026-01-01) da giu ket qua on dinh o ca hai kịch ban.

---

## 3. Freshness & monitor

Ca hai run deu co `freshness_check=FAIL` voi ly do `freshness_sla_exceeded` (SLA 24 gio, latest_exported_at=2026-04-10T08:00:00Z).

- inject bad: age_hours ~121.087
- fixed: age_hours ~121.099

Day la hanh vi hop le voi bo du lieu mau cu, khong phai loi code pipeline.

---

## 4. Corruption inject (Sprint 3)

Kich ban inject da dung:

- Chay `python etl_pipeline.py run --run-id sprint3-inject-bad --no-refund-fix --skip-validate`
- Tac dong:
	- Tat rule auto-fix refund 14->7
	- Co y bo qua halt de du lieu xau van duoc embed

Tin hieu phat hien:

- expectation `refund_no_stale_14d_window` FAIL (violations=1)
- eval `q_refund_window` co `hits_forbidden=yes`

Xu ly phuc hoi:

- Chay lai `python etl_pipeline.py run --run-id sprint3-fixed`
- Eval lai: `q_refund_window` chuyen sang `hits_forbidden=no`

---

## 5. Han che & viec chua lam

- Chua hop nhat 2 ket qua eval vao 1 CSV co cot `scenario`; hien tai luu 2 file tach rieng.
- Chua them tap cau hoi mo rong (>4 cau) de stress-test retrieval trong nhieu tinh huong hon.
