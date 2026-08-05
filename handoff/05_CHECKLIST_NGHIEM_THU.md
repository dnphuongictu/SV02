# Checklist nghiệm thu chuyển giao

## Nghiệm thu từng tuần

Mỗi nhóm trả lời bằng minh chứng trên màn hình:

- [ ] Tuần này hoàn thành issue/PR nào?
- [ ] Test hoặc dữ liệu nào chứng minh kết quả đúng?
- [ ] Ca sai/lỗi quan trọng nhất là gì?
- [ ] Tuần tới chỉ có một mục tiêu chính nào?
- [ ] Không có PII, secret hoặc file build/cache mới trong commit?
- [ ] Changelog/tài liệu/schema đã cập nhật nếu hành vi thay đổi?

## Cổng 1 — tiếp nhận dự án

- [ ] Cả ba thành viên clone và chạy ứng dụng độc lập.
- [ ] `npm test` đạt 24/24 trên ít nhất hai máy.
- [ ] Giải thích đúng `need_break`, `break_suggested`, `accepted`.
- [ ] Phân biệt mã sản phẩm, mã reference và dữ liệu synthetic.

## Cổng 2 — sẵn sàng pilot

- [ ] CI xanh và có test end-to-end luồng chính.
- [ ] Validator phát hiện dữ liệu lỗi theo dòng.
- [ ] Metric Fixed-45/Rule có test bằng tay độc lập.
- [ ] Phiếu đồng ý/quy trình xóa được giảng viên duyệt.
- [ ] Không có PII trong repo hoặc export thử.

## Cổng 3 — sẵn sàng AI

- [ ] Có ít nhất 100 phiên hợp lệ hoặc giải thích vì sao chưa đủ.
- [ ] Báo cáo phân bố/thiếu/trùng/theo người.
- [ ] Có baseline Fixed-45 và Rule trên cùng tập đánh giá.
- [ ] Có ít nhất 5 FP và 5 FN được phân tích.
- [ ] Kế hoạch chia dữ liệu loại bỏ leakage.

## Cổng 4 — sẵn sàng release

- [ ] Apache-2.0, SPDX, third-party notices và SBOM đầy đủ.
- [ ] Không đóng gói PDF/dataset/model chưa có quyền phân phối.
- [ ] README máy sạch chạy được trong 10 phút.
- [ ] PWA hoạt động offline trên desktop và điện thoại.
- [ ] Tag/release SemVer, changelog và checksum.
- [ ] Video demo, dữ liệu synthetic và demo offline dự phòng.
- [ ] Nhóm dự thi chính thức tối đa 3 người.

## Ký xác nhận chuyển giao

| Vai trò | Họ tên | Ngày | Xác nhận |
|---|---|---|---|
| Chủ dự án/giảng viên |  |  |  |
| Sinh viên vai trò A |  |  |  |
| Sinh viên vai trò B |  |  |  |
| Sinh viên vai trò C |  |  |  |
