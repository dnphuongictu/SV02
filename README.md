# FocusMate AI - du an khoi dau cho sinh vien NCKH

Day la de tai duoc chon lam du an mau dau tien trong bo 6 de tai. Phien ban nen la
mot web app chay cuc bo, khong can cai framework va khong can mo hinh AI.

## Bat dau trong 5 phut

Yeu cau: Python 3 (de mo web server) va Node.js 18+ (chi de chay test).

```powershell
cd 02_Smart_Study_Break
python -m http.server 8000 -d src
```

Mo `http://localhost:8000`, bam **Nap du lieu mau**, sau do them mot phien hoc.

Chay kiem thu baseline:

```powershell
node --test tests/ruleEngine.test.mjs
```

## Thu tu tai lieu

1. `docs/00_HUONG_DAN_GIANG_VIEN_VA_SINH_VIEN.md`: giao an 8 chang va tieu chi nghiem thu.
2. `docs/01_chuan_bi_du_lieu_bai_bao_mo_hinh.md`: tong quan du lieu, tai lieu, model.
3. `docs/02_DE_CUONG_NCKH_TOI_THIEU.md`: cau hoi, gia thuyet va thiet ke thuc nghiem.
4. `data/README.md`: schema va quy tac quan ly du lieu.

## Ranh gioi phien ban nen

Sinh vien chi sua `src/`, `tests/`, `data/weekly_logs/` va `reports/`. Thu muc
`source_code/from_*` la tai lieu tham khao nang, chua dung trong 4 tuan dau.

Phien ban 1 phai tra loi duoc mot cau hoi don gian: **khi nao nen goi y nghi de
nguoi hoc chap nhan ma khong bi lam phien?** AI/ML chi duoc them sau khi baseline
rule-based da chay, co log va co ket qua danh gia.
