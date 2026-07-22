"""Time-based synchronization and window helpers."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Window:
    index: int
    start_seconds: float
    end_seconds: float


def iter_windows(duration_seconds: float, window_seconds: float, step_seconds: float) -> Iterator[Window]:
    if duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative")
    if window_seconds <= 0 or step_seconds <= 0:
        raise ValueError("window_seconds and step_seconds must be positive")

    index = 0
    start = 0.0
    tolerance = 1e-9
    while start + window_seconds <= duration_seconds + tolerance:
        yield Window(index, start, start + window_seconds)
        index += 1
        start += step_seconds


def time_slice(values: np.ndarray, sampling_rate_hz: float, start_seconds: float, end_seconds: float) -> np.ndarray:
    if sampling_rate_hz <= 0:
        raise ValueError("sampling_rate_hz must be positive")
    start = max(0, int(round(start_seconds * sampling_rate_hz)))
    end = min(len(values), int(round(end_seconds * sampling_rate_hz)))
    return values[start:end]


def dominant_label(labels: np.ndarray, allowed: set[int]) -> tuple[int | None, float]:
    flat = np.asarray(labels).reshape(-1)
    if flat.size == 0:
        return None, 0.0
    values, counts = np.unique(flat, return_counts=True)
    best = int(np.argmax(counts))
    label = int(values[best])
    purity = float(counts[best] / flat.size)
    if label not in allowed:
        return None, purity
    return label, purity
