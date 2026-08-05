# Kế hoạch FocusMate Hybrid Decision Engine

Ngày chốt định hướng: **05/08/2026**

## 1. Quyết định kiến trúc dựa trên kết quả thật

FocusMate sẽ không dùng cảm biến đồng hồ hoặc SLM làm bộ quyết định chính. Hướng
phát triển được chốt là **rule an toàn + mô hình ML nhỏ trên dữ liệu có cấu trúc
+ ngưỡng cá nhân hóa + khả năng không đưa ra lời nhắc**.

Căn cứ:

- WESAD SVM HRV+ACC đạt macro-F1 0,9124 nhưng chỉ là stress-proxy, không phải
  `need_break`.
- WAUC MLP ACC-only đạt macro-F1 0,5354; kiểm tra Pixel Watch chưa ổn định.
- On_Hand_6 trên 200 ngữ cảnh: Random Forest 75,0%, hybrid 63,5%, policy 54,5%,
  SLM 48,0%. ML có giám sát trên trường cấu trúc là hướng thực tế nhất hiện có.

Các kết quả này chỉ định hướng kiến trúc; không được chuyển thành tuyên bố về độ
chính xác FocusMate trước khi có dữ liệu phiên học thật.

## 2. Quyết định sản phẩm

```text
Ngữ cảnh phiên học
  -> cổng không làm phiền
  -> P(need_break) từ model nhỏ
  -> ngưỡng cá nhân hóa
  -> vùng không chắc chắn/abstention
  -> gợi ý nghỉ có giải thích
  -> accepted/useful/break_taken feedback
```

Pseudocode:

```text
if cooldown_active or interrupt_risk == HIGH:
    SUPPRESS
elif model_not_ready:
    use Rule v1
elif probability >= personal_threshold:
    SUGGEST_BREAK
elif probability in uncertainty_band:
    ABSTAIN
else:
    CONTINUE
```

SLM/template chỉ tạo câu chữ sau khi quyết định đã được chốt. Wear OS là nhánh
nghiên cứu tắt mặc định và phải cho phép `UNKNOWN`.

## 3. Đầu vào và nhãn

### Đầu vào ưu tiên

- `duration_minutes`, thời gian từ lần nghỉ gần nhất.
- `task_type`, thời điểm trong ngày, số phiên liên tiếp.
- `focus_score`, `fatigue_score` tại điểm check-in.
- Thời gian từ lần từ chối gần nhất và lịch sử acceptance/useful.
- Cờ deadline/thi do người dùng chủ động khai báo.
- Thống kê lịch sử cá nhân, không dùng danh tính trực tiếp làm feature.

Không thu camera, microphone, nội dung màn hình, vị trí chính xác hoặc dữ liệu
sức khỏe khó tiếp cận.

### Nhãn cần có

| Nhãn | Ý nghĩa/thời điểm hỏi |
|---|---|
| `need_break` | Hỏi trước khi hiển thị quyết định |
| `interrupt_ok` | Thời điểm này có phù hợp để nhận lời nhắc không |
| `accepted` | Chấp nhận hay hoãn sau lời nhắc |
| `useful` | Lời nhắc có hữu ích không |
| `break_taken` | Người dùng có thực sự nghỉ sau đó không |

Một lời nhắc nên được đưa ra khi `need_break=true` và `interrupt_ok=true`.
`accepted=false` không tự động là false positive.

## 4. Quy mô dữ liệu

### Pilot quy trình

- 5-10 người, 100-150 phiên/điểm quyết định.
- Mục tiêu: kiểm tra UI, schema, validator, nhãn và privacy.
- Không dùng để khẳng định model tổng quát hoặc “độ chính xác cao”.

### Dữ liệu đánh giá chính

- Mục tiêu 15-30 người và 300-500 điểm quyết định hợp lệ.
- Ít nhất 20-30 phiên/người nếu điều kiện cho phép.
- Cá nhân hóa chỉ bật khi một người có tối thiểu khoảng 50 điểm quyết định và có
  cả hai lớp `need_break`.

Có thể lấy nhiều điểm quyết định trong phiên dài tại các mốc hợp lý, nhưng phải
giới hạn check-in để chính việc hỏi không gây gián đoạn.

## 5. Thứ tự model

1. Fixed-45.
2. Rule v1.
3. Logistic Regression có regularization.
4. Decision Tree nông.
5. Random Forest hoặc Gradient Boosting nhỏ.
6. Model toàn cục cộng ngưỡng cá nhân hóa.

Không huấn luyện model riêng/người khi dữ liệu còn ít. Ưu tiên model toàn cục,
sau đó điều chỉnh threshold theo tỷ lệ từ chối và chi phí false positive của
từng người.

## 6. Đánh giá đúng

- Leave-one-user-out: đánh giá khả năng áp dụng cho người mới.
- Chia theo thời gian: đánh giá cá nhân hóa cho người đã có lịch sử.
- Chọn feature/model/threshold trên development set.
- Không sửa model sau khi xem test set.
- Báo confusion matrix, precision, recall, F1, balanced accuracy, lời nhắc/giờ,
  acceptance, useful rate và calibration.
- Báo theo từng người và phân tích ít nhất 5 FP + 5 FN.
- So sánh mọi phương pháp trên đúng cùng tập mẫu.

Accuracy đơn thuần không phải metric chính vì lớp `need_break=false` có thể chiếm
đa số. Precision được ưu tiên để giảm làm phiền.

## 7. Cổng mục tiêu triển khai

Các con số sau là **mục tiêu nghiệm thu**, không phải cam kết trước dữ liệu:

- Precision ≥ 0,75.
- Recall ≥ 0,60.
- Balanced accuracy ≥ 0,70.
- Giảm ít nhất 20% số lời nhắc so với Fixed-45.
- Acceptance/useful rate không giảm so với Rule v1.
- Model có fallback, version, explanation và abstention.

Nếu không đạt, giữ Rule v1 làm bản production và báo trung thực kết quả ML âm.

## 8. Lộ trình thực hiện

### P0 — hoàn thiện đo lường

1. ~~Import/validator CSV schema v1.~~ Hoàn thành MVP ngày 05/08/2026.
2. ~~Module metric Fixed-45/Rule có test.~~ Hoàn thành bản context-only ngày
   05/08/2026; chưa replay cooldown lịch sử.
3. Check-in chủ động và thêm `interrupt_ok`, `useful`, `break_taken` vào schema.
4. Test end-to-end và CI.
5. Duyệt consent/quy trình xóa.

### P1 — pilot

1. Thu 100-150 điểm quyết định.
2. Báo cáo chất lượng, phân bố và ca sai.
3. Điều chỉnh UI/schema chỉ trên bằng chứng pilot; version mọi thay đổi.

### P2 — model

1. Tạo pipeline feature/train/evaluate tái lập.
2. Chạy Logistic/Tree/RF hoặc boosting cùng split.
3. Calibration và threshold theo chi phí FP.
4. Model card, export JSON/ONNX và fallback Rule.

### P3 — sản phẩm/thi

1. Dashboard so sánh Fixed-45/Rule/ML.
2. Demo local-first/offline, explanation và quyền xóa.
3. Freeze test set, release SemVer, SBOM/checksum và báo cáo hạn chế.

## 9. Các điều cấm về phương pháp

- Không dùng `break_suggested` làm `need_break`.
- Không dùng bốn dòng synthetic để báo độ chính xác.
- Không gọi WESAD score là cognitive-load/FocusMate accuracy.
- Không chia ngẫu nhiên từng dòng khi cùng người có nhiều phiên.
- Không thêm SLM/chatbot trước validator, metric và pilot.
- Không bật Wear proxy như tín hiệu production mặc định.
