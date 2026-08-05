# Sprint 02 — Ứng dụng cơ bản để sinh viên tiếp tục phát triển

Ngày chốt: 05/08/2026

## Kết quả đã hoàn thành

- PWA local-first chạy bằng trình duyệt, có timer, phục hồi phiên và cache offline.
- Thu nhãn độc lập `need_break`, sau đó mới chạy Rule v1 và ghi hành vi chấp nhận/từ chối.
- Nhập CSV có validator cho header, kiểu/miền giá trị, thời gian, mã phiên trùng và cột PII.
- Dashboard chạy Fixed-45 và Rule v1 trên cùng dữ liệu, hiển thị confusion matrix,
  precision, recall, F1, balanced accuracy và số lời nhắc.
- 24/24 kiểm thử đạt. Dữ liệu mẫu được ghi rõ là synthetic và không dùng để tuyên bố độ chính xác.

## Phần sinh viên tiếp tục chỉnh sửa

1. Thêm check-in `interrupt_ok` trước quyết định và phản hồi `useful`, `break_taken`
   sau lời nhắc; cập nhật đồng bộ schema, validator, export, test và tài liệu.
2. Thêm end-to-end test và CI để mọi pull request tự chạy kiểm thử.
3. Thực hiện pilot có phê duyệt, báo cáo chất lượng dữ liệu và đánh giá theo người/thời gian.
4. Chỉ sau pilot mới huấn luyện Logistic Regression/Tree/RF hoặc boosting; khi thiếu dữ
   liệu hoặc độ tin cậy thấp phải fallback Rule v1/abstain.

## Cách kiểm tra

```powershell
npm test
python -m http.server 8000 -d src
```

Mở `http://localhost:8000`, thử nạp `data/sample_study_sessions.csv`, đối chiếu bảng
metric rồi xuất CSV. Rule v1 trên dashboard không áp dụng cooldown lịch sử; giới hạn
này phải được giữ rõ khi trình bày kết quả.
