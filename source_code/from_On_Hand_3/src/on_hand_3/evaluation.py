"""Subject-independent evaluation utilities."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC


METADATA_COLUMNS = ("session_no", "pw_label")


def select_feature_columns(table: pd.DataFrame, modality: str = "both") -> list[str]:
    """Return the feature columns for a modality.

    `metadata` is a confound-control baseline (session_no, pw_label only, no
    physiological signal at all) used to check whether a modality's apparent
    predictive signal could instead be explained by session/task structure.
    """
    if modality == "metadata":
        columns = [column for column in METADATA_COLUMNS if column in table.columns]
        if not columns:
            raise ValueError(f"No metadata columns found among {METADATA_COLUMNS}")
        return columns

    prefixes = {
        "hrv": ("hrv_",),
        "acc": ("acc_",),
        "both": ("hrv_", "acc_"),
    }
    if modality not in prefixes:
        raise ValueError(f"Unknown modality: {modality}")
    columns = [column for column in table.columns if column.startswith(prefixes[modality])]
    if not columns:
        raise ValueError(f"No {modality} feature columns found")
    return columns


def residualize_against_metadata(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    metadata_train: pd.DataFrame,
    metadata_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replace each feature column with its residual after regressing on
    one-hot-encoded metadata (e.g. WAUC's `session_no`/`pw_label`), fit using
    training rows only.

    This is a confound-control step: WAUC's `mw_label` is not independent of
    its counterbalanced session structure (see `METADATA_COLUMNS` and the
    "metadata-only" modality above, which alone reaches macro-F1 rivaling the
    physiological modalities -- `paper/draft_v2.md` Section V-B-1). If a
    physiological feature's apparent predictive value survives having
    whatever session/task-structure signal it carries removed, that is
    evidence of genuine signal beyond the confound; if performance collapses
    toward chance after residualizing, the original signal was likely
    (at least partly) attributable to session structure rather than
    motion/cardiac physiology.

    NaNs in the input features are median-imputed (train-fold median) first,
    since `LinearRegression` cannot fit through missing values.
    """
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    imputed_train = pd.DataFrame(
        imputer.fit_transform(x_train), columns=x_train.columns, index=x_train.index
    )
    imputed_test = pd.DataFrame(
        imputer.transform(x_test), columns=x_test.columns, index=x_test.index
    )

    encoder = OneHotEncoder(handle_unknown="ignore")
    metadata_train_encoded = encoder.fit_transform(metadata_train)
    metadata_test_encoded = encoder.transform(metadata_test)

    residual_train = imputed_train.copy()
    residual_test = imputed_test.copy()
    for column in imputed_train.columns:
        regression = LinearRegression()
        regression.fit(metadata_train_encoded, imputed_train[column])
        residual_train[column] = imputed_train[column] - regression.predict(metadata_train_encoded)
        residual_test[column] = imputed_test[column] - regression.predict(metadata_test_encoded)
    return residual_train, residual_test


def build_estimator(model_name: str, random_seed: int = 42) -> Pipeline:
    if model_name == "svm":
        classifier = SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
            probability=True,
            random_state=random_seed,
        )
    elif model_name == "mlp":
        classifier = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            alpha=1e-4,
            batch_size=64,
            learning_rate_init=1e-3,
            max_iter=500,
            early_stopping=True,
            random_state=random_seed,
        )
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scaler", StandardScaler()),
            ("classifier", classifier),
        ]
    )


def run_loso(
    table: pd.DataFrame,
    *,
    model_name: str,
    modality: str = "both",
    random_seed: int = 42,
    residualize_metadata_columns: tuple[str, ...] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, Pipeline]:
    """Run LOSO with the standard handcrafted-feature pipeline.

    `residualize_metadata_columns`, if given (e.g. `("session_no",
    "pw_label")`), applies `residualize_against_metadata` to the feature
    columns before every fold's fit/predict, as a confound-control check --
    see that function's docstring. Passing this with `modality="metadata"`
    is nonsensical (it would residualize the confound columns against
    themselves) and raises `ValueError`.
    """
    required = {"subject_id", "label"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if table.subject_id.nunique() < 2:
        raise ValueError("LOSO requires at least two subjects")
    if residualize_metadata_columns and modality == "metadata":
        raise ValueError("residualize_metadata_columns is not meaningful for modality='metadata'")

    feature_columns = select_feature_columns(table, modality)
    x = table[feature_columns]
    y = table["label"].astype(int).to_numpy()
    groups = table["subject_id"].astype(str).to_numpy()
    metadata = table[list(residualize_metadata_columns)] if residualize_metadata_columns else None
    logo = LeaveOneGroupOut()
    folds: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []

    for fold_index, (train_index, test_index) in enumerate(logo.split(x, y, groups), start=1):
        if np.unique(y[train_index]).size < 2:
            raise ValueError(f"Training fold {fold_index} contains fewer than two classes")
        x_train, x_test = x.iloc[train_index], x.iloc[test_index]
        if metadata is not None:
            x_train, x_test = residualize_against_metadata(
                x_train, x_test, metadata.iloc[train_index], metadata.iloc[test_index]
            )
        estimator = build_estimator(model_name, random_seed + fold_index)
        estimator.fit(x_train, y[train_index])
        predicted = estimator.predict(x_test)
        probabilities = estimator.predict_proba(x_test)
        confidence = np.max(probabilities, axis=1)
        positive_class_index = list(estimator.classes_).index(1)
        probability_positive = probabilities[:, positive_class_index]
        held_out = str(groups[test_index][0])

        folds.append(
            {
                "fold": fold_index,
                "held_out_subject": held_out,
                "n_train": int(train_index.size),
                "n_test": int(test_index.size),
                "accuracy": float(accuracy_score(y[test_index], predicted)),
                "balanced_accuracy": float(balanced_accuracy_score(y[test_index], predicted)),
                "macro_f1": float(f1_score(y[test_index], predicted, average="macro", zero_division=0)),
            }
        )
        pw_labels = (
            table["pw_label"].to_numpy()[test_index] if "pw_label" in table.columns else None
        )
        for position, (row_index, truth, prediction, score, proba1) in enumerate(
            zip(test_index, y[test_index], predicted, confidence, probability_positive, strict=True)
        ):
            row = {
                "row_index": int(row_index),
                "subject_id": held_out,
                "y_true": int(truth),
                "y_pred": int(prediction),
                "confidence": float(score),
                "probability_class1": float(proba1),
            }
            if pw_labels is not None:
                row["pw_label"] = pw_labels[position].item()
            predictions.append(row)

    final_x = x
    if metadata is not None:
        final_x, _ = residualize_against_metadata(x, x, metadata, metadata)
    final_estimator = build_estimator(model_name, random_seed)
    final_estimator.fit(final_x, y)
    return pd.DataFrame(folds), pd.DataFrame(predictions), final_estimator


def save_loso_artifacts(
    output_dir: Path,
    model_name: str,
    modality: str,
    folds: pd.DataFrame,
    predictions: pd.DataFrame,
    estimator: Pipeline,
    feature_columns: list[str],
) -> None:
    destination = output_dir / f"{model_name}_{modality}"
    destination.mkdir(parents=True, exist_ok=True)
    folds.to_csv(destination / "fold_metrics.csv", index=False)
    predictions.to_csv(destination / "predictions.csv", index=False)
    joblib.dump(estimator, destination / "final_model.joblib")
    summary = {
        "model": model_name,
        "modality": modality,
        "n_folds": int(len(folds)),
        "feature_columns": feature_columns,
        "metrics_subject_mean": {
            metric: float(folds[metric].mean())
            for metric in ("accuracy", "balanced_accuracy", "macro_f1")
        },
        "metrics_subject_std": {
            metric: float(folds[metric].std(ddof=1))
            for metric in ("accuracy", "balanced_accuracy", "macro_f1")
        },
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
