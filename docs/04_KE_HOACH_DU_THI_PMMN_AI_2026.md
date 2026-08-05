# Kế hoạch FocusMate AI dự thi PMMN tích hợp AI 2026

Ngày lập: **05/08/2026**  
Hạn nộp kho mã nguồn theo thông báo: **30/09/2026**  
Chấm kho mã nguồn: **01-08/10/2026**  
Chung kết dự kiến: **10/10/2026**

**Trạng thái triển khai:** Sprint 1 đã bắt đầu ngày 05/08/2026. Timer thực tế,
khôi phục trạng thái và nền PWA/offline đã hoàn thành; xem
`../reports/02_SPRINT_01_IMPLEMENTATION_2026-08-05.md`.

Kiến trúc ML/sản phẩm sau Sprint 1 đã được chốt tại
`06_KE_HOACH_ML_THUC_TE_DO_CHINH_XAC.md`.

## 1. Kết luận định hướng

FocusMate không nên dừng ở một form nhập phiên học, cũng không nên lấy cảm biến
đồng hồ yếu làm điểm bán hàng chính. Sản phẩm dự thi nên là **trợ lý phiên học
local-first, cài được như PWA, học dần từ phản hồi của người dùng và giải thích
được vì sao gợi ý nghỉ**.

Thông điệp trình diễn:

> Một bộ hẹn giờ biết khi nào nên im lặng. FocusMate kết hợp thời lượng, loại
> nhiệm vụ, mức mệt, mức tập trung và lịch sử từ chối để chọn thời điểm nghỉ;
> dữ liệu ở trên thiết bị, người dùng xem/xuất/xóa được, và mọi quyết định đều
> có lý do.

## 2. Người dùng và tình huống ứng dụng

Người dùng chính là sinh viên tự học 30-120 phút trên máy tính hoặc điện thoại.
Luồng hoàn chỉnh phải diễn ra được trong demo 3 phút:

1. Chọn môn/nhiệm vụ và mục tiêu, bắt đầu bộ đếm.
2. FocusMate theo dõi thời lượng tại chỗ, không thu nội dung màn hình/camera/mic.
3. Đến thời điểm phù hợp, hệ thống gợi ý bài nghỉ 2-10 phút và nêu lý do.
4. Người dùng chọn nghỉ, hoãn hoặc từ chối; cooldown ngăn nhắc lặp.
5. Sau phiên, người dùng trả lời độc lập `need_break` và mức hữu ích.
6. Dashboard so sánh bộ hẹn giờ 45 phút, rule v1 và mô hình cá nhân hóa.
7. Người dùng xuất hoặc xóa toàn bộ dữ liệu.

## 3. Phạm vi sản phẩm v1.0

### Bắt buộc

- PWA responsive, offline sau lần mở đầu tiên, có cài đặt trên desktop/mobile.
- Bộ đếm phiên thật: bắt đầu, tạm dừng, kết thúc và phục hồi khi tải lại trang.
- Gợi ý nghỉ có hành động cụ thể, cooldown và chế độ không làm phiền.
- Local-first: không cần tài khoản/server; xuất CSV/JSON; xóa dữ liệu rõ ràng.
- Dashboard metric và so sánh ba phương pháp trên cùng dữ liệu.
- Mô hình nhỏ, minh bạch (Logistic Regression hoặc Decision Tree), có cold-start
  fallback về rule engine và chỉ bật khi đủ dữ liệu.
- Test logic, schema, import/export, metric và luồng PWA quan trọng.
- Dữ liệu demo mở/synthetic và hướng dẫn tái lập từ máy mới.

### Điểm cộng sau khi lõi ổn định

- Bộ sinh lời nhắc tiếng Việt bằng SLM chạy cục bộ hoặc template có kiểm soát.
- Wear OS experimental hiển thị ACC proxy với `UNKNOWN`/abstention.
- Chế độ giảng viên/nghiên cứu chỉ xem dữ liệu đã ẩn danh do người dùng chủ động
  xuất, không có thu thập ngầm.

### Không làm trong bản thi

- Chẩn đoán stress/sức khỏe; nhận dạng khuôn mặt; thu mic; theo dõi nội dung học.
- Chatbot chung chung không liên quan đến quyết định nghỉ.
- Cloud, đăng nhập và hạ tầng phức tạp nếu chưa hoàn tất PWA local-first.
- Tuyên bố độ chính xác từ bốn dòng synthetic hoặc từ WESAD stress-proxy.

## 4. AI có vai trò rõ ràng

| Thành phần | Vai trò | Điều kiện nghiệm thu |
|---|---|---|
| Fixed-45 | Đối chứng đơn giản | Chạy lại được trên mọi phiên |
| Rule v1 | Cold start và fallback | Có lý do, test biên và version |
| ML cá nhân hóa | Dự đoán `need_break` | Chia theo người/thời gian; không học từ chính `suggested` |
| SLM/template | Viết lời nhắc ngắn | Không thay đổi quyết định; có fallback offline |
| Wear proxy | Thử nghiệm nghiên cứu | Tắt mặc định; hiển thị nguồn/độ tin cậy/UNKNOWN |

Ngưỡng đề xuất để bật ML: tối thiểu 30 phiên hợp lệ/người và có cả hai lớp
`need_break`; nếu không đạt thì tiếp tục dùng rule. Đây là ngưỡng sản phẩm ban
đầu, cần ghi version và điều chỉnh bằng dữ liệu phát triển, không nhìn tập test.

Metric chính: precision (hạn chế làm phiền), recall, F1, số lời nhắc/giờ, tỷ lệ
chấp nhận, tỷ lệ “hữu ích”, độ trễ quyết định và dung lượng ứng dụng. Báo confusion
matrix, kết quả theo người và ít nhất 5 FP + 5 FN.

## 5. Khoảng trống so với thể lệ cuộc thi

### Các việc phải xử lý ngay

| Yêu cầu | Hiện trạng ngày 05/08 | Hành động |
|---|---|---|
| Nhóm tối đa 3 người | Dự thảo DT02 đang có 4 người | Chốt tối đa 3 thành viên chính thức với BTC; không nộp danh sách 4 người |
| Kho Internet công khai | `github.com/dnphuongictu/SV02` truy cập được | Dùng kho thật hằng ngày, PR/issue/milestone; không chỉ upload một lần |
| Lịch sử thay đổi | Kho hiện có 1 commit khởi tạo | Chia backlog thành issue và commit nhỏ có người review |
| Giấy phép OSI | Đã chọn Apache-2.0 ngày 05/08; đã có LICENSE và SPDX cho mã | Bổ sung tên pháp lý chủ sở hữu nếu muốn có copyright notice riêng |
| Tương thích giấy phép | Chủ dự án đã xác nhận sở hữu mã `source_code/from_*`; đã áp dụng Apache-2.0 và lập notices | Tiếp tục xác minh quyền phân phối dataset, model dẫn xuất, PDF và dependency bên thứ ba |
| Release | Chưa có tag/release | Tạo v0.1.0 trước 31/08 và v1.0.0 bằng định dạng mở trước 30/09 |
| Build from source | Web chạy được nhưng chưa có quy trình kiểm tra máy sạch/CI | Thêm `npm ci`, lint/test/build PWA và workflow CI |
| Bundling | Đang chép nguyên mã/artefact nghiên cứu vào kho | Tách `references/`; lập `THIRD_PARTY_NOTICES.md`, checksum và nguồn |
| Giao tiếp cộng đồng | Có README nhưng chưa changelog/contributing/issue mẫu | Thêm tài liệu cộng đồng và ít nhất một chu trình issue → PR → release |

Lưu ý pháp lý: quyền sở hữu mã On_Hand đã được chủ dự án xác nhận. Điều này không
tự động cấp lại giấy phép cho dataset, bài báo, runtime hoặc thư viện bên thứ ba;
các thành phần đó được quản lý tại `../THIRD_PARTY_NOTICES.md`.

## 6. Kế hoạch đến hạn nộp

| Thời gian | Kết quả bàn giao | Cổng nghiệm thu |
|---|---|---|
| 05-09/08 | Chốt 3 thành viên; backlog GitHub; quyết định license; audit mã/model kế thừa; wireframe luồng phiên học | Kho công khai, issue/milestone có người phụ trách; không còn artefact mơ hồ trong release scope |
| 10-18/08 | PWA timer, pause/resume, thông báo, cooldown, kết thúc phiên, import/export/delete | Cài và chạy offline trên 2 máy + 1 điện thoại; test logic đạt |
| 19-25/08 | Dashboard, confusion matrix, so sánh Fixed-45/Rule v1, data-quality report | Cùng một CSV cho ra kết quả tái lập; synthetic được gắn nhãn rõ |
| 26-31/08 | Phát hành v0.1.0; README, LICENSE, changelog, contributing, third-party notices, CI | Máy sạch làm theo README thành công; release tải được bằng định dạng mở |
| 01-10/09 | Pilot có đồng ý: mục tiêu 5-10 người, 100-150 phiên; ghi phản hồi hữu ích | Không có PII trong repo; báo thiếu dữ liệu/phân bố nhãn |
| 11-17/09 | ML nhỏ + fallback; đánh giá theo người/thời gian; phân tích FP/FN | So sánh công bằng với Fixed-45 và Rule; không leakage |
| 18-23/09 | Hoàn thiện UX, accessibility, privacy, demo offline; tùy chọn SLM/template | Người mới hoàn thành luồng chính không cần hướng dẫn miệng |
| 24-27/09 | Đóng băng tính năng; v1.0.0-rc; kiểm tra giấy phép, build sạch, bảo mật dữ liệu | Checklist PoF không còn mục đỏ; tất cả test/CI xanh |
| 28-30/09 | Release v1.0.0 và nộp form/kho mã nguồn | Tag/release trước hạn; checksum, hướng dẫn và video truy cập được |
| 01-08/10 | Chỉ sửa lỗi; luyện pitch, câu hỏi AI/license/data; chuẩn bị hackathon | Demo dự phòng offline và video; mỗi thành viên trình bày được phần mình |
| 10/10 | Chung kết | Demo 3 phút + 2 phút kiến trúc/kết quả + trả lời câu hỏi |

## 7. Phân công cho nhóm 3 người

| Vai trò | Trách nhiệm chính | Bằng chứng công khai |
|---|---|---|
| Sản phẩm/UX | PWA, timer, notification, accessibility, demo | Issue/PR, ảnh và kiểm thử trình duyệt |
| AI/dữ liệu | Schema, metric, baseline, ML, phân tích lỗi | Script tái lập, model card, data card |
| Mã nguồn mở/QA | CI, test, license, release, tài liệu cộng đồng | Changelog, release, audit license, bug tracker |

Trưởng nhóm điều phối nhưng không thay commit của thành viên khác. Mọi chức năng
quan trọng cần ít nhất một review chéo.

## 8. Ánh xạ trực tiếp 100 điểm

### 50 điểm PoF trước chung kết

- Quản lý mã nguồn: kho công khai, commit thật, issue/PR/milestone.
- License: giấy phép OSI cho mã sở hữu, header/SPDX, toàn văn và mục đích rõ.
- Release: SemVer, changelog, checksum, định dạng mở, tạo trước hạn.
- Build: một lệnh cài/test/build; CI trên máy sạch; không sửa mã để cấu hình.
- Dependency: lockfile/SBOM, không bundle thư viện, notices và license audit.
- Tài liệu: README, architecture, data/model card, contributing, bug tracker.

### 50 điểm sản phẩm tại chung kết

- Nguyên gốc: “timer biết im lặng”, feedback loop cá nhân hóa và local-first.
- Hoàn thiện: luồng thật từ bắt đầu phiên đến feedback/dashboard, chạy offline.
- Thân thiện: cài PWA, ít bước, lời nhắc có lý do, accessibility và xóa dữ liệu.
- AI: baseline rõ, ML nhỏ có đánh giá, SLM chỉ hỗ trợ ngôn ngữ, model card.
- Cộng đồng: live demo, roadmap/issue “good first issue”, tài liệu đóng góp và
  câu chuyện minh bạch về kết quả âm của cảm biến.

## 9. Definition of Done cho v1.0.0

- Một người mới clone kho, chạy test và mở ứng dụng trong tối đa 10 phút.
- PWA hoạt động offline và không mất phiên đang chạy khi reload.
- Dữ liệu có consent, export/delete; repo công khai không chứa PII.
- Fixed-45, Rule và ML chạy trên cùng tập đánh giá; có FP/FN và hạn chế.
- AI quyết định có fallback, version, explanation và không bịa dữ liệu cảm biến.
- Có LICENSE hợp lệ cho mã sở hữu và hồ sơ cho toàn bộ thành phần bên thứ ba.
- Có ít nhất v0.1.0 và v1.0.0, changelog, checksum, video demo và slide.
- Danh sách dự thi tối đa 3 người và thông tin nộp khớp thể lệ.
