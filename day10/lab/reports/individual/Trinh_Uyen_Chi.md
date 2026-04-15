# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Trịnh Uyên Chi  
**Vai trò:** Ingestion  
**Ngày nộp:** 15/04/2026  
**Độ dài yêu cầu:** **400–650 từ**



## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

- Tôi chịu trách nhiệm chính luồng Evaluation (kiểm thử chất lượng RAG) tại file eval_retrieval.py. Xuất báo cáo `docs/quality_report.md`.

**Kết nối với thành viên khác:**

* Tôi phối hợp với người viết luồng Extract & Transform. Khi họ viết xong các rule làm sạch (cleaned), tôi là người chạy hệ thống Retrieval để nghiệm thu xem rule đó có thực sự ngăn chặn được việc AI lấy nhầm dữ liệu (hallucinate) hay không.

**Bằng chứng (commit / comment trong code):**
 
* Tạo output files: eval_dirty.csv (run_id: sprint3_dirty) và eval_clean.csv (run_id: sprint3_clean).

## 2. Một quyết định kỹ thuật (100–150 từ)

Quyết định: Chủ động phân tách đường dẫn output (--out) để cô lập môi trường A/B Testing.

Lý do: Script eval_retrieval.py mặc định sẽ ghi kết quả vào chung một file before_after_eval.csv. Nếu chỉ chạy lệnh chạy mặc định, dữ liệu của lần test sau sẽ ghi đè lên lần test trước, gây khó khăn cho việc lấy minh chứng. Do đó, tôi quyết định can thiệp vào tham số dòng lệnh trong quá trình thực thi: chia làm 2 pha rõ rệt và trỏ output ra 2 file riêng biệt (eval_dirty.csv và eval_clean.csv). Quyết định luồng chạy này giúp bảo toàn được Artifacts (minh chứng) để team có thể mở song song đối chiếu dễ dàng trong lúc làm report.


## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Mô tả triệu chứng: Trong quá trình chạy kịch bản nghiệm thu Baseline (dữ liệu chưa làm sạch), tôi ghi nhận một anomaly ở tầng đầu ra: Hệ thống RAG truy xuất tài liệu vi phạm quy định (`hits_forbidden` = yes) khi người dùng hỏi về q_refund_window.

Cách phát hiện: Lỗi này được phát hiện thông qua việc thực thi file eval_retrieval.py trên bộ dữ liệu policy_export_dirty.csv. Log hệ thống trả về kết quả fail rõ ràng tại cột `hits_forbidden`.

---

## 4. Bằng chứng trước / sau (80–120 từ)

**Before** (run_id: sprint3_dirty):

CSV: `q_refund_window | top1_doc_id: policy_refund_v4 | contains_expected: yes | hits_forbidden: yes`

log: `expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1`
(Hệ thống đọc trúng dữ liệu cũ chứa 14 ngày, vi phạm metric hits_forbidden)

**After** (run_id: sprint3_clean):

CSV: `q_refund_window | top1_doc_id: policy_refund_v4 | contains_expected: yes | hits_forbidden: no`

log: `expectation[refund_no_stale_14d_window] OK (halt) :: violations=0`
(Dữ liệu đã được chuẩn hóa thành 7 ngày, hệ thống trả về kết quả an toàn)

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm 2 giờ, tôi sẽ viết một script tự động cảnh báo (Alert). Script này sẽ chạy file `eval_retrieval.py` ngay sau mỗi đợt chạy ETL. Nếu phát hiện bất kỳ câu hỏi nào có `hits_forbidden == yes`, pipeline sẽ gửi thông báo cho Data Engineer để kịp thời cách ly tài liệu đó, không cho phép AI đọc được.

_________________
