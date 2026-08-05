# Kiến trúc và danh mục artefact

Ngày kiểm kê: **05/08/2026**. Tài liệu này giúp người tiếp nhận biết artefact nào
dùng để chạy sản phẩm, artefact nào chỉ dùng nghiên cứu và claim nào được phép.

## 1. Thành phần sản phẩm

| Thành phần | Vai trò | Hợp đồng chính |
|---|---|---|
| `src/index.html`, `styles.css` | UI PWA | Không chứa logic quyết định |
| `src/js/timer.js` | State machine phiên học | Thời gian pause không được tính |
| `src/js/ruleEngine.js` | Rule v1 và cooldown | Thuần, có giải thích, fallback cold-start |
| `src/js/csv.js` | Parse/import/validate CSV | Không ghi dữ liệu nếu validation thất bại |
| `src/js/metrics.js` | Fixed-45, Rule v1 và metric | So sánh trên cùng tập, không chia cho 0 |
| `src/js/storage.js` | Adapter localStorage | DOM/storage không rò vào module logic |
| `src/js/app.js` | Nối UI với các module | Không nhân bản logic rule/metric |
| `src/manifest.webmanifest`, `sw.js` | Cài đặt và offline | Cập nhật cache khi asset đổi |
| `tests/*.test.mjs` | Regression suite | Baseline hiện tại 24/24 |

## 2. Hợp đồng dữ liệu

- `data/study_session.schema.json`: schema machine-readable v1.
- `data/sample_study_sessions.csv`: bốn phiên synthetic, chỉ demo/test.
- `data/README.md`: data dictionary, quy tắc nhãn, privacy và migration.
- `data/weekly_logs/`, `data/exports/`: bị Git bỏ qua; không commit dữ liệu mức
  người tham gia.

Ba biến không được đánh đồng:

- `need_break`: ground truth tự báo cáo, hỏi trước quyết định.
- `break_suggested`: prediction của hệ thống.
- `accepted`: hành vi sau lời nhắc, không tự động là đúng/sai.

## 3. Artefact nghiên cứu nền

### Mã nguồn tham khảo

| Vị trí | Quy mô kiểm kê | Mục đích | Trạng thái |
|---|---:|---|---|
| `source_code/from_On_Hand_3/` | 28 tệp, 130.499 byte | Tiền xử lý và thí nghiệm Python | Reference; không phải runtime PWA |
| `source_code/from_On_Hand_3_android_wear/` | 26 tệp, 163.579 byte | Prototype Wear OS | Experimental; tắt mặc định |

Chỉ lấy ý tưởng/đoạn mã sang production khi provenance, license, test và lý do
sản phẩm đã được ghi nhận. Không sửa trực tiếp thư mục `from_*` trong task PWA.

### Model WESAD kế thừa

| Model | Accuracy | Balanced accuracy | Macro-F1 | Kích thước |
|---|---:|---:|---:|---:|
| MLP ACC | 0,8700 | 0,8389 | 0,8471 | 72.881 B |
| MLP HRV | 0,8828 | 0,8754 | 0,8693 | 83.681 B |
| MLP HRV+ACC | 0,9075 | 0,8994 | 0,8937 | 94.849 B |
| SVM ACC | 0,8464 | 0,8313 | 0,8292 | 31.197 B |
| SVM HRV | 0,8929 | 0,8918 | 0,8838 | 34.877 B |
| SVM HRV+ACC | 0,9224 | 0,9159 | 0,9124 | 44.477 B |

Các số trên là kết quả **stress-proxy WESAD**, không phải độ chính xác của
FocusMate, không có giá trị xác nhận nhắc nghỉ học. Dùng chúng để hiểu pipeline
và tái lập nghiên cứu nền, không dùng để quảng bá sản phẩm.

### TFLite rehearsal

`models/from_On_Hand_3/tflite_rehearsal/` có 20 artefact chính gồm ONNX, sáu
biến thể TFLite, calibration array, schema FlatBuffers và báo cáo đối chiếu.
Toàn bộ `models/` có 37 tệp, khoảng 13,78 MB.

| Biến thể | Kích thước | Kết quả đã đo trên rehearsal |
|---|---:|---|
| FP32 | 57.412 B | accuracy 0,6239; balanced accuracy 0,6600; macro-F1 0,6217 |
| Full-int8 | 19.864 B | accuracy 0,2906; balanced accuracy 0,3978; macro-F1 0,2475 |

Đây là rehearsal desktop trên stress-proxy, không phải LOSO, không phải benchmark
thiết bị và không phải bằng chứng production. Kết quả int8 suy giảm mạnh nên
không bật model này trong PWA/Wear OS.

### Bài báo

`docs/papers/` có bảy PDF về workload-aware augmentation, wristband cognitive
load, interruptibility, mobile attention, HRV, on-device AI và TinyML. Đọc thứ tự
tại `docs/papers/README.md`. PDF không thuộc Apache-2.0 của kho; chỉ nằm trong gói
Full chuyển giao nội bộ cho tới khi xác minh quyền phân phối từng bài.

## 4. Artefact vận hành và bàn giao

| Artefact | Ý nghĩa |
|---|---|
| `AGENTS.md` | Nguồn quy tắc bắt buộc cho Codex/coding agents |
| `CLAUDE.md` | Cầu nối cho Claude, trỏ về `AGENTS.md` |
| `.github/workflows/ci.yml` | Chạy regression suite trên push/PR |
| `scripts/verify_handoff.ps1` | Kiểm tra file bắt buộc, JSON, test và SPDX |
| `handoff/` | Hồ sơ, onboarding, backlog, pilot, checklist và biểu mẫu |
| `demo/*Starter*.zip` | Gói nhẹ để học và phát triển PWA |
| `demo/*Full*.zip` | Gói nội bộ có source/model/PDF tham khảo |
| `*.sha256` | Checksum kiểm tra gói không bị thay đổi |

## 5. Quy tắc sử dụng kết quả

Một claim chỉ được đưa vào README, slide hoặc bài thi khi có đủ: input, phiên bản
code/commit, config, lệnh tái lập, protocol chia dữ liệu và metric thích hợp.
Synthetic chỉ chứng minh luồng chạy. Với dữ liệu FocusMate thật, phải chia theo
người hoặc thời gian và báo confusion matrix, precision, recall, F1, balanced
accuracy, số lời nhắc/giờ và useful rate.

Nếu model thiếu dữ liệu, ngoài miền hoặc không chắc chắn: abstain hoặc fallback
Rule v1. Mục tiêu là precision tốt và ít làm phiền, không phải accuracy cao giả tạo.
