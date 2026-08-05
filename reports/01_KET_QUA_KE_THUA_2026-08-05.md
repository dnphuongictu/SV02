# Cập nhật kết quả kế thừa cho FocusMate AI

Ngày đối chiếu: **05/08/2026**

## 1. Quy tắc sử dụng kết quả

FocusMate AI kế thừa ý tưởng, mã tham khảo và một số artefact từ On_Hand_3 và
On_Hand_6/ContextLens. Các con số dưới đây là **bằng chứng của dự án nguồn**,
không phải kết quả đánh giá lời nhắc nghỉ của FocusMate. Khi trình bày hoặc viết
báo cáo phải tách ba mức:

1. **Kết quả riêng của FocusMate:** thu được từ dữ liệu phiên học và mã trong
   `src/`, có lệnh tái lập trong kho này.
2. **Kết quả kế thừa:** dùng để chọn kiến trúc hoặc đặt giả thuyết, luôn ghi rõ
   dự án nguồn, dữ liệu, giao thức và giới hạn.
3. **Kết quả demo/synthetic:** chỉ chứng minh luồng phần mềm hoạt động, không
   dùng để tuyên bố độ chính xác ngoài thực tế.

## 2. Trạng thái riêng của FocusMate hiện tại

| Minh chứng | Kết quả | Cách diễn giải hợp lệ |
|---|---:|---|
| Kiểm thử `ruleEngine` | 7/7 test đạt ngày 05/08/2026 | Bộ luật v1.0 hoạt động đúng với các ca kiểm thử đã viết |
| Dữ liệu mẫu | 4 phiên synthetic, 2 người giả lập | Chỉ dùng kiểm tra nhập/xuất và giao diện |
| Confusion matrix trên mẫu | TP=2, TN=2, FP=0, FN=0 | Không phải kết quả khoa học vì nhãn và ca mẫu được thiết kế sẵn |
| Acceptance trên mẫu | 1/2 lời nhắc được chấp nhận = 50% | Chỉ kiểm tra phép tính; không suy rộng cho sinh viên thật |

Hiện chưa có dữ liệu pilot thật nên **chưa có** precision, recall, F1 hoặc tỷ lệ
chấp nhận đáng tin cậy cho bài toán gợi ý nghỉ.

## 3. Kết quả cập nhật từ On_Hand_3

### 3.1 WESAD: chỉ là stress-proxy

Trên 883 cửa sổ 60 giây của 15 người, đánh giá LOSO của mô hình SVM dùng
HRV+ACC đạt accuracy trung bình 0,9224, balanced accuracy 0,9159 và macro-F1
0,9124. Đây là cấu hình tốt nhất trong sáu baseline đã sao chép vào
`models/from_On_Hand_3/wesad_stress_proxy_baselines_60s/`.

Kết quả cao này **không được gọi là nhận biết tải nhận thức hoặc nhu cầu nghỉ**:
WESAD gán nhãn stress mạnh, không phải nhãn cognitive load hay `need_break`.

### 3.2 WAUC: cognitive-load ground truth và giới hạn triển khai

Kết quả nguồn mới hơn trên WAUC gồm 4.582 cửa sổ, 41 người và đánh giá LOSO:

| Mô hình | Tín hiệu | Macro-F1 | Balanced accuracy |
|---|---|---:|---:|
| SVM | HRV | 0,4893 | 0,5059 |
| MLP | HRV | 0,4972 | 0,5107 |
| SVM | ACC | 0,5231 | 0,5575 |
| MLP | ACC | 0,5354 | 0,5657 |
| SVM | HRV+ACC | 0,5289 | 0,5523 |
| MLP | HRV+ACC | 0,5379 | 0,5621 |

Khi chỉ xét điều kiện không có physical workload, SVM HRV+ACC đạt macro-F1
0,5650 và balanced accuracy 0,6123. Cải thiện còn nhỏ và cho thấy vận động là
yếu tố gây nhiễu quan trọng.

Do ứng dụng bên thứ ba trên Pixel Watch 2 không truy cập được PPG thô, bản Wear
OS dùng MLP ACC-only (macro-F1 0,5354), cửa sổ 60 giây/stride 30 giây. Forward
pass Kotlin đã được kiểm tra khớp 100% với pipeline sklearn trên 4.582 cửa sổ.

Hai phiên kiểm tra có kiểm soát trên một người cho kết quả không ổn định:

| Phiên | Mean P(HIGH), HIGH | Mean P(HIGH), LOW | Chênh lệch |
|---|---:|---:|---:|
| 30/07/2026, LOW → HIGH | 0,5591 | 0,4535 | +0,1056 |
| 31/07/2026, HIGH → LOW | 0,5961 | 0,7323 | -0,1362 |
| Gộp hai phiên | 0,5776 | 0,5929 | -0,0153 |

Phiên thứ hai bị nhiễu bởi mệt mỏi và chuyển động; 8/12 cửa sổ đúng hướng chỉ
là thống kê mô tả. Vì vậy, tín hiệu đồng hồ chỉ nên là **tính năng nghiên cứu
tùy chọn**, có khả năng abstain/`UNKNOWN`, không được tự động quyết định nhắc
nghỉ trong sản phẩm dự thi.

### 3.3 Bài học trực tiếp cho FocusMate

- Tự báo mệt/tập trung và lịch sử hành vi là đầu vào chính đáng tin cậy hơn cảm
  biến ACC-only trong phiên bản thi.
- Nếu trình diễn Wear OS, hiển thị xác suất, nguồn, độ tin cậy và cho phép bỏ qua;
  không gọi đầu ra là chẩn đoán stress.
- Không dùng điểm WESAD 0,9124 để quảng bá độ chính xác FocusMate.

## 4. Kết quả cập nhật từ On_Hand_6/ContextLens

Trên 200 ngữ cảnh có nhãn người cho bài toán chọn một trong bốn hành động thông
báo, kết quả là:

| Cách quyết định | Accuracy | Ghi chú |
|---|---:|---|
| Random Forest, LOO-CV | 75,0% | 95% Wilson CI: 68,6%-80,5% |
| Hybrid policy + SLM | 63,5% | 95% Wilson CI: 56,6%-69,9% |
| Policy | 54,5% | Quy tắc viết trước khi xem tập nhãn |
| SLM zero-shot | 48,0% | Không huấn luyện trên 200 nhãn |

Random Forest tốt hơn hybrid (McNemar exact p=0,0027), policy và SLM
(p<0,0001). Hybrid tốt hơn riêng policy (p=0,0014) và SLM (p<0,0001). Chênh
lệch policy với SLM không có ý nghĩa thống kê (p=0,1980).

Đây vẫn không phải bài toán `need_break`, nhưng là bằng chứng thiết kế hữu ích:

- Mô hình ML nhỏ trên dữ liệu có cấu trúc có thể phù hợp hơn SLM cho quyết định.
- SLM nên viết lời giải thích/gợi ý thân thiện, không làm bộ quyết định chính.
- Cần so sánh cùng tập mẫu, dùng dự đoán ngoài mẫu và báo khoảng tin cậy.

## 5. Kiến trúc kế thừa được chấp nhận

```text
Dữ liệu phiên học tại chỗ
  -> baseline 45 phút
  -> rule engine theo ngữ cảnh (cold start/fallback)
  -> mô hình nhỏ cá nhân hóa khi đủ dữ liệu
  -> cổng an toàn + cooldown + khả năng không đưa ra gợi ý
  -> bộ sinh lời nhắc tùy chọn
  -> phản hồi need_break / accepted / useful
```

Wear OS/ACC chỉ đi vào nhánh thử nghiệm và không thay thế phản hồi của người học.

## 6. Nguồn bằng chứng đã đối chiếu

- Bản sao trong dự án: các `summary.json` tại
  `models/from_On_Hand_3/wesad_stress_proxy_baselines_60s/` và
  `models/from_On_Hand_3/tflite_rehearsal/rehearsal_summary.json`.
- Upstream On_Hand_3 tại thời điểm 05/08/2026:
  `PHASE_WAUC_RUN_LOG.md`, `PROJECT_STATUS.md` và
  `artifacts/wauc_baselines_60s/*/summary.json`.
- Upstream On_Hand_6 tại thời điểm 05/08/2026:
  `docs/ON_HAND_3_CONTROLLED_VALIDATION_20260730.md`,
  `docs/ON_HAND_3_REPLICATION_20260731.md`,
  `results/decision_mode_comparison_human_gth_n200/` và
  `results/baseline_random_forest_gth_n200/`.

Trước khi phát hành công khai, cần thay các tham chiếu thư mục cục bộ bằng URL,
commit hash/DOI và kiểm tra giấy phép của từng artefact.
