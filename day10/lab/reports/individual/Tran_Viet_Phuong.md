# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Trần Việt Phương
**Vai trò:** Quality Owner
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ** (ngắn hơn Day 09 vì rubric slide cá nhân ~10% — vẫn phải đủ bằng chứng)

---

> Viết **"tôi"**, đính kèm **run_id**, **tên file**, **đoạn log** hoặc **dòng CSV** thật.  
> Nếu làm phần clean/expectation: nêu **một số liệu thay đổi** (vd `quarantine_records`, `hits_forbidden`, `top1_doc_expected`) khớp bảng `metric_impact` của nhóm.  
> Lưu: `reports/individual/[ten_ban].md`

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**
Tôi phụ trách phần Sprint 2, file expectations.py
- …

**Kết nối với thành viên khác:**
Tôi kết hợp cùng Mạnh làm file cleaning_rules.py để hoàn thiện Sprint 2
_________________

**Bằng chứng (commit / comment trong code):**
Commit hash: 07593e9521c300d09f1b6456878cd198b8ed24b3
_________________

---

## 2. Một quyết định kỹ thuật (100–150 từ)

> VD: chọn halt vs warn, chiến lược idempotency, cách đo freshness, format quarantine.
Chọn warn cho Expectation 9: suspicious_sla_rows. Việc đưa vào expectation này giúp phát hiện các trường hợp SLA không tuân thủ, nhưng không quá nghiêm trọng để dừng pipeline vì hoàn toàn có thể cảnh báo người dùng và cảnh báo cho người nhập csv.
_________________

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

> Mô tả triệu chứng → metric/check nào phát hiện → fix.

_________________

---

## 4. Bằng chứng trước / sau (80–120 từ)

> Dán ngắn 2 dòng từ `before_after_eval.csv` hoặc tương đương; ghi rõ `run_id`.
expectation[sla_p1_expected_response_and_resolution] FAIL (warn) :: suspicious_sla_rows=1
_________________

---

## 5. Cải tiến tiếp theo (40–80 từ)

> Nếu có thêm 2 giờ — một việc cụ thể (không chung chung).

Thêm các expectation để sát với thực tế, đảm bảo dữ liệu up-to-date và các chi tiết đầy đủ
_________________
