# Phân công và backlog cho nhóm 3 người

## Phân vai

| Vai trò | Trách nhiệm | Minh chứng mỗi tuần |
|---|---|---|
| A — Product/UX | PWA, timer, notification, accessibility, demo | PR giao diện + video/screenshot + test |
| B — AI/Data | schema, validator, metric, baseline, model | script tái lập + bảng metric + model/data card |
| C — OSS/QA | GitHub, CI, test, license, release, tài liệu | issue/PR review + CI + changelog/release |

Trưởng nhóm có thể giữ một vai trò nhưng không được commit thay hai người còn
lại. Mọi PR quan trọng cần ít nhất một review chéo.

## Quy tắc GitHub

- `main` luôn chạy được; không commit trực tiếp trừ sửa khẩn cấp có giải thích.
- Mỗi việc có issue, branch `feature/<ten-ngan>` hoặc `fix/<ten-ngan>`, PR và test.
- Commit nhỏ, mô tả kết quả; không dùng một commit “update project” cho cả tuần.
- Không commit `data/weekly_logs`, exports thật, tên người tham gia hoặc secret.
- Issue lỗi phải có bước tái hiện, kỳ vọng, kết quả thực tế và môi trường.

## Backlog phải tạo thành issue

### P0 — trước pilot

1. **Thiết lập CI cho Node tests**  
   Đạt khi push/PR tự chạy 24 test trên máy sạch.
2. **[Hoàn thành cục bộ] Import và validate CSV schema v1**  
   Đã có kiểm tra thiếu cột, sai miền, thời gian ngược, session trùng và header PII.
3. **[Hoàn thành cục bộ] Module metric Fixed-45 và Rule v1 context**  
   Đã có confusion matrix, precision, recall, F1, balanced accuracy và số lời nhắc.
4. **Check-in chủ động ở phút 45**  
   Đạt khi timer đang chạy có thể hỏi focus/fatigue, quyết định, nghỉ/hoãn và
   cooldown mà không bắt kết thúc phiên.
5. **Kiểm thử trình duyệt luồng chính**  
   Đạt khi tự động kiểm tra start → pause → reload → resume → finish → feedback.
6. **Data/consent review**  
   Đạt khi giảng viên duyệt biểu mẫu, mã ẩn danh và quy trình xóa trước dòng thật đầu tiên.

### P1 — pilot và AI

7. **Pilot 5-10 người, 100-150 phiên**  
   Đạt khi có báo cáo chất lượng, không PII, đủ bằng chứng đồng ý và quyền xóa.
8. **Dashboard so sánh**  
   Đạt khi lọc theo phương pháp/người/nhiệm vụ và hiển thị metric + FP/FN.
9. **Logistic Regression/Decision Tree**  
   Đạt khi dự đoán ngoài mẫu, chia theo người/thời gian, có fallback và model card.
10. **Phân tích ít nhất 5 FP + 5 FN**  
    Đạt khi từng ca có ngữ cảnh, nguyên nhân có thể và cải tiến không nhìn test.

### P2 — cuộc thi

11. Accessibility/mobile audit.
12. SBOM, checksum và license audit gói release.
13. Release v0.1.0, sau đó v1.0.0 trước 30/09.
14. Video demo 3-5 phút, demo offline dự phòng và pitch chung kết.

## Thứ tự không được đảo

Validator/metric và pilot phải có trước model cá nhân hóa. Không thêm chatbot,
cloud hoặc Wear OS nếu P0 chưa hoàn tất.
