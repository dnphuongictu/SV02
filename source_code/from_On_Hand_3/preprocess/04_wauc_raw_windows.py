#!/usr/bin/env python3
"""Export synchronized WAUC PPG/ACC windows for raw-signal CNNs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.wauc import LABEL_SCHEMES
from on_hand_3.wauc_raw_windows import build_wauc_raw_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/wauc/raw")
    parser.add_argument(
        "--ratings-csv", type=Path, default=ROOT / "data/raw/wauc/subjective_ratings_with_labels.csv"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/wauc_raw_60s.npz")
    parser.add_argument("--label-scheme", choices=LABEL_SCHEMES, default="mw_binary")
    parser.add_argument("--window-seconds", type=float, default=60.0)
    parser.add_argument("--step-seconds", type=float, default=30.0)
    parser.add_argument("--minimum-valid-rr", type=int, default=10)
    args = parser.parse_args()

    dataset = build_wauc_raw_dataset(
        args.data_dir,
        args.ratings_csv,
        label_scheme=args.label_scheme,
        window_seconds=args.window_seconds,
        step_seconds=args.step_seconds,
        minimum_valid_rr=args.minimum_valid_rr,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **dataset)
    subjects = np.unique(dataset["subject_id"])
    print(f"Saved {len(dataset['y']):,} windows from {len(subjects)} subjects to {args.output}")


if __name__ == "__main__":
    main()
