"""Export the trained WAUC ACC-only MLP (sklearn Pipeline) to a plain JSON
weight file so it can be re-implemented as a hand-written forward pass in
Kotlin, with no TFLite/ONNX dependency.

Verifies numeric parity against the original sklearn Pipeline before writing
the JSON: this script is only trustworthy if the exported weights reproduce
byte-for-byte-equivalent predictions to `pipeline.predict()`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
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


def _relu(values: np.ndarray) -> np.ndarray:
    return np.maximum(values, 0.0)


def _forward(weights: dict, x: np.ndarray) -> np.ndarray:
    """Pure-numpy re-implementation of the exported pipeline, mirroring the
    Kotlin port: median-impute -> standardize -> 3-layer MLP.

    sklearn's `MLPClassifier` collapses a 2-class problem to a single output
    unit with a logistic (sigmoid) activation, not a 2-unit softmax -- the
    final layer here has shape (32, 1). Threshold at 0.5 (equivalently: raw
    logit >= 0) matches `classes_[1]`, else `classes_[0]`.
    """

    median = np.asarray(weights["imputer_median"])
    mean = np.asarray(weights["scaler_mean"])
    scale = np.asarray(weights["scaler_scale"])

    filled = np.where(np.isnan(x), median, x)
    scaled = (filled - mean) / scale

    activations = scaled
    for layer_index, (coef, intercept) in enumerate(
        zip(weights["coefs"], weights["intercepts"], strict=True)
    ):
        activations = activations @ np.asarray(coef) + np.asarray(intercept)
        if layer_index < len(weights["coefs"]) - 1:
            activations = _relu(activations)

    classes = np.asarray(weights["classes"])
    logit = activations[:, 0]
    return np.where(logit >= 0.0, classes[1], classes[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("artifacts/wauc_baselines_60s/mlp_acc/final_model.joblib"),
    )
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("data/processed/wauc_mental_workload_60s.csv"),
        help="Feature table used for the parity check.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("android_wear/app/src/main/assets/mlp_acc_weights.json"),
    )
    args = parser.parse_args()

    pipeline = joblib.load(args.model)
    imputer = pipeline.named_steps["imputer"]
    scaler = pipeline.named_steps["scaler"]
    classifier = pipeline.named_steps["classifier"]

    if classifier.out_activation_ != "logistic" or classifier.n_outputs_ != 1:
        raise SystemExit(
            f"Unexpected classifier output layer (out_activation={classifier.out_activation_!r}, "
            f"n_outputs={classifier.n_outputs_}) -- this export script assumes a binary "
            "MLPClassifier with a single sigmoid output unit; update it before deploying."
        )

    weights = {
        "feature_columns": FEATURE_COLUMNS,
        "imputer_median": imputer.statistics_.tolist(),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefs": [coef.tolist() for coef in classifier.coefs_],
        "intercepts": [intercept.tolist() for intercept in classifier.intercepts_],
        "classes": classifier.classes_.tolist(),
        "out_activation": classifier.out_activation_,
    }

    table = pd.read_csv(args.features)
    x = table[FEATURE_COLUMNS].to_numpy(dtype=np.float64)

    expected = pipeline.predict(table[FEATURE_COLUMNS])
    reimplemented = _forward(weights, x)
    if not np.array_equal(expected, reimplemented):
        mismatches = int(np.sum(expected != reimplemented))
        raise SystemExit(
            f"Parity check FAILED: {mismatches}/{len(expected)} predictions differ "
            "between the sklearn Pipeline and the re-implemented forward pass. "
            "Do not deploy this export."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(weights), encoding="utf-8")
    print(f"Parity check PASSED: {len(expected)}/{len(expected)} predictions match.")
    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
