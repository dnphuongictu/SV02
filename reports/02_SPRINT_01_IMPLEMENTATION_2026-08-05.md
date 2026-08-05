# Báo cáo triển khai Sprint 1

Ngày thực hiện: **05/08/2026**

## Mục tiêu

Chuyển baseline nhập dữ liệu thủ công thành luồng phiên học sử dụng được và tạo
nền PWA local-first theo kế hoạch dự thi.

## Đã hoàn thành

- Tách logic bộ đếm thuần tại `src/js/timer.js`.
- Bắt đầu, tạm dừng, tiếp tục, kết thúc và cộng dồn thời gian chính xác.
- Lưu/khôi phục phiên đang chạy và phản hồi chưa hoàn tất bằng `localStorage`.
- Chỉ ghi phiên từ 5 phút để khớp miền hợp lệ hiện tại của Rule v1.0.
- Tách đúng thứ tự: người dùng khai báo `need_break`, hệ thống mới quyết định,
  sau đó người dùng mới chọn chấp nhận hoặc hoãn lời nhắc.
- Xuất CSV với tên cột snake_case khớp `study_session.schema.json`.
- Bổ sung `goal`, `duration_minutes` và `risk_score` vào schema.
- Thêm manifest, service worker, icon, offline status, install prompt và thông báo.
- Làm mới giao diện responsive và hỗ trợ `prefers-reduced-motion`.
- Thêm `CHANGELOG.md`.

## Kiểm chứng

| Kiểm tra | Kết quả |
|---|---|
| Rule engine | 7/7 test đạt |
| Timer | 6/6 test đạt |
| Tổng | 13/13 test đạt |
| JavaScript syntax | `node --check` đạt cho app, storage, timer và service worker |
| HTTP smoke test | `GET /` trả 200 |
| Asset PWA | Tất cả 8 tài sản app-shell tồn tại |
| Visual smoke test | Edge headless 1440×1100 hiển thị đúng, không lộ panel ẩn |

## Chưa hoàn thành

- Chưa có kiểm thử tự động DOM/end-to-end cho thao tác người dùng.
- Chưa có cơ chế check-in chủ động khi timer đạt ngưỡng 45 phút.
- Chưa có import CSV, dashboard confusion matrix hoặc model cá nhân hóa.
- Chưa có pilot thật.
- Đã chọn Apache-2.0 sau xác nhận của chủ sở hữu; quyền phân phối dataset/model/PDF
  bên thứ ba vẫn cần được kiểm toán trước release.

## Sprint tiếp theo đề xuất

1. Thêm kiểm thử end-to-end cho start/pause/reload/finish/feedback.
2. Thêm check-in ở phút 45 và notification có hành động hoãn/nghỉ.
3. Viết module metric và dashboard so sánh Fixed-45 với Rule v1.
4. Thêm validator/import CSV trước khi bắt đầu pilot.
