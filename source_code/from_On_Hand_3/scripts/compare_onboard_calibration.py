#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Compare on-device (Pixel Watch 2) ACC feature distributions against the
WAUC training distribution, to give quantitative evidence for the
accelerometer unit-conversion fix in `android_wear/.../AccCollector.kt`
(Empatica E4 raw ADC counts vs Android SI-unit accelerometer, ~6.5x scale
mismatch) beyond the qualitative rest-vs-shake confidence check already
recorded in PROJECT_STATUS.md.

Usage:
    adb pull /sdcard/Android/data/vn.edu.uit.tpkd.wear.cogload/files/prediction_log.csv \
        scratch/onboard_log.csv
    python scripts/compare_onboard_calibration.py \
        --training-features data/processed/wauc_mental_workload_60s.csv \
        --onboard-log scratch/onboard_log.csv \
        --output artifacts/calibration_comparison.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "acc_mean_magnitude",
    "acc_std_magnitude",
    "acc_dynamic_energy",
    "acc_zero_crossing_rate",
    "acc_std_x",
    "acc_std_y",
    "acc_std_z",
]


def summarize(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    summary = frame[columns].agg(["mean", "std", "min", "max"]).T
    summary.index.name = "feature"
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--training-features",
        type=Path,
        default=Path("data/processed/wauc_mental_workload_60s.csv"),
        help="WAUC handcrafted-feature table used to train the deployed MLP.",
    )
    parser.add_argument(
        "--onboard-log",
        type=Path,
        required=True,
        help="CSV pulled from the watch via `adb pull` (PredictionLogger.kt output).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/calibration_comparison.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    training = pd.read_csv(args.training_features)
    onboard = pd.read_csv(args.onboard_log)

    missing = set(FEATURE_COLUMNS) - set(onboard.columns)
    if missing:
        raise SystemExit(f"On-device log is missing expected columns: {sorted(missing)}")

    training_summary = summarize(training, FEATURE_COLUMNS)
    onboard_summary = summarize(onboard, FEATURE_COLUMNS)

    lines = [
        "# On-device vs. WAUC-training ACC feature calibration",
        "",
        f"Training table: `{args.training_features}` ({len(training)} windows, 41 subjects).",
        f"On-device log: `{args.onboard_log}` ({len(onboard)} windows, Pixel Watch 2, "
        "post unit-conversion-fix).",
        "",
        "| Feature | Train mean | Train std | Train min | Train max | "
        "On-device mean | On-device std | On-device min | On-device max | "
        "On-device mean within train [min,max]? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for feature in FEATURE_COLUMNS:
        train_row = training_summary.loc[feature]
        onboard_row = onboard_summary.loc[feature]
        within_range = bool(train_row["min"] <= onboard_row["mean"] <= train_row["max"])
        lines.append(
            f"| {feature} | {train_row['mean']:.4g} | {train_row['std']:.4g} | "
            f"{train_row['min']:.4g} | {train_row['max']:.4g} | "
            f"{onboard_row['mean']:.4g} | {onboard_row['std']:.4g} | "
            f"{onboard_row['min']:.4g} | {onboard_row['max']:.4g} | "
            f"{'yes' if within_range else '**NO**'} |"
        )
    lines.append("")
    out_of_range = [
        feature
        for feature in FEATURE_COLUMNS
        if not (
            training_summary.loc[feature, "min"]
            <= onboard_summary.loc[feature, "mean"]
            <= training_summary.loc[feature, "max"]
        )
    ]
    if out_of_range:
        lines.append(
            f"**{len(out_of_range)}/7 feature(s) fall outside the training range on average**: "
            f"{', '.join(out_of_range)}. This would indicate the unit-conversion fix is "
            "incomplete or a further calibration factor is needed for these specific features."
        )
    else:
        lines.append(
            "All 7 features fall within the WAUC training range on average, consistent with "
            "the unit-conversion fix bringing on-device features back into the training "
            "distribution."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
