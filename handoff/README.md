# Bộ chuyển giao sinh viên — FocusMate AI

Ngày đóng gói: **05/08/2026**

Đây là điểm bắt đầu duy nhất dành cho sinh viên tiếp nhận dự án. Đọc theo thứ tự:

1. `01_HO_SO_DU_AN.md` — hiểu bài toán, phạm vi và trạng thái hiện tại.
2. `02_BAT_DAU_TRONG_60_PHUT.md` — chạy ứng dụng/test và hoàn thành bài kiểm tra nhận dự án.
3. `03_PHAN_CONG_VA_BACKLOG.md` — chia việc cho nhóm 3 người và issue cần tạo.
4. `04_QUY_TRINH_PILOT.md` — chuẩn bị dữ liệu thật đúng phương pháp.
5. `05_CHECKLIST_NGHIEM_THU.md` — tiêu chí bàn giao hàng tuần và v1.0.0.
6. `templates/` — phiếu đồng ý, nhật ký tuần và báo cáo chất lượng dữ liệu.
7. `../docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md` — bản đồ mã, model, bài báo và
   ranh giới claim/license.

Trợ lý lập trình/AI phải đọc `AGENTS.md`, `CLAUDE.md` và
`docs/06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md` trước khi sửa dự án.

## Hai gói bàn giao

- **Student Starter**: PWA, test, schema, tài liệu và công cụ hệ thống; phù hợp
  để sinh viên bắt đầu chỉnh sửa.
- **Student Full**: thêm mã nền, model và PDF tham khảo; chỉ dùng nội bộ cho tới
  khi hoàn tất kiểm toán quyền phân phối từng artefact.

Mỗi ZIP có tệp `.sha256`; trong gói có `handoff/MANIFEST_SHA256.txt`. Sau khi
giải nén, chạy `powershell -ExecutionPolicy Bypass -File scripts/verify_handoff.ps1`.

## Nguyên tắc bàn giao

- `src/`, `tests/` là mã sản phẩm sinh viên tiếp tục phát triển.
- `data/sample_*` là synthetic; không dùng để tuyên bố độ chính xác.
- `source_code/from_*`, `models/from_*` là tài sản nền của chủ dự án; không nhận
  là đóng góp mới của sinh viên.
- Không commit dữ liệu nhận dạng hoặc dữ liệu pilot chưa được phép công khai.
- Mọi con số báo cáo phải có file đầu vào, phiên bản code và lệnh tái lập.

## Thông tin cuộc thi cần nhớ

- Nhóm dự thi tối đa **3 thành viên**.
- Hạn nộp kho mã nguồn dự kiến: **30/09/2026**.
- Kho đăng ký: `https://github.com/dnphuongictu/SV02`.
- Giấy phép mã nguồn: Apache-2.0.
- Dự thảo cũ từng ghi 4 thành viên; giảng viên/chủ dự án phải chốt lại tối đa 3
  người trước khi phân vai chính thức.
