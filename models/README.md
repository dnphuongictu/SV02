# Models - FocusMate AI

## Baseline khuyen nghi

Khong can model trong 2 tuan dau. Dung rule engine:

```text
if duration_minutes >= 50 and fatigue_score >= 6:
  suggest_break = true
if user_rejected_recently:
  delay_next_suggestion = 20 minutes
```

## Model nhe co the them

1. Decision Tree/Logistic Regression
   - Input: duration, fatigue, focus, time_of_day, rejected_recently.
   - Output: `suggest_break`.
   - Export: ONNX hoac JSON rule.

2. Gemma-3-270M-IT GGUF Q4_K_M
   - Link tham khao: https://huggingface.co/unsloth/gemma-3-270m-it-GGUF
   - Vai tro: sinh loi nhac/giai thich ngan, khong quyet dinh chinh.

3. SmolLM2-360M-Instruct GGUF Q4_K_M
   - Link tham khao: https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF
   - Vai tro: so sanh voi Gemma neu co thoi gian.
