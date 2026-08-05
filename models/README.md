# Models — FocusMate AI

PWA hiện tại **không cần model**. Rule v1 là cold-start/fallback chính thức.
Không nạp mặc định bất kỳ artefact nào trong `from_*` vào production.

## Kiến trúc model dự kiến

Khi đã có pilot hợp lệ, so sánh Logistic Regression, Decision Tree, Random
Forest hoặc boosting nhỏ trên dữ liệu cấu trúc. Input ứng viên gồm thời lượng,
mệt, tập trung, loại tác vụ, thời điểm và lịch sử từ chối; output là xác suất
`need_break`, sau đó qua threshold cá nhân, safety gate và abstention.

SLM nhỏ nếu có chỉ viết lại lời nhắc, không tạo nhãn và không ra quyết định.

## Artefact kế thừa

`from_On_Hand_3/` chứa 37 tệp (khoảng 13,78 MB): model/joblib và dự đoán WESAD,
cùng rehearsal ONNX/TFLite. Đây là stress-proxy và thử nghiệm triển khai, không
phải model nhắc nghỉ FocusMate. SVM HRV+ACC macro-F1 0,9124 không được gọi là độ
chính xác sản phẩm. Biến thể TFLite int8 còn suy giảm mạnh trong rehearsal.

Xem bảng đầy đủ và giới hạn tại
`../docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md`. Quyền phân phối model dẫn xuất
phải đối chiếu điều khoản dataset trước release; xem `../THIRD_PARTY_NOTICES.md`.
