# CLAUDE.md — Hướng dẫn làm việc với FocusMate AI

Luôn đọc và tuân thủ `AGENTS.md`; đây là nguồn quy tắc chính của dự án.

## Bối cảnh ngắn

FocusMate AI là PWA local-first gợi ý nghỉ học theo ngữ cảnh. Dự án không phải
ứng dụng chẩn đoán stress. Kiến trúc chính thức nằm tại
`docs/06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md`.

## Các quyết định đã chốt

- Production: safety rule + model tabular nhỏ + threshold cá nhân + abstention.
- Cold start/fallback: Rule v1.0.
- SLM: chỉ tạo câu chữ, không quyết định.
- Wear/ACC: experimental, tắt mặc định, có `UNKNOWN`.
- Metric ưu tiên: precision, F1, balanced accuracy, lời nhắc/giờ và useful rate.
- Pilot 100-150 điểm chỉ kiểm tra quy trình; đánh giá chính hướng tới 300-500
  điểm từ 15-30 người nếu điều kiện cho phép.

## Không được làm

- Không tạo số liệu, người tham gia hoặc kết quả giả.
- Không dùng synthetic/WESAD làm FocusMate accuracy.
- Không train model trước validator, metric và pilot hợp lệ.
- Không dùng `break_suggested` làm nhãn.
- Không đưa PII/dữ liệu pilot lên repo.
- Không sửa tài sản `from_*` trừ khi nhiệm vụ yêu cầu trực tiếp.

## Khi thực hiện task

1. Đọc schema, test và tài liệu liên quan trước khi sửa.
2. Giữ thay đổi nhỏ, tái lập được và có test.
3. Chạy `npm test` trước khi bàn giao.
4. Cập nhật changelog/report nếu hành vi hoặc kết quả thay đổi.
5. Phân biệt rõ “đã đo”, “mục tiêu” và “giả thuyết”.
6. Khi thêm/xóa model, dữ liệu hoặc reference, cập nhật
   `docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md` và notice liên quan.

## Ưu tiên tiếp theo

Check-in/nhãn mới → E2E/CI → pilot → model nhỏ → dashboard nâng cao/release.

Validator/import CSV và metric Fixed-45/Rule cơ bản đã hoàn thành trong MVP ngày
05/08/2026; không mở lại hai hạng mục này nếu không có lỗi hoặc yêu cầu mới.
