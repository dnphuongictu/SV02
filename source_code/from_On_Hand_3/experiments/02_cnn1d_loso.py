#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Train raw BVP/ACC CNN1D with LOSO and evaluate sequential T3A."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.cnn_training import train_cnn_loso


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/cnn1d_loso")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--kernel-size", type=int, default=5)
    parser.add_argument("--supports-per-class", type=int, default=10)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--save-fold-models", action="store_true")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore any existing fold_*/checkpoint.json and retrain every fold from scratch.",
    )
    parser.add_argument(
        "--t3a-stream-seeds",
        type=int,
        nargs="+",
        default=[0],
        help="Seeds for the T3A test-stream order; seed 0 keeps the natural dataset order.",
    )
    parser.add_argument(
        "--channels",
        nargs="+",
        default=None,
        help="Subset of channel_names to keep (e.g. bvp, or acc_x acc_y acc_z). Default: all channels.",
    )
    parser.add_argument(
        "--late-fusion-ppg-channels",
        type=int,
        default=None,
        help=(
            "Use two-branch late fusion instead of early (concat-then-conv) fusion: "
            "the first N channels (after --channels filtering) go through their own "
            "Conv1D branch as PPG, the rest through a separate branch as ACC."
        ),
    )
    parser.add_argument(
        "--t3a-supports-sweep",
        type=int,
        nargs="+",
        default=[],
        help=(
            "Additional supports_per_class values to evaluate T3A at (natural stream "
            "order only), reusing the same per-fold embeddings at ~zero extra training "
            "cost. Written to t3a_supports_sweep.csv / summary.json alongside the main "
            "--supports-per-class result."
        ),
    )
    args = parser.parse_args()

    archive = np.load(args.dataset)
    x = archive["X"]
    if args.channels is not None:
        channel_names = [str(name) for name in archive["channel_names"]]
        missing = sorted(set(args.channels) - set(channel_names))
        if missing:
            raise ValueError(f"Unknown channel(s) {missing}; available: {channel_names}")
        indices = [channel_names.index(name) for name in args.channels]
        x = x[:, indices, :]

    results = train_cnn_loso(
        x,
        archive["y"],
        archive["subject_id"],
        args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        patience=args.patience,
        kernel_size=args.kernel_size,
        supports_per_class=args.supports_per_class,
        random_seed=args.random_seed,
        save_fold_models=args.save_fold_models,
        t3a_stream_seeds=tuple(args.t3a_stream_seeds),
        resume=not args.no_resume,
        late_fusion_ppg_channels=args.late_fusion_ppg_channels,
        t3a_supports_sweep=tuple(args.t3a_supports_sweep),
    )
    print(results)


if __name__ == "__main__":
    main()
