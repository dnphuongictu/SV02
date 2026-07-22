# Du lieu - FocusMate AI

## Cau truc goi y

```text
data/
  sample_study_sessions.csv
  study_session.schema.json
  weekly_logs/
  exports/
```

## Truong du lieu chinh

- `session_id`
- `student_code`
- `start_time`
- `end_time`
- `subject`
- `task_type`
- `focus_score`
- `fatigue_score`
- `break_suggested`
- `need_break`: nguoi hoc tu bao co thuc su can nghi sau phien; day la nhan danh gia.
- `accepted`
- `rule_version`
- `decision_reason`
- `note`

Khong luu ten that cua sinh vien trong file public.

Schema may doc nam tai `study_session.schema.json`; huong dan dien giai nam tai
`docs/03_SO_TAY_DU_LIEU.md`.

Phan biet ba truong quan trong:

- `need_break` la cau tra loi doc lap cua nguoi hoc.
- `break_suggested` la du doan cua he thong.
- `accepted` chi la hanh vi sau khi co loi nhac, khong tu dong dong nghia voi
  `need_break`.

Mien gia tri: `focus_score` tu 1-5, `fatigue_score` tu 1-10, thoi gian ket thuc
phai sau thoi gian bat dau. Khong tu dien gia tri thieu bang 0.
