#!/usr/bin/env python3
"""Confound-controlled WAUC baselines: residualize each physiological feature
against session-structure metadata (session_no, pw_label) before
classification.

Motivation (see `paper/draft_v2.md` Section V-B-1 / VI, `PHASE_WAUC_RUN_LOG.md`):
a classifier given only `session_no`+`pw_label` -- zero physiological signal
-- rivals or exceeds the ACC/HRV/both handcrafted-feature baselines' macro-F1
on WAUC, because WAUC's mental-workload label is not independent of its
counterbalanced session design. This script asks the follow-up question that
metadata-only control could not answer on its own: once whatever session/task
-structure signal each physiological feature carries is regressed out
(`on_hand_3.evaluation.residualize_against_metadata`, fit per LOSO training
fold to avoid leakage), does the remainder still predict `mw_label` above
chance? If yes, that is evidence of genuine motion/cardiac signal beyond the
confound. If performance collapses toward chance, the original result was
likely (at least partly) attributable to session structure.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from on_hand_3.evaluation import run_loso, save_loso_artifacts, select_feature_columns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=["svm", "mlp"], default=["svm", "mlp"])
    parser.add_argument(
        "--modalities", nargs="+", choices=["hrv", "acc", "both"], default=["hrv", "acc", "both"]
    )
    parser.add_argument(
        "--metadata-columns", nargs="+", default=["session_no", "pw_label"]
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/confound_residualized")
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    table = pd.read_csv(args.features)
    metadata_columns = tuple(args.metadata_columns)
    for modality in args.modalities:
        columns = select_feature_columns(table, modality)
        for model_name in args.models:
            folds, predictions, estimator = run_loso(
                table,
                model_name=model_name,
                modality=modality,
                random_seed=args.random_seed,
                residualize_metadata_columns=metadata_columns,
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
                f"{model_name}/{modality} (residualized against {metadata_columns}): "
                f"macro-F1={folds.macro_f1.mean():.4f}, "
                f"balanced-accuracy={folds.balanced_accuracy.mean():.4f}"
            )


if __name__ == "__main__":
    main()
