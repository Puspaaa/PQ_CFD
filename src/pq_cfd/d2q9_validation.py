"""D2Q9 Taylor-Green validation diagnostics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any

import numpy as np

from pq_cfd.analysis import format_grid_shape
from pq_cfd.d2q9 import CS2, analytic_taylor_green_velocity, run_d2q9
from pq_cfd.metrics import relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationResult

D2Q9_VALIDATION_GRIDS = ((16, 16), (32, 32), (64, 64), (128, 128))
D2Q9_VALIDATION_TAUS = (0.6, 0.8, 1.0)
DEFAULT_DECAY_EXPONENT = 0.1
DEFAULT_DIVERGENCE_RMS_MAX = 1e-2
DEFAULT_DENSITY_DEVIATION_MAX = 5e-2

D2Q9_VALIDATION_CSV_COLUMNS = (
    "model",
    "grid_shape",
    "grid_points",
    "steps",
    "tau",
    "amplitude",
    "initial_condition",
    "grid_spacing_x",
    "grid_spacing_y",
    "target_decay_exponent",
    "actual_decay_exponent",
    "velocity_relative_l2_error",
    "vorticity_relative_l2_error",
    "kinetic_energy",
    "expected_kinetic_energy",
    "kinetic_energy_relative_error",
    "density_weighted_kinetic_energy",
    "incompressible_kinetic_energy",
    "expected_incompressible_kinetic_energy",
    "incompressible_kinetic_energy_relative_error",
    "divergence_l2_norm",
    "divergence_rms",
    "max_mach",
    "min_density",
    "max_density_deviation",
    "mass_drift_absolute",
    "mass_drift_relative",
    "runtime_seconds",
    "stable",
)


@dataclass(frozen=True, slots=True)
class D2Q9ValidationCase:
    """A Taylor-Green validation case at controlled analytic decay."""

    grid_shape: tuple[int, int]
    tau: float
    steps: int
    amplitude: float
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT
    initial_condition: str = "taylor_green"

    def to_config(self) -> SimulationConfig:
        """Convert the validation case into a solver config."""

        return SimulationConfig(
            grid_shape=self.grid_shape,
            steps=self.steps,
            tau=self.tau,
            initial_condition=self.initial_condition,
            sample_interval=None,
            amplitude=self.amplitude,
        )


@dataclass(frozen=True, slots=True)
class D2Q9ValidationRecord:
    """Stable scalar diagnostics from one D2Q9 validation run."""

    model: str
    grid_shape: tuple[int, int]
    grid_points: int
    steps: int
    tau: float
    amplitude: float
    initial_condition: str
    grid_spacing_x: float
    grid_spacing_y: float
    target_decay_exponent: float
    actual_decay_exponent: float
    velocity_relative_l2_error: float
    vorticity_relative_l2_error: float
    kinetic_energy: float
    expected_kinetic_energy: float
    kinetic_energy_relative_error: float
    density_weighted_kinetic_energy: float
    incompressible_kinetic_energy: float
    expected_incompressible_kinetic_energy: float
    incompressible_kinetic_energy_relative_error: float
    divergence_l2_norm: float
    divergence_rms: float
    max_mach: float
    min_density: float
    max_density_deviation: float
    mass_drift_absolute: float
    mass_drift_relative: float
    runtime_seconds: float
    stable: bool

    @classmethod
    def from_result(
        cls,
        case: D2Q9ValidationCase,
        result: SimulationResult,
    ) -> "D2Q9ValidationRecord":
        """Build validation diagnostics from a completed solver result."""

        nx, ny = case.grid_shape
        spacing = grid_spacings(case.grid_shape)
        expected_velocity = analytic_taylor_green_velocity(
            result.config,
            nx,
            ny,
            case.steps,
        )
        vorticity = periodic_vorticity(result.velocity, spacing=spacing)
        expected_vorticity = periodic_vorticity(expected_velocity, spacing=spacing)
        divergence = periodic_divergence(result.velocity, spacing=spacing)

        density_weighted_kinetic_energy = mean_kinetic_energy(
            result.density,
            result.velocity,
        )
        base_density = np.full((nx, ny), result.config.base_density, dtype=float)
        incompressible_kinetic_energy = mean_kinetic_energy(
            base_density,
            result.velocity,
        )
        expected_incompressible_kinetic_energy = mean_kinetic_energy(
            base_density,
            expected_velocity,
        )
        incompressible_kinetic_energy_relative_error = _relative_scalar_error(
            incompressible_kinetic_energy,
            expected_incompressible_kinetic_energy,
        )
        kinetic_energy_relative_error = _relative_scalar_error(
            density_weighted_kinetic_energy,
            expected_incompressible_kinetic_energy,
        )
        divergence_rms = normalized_l2_norm(divergence)
        max_mach = max_mach_number(result.velocity)
        min_density = float(np.min(result.density))
        max_density_deviation = float(
            np.max(np.abs(result.density - result.config.base_density))
        )
        velocity_error = relative_l2_error(result.velocity, expected_velocity)
        vorticity_error = relative_l2_error(vorticity, expected_vorticity)
        actual_decay_exponent = taylor_green_decay_exponent(
            case.grid_shape,
            case.tau,
            case.steps,
        )
        stable = bool(
            np.isfinite(velocity_error)
            and np.isfinite(vorticity_error)
            and np.isfinite(kinetic_energy_relative_error)
            and np.isfinite(incompressible_kinetic_energy_relative_error)
            and np.isfinite(max_mach)
            and max_mach < 0.1
            and divergence_rms < DEFAULT_DIVERGENCE_RMS_MAX
            and min_density > 0.0
            and max_density_deviation < DEFAULT_DENSITY_DEVIATION_MAX
            and result.metrics["mass_drift_relative"] < 1e-10
        )

        return cls(
            model=result.model,
            grid_shape=case.grid_shape,
            grid_points=int(np.prod(case.grid_shape)),
            steps=case.steps,
            tau=case.tau,
            amplitude=case.amplitude,
            initial_condition=case.initial_condition,
            grid_spacing_x=spacing[0],
            grid_spacing_y=spacing[1],
            target_decay_exponent=case.target_decay_exponent,
            actual_decay_exponent=actual_decay_exponent,
            velocity_relative_l2_error=velocity_error,
            vorticity_relative_l2_error=vorticity_error,
            kinetic_energy=density_weighted_kinetic_energy,
            expected_kinetic_energy=expected_incompressible_kinetic_energy,
            kinetic_energy_relative_error=kinetic_energy_relative_error,
            density_weighted_kinetic_energy=density_weighted_kinetic_energy,
            incompressible_kinetic_energy=incompressible_kinetic_energy,
            expected_incompressible_kinetic_energy=(
                expected_incompressible_kinetic_energy
            ),
            incompressible_kinetic_energy_relative_error=(
                incompressible_kinetic_energy_relative_error
            ),
            divergence_l2_norm=float(np.linalg.norm(divergence.ravel())),
            divergence_rms=divergence_rms,
            max_mach=max_mach,
            min_density=min_density,
            max_density_deviation=max_density_deviation,
            mass_drift_absolute=float(result.metrics["mass_drift_absolute"]),
            mass_drift_relative=float(result.metrics["mass_drift_relative"]),
            runtime_seconds=float(result.metrics["runtime_seconds"]),
            stable=stable,
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
            "grid_spacing_x": self.grid_spacing_x,
            "grid_spacing_y": self.grid_spacing_y,
            "target_decay_exponent": self.target_decay_exponent,
            "actual_decay_exponent": self.actual_decay_exponent,
            "velocity_relative_l2_error": self.velocity_relative_l2_error,
            "vorticity_relative_l2_error": self.vorticity_relative_l2_error,
            "kinetic_energy": self.kinetic_energy,
            "expected_kinetic_energy": self.expected_kinetic_energy,
            "kinetic_energy_relative_error": self.kinetic_energy_relative_error,
            "density_weighted_kinetic_energy": self.density_weighted_kinetic_energy,
            "incompressible_kinetic_energy": self.incompressible_kinetic_energy,
            "expected_incompressible_kinetic_energy": (
                self.expected_incompressible_kinetic_energy
            ),
            "incompressible_kinetic_energy_relative_error": (
                self.incompressible_kinetic_energy_relative_error
            ),
            "divergence_l2_norm": self.divergence_l2_norm,
            "divergence_rms": self.divergence_rms,
            "max_mach": self.max_mach,
            "min_density": self.min_density,
            "max_density_deviation": self.max_density_deviation,
            "mass_drift_absolute": self.mass_drift_absolute,
            "mass_drift_relative": self.mass_drift_relative,
            "runtime_seconds": self.runtime_seconds,
            "stable": self.stable,
        }


def d2q9_validation_cases(
    *,
    grids: tuple[tuple[int, int], ...] = D2Q9_VALIDATION_GRIDS,
    tau_values: tuple[float, ...] = D2Q9_VALIDATION_TAUS,
    amplitude: float = 0.02,
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT,
) -> list[D2Q9ValidationCase]:
    """Generate Taylor-Green validation cases at fixed analytic decay."""

    return [
        D2Q9ValidationCase(
            grid_shape=grid,
            tau=tau,
            steps=steps_for_decay_exponent(
                grid,
                tau,
                target_decay_exponent=target_decay_exponent,
            ),
            amplitude=amplitude,
            target_decay_exponent=target_decay_exponent,
        )
        for grid in grids
        for tau in tau_values
    ]


def run_d2q9_validation(
    cases: list[D2Q9ValidationCase] | tuple[D2Q9ValidationCase, ...],
) -> list[D2Q9ValidationRecord]:
    """Run validation cases and return full diagnostic records."""

    records: list[D2Q9ValidationRecord] = []
    for case in cases:
        result = run_d2q9(case.to_config())
        records.append(D2Q9ValidationRecord.from_result(case, result))
    return records


def write_d2q9_validation_csv(
    records: list[D2Q9ValidationRecord],
    path: str | Path,
) -> Path:
    """Write D2Q9 validation diagnostics to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=D2Q9_VALIDATION_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return output_path


def steps_for_decay_exponent(
    grid_shape: tuple[int, int],
    tau: float,
    *,
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT,
) -> int:
    """Return steps such that viscosity * (kx^2 + ky^2) * steps is controlled."""

    if target_decay_exponent <= 0.0:
        raise ValueError("target_decay_exponent must be positive.")
    decay_per_step = taylor_green_decay_exponent(grid_shape, tau, 1)
    if decay_per_step <= 0.0:
        raise ValueError("tau and grid_shape must produce positive viscous decay.")
    return max(1, int(ceil(target_decay_exponent / decay_per_step)))


def taylor_green_decay_exponent(
    grid_shape: tuple[int, int],
    tau: float,
    steps: int,
) -> float:
    """Return viscosity * (kx^2 + ky^2) * steps for the periodic TGV mode."""

    nx, ny = grid_shape
    if nx <= 0 or ny <= 0:
        raise ValueError("grid_shape values must be positive.")
    viscosity = CS2 * (tau - 0.5)
    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    return float(viscosity * (kx**2 + ky**2) * steps)


def grid_spacings(
    grid_shape: tuple[int, int],
    *,
    domain_lengths: tuple[float, float] = (1.0, 1.0),
) -> tuple[float, float]:
    """Return grid spacings for a periodic 2D domain."""

    nx, ny = grid_shape
    lx, ly = domain_lengths
    if nx <= 0 or ny <= 0:
        raise ValueError("grid_shape values must be positive.")
    if lx <= 0.0 or ly <= 0.0:
        raise ValueError("domain_lengths must be positive.")
    return lx / nx, ly / ny


def periodic_vorticity(
    velocity: np.ndarray,
    *,
    spacing: tuple[float, float] = (1.0, 1.0),
) -> np.ndarray:
    """Return scalar vorticity d(uy)/dx - d(ux)/dy with periodic differences."""

    ux = velocity[0]
    uy = velocity[1]
    dx, dy = _validate_spacing(spacing)
    return _central_periodic(uy, axis=0, spacing=dx) - _central_periodic(
        ux,
        axis=1,
        spacing=dy,
    )


def periodic_divergence(
    velocity: np.ndarray,
    *,
    spacing: tuple[float, float] = (1.0, 1.0),
) -> np.ndarray:
    """Return divergence d(ux)/dx + d(uy)/dy with periodic differences."""

    ux = velocity[0]
    uy = velocity[1]
    dx, dy = _validate_spacing(spacing)
    return _central_periodic(ux, axis=0, spacing=dx) + _central_periodic(
        uy,
        axis=1,
        spacing=dy,
    )


def mean_kinetic_energy(density: np.ndarray, velocity: np.ndarray) -> float:
    """Return mean kinetic energy density, 0.5 * rho * |u|^2."""

    speed_squared = velocity[0] ** 2 + velocity[1] ** 2
    return float(np.mean(0.5 * density * speed_squared))


def max_mach_number(velocity: np.ndarray) -> float:
    """Return maximum lattice Mach number."""

    speed = np.sqrt(velocity[0] ** 2 + velocity[1] ** 2)
    lattice_sound_speed = float(np.sqrt(CS2))
    return float(np.max(speed) / lattice_sound_speed)


def normalized_l2_norm(field: np.ndarray) -> float:
    """Return an RMS-style L2 norm normalized by the number of grid points."""

    if field.size == 0:
        raise ValueError("field must be non-empty.")
    return float(np.linalg.norm(field.ravel()) / np.sqrt(field.size))


def _central_periodic(field: np.ndarray, axis: int, *, spacing: float) -> np.ndarray:
    return 0.5 * (
        np.roll(field, shift=-1, axis=axis) - np.roll(field, shift=1, axis=axis)
    ) / spacing


def _validate_spacing(spacing: tuple[float, float]) -> tuple[float, float]:
    dx, dy = spacing
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("spacing values must be positive.")
    return dx, dy


def _relative_scalar_error(actual: float, expected: float) -> float:
    denominator = abs(expected)
    if denominator == 0.0:
        return abs(actual - expected)
    return abs(actual - expected) / denominator
