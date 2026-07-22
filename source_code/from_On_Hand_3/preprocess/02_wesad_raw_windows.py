#!/usr/bin/env python3
"""Export synchronized WESAD BVP/ACC windows for raw-signal CNNs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.raw_windows import build_wesad_raw_dataset
from on_hand_3.wesad import LABEL_SCHEMES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/wesad")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/wesad_raw_60s.npz")
    parser.add_argument("--label-scheme", choices=LABEL_SCHEMES, default="stress_binary")
    parser.add_argument("--window-seconds", type=float, default=60.0)
    parser.add_argument("--step-seconds", type=float, default=30.0)
    parser.add_argument("--minimum-label-purity", type=float, default=0.8)
    parser.add_argument("--minimum-valid-rr", type=int, default=10)
    args = parser.parse_args()

    dataset = build_wesad_raw_dataset(
        args.data_dir,
        label_scheme=args.label_scheme,
        window_seconds=args.window_seconds,
        step_seconds=args.step_seconds,
        minimum_label_purity=args.minimum_label_purity,
        minimum_valid_rr=args.minimum_valid_rr,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **dataset)
    subjects = np.unique(dataset["subject_id"])
    print(f"Saved {len(dataset['y']):,} windows from {len(subjects)} subjects to {args.output}")


if __name__ == "__main__":
    main()
