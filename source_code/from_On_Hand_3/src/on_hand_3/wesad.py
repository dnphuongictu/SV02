"""WESAD adapter with explicit stress-proxy semantics."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from .features import extract_window_features
from .windowing import dominant_label, iter_windows, time_slice

WESAD_RATES = {"bvp": 64.0, "acc": 32.0, "label": 700.0}
LABEL_SCHEMES = {
    "stress_binary": {
        1: (0, "baseline"),
        2: (1, "stress"),
    },
    "affect_3class": {
        1: (0, "baseline"),
        2: (1, "stress"),
        3: (2, "amusement"),
    },
}


def _subject_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("S")
    return (int(suffix) if suffix.isdigit() else 10**9, path.name)


def discover_subject_files(data_dir: Path) -> list[Path]:
    files = []
    for directory in sorted(data_dir.glob("S*"), key=_subject_sort_key):
        candidate = directory / f"{directory.name}.pkl"
        if candidate.is_file():
            files.append(candidate)
    return files


def load_subject_pickle(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load an official WESAD subject pickle.

    Pickle can execute code. Only pass files obtained from a trusted WESAD
    distribution.
    """

    with path.open("rb") as handle:
        payload = pickle.load(handle, encoding="latin1")
    bvp = np.asarray(payload["signal"]["wrist"]["BVP"], dtype=np.float64).reshape(-1)
    acc = np.asarray(payload["signal"]["wrist"]["ACC"], dtype=np.float64)
    labels = np.asarray(payload["label"]).reshape(-1)
    if acc.ndim != 2 or acc.shape[1] != 3:
        raise ValueError(f"Unexpected wrist ACC shape in {path}: {acc.shape}")
    return bvp, acc, labels


def subject_feature_table(
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
    minimum_frequency_duration_seconds: float = 120.0,
) -> pd.DataFrame:
    if label_scheme not in LABEL_SCHEMES:
        raise ValueError(f"Unknown label scheme: {label_scheme}")
    mapping = LABEL_SCHEMES[label_scheme]
    duration = min(
        len(bvp) / WESAD_RATES["bvp"],
        len(acc) / WESAD_RATES["acc"],
        len(labels) / WESAD_RATES["label"],
    )

    rows: list[dict[str, object]] = []
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
        features = extract_window_features(
            bvp_segment,
            acc_segment,
            bvp_sampling_rate_hz=WESAD_RATES["bvp"],
            minimum_frequency_duration_seconds=minimum_frequency_duration_seconds,
        )
        if features["quality_rr_count"] < minimum_valid_rr:
            continue

        target, target_name = mapping[source_label]
        rows.append(
            {
                "dataset": "wesad_stress_proxy",
                "subject_id": subject_id,
                "window_index": window.index,
                "start_seconds": window.start_seconds,
                "end_seconds": window.end_seconds,
                "label": target,
                "label_name": target_name,
                "label_purity": purity,
                **features,
            }
        )
    return pd.DataFrame(rows)


def build_wesad_feature_table(
    data_dir: Path,
    *,
    label_scheme: str = "stress_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_label_purity: float = 0.8,
    minimum_valid_rr: int = 10,
    minimum_frequency_duration_seconds: float = 120.0,
) -> pd.DataFrame:
    subject_files = discover_subject_files(data_dir)
    if not subject_files:
        raise FileNotFoundError(
            f"No WESAD subject files found below {data_dir}. "
            "Expected data/raw/wesad/S2/S2.pkl, etc."
        )

    tables = []
    for subject_file in subject_files:
        bvp, acc, labels = load_subject_pickle(subject_file)
        table = subject_feature_table(
            subject_file.parent.name,
            bvp,
            acc,
            labels,
            label_scheme=label_scheme,
            window_seconds=window_seconds,
            step_seconds=step_seconds,
            minimum_label_purity=minimum_label_purity,
            minimum_valid_rr=minimum_valid_rr,
            minimum_frequency_duration_seconds=minimum_frequency_duration_seconds,
        )
        if not table.empty:
            tables.append(table)
    if not tables:
        raise RuntimeError("WESAD files were found, but no valid labeled windows were produced")
    return pd.concat(tables, ignore_index=True)
