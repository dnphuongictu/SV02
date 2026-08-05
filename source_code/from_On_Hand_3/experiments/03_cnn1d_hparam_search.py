#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Hyperparameter search for the raw-signal CNN1D, selected on validation folds only.

Model selection here never looks at test-fold metrics: for each candidate
config we run the full LOSO loop (which already keeps a held-out validation
subject per fold, separate from the held-out test subject) and rank configs
by `validation_macro_f1_subject_mean`. Only after a winner is picked do we
report its test-fold metrics as the final result, and that is the one and
only time the test folds are consulted.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.cnn_training import train_cnn_loso


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/cnn1d_hparam_search")
    parser.add_argument("--learning-rates", type=float, nargs="+", default=[1e-3, 3e-4])
    parser.add_argument("--kernel-sizes", type=int, nargs="+", default=[5, 7])
    parser.add_argument("--search-epochs", type=int, default=20)
    parser.add_argument("--search-patience", type=int, default=5)
    parser.add_argument("--final-epochs", type=int, default=40)
    parser.add_argument("--final-patience", type=int, default=8)
    parser.add_argument("--t3a-stream-seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument(
        "--late-fusion-ppg-channels",
        type=int,
        default=None,
        help="Search/select using two-branch late fusion (see 02_cnn1d_loso.py) instead of early fusion.",
    )
    args = parser.parse_args()

    archive = np.load(args.dataset)
    x, y, groups = archive["X"], archive["y"], archive["subject_id"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    search_summaries = []
    for learning_rate, kernel_size in itertools.product(args.learning_rates, args.kernel_sizes):
        tag = f"lr{learning_rate:g}_k{kernel_size}"
        results = train_cnn_loso(
            x,
            y,
            groups,
            args.output_dir / "search" / tag,
            epochs=args.search_epochs,
            patience=args.search_patience,
            learning_rate=learning_rate,
            kernel_size=kernel_size,
            random_seed=args.random_seed,
            late_fusion_ppg_channels=args.late_fusion_ppg_channels,
        )
        validation_macro_f1 = float(results.best_validation_macro_f1.mean())
        search_summaries.append(
            {
                "tag": tag,
                "learning_rate": learning_rate,
                "kernel_size": kernel_size,
                "validation_macro_f1_subject_mean": validation_macro_f1,
            }
        )
        print(f"{tag}: validation_macro_f1_subject_mean={validation_macro_f1:.4f}")

    best = max(search_summaries, key=lambda item: item["validation_macro_f1_subject_mean"])
    (args.output_dir / "search_summary.json").write_text(
        json.dumps({"candidates": search_summaries, "selected": best}, indent=2),
        encoding="utf-8",
    )
    print(f"Selected config (by validation only): {best}")

    final_results = train_cnn_loso(
        x,
        y,
        groups,
        args.output_dir / "final",
        epochs=args.final_epochs,
        patience=args.final_patience,
        learning_rate=best["learning_rate"],
        kernel_size=best["kernel_size"],
        random_seed=args.random_seed,
        t3a_stream_seeds=tuple(args.t3a_stream_seeds),
        late_fusion_ppg_channels=args.late_fusion_ppg_channels,
    )
    print(final_results)


if __name__ == "__main__":
    main()
