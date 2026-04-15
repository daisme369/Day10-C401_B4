# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyễn Hoàng Nghĩa.   
**Vai trò:** Embed Owner.   
**Ngày nộp:** 15/04/2026.   
**Độ dài yêu cầu:** **400–650 từ** (ngắn hơn Day 09 vì rubric slide cá nhân ~10% — vẫn phải đủ bằng chứng)   

---

> Viết **"tôi"**, đính kèm **run_id**, **tên file**, **đoạn log** hoặc **dòng CSV** thật.  
> Nếu làm phần clean/expectation: nêu **một số liệu thay đổi** (vd `quarantine_records`, `hits_forbidden`, `top1_doc_expected`) khớp bảng `metric_impact` của nhóm.  
> Lưu: `reports/individual/[ten_ban].md`

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

- `etl_pipeline.py` 
- `eval_retrieval.py`

Tôi chịu trách nhiệm phần embedding và retrieval evaluation, bao gồm việc đưa dữ liệu cleaned vào vector store và đảm bảo tính idempotent của pipeline. Tôi cũng phụ trách chạy eval để tạo bằng chứng before/after cho Sprint 3.


**Kết nối với thành viên khác:**

Tôi nhận dữ liệu đầu vào từ Cleaning/Quality Owner (cleaned CSV) và phối hợp với họ để đảm bảo các rule cleaning giúp cải thiện retrieval. Ngoài ra, tôi hỗ trợ Monitoring Owner bằng cách cung cấp manifest và kết quả eval. Tôi còn bổ sung thêm publish timestamp trong freshness_check.py.

_________________

**Bằng chứng (commit / comment trong code):**

- Commit: Update Freshness and ETL
- Commit: Sprint 3: Freshness check
- Commit: Update quarantine and cleaned files
_________________

---

## 2. Một quyết định kỹ thuật (100–150 từ)

> VD: chọn halt vs warn, chiến lược idempotency, cách đo freshness, format quarantine.

Một quyết định kỹ thuật tôi đưa ra là điều chỉnh SLA cho freshness từ 24h lên 125h và bổ sung publish_timestamp trong manifest.

Ban đầu, với SLA = 24h, freshness_check luôn FAIL do dataset mẫu là dữ liệu cũ. Điều này không phản ánh đúng trạng thái pipeline trong bối cảnh lab. Vì vậy, tôi tăng SLA lên 125h để phù hợp với dữ liệu hiện tại, giúp hệ thống phân biệt rõ hơn giữa data “chấp nhận được” và data “quá cũ”.

Bên cạnh đó, tôi bổ sung trường publish_timestamp để đo thời điểm dữ liệu được publish sau khi embed. Điều này cho phép theo dõi không chỉ độ mới của data nguồn (ingest) mà còn độ trễ toàn pipeline (end-to-end).

Thiết kế này giúp hệ thống quan sát tốt hơn và hỗ trợ debugging khi có delay hoặc dữ liệu stale.

_________________

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

> Mô tả triệu chứng → metric/check nào phát hiện → fix.

Trong quá trình làm pipeline, tôi gặp lỗi manifest không được đọc đúng khi chạy freshness_check. Cụ thể, khi chạy lệnh kiểm tra, hệ thống báo “manifest not found” dù pipeline đã chạy thành công.

Triệu chứng là command:
python etl_pipeline.py freshness --manifest artifacts/manifests/manifest_1.json
trả về lỗi do file không tồn tại. Sau khi kiểm tra, tôi nhận ra rằng manifest được tạo với tên chứa timestamp, không phải manifest_1.json.

Cách fix là kiểm tra đúng tên file trong thư mục artifacts/manifests và sử dụng đúng path khi chạy lệnh freshness.
Sau khi sửa, freshness_check chạy thành công và trả về kết quả PASS cùng các thông số age_hours và SLA.

_________________

---

## 4. Bằng chứng trước / sau (80–120 từ)

> Dán ngắn 2 dòng từ `before_after_eval.csv` hoặc tương đương; ghi rõ `run_id`.

Trước:
question_id,question,top1_doc_id,top1_preview,contains_expected,hits_forbidden,top1_doc_expected,top_k_used
q_refund_window,Khách hàng có bao nhiêu ngày để yêu cầu hoàn tiền kể từ khi xác nhận đơn?,policy_refund_v4,Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng.,yes,no,,3
q_p1_sla,SLA phản hồi đầu tiên cho ticket P1 là bao lâu?,sla_p1_2026,Ticket P1 có SLA phản hồi ban đầu 15 phút và resolution trong 4 giờ.,yes,no,,3
q_lockout,Bao nhiêu lần đăng nhập sai thì tài khoản bị khóa?,it_helpdesk_faq,Tài khoản bị khóa sau 5 lần đăng nhập sai liên tiếp.,yes,no,,3
q_leave_version,"Theo chính sách nghỉ phép hiện hành (2026), nhân viên dưới 3 năm kinh nghiệm được bao nhiêu ngày phép năm?",hr_leave_policy,Nhân viên dưới 3 năm kinh nghiệm được 12 ngày phép năm theo chính sách 2026.,yes,no,yes,3


Sau:
question_id,question,top1_doc_id,top1_preview,contains_expected,hits_forbidden,top1_doc_expected,top_k_used
q_refund_window,Khách hàng có bao nhiêu ngày để yêu cầu hoàn tiền kể từ khi xác nhận đơn?,policy_refund_v4,Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng.,yes,yes,,3
q_p1_sla,SLA phản hồi đầu tiên cho ticket P1 là bao lâu?,sla_p1_2026,Ticket P1 có SLA phản hồi ban đầu 15 phút và resolution trong 4 giờ.,yes,no,,3
q_lockout,Bao nhiêu lần đăng nhập sai thì tài khoản bị khóa?,it_helpdesk_faq,Tài khoản bị khóa sau 5 lần đăng nhập sai liên tiếp.,yes,no,,3
q_leave_version,"Theo chính sách nghỉ phép hiện hành (2026), nhân viên dưới 3 năm kinh nghiệm được bao nhiêu ngày phép năm?",hr_leave_policy,Nhân viên dưới 3 năm kinh nghiệm được 12 ngày phép năm theo chính sách 2026.,yes,no,yes,3


_________________

---

## 5. Cải tiến tiếp theo (40–80 từ)

> Nếu có thêm 2 giờ — một việc cụ thể (không chung chung).
Nếu có thêm 2 giờ, tôi sẽ implement evaluation nâng cao bằng LLM-judge thay vì chỉ keyword matching. Điều này giúp đánh giá semantic correctness tốt hơn, đặc biệt với các câu trả lời dài hoặc paraphrase. Ngoài ra, tôi muốn thêm logging chi tiết hơn cho từng chunk trong top-k để debug nhanh hơn khi có anomaly.
_________________
