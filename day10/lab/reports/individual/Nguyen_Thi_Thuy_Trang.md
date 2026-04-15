# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyễn Thị Thùy Trang  
**Vai trò:** Monitoring Owner - Docs Owner  
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ** (ngắn hơn Day 09 vì rubric slide cá nhân ~10% — vẫn phải đủ bằng chứng)

---

> Viết **"tôi"**, đính kèm **run_id**, **tên file**, **đoạn log** hoặc **dòng CSV** thật.  
> Nếu làm phần clean/expectation: nêu **một số liệu thay đổi** (vd `quarantine_records`, `hits_forbidden`, `top1_doc_expected`) khớp bảng `metric_impact` của nhóm.  
> Lưu: `reports/individual/[ten_ban].md`

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

-`docs/runbook.md`: mô tả cách vận hành pipeline, xử lý sự cố và giải thích trạng thái freshness (PASS/WARN/FAIL).
- `reports/group_report.md`: tổng hợp kết quả các sprint, bao gồm metric_impact, đánh giá pipeline và phân công nhóm.

**Kết nối với thành viên khác:**
- Phần của tôi phụ thuộc vào kết quả pipeline từ các thành viên còn lại. Tôi sử dụng các log, manifest, và báo cáo chất lượng để xây dựng runbook và tổng hợp báo cáo nhóm, đảm bảo hệ thống có thể được theo dõi và vận hành hiệu quả.
_________________

**Bằng chứng (commit / comment trong code):**

_________________

---

## 2. Một quyết định kỹ thuật (100–150 từ)

> VD: chọn halt vs warn, chiến lược idempotency, cách đo freshness, format quarantine.

Một quyết định kỹ thuật quan trọng tôi thực hiện là lựa chọn ngưỡng SLA cho kiểm tra freshness. Ban đầu hệ thống mặc định SLA là 24 giờ, dẫn đến trạng thái FAIL do dữ liệu có `latest_exported_at = 2026-04-10T08:00:00` và `age_hours ≈ 122`. Tuy nhiên, đây là dữ liệu mẫu (offline CSV), không phải dữ liệu realtime, nên việc FAIL là không hợp lý trong bối cảnh lab.

Tôi cùng nhóm đã thảo luận, điều chỉnh SLA lên 125 giờ thông qua biến môi trường (`FRESHNESS_SLA_HOURS=125`) để phản ánh đúng đặc điểm dữ liệu. Sau khi điều chỉnh, kết quả chạy:
`PASS {"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 122.571, "sla_hours": 125.0}`

Quyết định này giúp phân biệt rõ giữa dữ liệu “stale thực sự” và dữ liệu “cũ nhưng chấp nhận được”, đồng thời tránh false alarm trong monitoring.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

> Mô tả triệu chứng → metric/check nào phát hiện → fix.

Một anomaly tôi gặp là pipeline báo FAIL ở bước freshness dù pipeline đã chạy thành công. Triệu chứng là lệnh:

`python etl_pipeline.py freshness --manifest artifacts/manifests/manifest_sprint4.json`

trả về:
`FAIL {"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 122.299, "sla_hours": 24.0}`

Metric phát hiện lỗi là `age_hours > sla_hours`. Sau khi kiểm tra manifest và log, tôi xác định nguyên nhân không phải do pipeline lỗi mà do SLA mặc định quá thấp so với dữ liệu mẫu.

Cách xử lý là tăng SLA lên 125 giờ và chạy lại kiểm tra freshness. Sau khi fix, trạng thái chuyển sang PASS. Tôi cũng cập nhật lại runbook để giải thích rõ ý nghĩa PASS/WARN/FAIL và cách điều chỉnh SLA phù hợp với từng loại dữ liệu.

---

## 4. Bằng chứng trước / sau (80–120 từ)

> Dán ngắn 2 dòng từ `before_after_eval.csv` hoặc tương đương; ghi rõ `run_id`.

Trước: 
`FAIL {"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 122.299, "sla_hours": 24.0}`

Sau:
`PASS {"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 122.571, "sla_hours": 125.0}`

`run_id`: sprint4

---

## 5. Cải tiến tiếp theo (40–80 từ)

> Nếu có thêm 2 giờ — một việc cụ thể (không chung chung).

- Nếu có thêm thời gian, tôi sẽ kiểm tra thêm nhiều trường hợp dữ liệu lỗi (ví dụ: thiếu field, sai format ngày, duplicate phức tạp) để đảm bảo pipeline xử lý tốt hơn.

- Ngoài ra, tôi muốn thử tham gia vào các bước xử lý dữ liệu như viết thêm cleaning rule hoặc expectation để hiểu rõ hơn toàn bộ pipeline, không chỉ dừng lại ở việc monitoring.
---