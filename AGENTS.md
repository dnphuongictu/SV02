# AGENTS.md — FocusMate AI

Tệp này là hướng dẫn bắt buộc cho mọi coding/research agent làm việc trong dự án.

## Mục tiêu sản phẩm

Xây dựng PWA local-first giúp sinh viên quản lý phiên học và gợi ý nghỉ đúng lúc
mà không làm phiền. Kiến trúc đã chốt là **Hybrid Decision Engine**: safety rule
+ ML nhỏ trên dữ liệu cấu trúc + threshold cá nhân + abstention. SLM chỉ viết lời
nhắc; Wear OS là nghiên cứu tùy chọn.

## Đọc trước khi sửa

1. `README.md`
2. `handoff/01_HO_SO_DU_AN.md`
3. `docs/06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md`
4. `data/README.md` và `data/study_session.schema.json`
5. `THIRD_PARTY_NOTICES.md`
6. `docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md`

## Lệnh chuẩn

```powershell
npm test
python -m http.server 8000 -d src
```

Baseline bàn giao: 24/24 test đạt. Không hoàn thành công việc nếu làm test cũ
thất bại hoặc thay đổi hành vi mà không thêm/sửa test và tài liệu tương ứng.

## Phạm vi tệp

- Sửa sản phẩm tại `src/`, test tại `tests/`, schema/sample tại `data/`.
- Báo cáo tại `reports/`; tài liệu kỹ thuật tại `docs/` hoặc `handoff/`.
- `source_code/from_*`, `models/from_*`, `docs/papers/*.pdf` là reference. Không
  sửa/copy vào production trừ khi nhiệm vụ yêu cầu rõ và provenance/license đã kiểm tra.
- Không commit dữ liệu pilot, PII, secret, build/cache hoặc bảng nối danh tính.

## Ràng buộc nghiên cứu không được vi phạm

- `need_break` là nhãn độc lập hỏi trước quyết định.
- `break_suggested` là prediction; không được sao chép thành ground truth.
- `accepted` là hành vi, không đồng nghĩa trực tiếp với prediction đúng/sai.
- Synthetic chỉ dùng test/demo.
- Đánh giá ML theo người hoặc thời gian; không random split từng dòng.
- Báo precision, recall, F1, balanced accuracy và confusion matrix; không chỉ accuracy.
- Mọi số liệu phải có input, commit/version, config và lệnh tái lập.
- Không quảng bá WESAD 0,9124 là độ chính xác FocusMate.
- ACC-only WAUC 0,5354 là proxy yếu; không bật production mặc định.

## Thứ tự ưu tiên bắt buộc

1. Check-in/nhãn `interrupt_ok`, `useful`, `break_taken`.
2. End-to-end tests và CI.
3. Pilot được duyệt.
4. Logistic/Tree/RF hoặc boosting và đánh giá đúng.
5. Dashboard nâng cao/release.

Không ưu tiên chatbot, cloud hoặc Wear OS trước khi P0 hoàn tất.

## Quy ước implementation

- Giữ PWA chạy không framework nếu chưa có lý do đo được để thêm framework.
- Module logic phải thuần và kiểm thử được; DOM/localStorage chỉ nối ở lớp app.
- Version schema, rule và model trong dữ liệu/output.
- Khi model thiếu dữ liệu/không chắc chắn, fallback Rule v1 hoặc abstain.
- Ưu tiên precision và giảm lời nhắc; mục tiêu không phải accuracy cao giả tạo.
- Mọi thay đổi schema phải cập nhật sample, validator, export, docs và migration.
- Mọi thay đổi artefact/model/reference phải cập nhật danh mục artefact và provenance.
- Giữ `SPDX-License-Identifier: Apache-2.0` trên mã thuộc sở hữu dự án.

## Definition of Done cho một task

- Hành vi có test và test đạt.
- Không làm lệch schema/methodology/license.
- README/changelog/report được cập nhật nếu người dùng hoặc kết quả thay đổi.
- Có mô tả giới hạn và ca biên.
- Không đưa claim mới nếu chưa có dữ liệu tái lập.

## Trạng thái và blocker hiện tại

- PWA timer/offline, import/validator CSV, dashboard baseline và 24 test đã có.
- Chưa có nhãn mở rộng, CI, pilot hoặc model cá nhân hóa.
- Nhóm thi phải chốt tối đa 3 thành viên.
- Thay đổi cục bộ cần được đồng bộ vào GitHub `dnphuongictu/SV02` bằng issue/PR.
