"""Create synchronized raw BVP/ACC windows for CNN experiments."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .features import extract_rr_intervals
from .wesad import LABEL_SCHEMES, WESAD_RATES, discover_subject_files, load_subject_pickle
from .windowing import dominant_label, iter_windows, time_slice


def _resample_acc(acc: np.ndarray, target_samples: int) -> np.ndarray:
    source_position = np.linspace(0.0, 1.0, len(acc), endpoint=False)
    target_position = np.linspace(0.0, 1.0, target_samples, endpoint=False)
    return np.column_stack(
        [np.interp(target_position, source_position, acc[:, axis]) for axis in range(3)]
    )


def subject_raw_windows(
    subject_id: str,
    bvp: np.ndarray,
    acc: np.ndarray,
    labels: np.ndarray,
    *,
    label_scheme: str = "stress_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_label_purity: float = 0.8,
    minimum_valid_rr: int = 10,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    if label_scheme not in LABEL_SCHEMES:
        raise ValueError(f"Unknown label scheme: {label_scheme}")
    mapping = LABEL_SCHEMES[label_scheme]
    duration = min(
        len(bvp) / WESAD_RATES["bvp"],
        len(acc) / WESAD_RATES["acc"],
        len(labels) / WESAD_RATES["label"],
    )
    sample_count = int(round(window_seconds * WESAD_RATES["bvp"]))
    windows, targets, metadata = [], [], []

    for window in iter_windows(duration, window_seconds, step_seconds):
        label_segment = time_slice(
            labels, WESAD_RATES["label"], window.start_seconds, window.end_seconds
        )
        source_label, purity = dominant_label(label_segment, set(mapping))
        if source_label is None or purity < minimum_label_purity:
            continue
        bvp_segment = time_slice(
            bvp, WESAD_RATES["bvp"], window.start_seconds, window.end_seconds
        )
        acc_segment = time_slice(
            acc, WESAD_RATES["acc"], window.start_seconds, window.end_seconds
        )
        if len(bvp_segment) != sample_count or len(acc_segment) < 2:
            continue
        rr = extract_rr_intervals(bvp_segment, WESAD_RATES["bvp"])
        if rr.rr_ms.size < minimum_valid_rr:
            continue

        synchronized_acc = _resample_acc(acc_segment, sample_count)
        raw_window = np.column_stack([bvp_segment, synchronized_acc]).T.astype(np.float32)
        target, target_name = mapping[source_label]
        windows.append(raw_window)
        targets.append(target)
        metadata.append(
            {
                "subject_id": subject_id,
                "window_index": window.index,
                "start_seconds": window.start_seconds,
                "end_seconds": window.end_seconds,
                "label_name": target_name,
                "label_purity": purity,
                "valid_rr_ratio": rr.valid_rr_ratio,
            }
        )

    empty = np.empty((0, 4, sample_count), dtype=np.float32)
    return (
        np.stack(windows) if windows else empty,
        np.asarray(targets, dtype=np.int64),
        metadata,
    )


def build_wesad_raw_dataset(
    data_dir: Path,
    *,
    label_scheme: str = "stress_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_label_purity: float = 0.8,
    minimum_valid_rr: int = 10,
) -> dict[str, np.ndarray]:
    subject_files = discover_subject_files(data_dir)
    if not subject_files:
        raise FileNotFoundError(f"No WESAD subject files found below {data_dir}")

    all_x, all_y, all_meta = [], [], []
    for subject_file in subject_files:
        bvp, acc, labels = load_subject_pickle(subject_file)
        x, y, metadata = subject_raw_windows(
            subject_file.parent.name,
            bvp,
            acc,
            labels,
            label_scheme=label_scheme,
            window_seconds=window_seconds,
            step_seconds=step_seconds,
            minimum_label_purity=minimum_label_purity,
            minimum_valid_rr=minimum_valid_rr,
        )
        if len(y):
            all_x.append(x)
            all_y.append(y)
            all_meta.extend(metadata)
    if not all_x:
        raise RuntimeError("No valid raw windows were produced")

    return {
        "X": np.concatenate(all_x),
        "y": np.concatenate(all_y),
        "subject_id": np.asarray([item["subject_id"] for item in all_meta]),
        "window_index": np.asarray([item["window_index"] for item in all_meta], dtype=np.int64),
        "start_seconds": np.asarray([item["start_seconds"] for item in all_meta], dtype=np.float64),
        "label_name": np.asarray([item["label_name"] for item in all_meta]),
        "label_purity": np.asarray([item["label_purity"] for item in all_meta], dtype=np.float32),
        "valid_rr_ratio": np.asarray(
            [item["valid_rr_ratio"] for item in all_meta], dtype=np.float32
        ),
        "channel_names": np.asarray(["bvp", "acc_x", "acc_y", "acc_z"]),
        "sampling_rate_hz": np.asarray(WESAD_RATES["bvp"]),
        "window_seconds": np.asarray(window_seconds),
    }
