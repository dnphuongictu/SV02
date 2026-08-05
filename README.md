# FocusMate AI

[![CI](https://github.com/dnphuongictu/SV02/actions/workflows/ci.yml/badge.svg)](https://github.com/dnphuongictu/SV02/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

FocusMate AI là PWA local-first giúp sinh viên quản lý phiên học và nhận gợi ý
nghỉ theo ngữ cảnh. Dữ liệu mặc định chỉ nằm trong trình duyệt; quyết định hiện
tại dùng Rule v1 có giải thích và cooldown, không dùng chatbot để quyết định.

> Một bộ hẹn giờ biết khi nào nên im lặng.

## Chạy trong 5 phút

Yêu cầu: Python 3, Node.js 18+ và một trình duyệt hiện đại.

```powershell
npm test
python -m http.server 8000 -d src
```

Mở `http://localhost:8000`. Kết quả chuẩn ngày 05/08/2026: **24/24 test đạt**.
Không cần cài dependency npm, GPU, dịch vụ cloud hoặc khóa API.

## MVP đã có

- Timer start/pause/resume/finish, khôi phục sau reload và hoạt động offline.
- Thu `need_break` độc lập trước quyết định; ghi nhận phản hồi sau lời nhắc.
- Rule v1.0 có lý do, điểm rủi ro và cooldown 20 phút.
- Nhật ký local-first; import/export CSV schema v1.
- Validator từ chối PII header, thiếu cột, sai miền, thời gian ngược và mã trùng.
- Dashboard so sánh Fixed-45 với Rule v1 bằng confusion matrix, precision,
  recall, F1 và balanced accuracy.
- Dữ liệu synthetic để demo/test và 24 kiểm thử tự động.

Chưa có dữ liệu pilot thật hoặc model cá nhân hóa. Bốn dòng synthetic không phải
bằng chứng về độ chính xác ngoài thực tế.

## Kiến trúc đã chốt

```text
PWA local-first
  -> timer + ngữ cảnh phiên
  -> nhãn need_break độc lập
  -> Rule v1 (cold start) / model tabular nhỏ (khi đủ dữ liệu)
  -> safety gate + threshold cá nhân + abstention + cooldown
  -> lời nhắc có giải thích
  -> feedback + dashboard + CSV
```

SLM nếu được thêm chỉ viết lại câu chữ. Wear OS/ACC là nhánh nghiên cứu tùy
chọn, tắt mặc định. Đây không phải ứng dụng chẩn đoán stress hay sức khỏe.

## Đọc và sửa ở đâu

| Vị trí | Vai trò | Sinh viên |
|---|---|---|
| `src/` | PWA và logic sản phẩm | Được sửa, phải có test |
| `tests/` | Hợp đồng hành vi | Thêm/sửa cùng tính năng |
| `data/` | Schema, sample synthetic, quy tắc dữ liệu | Được sửa đồng bộ validator/export/docs |
| `handoff/` | Lộ trình nhận dự án và biểu mẫu | Bắt đầu đọc tại đây |
| `docs/`, `reports/` | Kiến trúc, phương pháp và kết quả | Cập nhật khi claim/hành vi đổi |
| `source_code/from_*` | Mã nghiên cứu nền | Chỉ tham khảo, không sửa mặc định |
| `models/from_*` | Model/output thử nghiệm nền | Chỉ tham khảo, không bật production |
| `docs/papers/*.pdf` | Bài báo tham khảo | Không đưa vào release công khai |

Danh mục chi tiết, kích thước, ý nghĩa và giới hạn từng artefact nằm tại
[`docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md`](docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md).

## Lộ trình đọc cho nhóm sinh viên

1. [`handoff/README.md`](handoff/README.md) — điểm vào duy nhất của bộ bàn giao.
2. [`handoff/02_BAT_DAU_TRONG_60_PHUT.md`](handoff/02_BAT_DAU_TRONG_60_PHUT.md) — chạy và kiểm tra nhận dự án.
3. [`data/README.md`](data/README.md) — hợp đồng dữ liệu và quy tắc nhãn.
4. [`docs/06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md`](docs/06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md) — Hybrid Decision Engine và đánh giá ML.
5. [`CONTRIBUTING.md`](CONTRIBUTING.md) — branch, test, commit và pull request.

## Dùng Codex hoặc Claude

- Codex và coding agent: đọc `AGENTS.md` trước khi sửa. Hướng dẫn khởi động tại
  `.codex/README.md`.
- Claude Code: đọc `CLAUDE.md`, sau đó tuân theo `AGENTS.md`. Hướng dẫn tại
  `.claude/README.md`.
- Luôn yêu cầu trợ lý nêu file dự kiến sửa, chạy `npm test`, và phân biệt rõ
  “đã đo”, “mục tiêu” và “giả thuyết”. Không đưa dữ liệu pilot/PII/secret vào
  prompt hoặc commit.

## Ưu tiên tiếp theo

1. Thêm check-in và nhãn `interrupt_ok`, `useful`, `break_taken`.
2. Thêm E2E trình duyệt và giữ CI xanh.
3. Thực hiện pilot đã được phê duyệt.
4. Chỉ sau đó mới huấn luyện Logistic/Tree/RF hoặc boosting, đánh giá theo người
   hoặc thời gian và thêm abstention.
5. Hoàn thiện dashboard, model/data card và release.

Không ưu tiên chatbot, cloud hoặc Wear OS trước các hạng mục dữ liệu P0.

## Giấy phép và phát hành

Mã do chủ dự án sở hữu được phát hành theo Apache License 2.0. Dataset, model,
PDF và dependency bên thứ ba vẫn theo điều khoản nguồn; xem
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Gói Starter phù hợp để phát
triển PWA. Gói Full chỉ dùng chuyển giao nội bộ cho tới khi hoàn tất kiểm toán
quyền phân phối artefact tham khảo.

Kho dự thi: <https://github.com/dnphuongictu/SV02>. Các thay đổi cục bộ phải được
đồng bộ bằng issue/branch/pull request; nhóm thi cần chốt tối đa 3 thành viên.
