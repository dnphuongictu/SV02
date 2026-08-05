# Dữ liệu FocusMate AI

## Cấu trúc

```text
data/
  sample_study_sessions.csv   dữ liệu synthetic để chạy thử
  study_session.schema.json   schema máy đọc phiên bản 1
  weekly_logs/                dữ liệu pilot cục bộ, không commit dữ liệu nhạy cảm
  exports/                    bản xuất từ ứng dụng, mặc định không commit
```

## Từ điển dữ liệu

| Trường | Kiểu/miền | Ý nghĩa |
|---|---|---|
| `session_id` | chuỗi duy nhất | Mã phiên, không chứa danh tính |
| `student_code` | chuỗi ẩn danh | Ví dụ `P001`; không dùng mã sinh viên thật trong dữ liệu công khai |
| `start_time`, `end_time` | ISO 8601 | Thời gian bắt đầu/kết thúc |
| `subject` | chuỗi | Môn/chủ đề tổng quát, không ghi nội dung nhạy cảm |
| `task_type` | enum ứng dụng | reading, coding, debugging, writing hoặc exercise |
| `goal` | chuỗi ≤120 ký tự | Mục tiêu phiên, không bắt buộc |
| `duration_minutes` | 5-240 | Thời lượng tính từ timer; phiên ngắn hơn không ghi vào dữ liệu nghiên cứu |
| `focus_score` | 1-5 | Tự đánh giá sau phiên |
| `fatigue_score` | 1-10 | Tự đánh giá sau phiên |
| `need_break` | boolean | Nhãn độc lập: người học thực sự có cần nghỉ không |
| `break_suggested` | boolean | Dự đoán/đầu ra của hệ thống |
| `accepted` | boolean/null | Hành vi sau lời nhắc; null nếu không nhắc/chưa trả lời |
| `response_time` | ISO 8601/null | Thời điểm chấp nhận/từ chối, dùng tính cooldown |
| `risk_score` | 0-100 | Điểm giải thích của rule, không phải xác suất y khoa |
| `rule_version` | chuỗi | Phiên bản thuật toán tạo quyết định |
| `decision_reason` | chuỗi | Luật/lý do đã kích hoạt |
| `note` | chuỗi ≤160 ký tự | Ghi chú không nhạy cảm, không bắt buộc |

## Ba trường tuyệt đối không được trộn

- `need_break`: nhãn tự báo độc lập, dùng đánh giá dự đoán.
- `break_suggested`: đầu ra thuật toán; không sao chép sang `need_break`.
- `accepted`: hành vi sau lời nhắc; từ chối không tự động có nghĩa dự đoán sai.

## Quy tắc chất lượng và riêng tư

- `end_time` phải sau `start_time`; `duration_minutes` phải khớp chênh lệch thời gian trong sai số làm tròn hợp lý.
- Không điền giá trị thiếu bằng 0.
- Không lưu tên, email, điện thoại, mã sinh viên thật, nội dung màn hình, camera,
  microphone hoặc vị trí.
- Bảng nối mã nghiên cứu với danh tính, nếu thật sự cần, phải mã hóa và lưu riêng;
  không đưa lên GitHub hoặc gói bàn giao.
- Khi dùng ML, chia dữ liệu theo người hoặc theo thời gian; không chia ngẫu nhiên
  từng dòng khiến cùng một người xuất hiện ở cả train và test.

Quy trình pilot và mẫu đồng ý nằm trong `handoff/04_QUY_TRINH_PILOT.md` và
`handoff/templates/PHIEU_DONG_Y_THAM_GIA.md`.
