# Bắt đầu trong 60 phút

## Trước buổi nhận dự án

Cài Python 3, Node.js 18+ và Git. Không cần GPU, Android Studio hay model AI để
làm phần PWA lõi.

## 0-10 phút: lấy mã và đọc phạm vi

```powershell
git clone https://github.com/dnphuongictu/SV02.git
cd SV02
```

Đọc `README.md`, `handoff/01_HO_SO_DU_AN.md`, `LICENSE` và
`THIRD_PARTY_NOTICES.md`.

Nếu kho GitHub chưa chứa bản bàn giao mới nhất, dừng và báo giảng viên; không
chép chồng các thư mục tùy ý.

## 10-20 phút: chạy test

```powershell
npm test
```

Kết quả chuẩn tại thời điểm bàn giao: 24 test đạt, 0 test thất bại.

## 20-35 phút: chạy ứng dụng

```powershell
python -m http.server 8000 -d src
```

Mở `http://localhost:8000` và kiểm tra:

1. Bắt đầu một phiên.
2. Tạm dừng và tiếp tục.
3. Tải lại trang, xác nhận timer được khôi phục.
4. Nạp bốn phiên synthetic.
5. Xuất CSV, nhập lại CSV và xem dashboard Fixed-45/Rule v1 context.
6. Thử nhập một CSV sai để xem validator từ chối mà không ghi đè dữ liệu.
7. Mở DevTools/Network, chuyển offline và tải lại ứng dụng sau lần cache đầu.

Không cần chờ 5 phút trong buổi nhận: dùng dữ liệu synthetic để kiểm tra quyết
định; không sửa đồng hồ hoặc tạo dữ liệu giả rồi gọi là pilot.

## 35-50 phút: đọc mã theo thứ tự

1. `src/js/timer.js` — state machine thời gian.
2. `src/js/ruleEngine.js` — quyết định và cooldown.
3. `src/js/csv.js`, `src/js/metrics.js` — validator và baseline đánh giá.
4. `src/js/storage.js` — localStorage.
5. `src/js/app.js` — nối UI, timer, rule, import/export và dashboard.
6. `tests/*.test.mjs` — hành vi đã được bảo vệ.
7. `data/study_session.schema.json` — hợp đồng dữ liệu.

## 50-60 phút: bài kiểm tra nhận dự án

Mỗi sinh viên phải trả lời và trình diễn được:

- Vì sao `need_break` không được lấy từ `break_suggested`?
- Vì sao `accepted=false` chưa chắc là false positive?
- Vì sao WESAD macro-F1 0,9124 không phải độ chính xác FocusMate?
- Tệp nào được sửa, tệp nào chỉ là reference?
- Tạo một branch, sửa một dòng tài liệu, chạy test và mở pull request nháp.

Chỉ coi là nhận dự án thành công khi cả ba thành viên tự chạy được sản phẩm/test.
