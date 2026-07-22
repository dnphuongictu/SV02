# Sổ tay dữ liệu FocusMate

Mỗi dòng là một phiên học theo `data/study_session.schema.json`. Phân biệt:
`need_break` là tự báo độc lập sau phiên; `break_suggested` là dự đoán; `accepted`
là hành vi sau lời nhắc. Không sao chép dự đoán thành nhãn.

Dùng mã ẩn danh, không lưu tên/nội dung học riêng tư. Thời gian kết thúc phải sau
bắt đầu; focus 1-5; fatigue 1-10. Khi dùng ML, chia train/test theo người, không
chia ngẫu nhiên từng phiên. Ghi `rule_version` để tái lập quyết định.
