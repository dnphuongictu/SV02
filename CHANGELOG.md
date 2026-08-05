# Changelog

Mọi thay đổi đáng chú ý của FocusMate AI được ghi tại đây. Dự án dự kiến sử dụng
Semantic Versioning sau khi hoàn tất kiểm toán giấy phép và tạo release đầu tiên.

## Unreleased

### Added

- Apache License 2.0, SPDX headers, licensing policy and third-party notices.
- Kế hoạch Hybrid Decision Engine dựa trên kết quả thật và hướng dẫn thống nhất
  cho Claude/coding agents tại `CLAUDE.md`, `AGENTS.md`.
- Bộ đếm phiên học có bắt đầu, tạm dừng, tiếp tục và kết thúc.
- Khôi phục phiên đang chạy và phản hồi chưa hoàn tất từ `localStorage`.
- Luồng phản hồi độc lập `need_break` trước khi ghi nhận quyết định/chấp nhận.
- PWA manifest, service worker, trạng thái offline và nút cài đặt.
- Sáu kiểm thử cho logic bộ đếm, nâng tổng số test từ 7 lên 13.
- Bộ nhập/validator CSV local-first, từ chối header PII, thiếu cột, sai miền,
  thời gian ngược và mã phiên trùng.
- Dashboard baseline so sánh Fixed-45 và Rule v1 context bằng confusion matrix,
  precision, recall, F1, balanced accuracy và số lời nhắc.
- Mười một kiểm thử CSV/metric, nâng tổng số test từ 13 lên 24.
- Báo cáo kết quả kế thừa và kế hoạch dự thi PMMN tích hợp AI 2026.
- README mới, danh mục kiến trúc/artefact và onboarding cho Codex/Claude.
- GitHub Actions CI, issue/PR template, hướng dẫn đóng góp, bảo mật và cộng tác.
- Script kiểm tra cùng hai profile đóng gói Starter/Full có checksum.

### Changed

- Giao diện baseline nhập tay được chuyển thành luồng phiên học thực tế.
- Mẫu báo cáo phân biệt kết quả FocusMate, kết quả kế thừa và dữ liệu synthetic.
- Ngưỡng trong tài liệu model được đồng bộ với Rule v1.0 ở mức 45 phút.
- Phiên ngắn hơn 5 phút không được nhập vào dữ liệu nghiên cứu.
- Bộ test được gom qua `tests/all.test.mjs`; baseline bàn giao là 24 test đạt.

### Known limitations

- Chưa có dữ liệu pilot thật hoặc mô hình cá nhân hóa.
- Dashboard Rule v1 hiện đánh giá điều kiện ngữ cảnh của từng dòng và không replay
  cooldown lịch sử; không dùng kết quả này để tuyên bố hiệu quả cooldown.
- Dataset/model/PDF kế thừa chưa hoàn tất kiểm toán quyền phân phối và không nên
  nằm trong release cho đến khi được xác minh.
