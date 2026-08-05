# Đóng góp cho FocusMate AI

## Bắt đầu

1. Đọc `AGENTS.md` và bộ tài liệu bắt buộc được liệt kê trong đó.
2. Tạo issue mô tả giá trị người dùng, tiêu chí nghiệm thu và dữ liệu bị ảnh hưởng.
3. Tạo branch ngắn từ nhánh chính, ví dụ `feat/check-in-labels`.
4. Chạy `npm test` trước và sau khi sửa.

Ứng dụng chạy bằng `python -m http.server 8000 -d src`, không cần `npm install`.

## Quy ước thay đổi

- Logic thuần nằm trong module riêng và có unit test; `app.js` chỉ nối DOM/storage.
- Thay schema phải đồng bộ sample, validator, import/export, docs và migration.
- Không commit participant-level data, PII, secret, build/cache hoặc identity map.
- Không sửa/copy `from_*`, model hoặc PDF vào production khi chưa kiểm tra nguồn.
- Mã do dự án sở hữu giữ dòng `SPDX-License-Identifier: Apache-2.0`.
- Claim thực nghiệm phải ghi input, phiên bản code, config, lệnh và protocol.

## Pull request

PR nên nhỏ, liên kết issue và có:

- Mô tả hành vi trước/sau và giới hạn.
- Danh sách test đã chạy; cập nhật test nếu hành vi đổi.
- Ảnh/video khi UI đổi.
- Ghi chú schema, privacy, license và provenance nếu liên quan.
- Cập nhật README/changelog/report khi trải nghiệm hoặc kết quả đổi.

Không merge khi CI đỏ. Ít nhất một thành viên khác review thay đổi dữ liệu/metric.
