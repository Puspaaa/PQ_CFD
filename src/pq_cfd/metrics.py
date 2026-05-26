"""Shared numerical metrics."""

from __future__ import annotations

import numpy as np


def relative_l2_error(actual: np.ndarray, expected: np.ndarray) -> float:
    """Return ||actual - expected||_2 / ||expected||_2."""

    actual_arr = np.asarray(actual, dtype=float)
    expected_arr = np.asarray(expected, dtype=float)
    denominator = float(np.linalg.norm(expected_arr.ravel()))
    numerator = float(np.linalg.norm((actual_arr - expected_arr).ravel()))
    if denominator == 0.0:
        return numerator
    return numerator / denominator


def mass_metrics(initial_mass: float, final_mass: float) -> dict[str, float]:
    """Return absolute and relative mass drift metrics."""

    drift = float(final_mass - initial_mass)
    scale = abs(float(initial_mass))
    relative = abs(drift) / scale if scale > 0.0 else abs(drift)
    return {
        "mass_initial": float(initial_mass),
        "mass_final": float(final_mass),
        "mass_drift": drift,
        "mass_drift_absolute": abs(drift),
        "mass_drift_relative": relative,
    }
