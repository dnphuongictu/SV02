"""LOSO training loop for the raw-signal CNN1D and sequential T3A evaluation."""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import LeaveOneGroupOut

from .models import build_late_fusion_cnn1d, build_raw_cnn1d
from .t3a import T3A


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def channel_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=(0, 2), keepdims=True)
    std = x.std(axis=(0, 2), keepdims=True)
    return mean.astype(np.float32), np.maximum(std, 1e-6).astype(np.float32)


def _t3a_stream_predictions(
    embeddings: np.ndarray,
    classifier_weights: np.ndarray,
    supports_per_class: int,
    stream_seed: int,
) -> np.ndarray:
    """Run T3A once over `embeddings` in a given stream order and return predictions realigned to the original index order.

    `stream_seed == 0` keeps the natural (dataset) stream order so existing
    single-seed results stay reproducible; any other seed shuffles the order
    to check that T3A's sequential adaptation is not an artifact of one
    particular stream ordering.
    """
    order = (
        np.arange(len(embeddings))
        if stream_seed == 0
        else np.random.RandomState(stream_seed).permutation(len(embeddings))
    )
    adapter = T3A(classifier_weights, supports_per_class=supports_per_class)
    ordered_predictions, _ = adapter.predict(embeddings[order], update=True)
    predictions = np.empty_like(ordered_predictions)
    predictions[order] = ordered_predictions
    return predictions


def fit_cnn1d(
    train_x: np.ndarray,
    train_y: np.ndarray,
    validation_x: np.ndarray,
    validation_y: np.ndarray,
    *,
    class_count: int,
    kernel_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    patience: int,
    device: "torch.device",
    progress_prefix: str | None = None,
    late_fusion_ppg_channels: int | None = None,
):
    """Train one RawCNN1D (or LateFusionCNN1D) to convergence on a fixed train/validation split.

    Shared by the outer LOSO loop and standalone (non-LOSO) training such as
    the TFLite export rehearsal, so the optimization loop only lives once.
    When `progress_prefix` is set, prints one line per epoch so a long CPU
    run has visible heartbeat instead of going silent for minutes at a time.
    When `late_fusion_ppg_channels` is set, the first N input channels are
    treated as PPG and the rest as ACC, each routed through its own Conv1D
    branch (see `build_late_fusion_cnn1d`) instead of one shared early-fusion
    stack.
    """
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(train_x), torch.from_numpy(train_y)),
        batch_size=batch_size,
        shuffle=True,
    )
    validation_loader = DataLoader(
        TensorDataset(torch.from_numpy(validation_x), torch.from_numpy(validation_y)),
        batch_size=batch_size,
        shuffle=False,
    )

    if late_fusion_ppg_channels is None:
        model = build_raw_cnn1d(train_x.shape[1], class_count, kernel_size=kernel_size).to(device)
    else:
        model = build_late_fusion_cnn1d(
            late_fusion_ppg_channels,
            train_x.shape[1] - late_fusion_ppg_channels,
            class_count,
            kernel_size=kernel_size,
        ).to(device)
    counts = np.bincount(train_y, minlength=class_count)
    class_weights = len(train_y) / np.maximum(counts, 1) / class_count
    loss_function = torch.nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32, device=device)
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs))
    best_state = None
    best_validation_f1 = -np.inf
    stale_epochs = 0

    for epoch in range(1, epochs + 1):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(batch_x), batch_y)
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        validation_predictions = []
        with torch.no_grad():
            for batch_x, _ in validation_loader:
                validation_predictions.extend(
                    model(batch_x.to(device)).argmax(dim=1).cpu().numpy()
                )
        validation_f1 = f1_score(
            validation_y,
            np.asarray(validation_predictions),
            average="macro",
            zero_division=0,
        )
        improved = validation_f1 > best_validation_f1 + 1e-6
        if improved:
            best_validation_f1 = float(validation_f1)
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale_epochs = 0
        else:
            stale_epochs += 1

        if progress_prefix is not None:
            marker = "*" if improved else " "
            print(
                f"{progress_prefix} epoch {epoch}/{epochs}{marker} "
                f"val_macro_f1={validation_f1:.4f} best={best_validation_f1:.4f} "
                f"stale={stale_epochs}/{patience}",
                flush=True,
            )

        if stale_epochs >= patience:
            break

    if best_state is None:
        raise RuntimeError("training did not produce a checkpoint")
    model.load_state_dict(best_state)
    model.eval()
    return model, best_validation_f1


def _write_aggregate(
    records: list[dict[str, object]],
    multiseed_records: list[dict[str, object]],
    output_dir: Path,
    *,
    device: object,
    learning_rate: float,
    kernel_size: int,
    batch_size: int,
    t3a_stream_seeds: tuple[int, ...],
    supports_sweep_records: list[dict[str, object]] | None = None,
) -> pd.DataFrame:
    """(Re)write fold_metrics.csv/t3a_multiseed.csv/summary.json from records so far.

    Called after every fold (not just at the end) so progress is inspectable
    on disk, and so a killed/resumed run never loses already-completed folds.
    """
    results = pd.DataFrame(records).sort_values("fold").reset_index(drop=True)
    results.to_csv(output_dir / "fold_metrics.csv", index=False)
    summary = {
        "device": str(device),
        "folds": len(results),
        "learning_rate": learning_rate,
        "kernel_size": kernel_size,
        "batch_size": batch_size,
        "validation_macro_f1_subject_mean": float(results.best_validation_macro_f1.mean()),
        "base_macro_f1_subject_mean": float(results.base_macro_f1.mean()),
        "t3a_macro_f1_subject_mean": float(results.t3a_macro_f1.mean()),
        "t3a_delta_macro_f1": float((results.t3a_macro_f1 - results.base_macro_f1).mean()),
    }

    if len(t3a_stream_seeds) > 1 and multiseed_records:
        multiseed_results = pd.DataFrame(multiseed_records)
        multiseed_results.to_csv(output_dir / "t3a_multiseed.csv", index=False)
        per_seed_delta = (
            multiseed_results.assign(
                delta_macro_f1=multiseed_results.t3a_macro_f1 - multiseed_results.base_macro_f1
            )
            .groupby("t3a_stream_seed")
            .delta_macro_f1.mean()
        )
        summary["t3a_stream_seeds"] = list(t3a_stream_seeds)
        summary["t3a_delta_macro_f1_mean_over_seeds"] = float(per_seed_delta.mean())
        summary["t3a_delta_macro_f1_std_over_seeds"] = float(per_seed_delta.std(ddof=0))

    if supports_sweep_records:
        sweep_results = pd.DataFrame(supports_sweep_records)
        sweep_results.to_csv(output_dir / "t3a_supports_sweep.csv", index=False)
        per_supports_delta = (
            sweep_results.assign(
                delta_macro_f1=sweep_results.t3a_macro_f1 - sweep_results.base_macro_f1
            )
            .groupby("supports_per_class")
            .delta_macro_f1.agg(["mean", "std"])
        )
        summary["t3a_supports_sweep"] = {
            int(supports): {"delta_mean": float(row["mean"]), "delta_std": float(row["std"])}
            for supports, row in per_supports_delta.iterrows()
        }

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return results


def train_cnn_loso(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    output_dir: Path,
    *,
    epochs: int = 50,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    patience: int = 8,
    supports_per_class: int = 10,
    random_seed: int = 42,
    save_fold_models: bool = False,
    t3a_stream_seeds: tuple[int, ...] = (0,),
    kernel_size: int = 5,
    resume: bool = True,
    late_fusion_ppg_channels: int | None = None,
    t3a_supports_sweep: tuple[int, ...] = (),
) -> pd.DataFrame:
    import torch

    x = np.asarray(x, dtype=np.float32)
    y = np.asarray(y, dtype=np.int64)
    groups = np.asarray(groups).astype(str)
    if x.ndim != 3:
        raise ValueError("X must have shape (windows, channels, samples)")
    if len(x) != len(y) or len(y) != len(groups):
        raise ValueError("X, y and groups must have matching first dimension")
    if late_fusion_ppg_channels is not None and not (0 < late_fusion_ppg_channels < x.shape[1]):
        raise ValueError("late_fusion_ppg_channels must leave at least one channel for each branch")
    subjects = np.unique(groups)
    if subjects.size < 3:
        raise ValueError("CNN LOSO requires at least three subjects (train, validation, test)")

    if not t3a_stream_seeds:
        raise ValueError("t3a_stream_seeds must contain at least one seed")

    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    class_count = int(np.max(y)) + 1
    total_folds = subjects.size
    records: list[dict[str, object]] = []
    multiseed_records: list[dict[str, object]] = []
    supports_sweep_records: list[dict[str, object]] = []

    print(
        f"Starting CNN1D LOSO: {total_folds} folds, {len(x):,} windows, "
        f"{class_count} classes, device={device}, epochs<={epochs}, patience={patience}",
        flush=True,
    )

    for fold, (development_index, test_index) in enumerate(
        LeaveOneGroupOut().split(x, y, groups), start=1
    ):
        held_out_subject = str(groups[test_index][0])
        fold_dir = output_dir / f"fold_{fold:02d}_{held_out_subject}"
        checkpoint_path = fold_dir / "checkpoint.json"

        if resume and checkpoint_path.exists():
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            records.append(checkpoint["record"])
            multiseed_records.extend(checkpoint["multiseed"])
            supports_sweep_records.extend(checkpoint.get("supports_sweep", []))
            print(
                f"[{fold}/{total_folds}] {held_out_subject}: resumed from checkpoint "
                f"(base_macro_f1={checkpoint['record']['base_macro_f1']:.4f})"
            )
            results = _write_aggregate(
                records,
                multiseed_records,
                output_dir,
                device=device,
                learning_rate=learning_rate,
                kernel_size=kernel_size,
                batch_size=batch_size,
                t3a_stream_seeds=t3a_stream_seeds,
                supports_sweep_records=supports_sweep_records,
            )
            continue

        seed = random_seed + fold
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        development_subjects = sorted(np.unique(groups[development_index]))
        validation_subject = development_subjects[(fold - 1) % len(development_subjects)]
        validation_mask = groups[development_index] == validation_subject
        validation_index = development_index[validation_mask]
        train_index = development_index[~validation_mask]
        if np.unique(y[train_index]).size != class_count:
            raise ValueError(f"Fold {fold}: training partition is missing a class")

        mean, std = channel_stats(x[train_index])

        def normalized(indices: np.ndarray) -> np.ndarray:
            return (x[indices] - mean) / std

        model, best_validation_f1 = fit_cnn1d(
            normalized(train_index),
            y[train_index],
            normalized(validation_index),
            y[validation_index],
            class_count=class_count,
            kernel_size=kernel_size,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            patience=patience,
            device=device,
            progress_prefix=f"[{fold}/{total_folds}] {held_out_subject}",
            late_fusion_ppg_channels=late_fusion_ppg_channels,
        )
        best_state = model.state_dict()

        test_tensor = torch.from_numpy(normalized(test_index))
        base_predictions, embedding_batches = [], []
        with torch.no_grad():
            for start in range(0, len(test_tensor), batch_size):
                batch = test_tensor[start : start + batch_size].to(device)
                base_predictions.extend(model(batch).argmax(dim=1).cpu().numpy())
                embedding_batches.append(model.embeddings(batch).cpu().numpy())
        embeddings = np.concatenate(embedding_batches)
        classifier_weights = model.classifier[3].weight.detach().cpu().numpy()
        base_scores = compute_metrics(y[test_index], np.asarray(base_predictions))

        seed_scores: dict[int, dict[str, float]] = {}
        fold_multiseed: list[dict[str, object]] = []
        for stream_seed in t3a_stream_seeds:
            t3a_predictions = _t3a_stream_predictions(
                embeddings, classifier_weights, supports_per_class, stream_seed
            )
            scores = compute_metrics(y[test_index], t3a_predictions)
            seed_scores[stream_seed] = scores
            fold_multiseed.append(
                {
                    "fold": fold,
                    "held_out_subject": held_out_subject,
                    "t3a_stream_seed": stream_seed,
                    "base_macro_f1": base_scores["macro_f1"],
                    **{f"t3a_{name}": value for name, value in scores.items()},
                }
            )
        multiseed_records.extend(fold_multiseed)

        fold_supports_sweep: list[dict[str, object]] = []
        for supports_value in t3a_supports_sweep:
            sweep_predictions = _t3a_stream_predictions(
                embeddings, classifier_weights, supports_value, t3a_stream_seeds[0]
            )
            sweep_scores = compute_metrics(y[test_index], sweep_predictions)
            fold_supports_sweep.append(
                {
                    "fold": fold,
                    "held_out_subject": held_out_subject,
                    "supports_per_class": supports_value,
                    "base_macro_f1": base_scores["macro_f1"],
                    **{f"t3a_{name}": value for name, value in sweep_scores.items()},
                }
            )
        supports_sweep_records.extend(fold_supports_sweep)

        t3a_scores = seed_scores[t3a_stream_seeds[0]]
        record: dict[str, object] = {
            "fold": fold,
            "held_out_subject": held_out_subject,
            "validation_subject": validation_subject,
            "n_train": int(len(train_index)),
            "n_validation": int(len(validation_index)),
            "n_test": int(len(test_index)),
            "best_validation_macro_f1": best_validation_f1,
        }
        record.update({f"base_{name}": value for name, value in base_scores.items()})
        record.update({f"t3a_{name}": value for name, value in t3a_scores.items()})
        records.append(record)

        fold_dir.mkdir(parents=True, exist_ok=True)
        np.savez(
            fold_dir / "normalization.npz",
            channel_mean=mean,
            channel_std=std,
        )
        pd.DataFrame(
            {
                "subject_id": groups[test_index],
                "window_index_in_dataset": test_index,
                "y_true": y[test_index],
                "base_prediction": base_predictions,
                "t3a_prediction": t3a_predictions,
            }
        ).to_csv(fold_dir / "predictions.csv", index=False)
        if save_fold_models:
            torch.save(best_state, fold_dir / "model_state.pt")
        checkpoint_path.write_text(
            json.dumps(
                {
                    "record": record,
                    "multiseed": fold_multiseed,
                    "supports_sweep": fold_supports_sweep,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        print(
            f"[{fold}/{total_folds}] {held_out_subject}: "
            f"base_macro_f1={base_scores['macro_f1']:.4f}, "
            f"t3a_macro_f1={t3a_scores['macro_f1']:.4f}, "
            f"best_validation_macro_f1={best_validation_f1:.4f}"
        )

        results = _write_aggregate(
            records,
            multiseed_records,
            output_dir,
            device=device,
            learning_rate=learning_rate,
            kernel_size=kernel_size,
            batch_size=batch_size,
            t3a_stream_seeds=t3a_stream_seeds,
            supports_sweep_records=supports_sweep_records,
        )

    return results
