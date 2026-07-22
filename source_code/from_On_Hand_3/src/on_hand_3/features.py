"""Feature extraction for wrist BVP-derived intervals and accelerometry."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal
from scipy.integrate import trapezoid


@dataclass(frozen=True)
class RRResult:
    """Beat-to-beat intervals and signal-quality metadata."""

    rr_ms: np.ndarray
    peak_indices: np.ndarray
    raw_rr_count: int
    valid_rr_ratio: float


def _as_finite_1d(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64).reshape(-1)
    return array[np.isfinite(array)]


def extract_rr_intervals(
    bvp: np.ndarray,
    sampling_rate_hz: float,
    *,
    minimum_bpm: float = 35.0,
    maximum_bpm: float = 200.0,
    relative_deviation: float = 0.35,
) -> RRResult:
    """Estimate pulse-to-pulse intervals from a wrist BVP window.

    This is a transparent baseline peak detector, not a clinical-grade
    artifact-correction algorithm. Quality fields must be retained downstream.
    """

    values = np.asarray(bvp, dtype=np.float64).reshape(-1)
    if sampling_rate_hz <= 0:
        raise ValueError("sampling_rate_hz must be positive")
    finite = np.isfinite(values)
    if not np.any(finite):
        return RRResult(np.array([], dtype=np.float64), np.array([], dtype=int), 0, 0.0)
    if not np.all(finite):
        positions = np.arange(values.size)
        values = np.interp(positions, positions[finite], values[finite])
    if values.size < max(16, int(2 * sampling_rate_hz)):
        return RRResult(np.array([], dtype=np.float64), np.array([], dtype=int), 0, 0.0)

    centered = values - np.median(values)
    nyquist = sampling_rate_hz / 2.0
    low_hz = 0.5
    high_hz = min(4.0, nyquist * 0.95)
    if high_hz <= low_hz:
        filtered = centered
    else:
        sos = signal.butter(3, [low_hz / nyquist, high_hz / nyquist], btype="bandpass", output="sos")
        filtered = signal.sosfiltfilt(sos, centered)

    minimum_distance = max(1, int(sampling_rate_hz * 60.0 / maximum_bpm))
    prominence = max(float(np.std(filtered)) * 0.20, np.finfo(float).eps)
    peaks, _ = signal.find_peaks(filtered, distance=minimum_distance, prominence=prominence)

    if peaks.size < 2:
        return RRResult(np.array([], dtype=np.float64), peaks.astype(int), 0, 0.0)

    raw_rr = np.diff(peaks) * 1000.0 / sampling_rate_hz
    raw_count = int(raw_rr.size)
    physiological = (raw_rr >= 60_000.0 / maximum_bpm) & (raw_rr <= 60_000.0 / minimum_bpm)

    plausible = raw_rr[physiological]
    if plausible.size:
        median_rr = float(np.median(plausible))
        physiological &= np.abs(raw_rr - median_rr) <= relative_deviation * median_rr

    cleaned = raw_rr[physiological]
    ratio = float(cleaned.size / raw_count) if raw_count else 0.0
    return RRResult(cleaned.astype(np.float64), peaks.astype(int), raw_count, ratio)


def approximate_entropy(rr_ms: np.ndarray, m: int = 2, tolerance_ratio: float = 0.2) -> float:
    """Compute approximate entropy for a short interval sequence."""

    values = _as_finite_1d(rr_ms)
    if values.size < m + 2 or np.std(values) <= 0:
        return float("nan")
    tolerance = tolerance_ratio * float(np.std(values))

    def phi(order: int) -> float:
        patterns = np.lib.stride_tricks.sliding_window_view(values, order)
        distances = np.max(np.abs(patterns[:, None, :] - patterns[None, :, :]), axis=2)
        probabilities = np.mean(distances <= tolerance, axis=1)
        return float(np.mean(np.log(np.maximum(probabilities, np.finfo(float).tiny))))

    return phi(m) - phi(m + 1)


def _frequency_features(
    rr_ms: np.ndarray,
    minimum_duration_seconds: float,
) -> dict[str, float]:
    missing = {"hrv_lf_ms2": np.nan, "hrv_hf_ms2": np.nan, "hrv_lf_hf_ratio": np.nan}
    rr = _as_finite_1d(rr_ms)
    if rr.size < 4:
        return missing

    beat_time = np.cumsum(rr) / 1000.0
    duration = float(beat_time[-1] - beat_time[0])
    if duration < minimum_duration_seconds:
        return missing

    sample_rate = 4.0
    uniform_time = np.arange(beat_time[0], beat_time[-1], 1.0 / sample_rate)
    if uniform_time.size < 16:
        return missing
    tachogram = np.interp(uniform_time, beat_time, rr)
    tachogram = signal.detrend(tachogram)
    frequencies, psd = signal.welch(
        tachogram,
        fs=sample_rate,
        nperseg=min(256, tachogram.size),
    )

    def band_power(low: float, high: float) -> float:
        mask = (frequencies >= low) & (frequencies < high)
        if np.count_nonzero(mask) < 2:
            return 0.0
        return float(trapezoid(psd[mask], frequencies[mask]))

    lf = band_power(0.04, 0.15)
    hf = band_power(0.15, 0.40)
    return {
        "hrv_lf_ms2": lf,
        "hrv_hf_ms2": hf,
        "hrv_lf_hf_ratio": lf / hf if hf > 0 else np.nan,
    }


def hrv_features(
    rr_ms: np.ndarray,
    *,
    minimum_frequency_duration_seconds: float = 120.0,
) -> dict[str, float]:
    """Extract time, nonlinear and frequency-domain HRV features."""

    rr = _as_finite_1d(rr_ms)
    names = {
        "hrv_rmssd_ms": np.nan,
        "hrv_sdnn_ms": np.nan,
        "hrv_pnn50_percent": np.nan,
        "hrv_mean_rr_ms": np.nan,
        "hrv_median_rr_ms": np.nan,
        "hrv_mean_hr_bpm": np.nan,
        "hrv_std_hr_bpm": np.nan,
        "hrv_approx_entropy": np.nan,
        "hrv_sd1_ms": np.nan,
        "hrv_sd2_ms": np.nan,
        "hrv_sd1_sd2_ratio": np.nan,
    }
    names.update(_frequency_features(rr, minimum_frequency_duration_seconds))
    if rr.size < 2:
        return names

    differences = np.diff(rr)
    sdnn = float(np.std(rr, ddof=1)) if rr.size > 1 else np.nan
    rmssd = float(np.sqrt(np.mean(differences**2)))
    sd_diff = float(np.std(differences, ddof=1)) if differences.size > 1 else np.nan
    sd1 = sd_diff / np.sqrt(2.0) if np.isfinite(sd_diff) else np.nan
    sd2_sq = 2.0 * sdnn**2 - 0.5 * sd_diff**2 if np.isfinite(sd_diff) else np.nan
    sd2 = float(np.sqrt(max(sd2_sq, 0.0))) if np.isfinite(sd2_sq) else np.nan
    heart_rate = 60_000.0 / rr

    names.update(
        {
            "hrv_rmssd_ms": rmssd,
            "hrv_sdnn_ms": sdnn,
            "hrv_pnn50_percent": float(100.0 * np.mean(np.abs(differences) > 50.0)),
            "hrv_mean_rr_ms": float(np.mean(rr)),
            "hrv_median_rr_ms": float(np.median(rr)),
            "hrv_mean_hr_bpm": float(np.mean(heart_rate)),
            "hrv_std_hr_bpm": float(np.std(heart_rate, ddof=1)),
            "hrv_approx_entropy": approximate_entropy(rr),
            "hrv_sd1_ms": sd1,
            "hrv_sd2_ms": sd2,
            "hrv_sd1_sd2_ratio": sd1 / sd2 if np.isfinite(sd1) and sd2 > 0 else np.nan,
        }
    )
    return names


def acc_features(acc_xyz: np.ndarray) -> dict[str, float]:
    """Extract lightweight motion and micro-motion descriptors."""

    acc = np.asarray(acc_xyz, dtype=np.float64)
    if acc.ndim != 2 or acc.shape[1] != 3:
        raise ValueError("acc_xyz must have shape (samples, 3)")
    if acc.shape[0] < 2:
        return {
            "acc_mean_magnitude": np.nan,
            "acc_std_magnitude": np.nan,
            "acc_dynamic_energy": np.nan,
            "acc_zero_crossing_rate": np.nan,
            "acc_std_x": np.nan,
            "acc_std_y": np.nan,
            "acc_std_z": np.nan,
        }

    magnitude = np.linalg.norm(acc, axis=1)
    dynamic = acc - np.mean(acc, axis=0, keepdims=True)
    centered_magnitude = magnitude - np.mean(magnitude)
    signs = np.signbit(centered_magnitude)
    zcr = float(np.mean(signs[1:] != signs[:-1]))
    axis_std = np.std(acc, axis=0, ddof=1)
    return {
        "acc_mean_magnitude": float(np.mean(magnitude)),
        "acc_std_magnitude": float(np.std(magnitude, ddof=1)),
        "acc_dynamic_energy": float(np.mean(np.sum(dynamic**2, axis=1))),
        "acc_zero_crossing_rate": zcr,
        "acc_std_x": float(axis_std[0]),
        "acc_std_y": float(axis_std[1]),
        "acc_std_z": float(axis_std[2]),
    }


def extract_window_features(
    bvp: np.ndarray,
    acc_xyz: np.ndarray,
    *,
    bvp_sampling_rate_hz: float = 64.0,
    minimum_frequency_duration_seconds: float = 120.0,
) -> dict[str, float]:
    """Build one flat feature record for a synchronized BVP/ACC window."""

    rr = extract_rr_intervals(bvp, bvp_sampling_rate_hz)
    result = hrv_features(
        rr.rr_ms,
        minimum_frequency_duration_seconds=minimum_frequency_duration_seconds,
    )
    result.update(acc_features(acc_xyz))
    result.update(
        {
            "quality_peak_count": int(rr.peak_indices.size),
            "quality_rr_count": int(rr.rr_ms.size),
            "quality_valid_rr_ratio": rr.valid_rr_ratio,
        }
    )
    return result
