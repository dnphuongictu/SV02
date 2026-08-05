#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Convert extracted WESAD subjects into a leakage-safe feature table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.wesad import LABEL_SCHEMES, build_wesad_feature_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/wesad")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/wesad_stress_proxy.csv")
    parser.add_argument("--label-scheme", choices=LABEL_SCHEMES, default="stress_binary")
    parser.add_argument("--window-seconds", type=float, default=60.0)
    parser.add_argument("--step-seconds", type=float, default=30.0)
    parser.add_argument("--minimum-label-purity", type=float, default=0.8)
    parser.add_argument("--minimum-valid-rr", type=int, default=10)
    parser.add_argument("--minimum-frequency-duration-seconds", type=float, default=120.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    table = build_wesad_feature_table(
        args.data_dir,
        label_scheme=args.label_scheme,
        window_seconds=args.window_seconds,
        step_seconds=args.step_seconds,
        minimum_label_purity=args.minimum_label_purity,
        minimum_valid_rr=args.minimum_valid_rr,
        minimum_frequency_duration_seconds=args.minimum_frequency_duration_seconds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    print(f"Saved {len(table):,} windows from {table.subject_id.nunique()} subjects to {args.output}")
    print(table.groupby(["subject_id", "label_name"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
