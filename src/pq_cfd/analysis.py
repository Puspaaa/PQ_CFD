"""Classical benchmark sweeps for the baseline LBM solvers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from pq_cfd.d1q3 import run_d1q3
from pq_cfd.d2q9 import run_d2q9
from pq_cfd.types import SimulationConfig, SimulationResult

D1Q3_DEFAULT_GRIDS = (32, 64, 128, 256)
D1Q3_DEFAULT_TAUS = (0.55, 0.6, 0.8, 1.0)
D2Q9_DEFAULT_GRIDS = ((16, 16), (32, 32), (64, 64))
D2Q9_DEFAULT_TAUS = (0.6, 0.8, 1.0)

SWEEP_CSV_COLUMNS = (
    "model",
    "grid_shape",
    "grid_points",
    "steps",
    "tau",
    "amplitude",
    "initial_condition",
    "boundary_mode",
    "relative_error",
    "relative_error_metric",
    "mass_drift_absolute",
    "mass_drift_relative",
    "runtime_seconds",
    "diffusivity",
    "viscosity",
)


@dataclass(frozen=True, slots=True)
class SweepCase:
    """One benchmark case to run through a baseline solver."""

    model: str
    grid_shape: tuple[int, ...]
    steps: int
    tau: float
    amplitude: float
    initial_condition: str
    boundary_mode: str = "periodic"
    sample_interval: int | None = None

    def to_config(self) -> SimulationConfig:
        """Convert the sweep case into the solver's public config type."""

        return SimulationConfig(
            grid_shape=self.grid_shape,
            steps=self.steps,
            tau=self.tau,
            initial_condition=self.initial_condition,
            boundary_mode=self.boundary_mode,
            sample_interval=self.sample_interval,
            amplitude=self.amplitude,
        )


@dataclass(frozen=True, slots=True)
class SweepRecord:
    """Stable scalar summary of one completed benchmark case."""

    model: str
    grid_shape: tuple[int, ...]
    grid_points: int
    steps: int
    tau: float
    amplitude: float
    initial_condition: str
    boundary_mode: str
    relative_error: float
    relative_error_metric: str
    mass_drift_absolute: float
    mass_drift_relative: float
    runtime_seconds: float
    diffusivity: float | None
    viscosity: float | None

    @classmethod
    def from_result(cls, case: SweepCase, result: SimulationResult) -> "SweepRecord":
        """Build a record from a solver result."""

        relative_error_metric = _relative_error_metric(result)
        return cls(
            model=result.model,
            grid_shape=tuple(case.grid_shape),
            grid_points=int(np.prod(case.grid_shape)),
            steps=case.steps,
            tau=case.tau,
            amplitude=case.amplitude,
            initial_condition=case.initial_condition,
            boundary_mode=case.boundary_mode,
            relative_error=float(result.metrics[relative_error_metric]),
            relative_error_metric=relative_error_metric,
            mass_drift_absolute=float(result.metrics["mass_drift_absolute"]),
            mass_drift_relative=float(result.metrics["mass_drift_relative"]),
            runtime_seconds=float(result.metrics["runtime_seconds"]),
            diffusivity=_optional_float(result.metrics.get("diffusivity")),
            viscosity=_optional_float(result.metrics.get("viscosity")),
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a CSV-friendly row with stable column names."""

        return {
            "model": self.model,
            "grid_shape": format_grid_shape(self.grid_shape),
            "grid_points": self.grid_points,
            "steps": self.steps,
            "tau": self.tau,
            "amplitude": self.amplitude,
            "initial_condition": self.initial_condition,
            "boundary_mode": self.boundary_mode,
            "relative_error": self.relative_error,
            "relative_error_metric": self.relative_error_metric,
            "mass_drift_absolute": self.mass_drift_absolute,
            "mass_drift_relative": self.mass_drift_relative,
            "runtime_seconds": self.runtime_seconds,
            "diffusivity": "" if self.diffusivity is None else self.diffusivity,
            "viscosity": "" if self.viscosity is None else self.viscosity,
        }


def run_sweep(cases: list[SweepCase] | tuple[SweepCase, ...]) -> list[SweepRecord]:
    """Run benchmark cases and return scalar records."""

    records: list[SweepRecord] = []
    for case in cases:
        model = normalize_model(case.model)
        config = case.to_config()
        if model == "D1Q3":
            result = run_d1q3(config)
        elif model == "D2Q9":
            result = run_d2q9(config)
        else:
            raise ValueError(f"Unsupported sweep model: {case.model!r}")
        records.append(SweepRecord.from_result(case, result))
    return records


def write_sweep_csv(records: list[SweepRecord], path: str | Path) -> Path:
    """Write sweep records to CSV and return the output path."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SWEEP_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return output_path


def default_d1q3_sweep_cases(
    *,
    grids: tuple[int, ...] = D1Q3_DEFAULT_GRIDS,
    tau_values: tuple[float, ...] = D1Q3_DEFAULT_TAUS,
    amplitude: float = 0.02,
) -> list[SweepCase]:
    """Return the default D1Q3 analysis cases."""

    return [
        SweepCase(
            model="D1Q3",
            grid_shape=(nx,),
            steps=nx,
            tau=tau,
            amplitude=amplitude,
            initial_condition="sinusoidal",
        )
        for nx in grids
        for tau in tau_values
    ]


def default_d2q9_sweep_cases(
    *,
    grids: tuple[tuple[int, int], ...] = D2Q9_DEFAULT_GRIDS,
    tau_values: tuple[float, ...] = D2Q9_DEFAULT_TAUS,
    amplitude: float = 0.02,
) -> list[SweepCase]:
    """Return the default D2Q9 analysis cases."""

    return [
        SweepCase(
            model="D2Q9",
            grid_shape=grid,
            steps=grid[0],
            tau=tau,
            amplitude=amplitude,
            initial_condition="taylor_green",
        )
        for grid in grids
        for tau in tau_values
    ]


def default_sweep_cases(
    *,
    d1_grids: tuple[int, ...] = D1Q3_DEFAULT_GRIDS,
    d2_grids: tuple[tuple[int, int], ...] = D2Q9_DEFAULT_GRIDS,
    d1_tau_values: tuple[float, ...] = D1Q3_DEFAULT_TAUS,
    d2_tau_values: tuple[float, ...] = D2Q9_DEFAULT_TAUS,
    amplitude: float = 0.02,
) -> list[SweepCase]:
    """Return the combined default D1Q3 and D2Q9 analysis cases."""

    return [
        *default_d1q3_sweep_cases(
            grids=d1_grids,
            tau_values=d1_tau_values,
            amplitude=amplitude,
        ),
        *default_d2q9_sweep_cases(
            grids=d2_grids,
            tau_values=d2_tau_values,
            amplitude=amplitude,
        ),
    ]


def format_grid_shape(grid_shape: tuple[int, ...]) -> str:
    """Format a grid shape for plot labels and CSV output."""

    return "x".join(str(size) for size in grid_shape)


def normalize_model(model: str) -> str:
    """Return the canonical model name used by the sweep runner."""

    normalized = model.upper()
    if normalized not in {"D1Q3", "D2Q9"}:
        raise ValueError(f"Unsupported sweep model: {model!r}")
    return normalized


def _relative_error_metric(result: SimulationResult) -> str:
    if result.model == "D1Q3":
        return "relative_l2_error_density"
    if result.model == "D2Q9":
        return "relative_l2_error_velocity"
    raise ValueError(f"Unsupported result model: {result.model!r}")


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)
