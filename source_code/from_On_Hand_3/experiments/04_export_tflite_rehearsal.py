#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Phase 3 deployment REHEARSAL: export the raw-signal CNN1D to TFLite and
compare FP32 vs full-INT8 on desktop.

This is explicitly NOT a cognitive-load result and NOT a Pixel Watch 2
benchmark:

- The model is trained on WESAD stress-proxy labels (see CLAUDE.md warning),
  not cognitive-load ground truth.
- The train/validation/eval subject split below is a SINGLE split (not LOSO),
  used only to produce one exportable checkpoint and a rough sanity number for
  quantization degradation. It is not a generalization claim.
- All latency numbers are desktop CPU only. Implementation_Plan.md is explicit
  that device latency must never be inferred from desktop numbers; a real
  Pixel Watch 2 benchmark is still required before any deployment decision.

Pipeline: torch model -> ONNX -> onnx2tf -> TFLite (float32, full-INT8).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.cnn_training import channel_stats, compute_metrics, fit_cnn1d  # noqa: E402


def _subject_split(subjects: list[str]) -> tuple[list[str], str, list[str]]:
    ordered = sorted(subjects)
    if len(ordered) < 4:
        raise ValueError("Need at least 4 subjects for train/validation/eval split")
    eval_subjects = ordered[-2:]
    validation_subject = ordered[-3]
    train_subjects = ordered[:-3]
    return train_subjects, validation_subject, eval_subjects


def _benchmark_tflite(model_path: Path, samples_nwc: np.ndarray, y_true: np.ndarray, repeats: int) -> dict:
    import tensorflow as tf

    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    input_scale, input_zero_point = input_detail["quantization"]
    output_scale, output_zero_point = output_detail["quantization"]

    def quantize_input(sample: np.ndarray) -> np.ndarray:
        if input_detail["dtype"] == np.float32:
            return sample.astype(np.float32)
        quantized = np.round(sample / input_scale + input_zero_point)
        return np.clip(quantized, -128, 127).astype(input_detail["dtype"])

    def dequantize_output(raw_output: np.ndarray) -> np.ndarray:
        if output_detail["dtype"] == np.float32:
            return raw_output
        return (raw_output.astype(np.float32) - output_zero_point) * output_scale

    predictions = []
    for sample in samples_nwc:
        interpreter.set_tensor(input_detail["index"], quantize_input(sample[np.newaxis, ...]))
        interpreter.invoke()
        logits = dequantize_output(interpreter.get_tensor(output_detail["index"]))
        predictions.append(int(np.argmax(logits[0])))

    warmup_sample = quantize_input(samples_nwc[0][np.newaxis, ...])
    for _ in range(5):
        interpreter.set_tensor(input_detail["index"], warmup_sample)
        interpreter.invoke()
    timings = []
    for _ in range(repeats):
        sample = quantize_input(samples_nwc[np.random.randint(len(samples_nwc))][np.newaxis, ...])
        start = time.perf_counter()
        interpreter.set_tensor(input_detail["index"], sample)
        interpreter.invoke()
        interpreter.get_tensor(output_detail["index"])
        timings.append(time.perf_counter() - start)

    scores = compute_metrics(y_true, np.asarray(predictions))
    return {
        "model_size_bytes": model_path.stat().st_size,
        "desktop_latency_ms_mean": float(np.mean(timings) * 1000.0),
        "desktop_latency_ms_p95": float(np.percentile(timings, 95) * 1000.0),
        "predictions": predictions,
        **{f"eval_{name}": value for name, value in scores.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/tflite_rehearsal")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--kernel-size", type=int, default=5)
    parser.add_argument("--calibration-samples", type=int, default=100)
    parser.add_argument("--latency-repeats", type=int, default=50)
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()

    import torch

    torch.manual_seed(args.random_seed)
    np.random.seed(args.random_seed)

    archive = np.load(args.dataset)
    x = np.asarray(archive["X"], dtype=np.float32)
    y = np.asarray(archive["y"], dtype=np.int64)
    subjects = np.asarray(archive["subject_id"]).astype(str)
    class_count = int(np.max(y)) + 1

    train_subjects, validation_subject, eval_subjects = _subject_split(sorted(set(subjects.tolist())))
    train_mask = np.isin(subjects, train_subjects)
    validation_mask = subjects == validation_subject
    eval_mask = np.isin(subjects, eval_subjects)
    print(f"train_subjects={train_subjects}")
    print(f"validation_subject={validation_subject}")
    print(f"eval_subjects={eval_subjects} (single split, NOT LOSO — sanity check only)")

    mean, std = channel_stats(x[train_mask])

    def normalized(mask: np.ndarray) -> np.ndarray:
        return (x[mask] - mean) / std

    device = torch.device("cpu")
    model, best_validation_f1 = fit_cnn1d(
        normalized(train_mask),
        y[train_mask],
        normalized(validation_mask),
        y[validation_mask],
        class_count=class_count,
        kernel_size=args.kernel_size,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        patience=args.patience,
        device=device,
    )

    eval_x = normalized(eval_mask)
    eval_y = y[eval_mask]
    with torch.no_grad():
        torch_logits = model(torch.from_numpy(eval_x))
        torch_predictions = torch_logits.argmax(dim=1).numpy()
    torch_scores = compute_metrics(eval_y, torch_predictions)
    print(f"Single-split (non-LOSO) sanity eval on {eval_subjects}: {torch_scores}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = args.output_dir / "model.onnx"
    dummy = torch.zeros(1, x.shape[1], x.shape[2], dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy,
        str(onnx_path),
        input_names=["input"],
        output_names=["logits"],
        opset_version=13,
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
    )

    calibration_pool = normalized(train_mask)
    calibration_count = min(args.calibration_samples, len(calibration_pool))
    calibration_indices = np.random.choice(len(calibration_pool), size=calibration_count, replace=False)
    calibration_nwc = np.transpose(calibration_pool[calibration_indices], (0, 2, 1)).astype(np.float32)
    calibration_path = args.output_dir / "calibration.npy"
    np.save(calibration_path, calibration_nwc)

    import onnx2tf

    tf_output_dir = args.output_dir / "tf"
    onnx2tf.convert(
        input_onnx_file_path=str(onnx_path),
        output_folder_path=str(tf_output_dir),
        output_signaturedefs=True,
        output_integer_quantized_tflite=True,
        custom_input_op_name_np_data_path=[
            ["input", str(calibration_path), [0.0], [1.0]],
        ],
        non_verbose=True,
    )

    eval_nwc = np.transpose(eval_x, (0, 2, 1)).astype(np.float32)
    fp32_result = _benchmark_tflite(
        tf_output_dir / "model_float32.tflite", eval_nwc, eval_y, args.latency_repeats
    )
    int8_result = _benchmark_tflite(
        tf_output_dir / "model_full_integer_quant.tflite", eval_nwc, eval_y, args.latency_repeats
    )
    agreement = float(
        np.mean(np.asarray(fp32_result["predictions"]) == np.asarray(int8_result["predictions"]))
    )

    summary = {
        "warning": "REHEARSAL ONLY on WESAD stress-proxy; not cognitive-load, not LOSO, not a device benchmark",
        "train_subjects": train_subjects,
        "validation_subject": validation_subject,
        "eval_subjects": eval_subjects,
        "best_validation_macro_f1": best_validation_f1,
        "torch_fp32_eval": torch_scores,
        "tflite_fp32": {k: v for k, v in fp32_result.items() if k != "predictions"},
        "tflite_int8": {k: v for k, v in int8_result.items() if k != "predictions"},
        "fp32_vs_int8_prediction_agreement": agreement,
        "size_reduction_ratio": fp32_result["model_size_bytes"] / int8_result["model_size_bytes"],
        "desktop_latency_speedup_ratio": (
            fp32_result["desktop_latency_ms_mean"] / int8_result["desktop_latency_ms_mean"]
        ),
    }
    (args.output_dir / "rehearsal_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
