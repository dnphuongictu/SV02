#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Post-hoc statistical rigor pass over already-trained LOSO artifacts.

Adds, without retraining anything: bootstrap confidence intervals over
subjects, a subject-structure-preserving permutation test, pooled ROC-AUC
(handcrafted-feature baselines only, which record predict_proba), pooled
confusion matrices, and per-subject metric distribution summaries.

Two artifact layouts are supported:
  - "baseline" (SVM/MLP, `src/on_hand_3/evaluation.py`): a single
    `predictions.csv` (subject_id, y_true, y_pred, confidence,
    probability_class1) plus `fold_metrics.csv` in the directory root.
  - "cnn" (`src/on_hand_3/cnn_training.py`): per-fold `fold_NN_S##/predictions.csv`
    (subject_id, y_true, base_prediction, t3a_prediction) plus a root
    `fold_metrics.csv` with per-fold base/t3a metrics. CNN runs never record
    prediction probabilities, so ROC-AUC is skipped for these and noted as
    such in the output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))


def bootstrap_ci_over_subjects(
    per_subject_metric: pd.Series, *, iterations: int, seed: int
) -> dict[str, float]:
    """Bootstrap CI for the subject-mean of an already-computed per-fold metric.

    Each LOSO fold's metric is treated as one i.i.d. observation (matching
    this project's "subject mean" reporting convention throughout the
    RUN_LOG files) and resampled with replacement.
    """
    values = per_subject_metric.to_numpy(dtype=float)
    rng = np.random.RandomState(seed)
    means = np.empty(iterations, dtype=float)
    for i in range(iterations):
        sample = rng.choice(values, size=values.size, replace=True)
        means[i] = sample.mean()
    return {
        "observed_mean": float(values.mean()),
        "ci_low_2.5pct": float(np.percentile(means, 2.5)),
        "ci_high_97.5pct": float(np.percentile(means, 97.5)),
        "bootstrap_std": float(means.std(ddof=1)),
    }


def permutation_test(
    table: pd.DataFrame,
    y_pred_column: str,
    *,
    group_columns: list[str],
    observed_macro_f1: float,
    iterations: int,
    seed: int,
) -> dict[str, float]:
    """Permute y_true within each group (subject, or subject x pw_label) and
    recompute pooled macro-F1 against the model's *actual* (unpermuted)
    predictions, to test whether the observed score could arise by chance
    given each group's own label distribution.
    """
    rng = np.random.RandomState(seed)
    y_pred = table[y_pred_column].to_numpy()
    y_true_original = table["y_true"].to_numpy()
    grouped_indices = [group.index.to_numpy() for _, group in table.groupby(group_columns)]
    group_values = [y_true_original[indices] for indices in grouped_indices]
    null_scores = np.empty(iterations, dtype=float)
    y_true_permuted = y_true_original.copy()
    for i in range(iterations):
        for indices, values in zip(grouped_indices, group_values, strict=True):
            y_true_permuted[indices] = rng.permutation(values)
        null_scores[i] = _macro_f1(y_true_permuted, y_pred)
    p_value = float(np.mean(null_scores >= observed_macro_f1))
    return {
        "null_mean": float(null_scores.mean()),
        "null_std": float(null_scores.std(ddof=1)),
        "p_value": p_value,
    }


def analyze_baseline_dir(directory: Path, *, iterations: int, seed: int) -> dict:
    predictions = pd.read_csv(directory / "predictions.csv")
    fold_metrics = pd.read_csv(directory / "fold_metrics.csv")

    observed_macro_f1 = _macro_f1(predictions["y_true"], predictions["y_pred"])
    result: dict = {
        "directory": str(directory),
        "kind": "baseline",
        "n_windows": int(len(predictions)),
        "n_subjects": int(fold_metrics["held_out_subject"].nunique()),
        "pooled_macro_f1": observed_macro_f1,
        "subject_mean_macro_f1_bootstrap": bootstrap_ci_over_subjects(
            fold_metrics["macro_f1"], iterations=iterations, seed=seed
        ),
        "subject_mean_balanced_accuracy_bootstrap": bootstrap_ci_over_subjects(
            fold_metrics["balanced_accuracy"], iterations=iterations, seed=seed + 1
        ),
        "per_subject_macro_f1_distribution": {
            "min": float(fold_metrics["macro_f1"].min()),
            "median": float(fold_metrics["macro_f1"].median()),
            "max": float(fold_metrics["macro_f1"].max()),
            "iqr_25": float(fold_metrics["macro_f1"].quantile(0.25)),
            "iqr_75": float(fold_metrics["macro_f1"].quantile(0.75)),
            "std": float(fold_metrics["macro_f1"].std(ddof=1)),
        },
        "permutation_test_subject_only": permutation_test(
            predictions,
            "y_pred",
            group_columns=["subject_id"],
            observed_macro_f1=observed_macro_f1,
            iterations=iterations,
            seed=seed + 2,
        ),
        "confusion_matrix_pooled": confusion_matrix(
            predictions["y_true"], predictions["y_pred"]
        ).tolist(),
    }
    if "probability_class1" in predictions.columns:
        result["roc_auc_pooled"] = float(
            roc_auc_score(predictions["y_true"], predictions["probability_class1"])
        )
    else:
        result["roc_auc_pooled"] = None
        result["roc_auc_note"] = (
            "predictions.csv predates the probability_class1 column; rerun "
            "experiments/01_loso_baselines.py to regenerate it."
        )
    if "pw_label" in predictions.columns:
        result["permutation_test_subject_and_pw"] = permutation_test(
            predictions,
            "y_pred",
            group_columns=["subject_id", "pw_label"],
            observed_macro_f1=observed_macro_f1,
            iterations=iterations,
            seed=seed + 3,
        )
    return result


def analyze_cnn_dir(directory: Path, *, iterations: int, seed: int) -> dict:
    fold_metrics = pd.read_csv(directory / "fold_metrics.csv")
    fold_dirs = sorted(path for path in directory.glob("fold_*") if path.is_dir())
    all_predictions = pd.concat(
        (pd.read_csv(fold_dir / "predictions.csv") for fold_dir in fold_dirs), ignore_index=True
    )

    result: dict = {"directory": str(directory), "kind": "cnn", "n_windows": int(len(all_predictions))}
    for prediction_column, metric_column in (
        ("base_prediction", "base_macro_f1"),
        ("t3a_prediction", "t3a_macro_f1"),
    ):
        observed_macro_f1 = _macro_f1(all_predictions["y_true"], all_predictions[prediction_column])
        result[prediction_column] = {
            "n_subjects": int(fold_metrics["held_out_subject"].nunique()),
            "pooled_macro_f1": observed_macro_f1,
            "subject_mean_macro_f1_bootstrap": bootstrap_ci_over_subjects(
                fold_metrics[metric_column], iterations=iterations, seed=seed
            ),
            "per_subject_macro_f1_distribution": {
                "min": float(fold_metrics[metric_column].min()),
                "median": float(fold_metrics[metric_column].median()),
                "max": float(fold_metrics[metric_column].max()),
                "iqr_25": float(fold_metrics[metric_column].quantile(0.25)),
                "iqr_75": float(fold_metrics[metric_column].quantile(0.75)),
                "std": float(fold_metrics[metric_column].std(ddof=1)),
            },
            "permutation_test_subject_only": permutation_test(
                all_predictions,
                prediction_column,
                group_columns=["subject_id"],
                observed_macro_f1=observed_macro_f1,
                iterations=iterations,
                seed=seed + 2,
            ),
            "confusion_matrix_pooled": confusion_matrix(
                all_predictions["y_true"], all_predictions[prediction_column]
            ).tolist(),
            "roc_auc_pooled": None,
            "roc_auc_note": "CNN predictions.csv records argmax labels only, no probabilities.",
        }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dirs", nargs="*", type=Path, default=[])
    parser.add_argument("--cnn-dirs", nargs="*", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/statistical_analysis")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for directory in args.baseline_dirs:
        print(f"Analyzing baseline dir: {directory}")
        results.append(analyze_baseline_dir(directory, iterations=args.iterations, seed=args.seed))
    for directory in args.cnn_dirs:
        print(f"Analyzing CNN dir: {directory}")
        results.append(analyze_cnn_dir(directory, iterations=args.iterations, seed=args.seed))

    output_path = args.output_dir / "statistical_analysis.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")

    summary_rows = []
    for entry in results:
        if entry["kind"] == "baseline":
            ci = entry["subject_mean_macro_f1_bootstrap"]
            perm = entry["permutation_test_subject_only"]
            summary_rows.append(
                {
                    "directory": entry["directory"],
                    "prediction": "base",
                    "macro_f1": ci["observed_mean"],
                    "ci_low": ci["ci_low_2.5pct"],
                    "ci_high": ci["ci_high_97.5pct"],
                    "roc_auc": entry["roc_auc_pooled"],
                    "permutation_p_value": perm["p_value"],
                }
            )
        else:
            for prediction_column in ("base_prediction", "t3a_prediction"):
                sub = entry[prediction_column]
                ci = sub["subject_mean_macro_f1_bootstrap"]
                perm = sub["permutation_test_subject_only"]
                summary_rows.append(
                    {
                        "directory": entry["directory"],
                        "prediction": prediction_column,
                        "macro_f1": ci["observed_mean"],
                        "ci_low": ci["ci_low_2.5pct"],
                        "ci_high": ci["ci_high_97.5pct"],
                        "roc_auc": sub["roc_auc_pooled"],
                        "permutation_p_value": perm["p_value"],
                    }
                )
    summary = pd.DataFrame(summary_rows)
    summary_path = args.output_dir / "summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Wrote {summary_path}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
