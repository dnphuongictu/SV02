"""Create synchronized raw PPG/ACC windows from WAUC for CNN experiments."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .features import extract_rr_intervals
from .wauc import (
    LABEL_SCHEMES,
    WAUC_RATES,
    discover_subject_dirs,
    load_session_labels,
    load_subject_sessions,
    participant_id_for_subject,
)
from .windowing import iter_windows, time_slice


def _resample_acc(acc: np.ndarray, target_samples: int) -> np.ndarray:
    source_position = np.linspace(0.0, 1.0, len(acc), endpoint=False)
    target_position = np.linspace(0.0, 1.0, target_samples, endpoint=False)
    return np.column_stack(
        [np.interp(target_position, source_position, acc[:, axis]) for axis in range(3)]
    )


def subject_raw_windows(
    subject_id: str,
    ppg_by_session: dict[int, np.ndarray],
    acc_by_session: dict[int, np.ndarray],
    labels,
    *,
    label_scheme: str = "mw_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_valid_rr: int = 10,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    if label_scheme not in LABEL_SCHEMES:
        raise ValueError(f"Unknown label scheme: {label_scheme}")
    mapping = LABEL_SCHEMES[label_scheme]
    participant_id = participant_id_for_subject(subject_id)
    subject_labels = labels[labels.participant_id == participant_id].set_index("session_no")
    sample_count = int(round(window_seconds * WAUC_RATES["ppg"]))
    windows, targets, metadata = [], [], []

    for session_no, ppg in ppg_by_session.items():
        acc = acc_by_session.get(session_no)
        if acc is None or session_no not in subject_labels.index:
            continue
        mw_label = int(subject_labels.loc[session_no, "mw_labels"])
        pw_label = int(subject_labels.loc[session_no, "pw_labels"])
        if mw_label not in mapping:
            continue
        target, target_name = mapping[mw_label]

        duration = min(len(ppg) / WAUC_RATES["ppg"], len(acc) / WAUC_RATES["acc"])
        for window in iter_windows(duration, window_seconds, step_seconds):
            ppg_segment = time_slice(ppg, WAUC_RATES["ppg"], window.start_seconds, window.end_seconds)
            acc_segment = time_slice(acc, WAUC_RATES["acc"], window.start_seconds, window.end_seconds)
            if len(ppg_segment) != sample_count or len(acc_segment) < 2:
                continue
            rr = extract_rr_intervals(ppg_segment, WAUC_RATES["ppg"])
            if rr.rr_ms.size < minimum_valid_rr:
                continue

            synchronized_acc = _resample_acc(acc_segment, sample_count)
            raw_window = np.column_stack([ppg_segment, synchronized_acc]).T.astype(np.float32)
            windows.append(raw_window)
            targets.append(target)
            metadata.append(
                {
                    "subject_id": subject_id,
                    "session_no": session_no,
                    "pw_label": pw_label,
                    "window_index": window.index,
                    "start_seconds": window.start_seconds,
                    "end_seconds": window.end_seconds,
                    "label_name": target_name,
                    "valid_rr_ratio": rr.valid_rr_ratio,
                }
            )

    empty = np.empty((0, 4, sample_count), dtype=np.float32)
    return (
        np.stack(windows) if windows else empty,
        np.asarray(targets, dtype=np.int64),
        metadata,
    )


def build_wauc_raw_dataset(
    data_dir: Path,
    ratings_csv: Path,
    *,
    label_scheme: str = "mw_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_valid_rr: int = 10,
    minimum_windows_per_class: int = 5,
) -> dict[str, np.ndarray]:
    subject_dirs = discover_subject_dirs(data_dir)
    if not subject_dirs:
        raise FileNotFoundError(
            f"No WAUC subject directories with e4_ppg.csv/e4_acc.csv found below {data_dir}"
        )
    labels = load_session_labels(ratings_csv)

    all_x, all_y, all_meta = [], [], []
    for subject_dir in subject_dirs:
        ppg_by_session, acc_by_session = load_subject_sessions(subject_dir)
        x, y, metadata = subject_raw_windows(
            subject_dir.name,
            ppg_by_session,
            acc_by_session,
            labels,
            label_scheme=label_scheme,
            window_seconds=window_seconds,
            step_seconds=step_seconds,
            minimum_valid_rr=minimum_valid_rr,
        )
        if len(y):
            all_x.append(x)
            all_y.append(y)
            all_meta.extend(metadata)
    if not all_x:
        raise RuntimeError("No valid raw windows were produced")

    x_all = np.concatenate(all_x)
    y_all = np.concatenate(all_y)
    subject_all = np.asarray([item["subject_id"] for item in all_meta])

    # Same sensor-failure quality gate as build_wauc_feature_table: drop
    # subjects that never accumulate enough windows in every label class.
    counts = pd.DataFrame({"subject_id": subject_all, "label": y_all}).groupby(
        ["subject_id", "label"]
    ).size().unstack(fill_value=0)
    keep_subjects = set(counts.index[counts.ge(minimum_windows_per_class).all(axis=1)])
    dropped = sorted(set(counts.index) - keep_subjects)
    if dropped:
        print(f"Dropping subjects with sparse/missing label classes (likely sensor failure): {dropped}")
    keep_mask = np.isin(subject_all, sorted(keep_subjects))
    x_all = x_all[keep_mask]
    y_all = y_all[keep_mask]
    all_meta = [item for item, keep in zip(all_meta, keep_mask) if keep]

    return {
        "X": x_all,
        "y": y_all,
        "subject_id": np.asarray([item["subject_id"] for item in all_meta]),
        "session_no": np.asarray([item["session_no"] for item in all_meta], dtype=np.int64),
        "pw_label": np.asarray([item["pw_label"] for item in all_meta], dtype=np.int64),
        "window_index": np.asarray([item["window_index"] for item in all_meta], dtype=np.int64),
        "start_seconds": np.asarray([item["start_seconds"] for item in all_meta], dtype=np.float64),
        "label_name": np.asarray([item["label_name"] for item in all_meta]),
        "valid_rr_ratio": np.asarray(
            [item["valid_rr_ratio"] for item in all_meta], dtype=np.float32
        ),
        "channel_names": np.asarray(["ppg", "acc_x", "acc_y", "acc_z"]),
        "sampling_rate_hz": np.asarray(WAUC_RATES["ppg"]),
        "window_seconds": np.asarray(window_seconds),
    }
