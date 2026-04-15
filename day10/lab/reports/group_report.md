# Báo Cáo Nhóm — Lab Day 10: Data Pipeline & Data Observability

**Tên nhóm:** C401-B4  
**Thành viên:**
| Tên | Vai trò (Day 10) | Email |
|-----|------------------|-------|
| Nguyễn Ngọc Tân | Ingestion Owner | ngoctannew@gmail.com |
| Trần Việt Phương | Cleaning Owner | phuong251202@gmail.com |
| Phạm Hoàng Tiến Mạnh | Quality Owner | phamnguyentienmanh2004@gmail.com |
| Trịnh Uyên Chi | Evaluation Owner | trinhuyenchi2003@gmail.com |
| Nguyễn Hoàng Nghĩa | Embed & Idempotency Owner | nhnghia210@gmail.com |
| Lê Đức Anh | Docs Owner | ducanh198369@gmail.com |
| Nguyễn Thị Thùy Trang | Monitoring Owner | nguyenthuytrang372004@gmail.com |

**Ngày nộp:** 15/04/2026  
**Repo:** `https://github.com/daisme369/Day10-C401_B4.git`  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Nộp tại:** `reports/group_report.md`  
> **Deadline commit:** xem `SCORING.md` (code/trace sớm; report có thể muộn hơn nếu được phép).  
> Phải có **run_id**, **đường dẫn artifact**, và **bằng chứng before/after** (CSV eval hoặc screenshot).

---

## 1. Pipeline tổng quan (150–200 từ)

> Nguồn raw là gì (CSV mẫu / export thật)? Chuỗi lệnh chạy end-to-end? `run_id` lấy ở đâu trong log?

**Tóm tắt luồng:**
Nguồn raw của pipeline là file `data/raw/policy_export_dirty.csv`, mô phỏng dữ liệu export từ hệ thống nội bộ (DB/API) trong bối cảnh IT Helpdesk + HR + Policy system. Dataset này chứa nhiều lỗi thực tế như duplicate records, thiếu hoặc sai định dạng ngày, chunk rỗng, doc_id sai chuẩn, và xung đột policy version.

Pipeline được thiết kế theo luồng end-to-end: ingest → clean → validate (expectation suite) → embed → generate manifest → freshness check. Mỗi lần chạy pipeline sẽ sinh `run_id` (UTC timestamp hoặc custom value(sprint)) và được ghi vào log + manifest để đảm bảo traceability toàn bộ hệ thống.
_________________

**Lệnh chạy một dòng (copy từ README thực tế của nhóm):**

```
python etl_pipeline.py run --run-id sprint4
```

---

## 2. Cleaning & expectation (150–200 từ)

> Baseline đã có nhiều rule (allowlist, ngày ISO, HR stale, refund, dedupe…). Nhóm thêm **≥3 rule mới** + **≥2 expectation mới**. Khai báo expectation nào **halt**.

Nhóm bổ sung thêm các rule mới để tăng độ an toàn dữ liệu:

- Rule kiểm tra độ dài `chunk_text`: các đoạn quá ngắn (dưới ngưỡng `MIN_CHUNK_CHARS`) sẽ bị đưa vào quarantine nhằm tránh dữ liệu không đủ ngữ cảnh.
- Rule phát hiện HTML/script injection: nếu nội dung chứa tag HTML sẽ bị loại bỏ để tránh nhiễu hoặc lỗi downstream.
- Rule kiểm tra `exported_at` không được nằm trong tương lai so với thời điểm pipeline chạy, giúp phát hiện lỗi hệ thống hoặc dữ liệu sai timestamp.

Về expectation, nhóm bổ sung các kiểm tra sau cleaning:

- E7: không còn `effective_date` rỗng sau cleaning (**halt**).
- E8: `exported_at` phải đúng định dạng ISO datetime (**halt**).
- E9: SLA P1 phải đúng chuẩn “15 phút / 4 giờ” (chấp nhận dạng viết tắt như 15p, 4h) (**warn**).

Trong đó, E7 và E8 là các expectation ở mức **halt**, nghĩa là nếu fail thì pipeline sẽ dừng để tránh đưa dữ liệu không hợp lệ vào hệ thống embedding.

### 2a. Bảng metric_impact (bắt buộc — chống trivial)

| Rule / Expectation mới | Trước (số liệu) | Sau / khi inject (số liệu) | Chứng cứ (log / CSV / commit) |
|------------------------|-----------------|-----------------------------|-------------------------------|
| Chunk too short (Rule 7) | 0 record bị loại | +1 record bị quarantine khi inject text ngắn | quarantine CSV (reason=chunk_text_too_short) |
| HTML detection (Rule 8) | 0 record lỗi | +1 record bị quarantine khi inject `<script>` | quarantine CSV (reason=chunk_text_contains_html) |
| Future timestamp (Rule 9) | 0 record lỗi | +1 record bị quarantine khi inject exported_at tương lai | quarantine CSV (reason=exported_at_future_timestamp) |
| E7: missing_effective_date_rows | PASS | FAIL khi inject record thiếu date | log expectation FAIL + halt |
| E8:non_iso_exported_at_rows | PASS | FAIL khi inject sai format (VD: 2026/04/10) | log expectation FAIL + halt |
| E9: suspicious_sla_rows | PASS | WARN khi sửa nội dung SLA sai chi tiết, nghi ngờ dữ liệu cũ | log expectation WARN |


**Rule chính (baseline + mở rộng):**

- Quarantine: doc_id không thuộc allowlist (export lạ / catalog sai).
- Chuẩn hoá effective_date sang YYYY-MM-DD; quarantine nếu không parse được.
-  Quarantine: chunk hr_leave_policy có effective_date < 2026-01-01 (bản HR cũ / conflict version).
- Quarantine: chunk_text rỗng hoặc effective_date rỗng sau chuẩn hoá.
- Loại trùng nội dung chunk_text (giữ bản đầu).
- Fix stale refund: policy_refund_v4 chứa '14 ngày làm việc' → 7 ngày.
- (Mở rộng) Kiểm tra độ dài `chunk_text` tối thiểu  
- (Mở rộng) Phát hiện HTML/script injection  
- (Mở rộng) Kiểm tra `exported_at` không nằm trong tương lai  

**Ví dụ 1 lần expectation fail (nếu có) và cách xử lý:**

Khi chạy pipeline với dữ liệu inject có `exported_at` sai định dạng (ví dụ: `2026/04/10`), expectation E8 sẽ FAIL và pipeline dừng do đây là lỗi ở mức halt. Log hiển thị expectation FAIL với severity cao.

Cách xử lý là chuẩn hóa lại định dạng thời gian về ISO (`YYYY-MM-DDTHH:MM:SS`) hoặc loại bỏ record lỗi trước khi đưa vào pipeline. Sau khi sửa, chạy lại pipeline thì expectation PASS và dữ liệu được phép embed.

---

## 3. Before / after ảnh hưởng retrieval hoặc agent (200–250 từ)

> Bắt buộc: inject corruption (Sprint 3) — mô tả + dẫn `artifacts/eval/…` hoặc log.

**Kịch bản inject:**

Nhóm thực hiện inject corruption bằng cách chạy pipeline với flag: 
`python etl_pipeline.py run --no-refund-fix --skip-validate --run-id sprint3_dirty`


Trong kịch bản này, rule sửa lỗi policy hoàn tiền (từ 14 → 7 ngày) bị tắt, đồng thời expectation suite bị bỏ qua. Kết quả là dữ liệu sai (policy “14 ngày”) vẫn được giữ lại và embed vào vector store. Ngoài ra, việc bỏ validate cho phép các bản ghi lỗi (duplicate, sai format, thiếu field) không bị chặn, làm giảm chất lượng dữ liệu đầu vào cho retrieval.

Sau đó, nhóm chạy lại pipeline ở chế độ chuẩn (không sử dụng các flag inject) để tạo dữ liệu sạch và embed lại vector store.

**Kết quả định lượng (từ CSV / bảng):**

Kết quả được lưu trong hai file:
- `artifacts/eval/eval_dirty.csv` (sau khi inject corruption)
- `artifacts/eval/eval_clean.csv` (sau khi chạy pipeline chuẩn)

So sánh truy vấn kiểm tra policy hoàn tiền (`q_refund_window`):

- **Dirty run:** top-k retrieval chứa chunk có nội dung “14 ngày”, dẫn đến câu trả lời sai hoặc mâu thuẫn (hits_forbidden xuất hiện).
- **Clean run:** chỉ còn chunk “7 ngày” sau khi áp dụng cleaning rule và expectation, kết quả retrieval chính xác và nhất quán.

Điều này chứng minh rằng khi bỏ qua bước validate và cleaning, vector store có thể chứa dữ liệu sai, làm agent trả lời không đúng. Ngược lại, pipeline chuẩn giúp đảm bảo dữ liệu đầu vào chất lượng, từ đó cải thiện rõ rệt độ chính xác của retrieval và agent response.s

---

## 4. Freshness & monitoring (100–150 từ)

> SLA bạn chọn, ý nghĩa PASS/WARN/FAIL trên manifest mẫu.

- Nhóm lựa chọn SLA freshness là 125 giờ, dựa trên đặc điểm dataset có tính chất static (policy nội bộ, không cập nhật liên tục). Kết quả kiểm tra freshness từ manifest:
`PASS {"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 122.571, "sla_hours": 125.0}`


- Ý nghĩa các trạng thái:

    - PASS: dữ liệu còn “fresh”, thời gian từ lần export gần nhất nhỏ hơn SLA (122h < 125h), pipeline có thể sử dụng bình thường.
    - WARN: dữ liệu gần chạm ngưỡng SLA, cần theo dõi hoặc chuẩn bị refresh.
    - FAIL: dữ liệu đã quá hạn SLA, cần chạy lại pipeline để cập nhật dữ liệu mới, nếu không có thể gây sai lệch trong retrieval.

Việc theo dõi freshness giúp đảm bảo agent luôn truy cập đúng phiên bản dữ liệu mới nhất và tránh sử dụng dữ liệu stale trong hệ thống.

---

## 5. Liên hệ Day 09 (50–100 từ)

> Dữ liệu sau embed có phục vụ lại multi-agent Day 09 không? Nếu có, mô tả tích hợp; nếu không, giải thích vì sao tách collection.

Dữ liệu sau khi được làm sạch và embed ở Day 10 có thể tái sử dụng cho hệ thống multi-agent Day 09 qua retrieval (RAG). Agent truy vấn sẽ gọi vecto database (ChromaDB) để tìm các document liên quan, từ đó cải thiện độ chính xác câu trả lời. Việc đảm bảo chất lượng dữ liệu (cleaning, validation) giúp giảm lỗi retrieval.

---

## 6. Rủi ro còn lại & việc chưa làm

Mặc dù pipeline đã xử lý tốt các lỗi phổ biến (duplicate, thiếu ngày, sai format, stale policy), vẫn còn một số rủi ro:

- **Stale data chưa bị chặn hoàn toàn**: freshness hiện chỉ check ở mức SLA (125 giờ), chưa có cơ chế tự động alert hoặc block pipeline khi dữ liệu quá cũ.
- **Expectation coverage chưa đầy đủ**: mới kiểm tra một số điều kiện cơ bản (date, format, SLA text), chưa validate sâu về semantic (ví dụ: nội dung policy mâu thuẫn nhau).
- **Retrieval chưa kiểm soát context cũ hoàn toàn**: dù đã prune embedding, vẫn có khả năng top-k chứa thông tin chưa tối ưu nếu chunking hoặc metadata chưa đủ tốt.
- **Chưa có alert/monitoring real-time**: pipeline chỉ log ra file, chưa tích hợp hệ thống cảnh báo (email, dashboard).

Hướng cải thiện:
- Thêm alert khi freshness FAIL hoặc expectation halt.
- Mở rộng expectation theo semantic consistency.
- Gắn lineage_id cho từng chunk.
- Tích hợp monitoring dashboard (Prometheus/Grafana).
- …
