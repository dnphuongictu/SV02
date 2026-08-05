#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Run subject-independent SVM/MLP baselines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.evaluation import run_loso, save_loso_artifacts, select_feature_columns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=["svm", "mlp"], default=["svm", "mlp"])
    parser.add_argument(
        "--modalities", nargs="+", choices=["hrv", "acc", "both", "metadata"], default=["both"]
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/baselines")
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    table = pd.read_csv(args.features)
    for modality in args.modalities:
        columns = select_feature_columns(table, modality)
        for model_name in args.models:
            folds, predictions, estimator = run_loso(
                table,
                model_name=model_name,
                modality=modality,
                random_seed=args.random_seed,
            )
            save_loso_artifacts(
                args.output_dir,
                model_name,
                modality,
                folds,
                predictions,
                estimator,
                columns,
            )
            print(
                f"{model_name}/{modality}: "
                f"macro-F1={folds.macro_f1.mean():.4f}, "
                f"balanced-accuracy={folds.balanced_accuracy.mean():.4f}"
            )


if __name__ == "__main__":
    main()
