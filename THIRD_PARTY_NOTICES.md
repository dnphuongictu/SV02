# Third-party notices

Ngày kiểm kê: **05/08/2026**

Tệp này phân biệt mã do chủ dự án sở hữu với runtime, thư viện, dữ liệu, bài báo
và artefact có nguồn gốc bên ngoài. Apache-2.0 của kho **không thay thế** giấy
phép hoặc điều khoản của bên thứ ba.

## Phạm vi Apache-2.0 do chủ dự án xác nhận

Chủ dự án xác nhận sở hữu và có quyền cấp phép Apache-2.0 cho:

- Mã sản phẩm FocusMate tại `src/` và kiểm thử tại `tests/`.
- Mã nghiên cứu On_Hand_3 tại `source_code/from_On_Hand_3/`.
- Mã Wear OS tham khảo tại `source_code/from_On_Hand_3_android_wear/`, ngoại
  trừ Gradle Wrapper và các dependency được nêu dưới đây.
- Tài liệu, schema và báo cáo do nhóm dự án tự viết, trừ các PDF bài báo.

Các tệp mã thuộc phạm vi này dùng SPDX identifier:
`SPDX-License-Identifier: Apache-2.0`.

## Thành phần bên thứ ba không được bundle trong PWA lõi

| Thành phần | Cách sử dụng | Trạng thái phát hành |
|---|---|---|
| Python 3 và Node.js | Runtime/tool kiểm thử | Không bundle; người dùng tự cài |
| NumPy, pandas, SciPy, scikit-learn, joblib | Pipeline nghiên cứu On_Hand_3 | Không cần cho PWA; phải khóa phiên bản và tạo SBOM nếu phát hành pipeline |
| Android Gradle Plugin, Kotlin plugin | Build Wear OS reference | Tải từ repository khai báo trong Gradle |
| AndroidX Wear/Core | Dependency Wear OS | Tải từ Google/Maven repository; giữ notice/giấy phép của artefact |
| Google Play services Wearable | Kết nối Wear OS | Chịu điều khoản Google tương ứng; không thuộc Apache-2.0 của dự án |
| Gradle Wrapper | Công cụ build đi kèm | Thành phần của Gradle; giữ nguyên wrapper và notice upstream |

Release PWA lõi không cần các dependency Python/Android nói trên.

## Dữ liệu và artefact nghiên cứu

| Tài sản | Vị trí | Quy tắc |
|---|---|---|
| Kết quả/model dẫn xuất WESAD | `models/from_On_Hand_3/wesad_*` | Chủ dự án sở hữu mã và output đã tạo, nhưng quyền phân phối vẫn phải đối chiếu điều khoản dataset WESAD trước release |
| Artefact TFLite/ONNX rehearsal | `models/from_On_Hand_3/tflite_rehearsal/` | Chỉ là reference; phải ghi model/schema/toolchain và checksum nếu phát hành |
| WAUC | Không bundle raw dataset trong kho FocusMate | Người dùng phải lấy từ nguồn hợp lệ; không tái phân phối raw data |
| Dữ liệu phiên mẫu FocusMate | `data/sample_study_sessions.csv` | Synthetic do dự án tạo; thuộc Apache-2.0 trừ khi được ghi khác |

Model card và data card phải ghi dataset, protocol, metric, giới hạn và điều khoản
phân phối; quyền sở hữu trọng số không tự động cấp lại quyền đối với dữ liệu nguồn.

## Bài báo tham khảo

Các PDF tại `docs/papers/` là tài liệu tham khảo và **không** được cấp phép lại
theo Apache-2.0. Không đưa các PDF này vào release công khai trừ khi giấy phép
hoặc quyền phân phối của từng bài đã được xác minh. Thay vào đó nên ghi DOI/URL
trong `docs/papers/README.md`.

## Mã được sinh tự động

- `models/from_On_Hand_3/tflite_rehearsal/tf/schema.fbs` chứa thông báo Apache-2.0
  của TensorFlow và phải giữ nguyên.
- `schema_generated.py` được FlatBuffers compiler sinh từ schema nói trên; không
  chỉnh sửa thủ công và phải phân phối cùng notice/schema nguồn.

## Việc còn lại trước v0.1.0

1. Tạo lockfile hoặc requirements có phiên bản cho pipeline được phát hành.
2. Sinh SBOM cho PWA và component Wear/Python nếu chúng nằm trong release.
3. Ghi URL, phiên bản, checksum và license của từng model/dataset thực sự phát hành.
4. Loại PDF và artefact chưa xác minh khỏi gói release.
