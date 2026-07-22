# Hướng dẫn từng bước dự án FocusMate AI

Tài liệu này dùng cho một nhóm 3-4 sinh viên chưa vững lập trình và chưa từng làm
nghiên cứu khoa học. Giảng viên chỉ cho nhóm sang chặng tiếp theo khi sản phẩm của
chặng hiện tại đã đạt tiêu chí nghiệm thu.

## 1. Vì sao chọn FocusMate AI làm dự án đầu tiên

| Tiêu chí | Nhận xét |
|---|---|
| Bài toán | Gần gũi, sinh viên tự dùng và tự kiểm thử được |
| Kỹ thuật ban đầu | Web cơ bản, localStorage, luật `if/else`; không cần GPU |
| Dữ liệu | Tự thu theo phiên học, ít nhạy cảm nếu dùng mã ẩn danh |
| Baseline | Giải thích được, đo được, có kiểm thử |
| Hướng NCKH | So sánh nhắc nghỉ cố định với nhắc nghỉ theo ngữ cảnh |
| Khả năng mở rộng | Decision Tree, cá nhân hóa, Android/Wear OS sau khi có dữ liệu |

Các dự án SafeDrive, PrivacySense và UIGrade vẫn có giá trị, nhưng đòi hỏi nhiều
khâu kỹ thuật trước khi sinh viên tạo được dữ liệu nghiên cứu đầu tiên.

## 2. Phạm vi bắt buộc và phần chưa làm

Phiên bản nền tảng chỉ gồm:

1. Ghi một phiên học bằng mã sinh viên ẩn danh.
2. Tính quyết định nghỉ bằng bộ luật v1.0.
3. Hiện lý do của quyết định.
4. Lưu dữ liệu trên trình duyệt và xuất CSV.
5. Tính bốn số tổng quan.
6. Có kiểm thử cho bộ luật.

Trong 4 tuần đầu, **không** làm đăng nhập, chatbot, LLM, nhận dạng khuôn mặt,
đọc nhịp tim, đồng bộ cloud hoặc ứng dụng Android. Những phần này không giúp trả
lời câu hỏi nghiên cứu ban đầu nhưng làm tăng số lỗi phải xử lý.

## 3. Vai trò trong nhóm

| Vai trò | Trách nhiệm chính | Minh chứng hàng tuần |
|---|---|---|
| Trưởng nhóm/nghiên cứu | Câu hỏi, nhật ký quyết định, tiến độ | `reports/nhat_ky.md` |
| Lập trình | Web, bộ luật, kiểm thử | commit/code và kết quả test |
| Dữ liệu | Phiếu đồng ý, từ điển dữ liệu, kiểm tra CSV | báo cáo chất lượng dữ liệu |
| Đánh giá/trình bày | Metric, biểu đồ, slide/demo | bảng kết quả có diễn giải |

Nếu nhóm có 3 người, trưởng nhóm kiêm đánh giá. Mỗi phần mã phải có ít nhất một
người khác chạy lại được.

## 4. Chặng 0 - hiểu bài toán (1 buổi)

### Giảng viên giải thích

- “Nhắc đúng” không đồng nghĩa với “nhắc nhiều”.
- Một lời nhắc có ích khi người học thật sự cần nghỉ và không đang ở giai đoạn
  không nên bị ngắt quãng.
- AI chưa phải mục tiêu đầu tiên. Mục tiêu là tạo một quyết định đo được.

### Sinh viên thực hiện

Viết một trang trả lời bốn câu:

1. Người dùng là ai?
2. Vấn đề cụ thể là gì?
3. Hệ thống nhận đầu vào nào và trả đầu ra nào?
4. Dùng số đo nào để biết hệ thống tốt hơn?

### Nghiệm thu

Nhóm nói được trong 2 phút: “FocusMate dùng thời lượng, mức mệt và mức tập trung
để quyết định có gợi ý nghỉ; nhóm đo precision, recall và tỷ lệ chấp nhận.”

## 5. Chặng 1 - chạy sản phẩm mẫu (1 buổi)

### Sinh viên thực hiện

```powershell
cd 02_Smart_Study_Break
python -m http.server 8000 -d src
```

Mở `http://localhost:8000`, sau đó:

1. Nạp bốn phiên mẫu.
2. Thêm một phiên 30 phút, mệt 3; giải thích vì sao không nhắc.
3. Thêm một phiên 60 phút, mệt 4; giải thích vì sao có nhắc.
4. Xuất CSV và mở bằng Excel/LibreOffice.
5. Chạy `node --test tests/ruleEngine.test.mjs`.

### Nghiệm thu

- Một máy khác chạy lại được theo README.
- 7 test đạt.
- File CSV không có tên thật, email hoặc số điện thoại.

## 6. Chặng 2 - đọc và sửa mã có kiểm soát (1 tuần)

Thứ tự đọc mã:

1. `src/index.html`: dữ liệu nào người dùng nhập.
2. `src/js/ruleEngine.js`: quyết định được tạo thế nào.
3. `tests/ruleEngine.test.mjs`: ví dụ nào chứng minh luật đúng.
4. `src/js/storage.js`: dữ liệu lưu ở đâu.
5. `src/js/app.js`: nối giao diện, luật và lưu trữ.

Bài tập nhỏ theo thứ tự:

1. Đổi ngưỡng thời lượng từ 45 thành 50 phút.
2. Sửa test tương ứng và giải thích vì sao test cũ thất bại.
3. Thêm trường ghi chú vào form và CSV.
4. Thêm nút xóa một dòng, không chỉ xóa tất cả.

### Nghiệm thu

Mỗi thay đổi phải có ảnh trước/sau, test đạt và một đoạn 3-5 câu giải thích.

## 7. Chặng 3 - chuẩn hóa dữ liệu (1 tuần)

### Ba loại dữ liệu phải phân biệt

- `need_break`: nhãn độc lập do người học trả lời sau phiên; dùng để đánh giá
  hệ thống có đoán đúng nhu cầu nghỉ không.
- `suggested`: đầu ra của thuật toán; không được dùng làm nhãn đúng.
- `accepted`: người học có làm theo lời nhắc không; chỉ có nghĩa khi đã nhắc.

### Quy trình thử trước

1. Tạo 20 phiên giả lập, cố ý nhập cả trường hợp biên.
2. Xuất CSV.
3. Kiểm tra miền giá trị, ô trống, mã trùng và thời lượng bất thường.
4. Đóng băng schema v1 trước khi thu thật.

### Thu thật tối thiểu

- 5-10 sinh viên, mỗi người 10-20 phiên trong 1-2 tuần.
- Mục tiêu ban đầu 100-150 phiên, không tuyên bố đây là mẫu đại diện rộng.
- Dùng mã `SV01`, `SV02`; bảng nối mã với danh tính (nếu thật sự cần) phải lưu
  riêng, không đưa vào repo.
- Người tham gia được biết mục đích, dữ liệu thu, quyền dừng và cách xóa dữ liệu.

### Nghiệm thu

Tệp `reports/data_quality.md` nêu số dòng, số người, tỷ lệ thiếu và phân bố nhãn.

## 8. Chặng 4 - đánh giá baseline (1 tuần)

Xem `need_break` là nhãn đúng và `suggested` là dự đoán:

| Trường hợp | Ý nghĩa |
|---|---|
| `need_break=true`, `suggested=true` | TP - nhắc đúng |
| `need_break=false`, `suggested=true` | FP - làm phiền |
| `need_break=false`, `suggested=false` | TN - không làm phiền đúng |
| `need_break=true`, `suggested=false` | FN - bỏ lỡ nhu cầu nghỉ |

Tính:

- Precision = TP / (TP + FP): trong các lần nhắc, bao nhiêu lần thật sự cần.
- Recall = TP / (TP + FN): trong các lần cần nghỉ, phát hiện được bao nhiêu.
- F1 = trung bình điều hòa của precision và recall.
- Acceptance rate = số lần chấp nhận / số lời nhắc đã được trả lời.

Không chỉ báo cáo accuracy vì dữ liệu có thể lệch nhiều về “không cần nghỉ”. Báo
cả confusion matrix và kết quả theo từng người; không trộn các phiên của cùng một
người vào cả train và test khi bắt đầu dùng ML.

### Nghiệm thu

Có một bảng metric, confusion matrix, ít nhất 5 ca sai và giải thích nguyên nhân.

## 9. Chặng 5 - thiết kế so sánh công bằng (1-2 tuần)

So sánh offline trên cùng một tập dữ liệu:

- Baseline A: luôn nhắc sau 45 phút.
- Baseline B: bộ luật FocusMate v1.0.
- Phiên bản C (sau này): Decision Tree hoặc Logistic Regression.

Mỗi phương pháp phải nhận cùng dữ liệu kiểm thử. Ngưỡng chỉ được chỉnh trên tập
phát triển; không nhìn tập test rồi sửa luật. Với dữ liệu ít, báo kết quả theo
người và dùng leave-one-subject-out khi đủ khả năng.

### Nghiệm thu

Nhóm kết luận dựa trên bảng số, không dùng câu “AI thông minh hơn” nếu chưa có
thực nghiệm hỗ trợ.

## 10. Chặng 6 - cải tiến có giả thuyết (1-2 tuần)

Chỉ chọn **một** cải tiến:

- Thêm loại nhiệm vụ để giảm nhắc khi đang thi/làm bài gấp.
- Cá nhân hóa ngưỡng mệt hoặc thời lượng theo người dùng.
- Học Decision Tree từ dữ liệu đã thu.
- Thêm cơ chế cooldown thích ứng theo lịch sử từ chối.

Mẫu viết giả thuyết: “Nếu cá nhân hóa ngưỡng thời lượng theo người dùng thì
precision tăng, trong khi recall không giảm quá 5 điểm phần trăm so với v1.0.”

### Nghiệm thu

Có ablation/so sánh chỉ thay một yếu tố, có bảng trước-sau và ghi rõ hạn chế.

## 11. Chặng 7 - báo cáo và tái lập (1 tuần)

Gói nộp cuối kỳ gồm:

1. README chạy được trên máy mới.
2. Mã nguồn và test.
3. Schema, dữ liệu mẫu công khai và quy trình xin đồng ý.
4. Dữ liệu thật đã ẩn danh hoặc chỉ thống kê nếu không được phép chia sẻ.
5. Script/bảng tính metric có thể chạy lại.
6. Báo cáo: vấn đề, related work, phương pháp, kết quả, hạn chế, đạo đức.
7. Video demo 3-5 phút.

## 12. Checklist họp hàng tuần cho giảng viên

Mỗi nhóm chỉ trả lời bốn câu, có minh chứng trên màn hình:

1. Tuần này đã tạo ra đầu ra nào?
2. Số liệu hoặc test nào chứng minh đầu ra đúng?
3. Lỗi/ca sai quan trọng nhất là gì?
4. Tuần sau chỉ làm một mục tiêu kiểm chứng được nào?

Nếu sinh viên chỉ trình bày slide mà không chạy sản phẩm hoặc không mở dữ liệu,
chưa nghiệm thu chặng đó.

## 13. Rubric 100 điểm

| Hạng mục | Điểm |
|---|---:|
| Phát biểu bài toán, câu hỏi và giả thuyết | 15 |
| Sản phẩm chạy được, mã có cấu trúc | 20 |
| Dữ liệu, đồng ý tham gia, chất lượng dữ liệu | 20 |
| Baseline và thiết kế so sánh công bằng | 15 |
| Metric, phân tích lỗi và hạn chế | 20 |
| Khả năng tái lập, demo và trình bày | 10 |

LLM/chatbot chỉ là điểm cộng sau khi sáu phần trên đã đạt; không thay thế dữ liệu,
baseline hoặc đánh giá.
