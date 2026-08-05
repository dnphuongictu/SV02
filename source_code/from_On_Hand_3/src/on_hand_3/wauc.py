# SPDX-License-Identifier: Apache-2.0

"""WAUC adapter — genuine MATB-II mental-workload ground truth (not a stress proxy).

Each subject recorded 6 MATB-II sessions (`info == "session"` rows in the raw
Empatica E4 CSVs), one per combination of mental workload (low/high) and
physical workload (none/medium/high), order counterbalanced per subject. The
raw CSVs carry no label; ground truth comes from
`subjective_ratings_with_labels.csv`, joined on (participant_id, session_no).
See DATA_STATUS.md for how this mapping was verified.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .features import extract_window_features
from .windowing import iter_windows, time_slice

WAUC_RATES = {"ppg": 64.0, "acc": 32.0}
LABEL_SCHEMES = {
    "mw_binary": {
        0: (0, "low_mw"),
        1: (1, "high_mw"),
    },
}


def _subject_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("S")
    return (int(suffix) if suffix.isdigit() else 10**9, path.name)


def discover_subject_dirs(data_dir: Path) -> list[Path]:
    """Return subject directories that have both wrist PPG and ACC recordings.

    A handful of WAUC subjects (S01, S25, S28, S38 in the public release) are
    missing `e4_ppg.csv`/`e4_acc.csv` and are silently excluded here.
    """
    dirs = []
    for directory in sorted(data_dir.glob("S*"), key=_subject_sort_key):
        if (directory / "e4_ppg.csv").is_file() and (directory / "e4_acc.csv").is_file():
            dirs.append(directory)
    return dirs


def participant_id_for_subject(subject_dir_name: str) -> int:
    suffix = subject_dir_name.removeprefix("S")
    if not suffix.isdigit():
        raise ValueError(f"Cannot derive participant id from {subject_dir_name}")
    return 1000 + int(suffix)


def load_session_labels(ratings_csv: Path) -> pd.DataFrame:
    table = pd.read_csv(ratings_csv)
    table = table.rename(columns={"Participant ID": "participant_id"})
    table["participant_id"] = table["participant_id"].astype(int)
    table["session_no"] = table["session_no"].astype(int)
    table["mw_labels"] = table["mw_labels"].astype(int)
    table["pw_labels"] = table["pw_labels"].astype(int)
    return table[["participant_id", "session_no", "mw_labels", "pw_labels"]]


def load_subject_sessions(subject_dir: Path) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    """Return per-`session_no` PPG and ACC arrays, restricted to MATB-II task rows.

    Rows tagged `info == "baseline-1"`/`"baseline-2"` (rest before/after each
    task block) are dropped; only `info == "session"` carries the mental
    workload condition being classified.
    """
    ppg_table = pd.read_csv(subject_dir / "e4_ppg.csv")
    acc_table = pd.read_csv(subject_dir / "e4_acc.csv")
    ppg_task = ppg_table[ppg_table["info"] == "session"].sort_values("time")
    acc_task = acc_table[acc_table["info"] == "session"].sort_values("time")
    ppg_by_session = {
        int(session_no): group["ppg"].to_numpy(dtype=np.float64)
        for session_no, group in ppg_task.groupby("session_no")
    }
    acc_by_session = {
        int(session_no): group[["accX", "accY", "accZ"]].to_numpy(dtype=np.float64)
        for session_no, group in acc_task.groupby("session_no")
    }
    return ppg_by_session, acc_by_session


def subject_feature_table(
    subject_id: str,
    ppg_by_session: dict[int, np.ndarray],
    acc_by_session: dict[int, np.ndarray],
    labels: pd.DataFrame,
    *,
    label_scheme: str = "mw_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_valid_rr: int = 10,
    minimum_frequency_duration_seconds: float = 120.0,
) -> pd.DataFrame:
    if label_scheme not in LABEL_SCHEMES:
        raise ValueError(f"Unknown label scheme: {label_scheme}")
    mapping = LABEL_SCHEMES[label_scheme]
    participant_id = participant_id_for_subject(subject_id)
    subject_labels = labels[labels.participant_id == participant_id].set_index("session_no")

    rows: list[dict[str, object]] = []
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
            features = extract_window_features(
                ppg_segment,
                acc_segment,
                bvp_sampling_rate_hz=WAUC_RATES["ppg"],
                minimum_frequency_duration_seconds=minimum_frequency_duration_seconds,
            )
            if features["quality_rr_count"] < minimum_valid_rr:
                continue

            rows.append(
                {
                    "dataset": "wauc_mental_workload",
                    "subject_id": subject_id,
                    "session_no": session_no,
                    "pw_label": pw_label,
                    "window_index": window.index,
                    "start_seconds": window.start_seconds,
                    "end_seconds": window.end_seconds,
                    "label": target,
                    "label_name": target_name,
                    "label_purity": 1.0,
                    **features,
                }
            )
    return pd.DataFrame(rows)


def drop_subjects_with_sparse_classes(
    table: pd.DataFrame, *, minimum_windows_per_class: int = 5
) -> pd.DataFrame:
    """Drop subjects that never accumulate enough windows in every label class.

    A handful of WAUC subjects have a wrist PPG sensor that reads flat/zero
    for some or all sessions (verified by inspecting raw values, not
    inferred). The per-window RR-quality filter already rejects those dead
    segments, but that can leave a subject with windows for only one label
    (e.g. all surviving windows are `high_mw`). Such a subject cannot
    contribute a meaningful LOSO fold — its "difficulty" is a sensor failure,
    not a modelling result — so it is dropped here rather than silently
    degrading the aggregate macro-F1.
    """
    counts = table.groupby(["subject_id", "label"]).size().unstack(fill_value=0)
    keep = counts.ge(minimum_windows_per_class).all(axis=1)
    dropped = sorted(counts.index[~keep])
    if dropped:
        print(f"Dropping subjects with sparse/missing label classes (likely sensor failure): {dropped}")
    return table[table.subject_id.isin(counts.index[keep])].reset_index(drop=True)


def build_wauc_feature_table(
    data_dir: Path,
    ratings_csv: Path,
    *,
    label_scheme: str = "mw_binary",
    window_seconds: float = 60.0,
    step_seconds: float = 30.0,
    minimum_valid_rr: int = 10,
    minimum_frequency_duration_seconds: float = 120.0,
    minimum_windows_per_class: int = 5,
) -> pd.DataFrame:
    subject_dirs = discover_subject_dirs(data_dir)
    if not subject_dirs:
        raise FileNotFoundError(
            f"No WAUC subject directories with e4_ppg.csv/e4_acc.csv found below {data_dir}"
        )
    labels = load_session_labels(ratings_csv)

    tables = []
    for subject_dir in subject_dirs:
        ppg_by_session, acc_by_session = load_subject_sessions(subject_dir)
        table = subject_feature_table(
            subject_dir.name,
            ppg_by_session,
            acc_by_session,
            labels,
            label_scheme=label_scheme,
            window_seconds=window_seconds,
            step_seconds=step_seconds,
            minimum_valid_rr=minimum_valid_rr,
            minimum_frequency_duration_seconds=minimum_frequency_duration_seconds,
        )
        if not table.empty:
            tables.append(table)
    if not tables:
        raise RuntimeError("WAUC files were found, but no valid labeled windows were produced")
    combined = pd.concat(tables, ignore_index=True)
    return drop_subjects_with_sparse_classes(
        combined, minimum_windows_per_class=minimum_windows_per_class
    )
