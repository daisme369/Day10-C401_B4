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

_________________

**Lệnh chạy một dòng (copy từ README thực tế của nhóm):**

_________________

---

## 2. Cleaning & expectation (150–200 từ)

> Baseline đã có nhiều rule (allowlist, ngày ISO, HR stale, refund, dedupe…). Nhóm thêm **≥3 rule mới** + **≥2 expectation mới**. Khai báo expectation nào **halt**.

### 2a. Bảng metric_impact (bắt buộc — chống trivial)

| Rule / Expectation mới (tên ngắn) | Trước (số liệu) | Sau / khi inject (số liệu) | Chứng cứ (log / CSV / commit) |
|-----------------------------------|------------------|-----------------------------|-------------------------------|
| … | … | … | … |

**Rule chính (baseline + mở rộng):**

- …

**Ví dụ 1 lần expectation fail (nếu có) và cách xử lý:**

_________________

---

## 3. Before / after ảnh hưởng retrieval hoặc agent (200–250 từ)

> Bắt buộc: inject corruption (Sprint 3) — mô tả + dẫn `artifacts/eval/…` hoặc log.

**Kịch bản inject:**

_________________

**Kết quả định lượng (từ CSV / bảng):**

_________________

---

## 4. Freshness & monitoring (100–150 từ)

> SLA bạn chọn, ý nghĩa PASS/WARN/FAIL trên manifest mẫu.

_________________

---

## 5. Liên hệ Day 09 (50–100 từ)

> Dữ liệu sau embed có phục vụ lại multi-agent Day 09 không? Nếu có, mô tả tích hợp; nếu không, giải thích vì sao tách collection.

Dữ liệu sau khi được làm sạch và embed ở Day 10 có thể tái sử dụng cho hệ thống multi-agent Day 09 qua retrieval (RAG). Agent truy vấn sẽ gọi vecto database (ChromaDB) để tìm các document liên quan, từ đó cải thiện độ chính xác câu trả lời. Việc đảm bảo chất lượng dữ liệu (cleaning, validation) giúp giảm lỗi retrieval.

---

## 6. Rủi ro còn lại & việc chưa làm

- …
