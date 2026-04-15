# Quality report — Lab Day 10 (nhóm)

**run_id:** sprint3 

**Ngày:** 15/04/2026

---

## 1. Tóm tắt số liệu

| Chỉ số | Trước | Sau | Ghi chú |
|--------|-------|-----|---------|
| raw_records | 11 | 11 | Tổng số dòng đọc từ file raw CSV ban đầu. |
| cleaned_records | 6 | 6 | Số bản ghi được nạp vào ChromaDB. |
| quarantine_records | 5 | 5 | Số lượng bản ghi bị cách ly |
| Expectation halt? | Không (bypass validate) | Không | Pipeline chạy mượt mà (exit 0), không bị dừng đột ngột. |

---

## 2. Before / after retrieval (bắt buộc)

> Đính kèm 2 file: `artifacts/eval/eval_dirty.csv` và `artifacts/eval/eval_clean.csv`.

**Câu hỏi then chốt:** refund window (`q_refund_window`)  

"Khách hàng có bao nhiêu ngày để yêu cầu hoàn tiền kể từ khi xác nhận đơn?"

**Trước:**  
* Hệ thống giữ nguyên thông tin sai lệch (14 ngày) trong Vector DB. Khi truy vấn, AI đọc trúng văn bản sai nên chỉ số hits_forbidden bị fail.

* Trích xuất từ file eval_dirty.csv:
```
question_id,question,top1_doc_id,top1_preview,contains_expected,hits_forbidden,top1_doc_expected,top_k_used
q_refund_window,Khách hàng có bao nhiêu ngày để yêu cầu hoàn tiền kể từ khi xác nhận đơn?,policy_refund_v4,Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng.,yes,yes,,3
```

**Sau:**
* Rule xử lý của luồng ETL đã tự động chuẩn hóa chuỗi chính sách từ 14 ngày về 7 ngày. Dữ liệu nạp vào DB là dữ liệu chuẩn. Hệ thống RAG trả về kết quả xuất sắc, không còn hit vào keyword sai.

* Trích xuất từ file eval_clean.csv: q_refund_window | top1_doc_id:
```
question_id,question,top1_doc_id,top1_preview,contains_expected,hits_forbidden,top1_doc_expected,top_k_used
q_refund_window,Khách hàng có bao nhiêu ngày để yêu cầu hoàn tiền kể từ khi xác nhận đơn?,policy_refund_v4,Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng.,yes,no,,3
```

---

## 3. Freshness & monitor

> Kết quả `freshness_check` (PASS/WARN/FAIL) và giải thích SLA bạn chọn.

---

## 4. Corruption inject (Sprint 3)

> Mô tả cố ý làm hỏng dữ liệu kiểu gì (duplicate / stale / sai format) và cách phát hiện.

---

## 5. Hạn chế & việc chưa làm

- …
