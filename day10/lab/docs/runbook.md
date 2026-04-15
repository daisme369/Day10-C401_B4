# Runbook — Lab Day 10 (incident tối giản)

---

## Symptom

> User / agent thấy gì? (VD: trả lời “14 ngày” thay vì 7 ngày)
Dữ liệu vẫn được hệ thống chấp nhận (PASS - 125 > 122.571), nhưng đã gần chạm ngưỡng SLA, có nguy cơ trở nên lỗi thời nếu không được cập nhật kịp thời.
---

## Detection

> Metric nào báo? (freshness, expectation fail, eval `hits_forbidden`)
- Freshness check trả về PASS với:
    - age_hours ≈ 122h
    - sla_hours = 125h
- Trạng thái PASS nhưng gần ngưỡng SLA, có nguy cơ chuyển sang WARN/FAIL nếu không cập nhật
- Eval retrieval vẫn trả kết quả đúng nhưng có thể chứa thông tin sắp stale
---

## Diagnosis

| Bước | Việc làm | Kết quả mong đợi |
|------|----------|------------------|
| 1 | Kiểm tra `artifacts/manifests/manifest_sprint4.json` | Xác nhận latest_exported_at = 2026-04-10T08:00:00 |
| 2 | Mở `artifacts/quarantine/quarantine_sprint4.csv` | Kiểm tra có dữ liệu bị loại do rule cleaning hoặc expectation, xác nhận pipeline không có spike bất thường |
| 3 | Chạy `python eval_retrieval.py` | Kết quả retrieval vẫn đúng nhưng có dấu hiệu tiệm cận rủi ro stale (không lỗi nhưng cần theo dõi freshness) |

---

## Mitigation

> Rerun pipeline, rollback embed, tạm banner “data stale”, …
- Chủ động chạy lại pipeline để làm mới dữ liệu: `python etl_pipeline.py run --run-id sprint4_refresh`
- Kiểm tra nguồn dữ liệu (CSV/API) có update mới hay không
- Nếu gần SLA, cân nhắc cảnh báo nhẹ cho hệ thống hoặc người dùng
- Theo dõi freshness định kỳ để tránh chuyển sang FAIL

---

## Prevention

> Thêm expectation, alert, owner — nối sang Day 11 nếu có guardrail.
- Thiết lập alert threshold trước FAIL (ví dụ WARN khi >80% SLA)
- Chạy pipeline định kỳ để tránh chạm ngưỡng SLA
- Định nghĩa SLA phù hợp theo từng loại dữ liệu
- Gán owner cho từng nguồn dữ liệu để đảm bảo cập nhật đúng hạn
- Kết hợp freshness + monitoring dashboard để theo dõi trend age_hours
