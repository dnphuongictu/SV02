# FocusMate AI - Chuan bi du lieu, bai bao va mo hinh

## Bo nen sinh vien

Bat dau tai `../README.md` va `00_HUONG_DAN_GIANG_VIEN_VA_SINH_VIEN.md`. Schema
nam tai `../data/study_session.schema.json`; mau bao cao nam tai
`../reports/MAU_BAO_CAO_KET_QUA.md`.

## 1. Bai toan

Xay dung tro ly hoc tap giup sinh vien quan ly phien hoc, nhac nghi dung thoi diem va tranh lam phien khi dang tap trung. Phien ban dau nen rule-based, sau do moi them AI de giai thich/ca nhan hoa.

## 2. Du lieu can chuan bi

### Du lieu tu ung dung

Moi sinh vien thu 7 ngay, moi ngay 2-4 phien hoc:

- Thoi gian bat dau/ket thuc.
- Mon hoc/loai nhiem vu.
- Muc tap trung tu danh gia 1-5.
- Muc met 1-10.
- So lan nhac nghi.
- Nguoi dung co chap nhan nghi khong.
- Ly do tri hoan neu khong nghi.

Da co file mau tai `data/sample_study_sessions.csv`.

### Nhan can tao

- `should_break`: nen nhac nghi hay khong.
- `interrupt_risk`: thap/vua/cao.
- `accepted`: nguoi dung co dong y nghi khong.

Luu y phuong phap: trong phien ban nen, dung `need_break` (nguoi hoc tu tra loi
sau phien) lam nhan danh gia. `break_suggested` la dau ra cua thuat toan, khong
duoc dung lam nhan dung. Xem schema chi tiet tai `data/README.md`.

## 3. Bai bao/tai lieu can doc

1. Tai lieu noi bo: `On_Hand_3` ve cognitive load.
2. Tai lieu noi bo: `On_Hand_6` ve context-to-action reasoning.
3. Tai lieu noi bo: `InterruptionGuard-Edge` trong tong hop ContextEdge.
4. Android Health/UsageStats documentation neu muon mo rong tracking app usage: https://developer.android.com/reference/android/app/usage/UsageStatsManager
5. Google AI Edge/LiteRT optimization neu them model nhe: https://developers.google.com/edge/litert/conversion/tensorflow/quantization/model_optimization

## 4. Mo hinh nen/nen dung

| Cap do | Lua chon | Dinh dang |
|---|---|---|
| Baseline | Rule engine | Khong can model |
| Nhe | Decision Tree/Logistic Regression | ONNX hoac JSON rule |
| AI giai thich | Gemma-3-270M-IT | GGUF Q4_K_M |
| AI thay the | SmolLM2-360M-Instruct | GGUF Q4_K_M |

Khuyen nghi: chi dung SLM de viet loi nhac/giai thich, khong dung SLM quyet dinh nhac nghi trong phien ban dau.

## 5. Viec can lam tuan dau

1. Doc `README.md` va chay web nen da co trong `src/`.
2. Nap du lieu mau, them phien va xuat CSV.
3. Chay 7 test cua bo luat trong `tests/ruleEngine.test.mjs`.
4. Giai thich su khac nhau giua `need_break`, `break_suggested` va `accepted`.
5. Lam theo Chang 0-2 trong `docs/00_HUONG_DAN_GIANG_VIEN_VA_SINH_VIEN.md`.

## 6. Ket qua toi thieu

- Demo quan ly phien hoc.
- 50-100 session log.
- Bao cao rule nao nhac dung/sai.
- Chuc nang goi y nghi ngan gon.
