# Danh mục hai gói bàn giao

## Student Starter

Bao gồm PWA (`src/`), 24 test, schema/sample synthetic, tài liệu, báo cáo, biểu
mẫu, cấu hình Codex/Claude/GitHub và `models/README.md`. Gói cố ý loại:

- `docs/papers/*.pdf` vì có quyền phân phối riêng;
- `models/from_*` và `source_code/from_*` vì chưa cần cho P0;
- dữ liệu người tham gia, export cục bộ, cache, build và secret.

Đây là gói mặc định giao cho sinh viên để bắt đầu sửa PWA.

## Student Full — internal only

Bao gồm toàn bộ Starter cộng với mã nghiên cứu On_Hand_3/Wear OS, model WESAD,
artefact ONNX/TFLite và PDF tham khảo. Gói này phục vụ đọc/tái lập nội bộ, không
được coi là release công khai cho đến khi kiểm toán quyền phân phối từng dataset,
model và PDF hoàn tất.

## Kiểm tra tính toàn vẹn

Mỗi ZIP có tệp `.sha256`. Bên trong mỗi gói có
`handoff/MANIFEST_SHA256.txt`, liệt kê SHA-256 của từng tệp (trừ chính manifest).
Sau khi giải nén:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_handoff.ps1
```

Đối chiếu một tệp thủ công bằng `Get-FileHash -Algorithm SHA256 <path>`.
