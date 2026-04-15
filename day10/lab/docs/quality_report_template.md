# Quality report — Lab Day 10 (nhóm)

**run_id:** _______________  
**Ngày:** _______________

---

## 1. Tóm tắt số liệu

| Chỉ số | Trước | Sau | Ghi chú |
|--------|-------|-----|---------|
| raw_records | | | |
| cleaned_records | | | |
| quarantine_records | | | |
| Expectation halt? | | | |

---

## 2. Before / after retrieval (bắt buộc)

> Đính kèm hoặc dẫn link tới `artifacts/eval/before_after_eval.csv` (hoặc 2 file before/after).

**Câu hỏi then chốt:** refund window (`q_refund_window`)  
**Trước:** (copy dòng CSV hoặc paste top-k)  
**Sau:**

**Merit (khuyến nghị):** versioning HR — `q_leave_version` (`contains_expected`, `hits_forbidden`, cột `top1_doc_expected`)

**Trước:**  
**Sau:**

---

## 3. Freshness & monitor

> Kết quả `freshness_check` (PASS/WARN/FAIL) và giải thích SLA bạn chọn.
### Freshness & monitor

Kết quả: PASS

- latest_exported_at: 2026-04-10T08:00:00
- publish_timestamp: 2026-04-15T10:27:40
- age_hours: 122.461
- sla_hours: 125.0

Giải thích:
Freshness được tính dựa trên latest_exported_at (ingest boundary).
Do age_hours (122.461) < SLA (125h) nên hệ thống trả về PASS.

Thiết kế:
- SLA được cấu hình qua biến môi trường FRESHNESS_SLA_HOURS
- Nhóm đo freshness tại 2 boundary:
  + Ingest: latest_exported_at
  + Publish: publish_timestamp

Ý nghĩa:
- Ingest freshness đảm bảo dữ liệu nguồn còn mới
- Publish timestamp giúp theo dõi độ trễ toàn pipeline (end-to-end)

---

## 4. Corruption inject (Sprint 3)

> Mô tả cố ý làm hỏng dữ liệu kiểu gì (duplicate / stale / sai format) và cách phát hiện.
Nhóm thực hiện inject dữ liệu lỗi để kiểm tra pipeline:

* Stale policy (refund 14 days)
- Inject: chạy pipeline với --no-refund-fix --skip-validate
- Ảnh hưởng:
  + Retrieval trả lời sai (14 days thay vì 7)
  + Context chứa chunk lỗi
- Phát hiện:
  + contains_expected = no
  + hits_forbidden = yes
---

## 5. Hạn chế & việc chưa làm

- …
