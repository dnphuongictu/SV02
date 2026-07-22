# Đề cương NCKH tối thiểu - FocusMate AI

## 1. Tên đề tài dự kiến

**FocusMate AI: Gợi ý nghỉ học theo ngữ cảnh nhằm giảm gián đoạn không cần thiết
cho sinh viên**

Tên tiếng Anh: **FocusMate AI: Context-aware Study Break Recommendations for
Reducing Unnecessary Interruptions**.

## 2. Vấn đề nghiên cứu

Các bộ hẹn giờ cố định thường nhắc nghỉ sau cùng một khoảng thời gian, dù mức mệt,
mức tập trung và nhiệm vụ của người học khác nhau. Lời nhắc sai thời điểm có thể
bị bỏ qua hoặc gây gián đoạn. Đề tài khảo sát liệu một baseline theo ngữ cảnh đơn
giản có cải thiện chất lượng lời nhắc so với ngưỡng thời gian cố định hay không.

## 3. Câu hỏi nghiên cứu

- RQ1: Bộ luật dùng thời lượng, mức mệt và mức tập trung có dự đoán nhu cầu nghỉ
  tốt hơn luật cố định 45 phút không?
- RQ2: Cơ chế không làm phiền 20 phút sau khi từ chối ảnh hưởng thế nào đến số
  lời nhắc và tỷ lệ chấp nhận?
- RQ3 (mở rộng): Cá nhân hóa theo người dùng có cải thiện F1 mà không tăng số lần
  làm phiền không?

## 4. Giả thuyết

- H1: Baseline theo ngữ cảnh có precision cao hơn luật 45 phút.
- H2: Cooldown làm giảm số lời nhắc lặp lại và tăng acceptance rate.
- H3 chỉ kiểm tra khi mỗi người có đủ dữ liệu: mô hình cá nhân hóa cải thiện F1 so
  với một bộ ngưỡng chung.

## 5. Biến nghiên cứu

| Loại | Biến |
|---|---|
| Đầu vào | thời lượng, mức tập trung 1-5, mức mệt 1-10, loại nhiệm vụ, lịch sử từ chối |
| Đầu ra thuật toán | `suggested`, `risk_score`, `decision_reason`, `rule_version` |
| Nhãn đánh giá | `need_break` do người học tự báo sau phiên |
| Hành vi phụ | `accepted` khi có lời nhắc |

`suggested` tuyệt đối không được sao chép sang `need_break` vì sẽ làm kết quả đánh
giá đúng một cách giả tạo.

## 6. Đối tượng và dữ liệu thăm dò

- Đối tượng dự kiến: sinh viên tự nguyện, đủ tuổi theo yêu cầu của đơn vị.
- Pilot: 5-10 người, 100-150 phiên trong 1-2 tuần.
- Đây là nghiên cứu thăm dò; không khái quát kết luận cho toàn bộ sinh viên.
- Không thu tên thật, nội dung học, camera, microphone hoặc vị trí ở phiên bản này.

Trước khi thu dữ liệu thật, giảng viên cần duyệt nội dung đồng ý tham gia theo quy
định của trường/đơn vị. Người tham gia phải biết cách yêu cầu xóa dữ liệu.

## 7. Phương pháp

1. Chạy pilot bằng sản phẩm nền tảng.
2. Làm sạch dữ liệu theo schema v1.
3. Chia dữ liệu theo người tham gia; không để một người xuất hiện ở cả train và
   test nếu có huấn luyện mô hình.
4. Chạy lại hai quyết định trên cùng dữ liệu: luật cố định 45 phút và FocusMate
   v1.0.
5. So sánh confusion matrix, precision, recall, F1, số lời nhắc/người và tỷ lệ
   chấp nhận.
6. Phân tích thủ công tối thiểu 5 false positive và 5 false negative.

## 8. Baseline

Baseline A:

```text
suggested = duration_minutes >= 45
```

Baseline B là `src/js/ruleEngine.js`. Mọi kết quả phải lưu `rule_version` để biết
được dữ liệu sinh bởi phiên bản nào.

Chỉ thêm Decision Tree/Logistic Regression sau khi có dữ liệu đủ sạch. Nếu dùng
ML, phải so sánh với cả A và B; không chỉ báo cáo riêng điểm của mô hình mới.

## 9. Kết quả mong đợi

- Một web app chạy local và xuất dữ liệu chuẩn hóa.
- Một bộ dữ liệu pilot đã ẩn danh.
- Báo cáo so sánh ít nhất hai baseline.
- Danh sách ca sai và một đề xuất cải tiến có căn cứ.

Không đặt trước mục tiêu “đạt 90% accuracy”. Với mẫu nhỏ, chất lượng quy trình,
tính tái lập và cách diễn giải hạn chế quan trọng hơn một con số cao.

## 10. Nguy cơ đối với độ tin cậy

- Nhãn tự báo có thể chủ quan.
- Người tham gia biết mình đang được quan sát nên thay đổi hành vi.
- Mẫu ít và cùng một trường nên khó khái quát.
- `accepted=false` có thể do bận, không nhất thiết thuật toán dự đoán sai nhu cầu.
- Các phiên từ cùng người có tương quan; chia ngẫu nhiên theo dòng có thể gây rò
  rỉ dữ liệu.

Các nguy cơ này phải xuất hiện trong phần hạn chế của báo cáo.
