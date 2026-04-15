# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Lê Đức Anh  
**Vai trò:** Ingestion / Cleaning / Embed / Monitoring — Monitoring  
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ** (ngắn hơn Day 09 vì rubric slide cá nhân ~10% — vẫn phải đủ bằng chứng)

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

- `docs/pipeline_architecture.md`
- `docs/data_contract.md`
- kiểm tra luồng chạy và ghép các sprint thành một quy trình hoàn chỉnh

Tôi phụ trách Sprint 4 theo hướng documentation và điều phối cuối: rà lại kiến trúc pipeline, bổ sung source map và schema trong data contract, rồi kiểm tra các sprint trước để nối thành một pipeline hoàn chỉnh từ ingest → clean → validate → embed → monitor. Tôi cũng hỗ trợ kiểm soát source, đọc artifact log/manifest, và debug nhẹ khi phát hiện mismatch giữa tài liệu với output thật.

**Kết nối với thành viên khác:**

Tôi đối chiếu với phần cleaning/quality của Sprint 2–3 để bảo đảm tài liệu không mô tả sai hành vi pipeline. Khi thấy bug nhỏ ở expectation regex, tôi báo lại để team thống nhất cách viết rule ổn định hơn và tránh lệch giữa report với code.

**Bằng chứng (commit / comment trong code):**

`docs/pipeline_architecture.md`, `docs/data_contract.md`.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Vì vai trò của tôi thiên về documentation nên tôi không là người quyết định chính các rule clean hay chiến lược embed. Quyết định kỹ thuật gần nhất mà tôi tham gia là khi review expectation: tôi đề xuất dùng regex theo kiểu `search` thay vì `match` để giảm nguy cơ bỏ sót chuỗi có tiền tố hoặc format không hoàn toàn “đứng đầu chuỗi”. Mục tiêu là làm kiểm tra ổn định hơn và giảm false negative khi dữ liệu thay đổi nhẹ. Ngoài ra, tôi ưu tiên ghi rõ ranh giới `halt`/`warn` trong tài liệu để nhóm biết khi nào pipeline phải dừng, khi nào chỉ cảnh báo.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Tôi không trực tiếp sửa logic clean, nhưng tôi tham gia debug ở mức tài liệu và trace artifact. Lỗi dễ thấy nhất là khi chạy `sprint3-inject-bad`, expectation `refund_no_stale_14d_window` bị FAIL với `violations=1`, và file eval cho thấy `q_refund_window` có `hits_forbidden=yes`. Tôi dùng tín hiệu đó để đối chiếu với report và cập nhật phần mô tả pipeline/contract cho khớp hành vi thật. Khi pipeline được chạy lại ở `sprint3-fixed`, expectation này trở lại `OK` và `hits_forbidden` chuyển sang `no`, nên tôi ghi rõ đây là ví dụ của luồng kiểm soát source và debug giữa các sprint.
---

## 4. Bằng chứng trước / sau (80–120 từ)

`run_id`: `sprint3-inject-bad` và `sprint3-fixed`.

- Trước fix: `q_refund_window,...,contains_expected=yes,hits_forbidden=yes,...`
- Sau fix: `q_refund_window,...,contains_expected=yes,hits_forbidden=no,...`

Tôi dùng đúng cặp artifact này để đối chiếu giữa Sprint 3 và Sprint 4: dữ liệu xấu có thể làm retrieval trả về context stale, còn run chuẩn thì không còn chunk sai cửa sổ hoàn tiền.

---

## 5. Cải tiến tiếp theo (40–80 từ)