"""Public data types for the baseline solvers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Configuration shared by the D1Q3 and D2Q9 baseline solvers."""

    grid_shape: tuple[int, ...]
    steps: int
    tau: float
    initial_condition: str = "sinusoidal"
    boundary_mode: str = "periodic"
    sample_interval: int | None = 10
    amplitude: float = 0.05
    base_density: float = 1.0
    advection_velocity: float = 0.0


@dataclass(frozen=True, slots=True)
class SimulationHistory:
    """Sampled macroscopic fields from a simulation."""

    steps: tuple[int, ...]
    density: tuple[np.ndarray, ...]
    velocity: tuple[np.ndarray, ...]


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Final fields, sampled history, and metrics from a baseline run."""

    model: str
    config: SimulationConfig
    density: np.ndarray
    velocity: np.ndarray
    distributions: np.ndarray
    history: SimulationHistory
    metrics: Mapping[str, float]
