# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyen Ngoc Tan  
**Vai trò:** Ingest & Schema Owner  
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ**

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

Tôi phụ trách Sprint 1: đọc raw export `data/raw/policy_export_dirty.csv`, điền source map trong `docs/data_contract.md` và chạy ETL với `python etl_pipeline.py run --run-id sprint1`. Phần này tập trung vào lớp ingest và schema, tức xác định rõ dữ liệu đầu vào gồm những cột nào, nguồn canonical nào được phép đi vào pipeline, failure mode chính là gì và metric nào dùng để theo dõi chất lượng.

**Kết nối với thành viên khác:**

Output của tôi là contract và log nền cho các bước sau. `etl_pipeline.py` đọc file raw, đếm `raw_records`, gọi cleaning, rồi ghi `cleaned_records`, `quarantine_records`, manifest và log. Nhờ đó thành viên làm cleaning, expectation và embed có chung một chuẩn schema để bám theo.

**Bằng chứng (commit / comment trong code):**

Bằng chứng rõ nhất nằm ở `docs/data_contract.md` và `SPRINT1_COMPLETION.md`, nơi ghi lệnh chạy, kết quả DoD và các artifact tương ứng với `run_id=sprint1`.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Quyết định kỹ thuật quan trọng nhất của tôi là **source map phải gắn với failure mode và metric**, chứ không chỉ liệt kê tên file. Nếu chỉ ghi “nguồn A, nguồn B”, tài liệu sẽ không giúp gì cho bước vận hành vì nhóm không biết mỗi nguồn thường hỏng kiểu gì và phải nhìn metric nào khi pipeline lệch.

Vì vậy trong `docs/data_contract.md` tôi ghi mỗi nguồn cùng một failure mode chính và một metric đi kèm, ví dụ `policy_refund_v4` gắn với `stale_refund_window`, `hr_leave_policy` gắn với `stale_hr_policy_effective_date`, còn file raw tổng `policy_export_dirty.csv` gắn với số lượng `cleaned` và `quarantine`. Cách ghi này giúp contract không chỉ là tài liệu mô tả schema, mà còn là tài liệu vận hành cho cả nhóm.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Anomaly tôi xử lý ở Sprint 1 là sự lệch giữa dữ liệu thực tế và allowlist/schema kỳ vọng. Khi đọc `policy_export_dirty.csv`, tôi thấy file có đủ 10 dòng nhưng không phải tất cả đều hợp lệ để đi tiếp. Có ít nhất các nhóm lỗi rõ ràng: `unknown_doc_id`, `missing_effective_date` và `stale_hr_policy_effective_date`. Điều này cho thấy ingest không thể chỉ đọc CSV rồi đẩy thẳng sang embed.

Điểm tôi rút ra là source map phải phản ánh đúng rủi ro của từng nguồn ngay từ đầu. Nếu không ghi rõ trong contract, những lỗi như `legacy_catalog_xyz_zzz` hay một bản HR cũ từ năm 2025 rất dễ bị xem là dữ liệu bình thường. Việc mô tả schema cleaned, owner và hành động quarantine trong `docs/data_contract.md` giúp nhóm phân biệt được đâu là dữ liệu hợp lệ, đâu là dữ liệu cần cô lập để review.

---

## 4. Bằng chứng trước / sau (80–120 từ)

Theo `SPRINT1_COMPLETION.md`, khi chạy:

```text
python etl_pipeline.py run --run-id sprint1
```

log Sprint 1 ghi:

```text
run_id=sprint1
raw_records=10
cleaned_records=6
quarantine_records=4
```

Đây là bằng chứng DoD của phần tôi làm đã đạt: pipeline đọc được full 10 record raw, sau đó tách thành 6 dòng cleaned và 4 dòng quarantine. Ngoài ra file này còn ghi thêm `cleaned_csv`, `quarantine_csv`, `manifest_written` và `PIPELINE_OK`. Hiện tại thư mục `artifacts/` trong repo chỉ còn các file `sprint` và `sprint2`, nên tôi dùng `SPRINT1_COMPLETION.md` làm bằng chứng lưu vết cho run `sprint1`.

---

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm 2 giờ, tôi sẽ chuẩn hóa lại `docs/data_contract.md` và `contracts/data_contract.yaml` để tránh lệch số liệu giữa tài liệu và artifact, đồng thời khôi phục lại đầy đủ bộ file `run_sprint1.log`, `cleaned_sprint1.csv`, `quarantine_sprint1.csv` và `manifest_sprint1.json` trong `artifacts/` để việc review không phải dựa vào completion note.
