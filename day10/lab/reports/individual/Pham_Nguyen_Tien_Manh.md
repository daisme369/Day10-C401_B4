# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Phạm Nguyễn Tiến Mạnh  
**Vai trò:** Cleaning Owner  
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ**

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

Tôi phụ trách file `transform/cleaning_rules.py`. Cụ thể, tôi bổ sung 3 rule mới vào hàm `clean_rows()` nằm ngoài baseline đã có sẵn, gồm: Rule 7 quarantine chunk_text quá ngắn, Rule 8 phát hiện HTML/script injection trong chunk_text, và Rule 9 quarantine exported_at là timestamp tương lai.

**Kết nối với thành viên khác:**
Output của tôi là list `cleaned` và `quarantine` được trả về từ `clean_rows()`. `etl_pipeline.py` (do thành viên khác phụ trách) gọi trực tiếp hàm này, sau đó truyền `cleaned` vào bước embed ChromaDB.

**Bằng chứng:**

Commit hash: e5695785dc5901f578fb47b360bfd1dafbc8df78

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Khi thiết kế Rule 9 (future timestamp), tôi phải quyết định xử lý thế nào nếu `exported_at` bị rỗng hoặc không đúng định dạng. Có hai hướng: (1) quarantine luôn nếu không parse được, hoặc (2) bỏ qua và để row đi tiếp.

Tôi chọn hướng 2 — nếu `exported_at` rỗng hoặc sai định dạng thì **không quarantine** vì lý do là: baseline đã thiết kế `exported_at` là field không bắt buộc (hàm `write_cleaned_csv` ghi `exported_at or ""`). Quarantine thêm vì thiếu timestamp sẽ làm tăng quarantine_records không đúng mục tiêu của rule này. Rule 9 chỉ xử lý đúng một anomaly cụ thể là **timestamp hợp lệ nhưng nằm trong tương lai**, các trường hợp còn lại để nguyên, tránh làm rule có side effect ngoài ý muốn. Điều này cũng giúp `metric_impact` của Rule 9 sạch và đo được đúng: chỉ inject future timestamp mới trigger quarantine, inject rỗng thì không.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Trong quá trình kiểm tra bộ mẫu `policy_export_dirty.csv`, tôi phát hiện row `chunk_id=9` có `doc_id=legacy_catalog_xyz_zzz`. Row này bị quarantine đúng bởi baseline Rule 1 (unknown*doc_id). Tuy nhiên khi đọc kỹ `chunk_text` của nó — *"Chunk nội dung đủ dài để vượt ngưỡng expectation độ dài tối thiểu trong cleaned export"\_ — tôi nhận ra đây là row được inject có chủ đích để test expectation, không phải lỗi dữ liệu thật.

Điều này khiến tôi nhận ra Rule 7 (min chunk length) cần đặt ngưỡng `MIN_CHUNK_CHARS = 20` đủ thấp để không quarantine nhầm các chunk hợp lệ ngắn như tên mục hay tiêu đề, nhưng vẫn loại được noise thực sự (ví dụ `"OK"`, `"N/A"`, `"---"`). Tôi kiểm tra toàn bộ 10 row trong CSV và xác nhận không có row hợp lệ nào ngắn hơn 20 ký tự, đảm bảo baseline `cleaned_records` không bị ảnh hưởng bởi rule mới.

---

## 4. Bằng chứng trước / sau (80–120 từ)

Thêm vào file policy_export_dirty row này xem rule mới (check exported_at là timestamp tương lai) có hoạt động không:

> 11,it_helpdesk_faq,"abcdjffjfjfdkdkdkdhfhfjfjfjfjfjfjffjffh",01/02/2026,2026-12-12T08:00:00

Trước khi có rule mới (check exported_at là timestamp tương lai):

```
run_id=2026-04-15T14-46Z
raw_records=11
cleaned_records=7
quarantine_records=4
```

Sau khi thêm rule mới

```
run_id=2026-04-15T14-42Z
raw_records=11
cleaned_records=6
quarantine_records=5
```

---

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm 2 giờ, tôi sẽ thêm **Rule 10: phát hiện PII trong chunk_text** — cụ thể dùng regex để bắt số điện thoại Việt Nam (09xx, 03xx...) và địa chỉ email xuất hiện trong nội dung policy. Các chunk chứa PII sẽ bị quarantine với `reason=pii_detected` thay vì embed vào vector store, tránh rủi ro rò rỉ dữ liệu cá nhân qua kết quả tìm kiếm semantic.
