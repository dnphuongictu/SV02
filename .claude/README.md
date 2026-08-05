# Dùng Claude Code với FocusMate AI

`CLAUDE.md` ở thư mục gốc là điểm vào cho Claude Code và luôn trỏ về
`AGENTS.md` làm nguồn quy tắc chính. Khi bắt đầu phiên mới, dùng prompt:

```text
Đọc CLAUDE.md, AGENTS.md và các tài liệu bắt buộc. Xác nhận test baseline, phạm
vi được sửa và ràng buộc nghiên cứu trước khi triển khai. Mọi thay đổi phải có
test, cập nhật tài liệu liên quan và chạy npm test.
```

Không yêu cầu Claude huấn luyện model trước pilot hợp lệ; không đưa PII/secret
vào context; không sửa `source_code/from_*`, `models/from_*` hoặc PDF nếu task
không yêu cầu rõ và chưa kiểm tra provenance/license.
