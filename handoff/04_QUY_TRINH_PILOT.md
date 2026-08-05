# Quy trình pilot dữ liệu FocusMate

Tài liệu này là quy trình kỹ thuật/nghiên cứu nội bộ, không thay thế phê duyệt
đạo đức hoặc quy định của trường. Giảng viên phải duyệt trước khi thu thật.

## Mục tiêu

- 5-10 người tự nguyện.
- 10-20 phiên/người trong 1-2 tuần.
- Tổng mục tiêu 100-150 phiên hợp lệ.
- Không tuyên bố mẫu đại diện cho toàn bộ sinh viên.

## Trước khi thu

1. Chốt schema v1 và version ứng dụng/rule.
2. Dùng 20 phiên synthetic/kiểm thử để chạy validator và metric.
3. Giảng viên duyệt phiếu đồng ý, cách rút lui và xóa dữ liệu.
4. Tạo mã `P001`, `P002`; không dùng mã sinh viên thật.
5. Nếu cần bảng nối danh tính, lưu mã hóa ở nơi riêng do giảng viên quản lý.
6. Kiểm tra export không chứa tên, email, điện thoại hoặc nội dung học riêng tư.

## Hướng dẫn người tham gia

- Chọn môn/nhiệm vụ tổng quát, không ghi nội dung nhạy cảm.
- Dùng timer cho phiên học tự nhiên từ 5-240 phút.
- Sau phiên, trả lời focus, fatigue và `need_break` trước khi xem quyết định.
- Nếu có lời nhắc, chọn nghỉ hoặc để sau đúng với hành vi thực tế.
- Không cố tạo dữ liệu “đẹp” và không thay đổi câu trả lời theo dự đoán.
- Có quyền dừng, không trả lời, yêu cầu xuất hoặc xóa dữ liệu.

## Kiểm tra chất lượng mỗi ngày

- Số dòng và số mã người tham gia.
- Session ID trùng.
- Thiếu trường bắt buộc hoặc ngoài miền.
- `end_time <= start_time` hoặc duration không hợp lý.
- `accepted` có giá trị khi `break_suggested=false`.
- Phân bố `need_break`; cảnh báo nếu chỉ có một lớp.
- Số phiên/người; không để một người chi phối toàn bộ dữ liệu.

Không sửa im lặng dữ liệu gốc. Lưu bản raw read-only, mọi làm sạch tạo file mới
và nhật ký thay đổi.

## Tổ chức dữ liệu cục bộ

```text
data_local/                 KHÔNG commit
  consent/                  phiếu đồng ý, tách khỏi dữ liệu
  raw/YYYY-MM-DD/           export gốc read-only
  cleaned/v1/               dữ liệu đã validate/làm sạch
  deletion_log/             yêu cầu và xác nhận xóa
reports/
  data_quality.md           chỉ thống kê ẩn danh được phép công bố
```

## Đánh giá

- Ground truth: `need_break`.
- Prediction: `break_suggested` cho Fixed-45/Rule/ML.
- Metric: confusion matrix, precision, recall, F1, lời nhắc/giờ.
- Hành vi phụ: acceptance rate và useful rate nếu bổ sung câu hỏi hữu ích.
- Báo theo từng người và tổng; dùng khoảng tin cậy khi đủ điều kiện.
- ML phải chia theo người hoặc theo thời gian và không chỉnh theo tập test.

## Dừng pilot nếu

- Phát hiện PII trong export/repo.
- Không chứng minh được đồng ý tham gia hoặc quyền xóa.
- Ứng dụng gán prediction thành ground truth.
- Mất/méo dữ liệu do schema thay đổi không version.
- Người tham gia báo khó chịu, rủi ro hoặc muốn rút lui.
