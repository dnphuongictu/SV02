# Dùng Codex với FocusMate AI

Codex phải coi `AGENTS.md` ở thư mục gốc là nguồn chỉ dẫn bắt buộc. Trước task
đầu tiên, yêu cầu Codex đọc theo thứ tự trong mục “Đọc trước khi sửa”, kiểm tra
`npm test`, rồi mới đề xuất file cần thay đổi.

Prompt khởi động gợi ý:

```text
Đọc AGENTS.md và các tài liệu bắt buộc. Hãy tóm tắt phạm vi task, các ràng buộc
schema/phương pháp/license, nêu file dự kiến sửa, triển khai kèm test và chạy
npm test. Không sửa thư mục from_* hoặc dùng synthetic/WESAD làm claim sản phẩm.
```

Với task dữ liệu/ML, thêm yêu cầu:

```text
Phân biệt need_break, break_suggested và accepted; chia đánh giá theo người hoặc
thời gian; báo confusion matrix, precision, recall, F1 và balanced accuracy.
```

Không dán PII, dữ liệu pilot, secret hoặc bảng nối danh tính vào hội thoại. Codex
không tự có quyền phát hành, xóa dữ liệu hay thay đổi artefact reference.
