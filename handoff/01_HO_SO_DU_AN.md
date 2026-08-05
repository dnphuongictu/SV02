# Hồ sơ dự án FocusMate AI

## 1. Bài toán

Các bộ hẹn giờ cố định thường nhắc sau cùng một khoảng thời gian, bất kể người
học đang mệt, đang tập trung sâu hay vừa từ chối lời nhắc. FocusMate nghiên cứu
cách gợi ý nghỉ theo ngữ cảnh để giảm lời nhắc không cần thiết.

Thông điệp sản phẩm:

> Một bộ hẹn giờ biết khi nào nên im lặng.

## 2. Người dùng và giá trị

- Người dùng chính: sinh viên tự học 30-120 phút.
- Giá trị: quản lý phiên học, gợi ý nghỉ có lý do, chống nhắc lặp, xem lại dữ
  liệu và giữ dữ liệu trên thiết bị.
- Không phải sản phẩm chẩn đoán stress, sức khỏe hoặc năng lực học tập.

## 3. Câu hỏi nghiên cứu

- RQ1: Rule theo thời lượng, mệt và tập trung có precision tốt hơn Fixed-45 không?
- RQ2: Cooldown 20 phút ảnh hưởng thế nào đến số lời nhắc và acceptance rate?
- RQ3: Khi đủ dữ liệu, model cá nhân hóa có cải thiện F1 mà không tăng làm phiền?

## 4. Kiến trúc

```text
PWA local-first
  -> timer + metadata phiên
  -> phản hồi need_break độc lập
  -> Fixed-45 / Rule v1 / Personal ML
  -> safety gate + cooldown + explanation
  -> accepted/useful feedback
  -> dashboard và export CSV
```

SLM nếu được thêm chỉ viết lại lời nhắc. Nó không làm bộ quyết định chính.

## 5. Trạng thái khi bàn giao

### Đã có

- PWA responsive, manifest và service worker offline.
- Timer start/pause/resume/finish, lưu và khôi phục trạng thái.
- Rule v1.0 và cooldown 20 phút.
- Phản hồi `need_break` trước quyết định, `accepted` sau quyết định.
- Nhật ký localStorage, dữ liệu synthetic và xuất CSV theo schema v1.
- Import/validator CSV và dashboard baseline Fixed-45/Rule v1 context.
- 24 test: CSV, metric, rule engine và timer, tất cả đang đạt.
- GitHub Actions CI và script kiểm tra gói bàn giao.
- Apache-2.0, SPDX header, changelog và third-party notices.
- Báo cáo kết quả kế thừa từ On_Hand_3/On_Hand_6.

### Chưa có

- Check-in chủ động ở ngưỡng 45 phút.
- Test end-to-end trình duyệt.
- Dữ liệu pilot thật.
- Model cá nhân hóa và model card.
- Release v0.1.0/v1.0.0.

## 6. Kết quả kế thừa được phép trích dẫn

- WESAD SVM HRV+ACC macro-F1 0,9124: chỉ là stress-proxy, không phải độ chính xác
  nhắc nghỉ.
- WAUC MLP ACC-only macro-F1 0,5354: tín hiệu cognitive-load yếu; Wear OS chỉ là
  nhánh nghiên cứu tùy chọn.
- On_Hand_6 trên 200 ngữ cảnh: Random Forest 75,0%, hybrid 63,5%, policy 54,5%,
  SLM 48,0%. Đây là căn cứ chọn ML nhỏ cho dữ liệu có cấu trúc.

Chi tiết và giới hạn nằm tại `reports/01_KET_QUA_KE_THUA_2026-08-05.md`.

## 7. Quyền sở hữu và giấy phép

Chủ dự án xác nhận sở hữu mã FocusMate, On_Hand_3 và Wear OS reference, cấp phép
Apache-2.0. Dataset, PDF, runtime, thư viện và model dẫn xuất vẫn phải tuân thủ
điều khoản nguồn; xem `THIRD_PARTY_NOTICES.md`.

## 8. Definition of Done sản phẩm

- Người mới clone, chạy test và mở ứng dụng trong tối đa 10 phút.
- PWA hoạt động offline, không mất phiên khi reload.
- Fixed-45, Rule và ML chạy trên cùng dữ liệu đánh giá.
- Có dữ liệu pilot hợp lệ, confusion matrix, FP/FN và hạn chế.
- Không có PII trong repo; người dùng xuất/xóa được dữ liệu.
- CI xanh; có release SemVer, checksum, hướng dẫn và video demo.
