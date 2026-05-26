"""D2Q9 Taylor-Green diagnostics and convergence gates."""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from math import ceil
from pathlib import Path
from typing import Any

import numpy as np

from pq_cfd.analysis import format_grid_shape
from pq_cfd.d2q9 import CS2, analytic_taylor_green_velocity, run_d2q9
from pq_cfd.metrics import relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationResult

D2Q9_DIAGNOSTIC_GRIDS = ((16, 16), (32, 32), (64, 64), (128, 128))
D2Q9_DIAGNOSTIC_TAUS = (0.8,)
DEFAULT_DECAY_EXPONENT = 0.1
DEFAULT_DIVERGENCE_RMS_MAX = 1e-2
DEFAULT_DENSITY_DEVIATION_MAX = 5e-2
DEFAULT_MIN_VELOCITY_ORDER = 1.5

STATUS_PASSED = "passed"
STATUS_INVESTIGATION_REQUIRED = "investigation_required"
STATUS_FAILED = "failed"

D2Q9_DIAGNOSTIC_CSV_COLUMNS = (
    "model",
    "grid_shape",
    "grid_points",
    "grid_spacing",
    "steps",
    "tau",
    "amplitude",
    "target_decay_exponent",
    "actual_decay_exponent",
    "velocity_relative_l2_error",
    "velocity_observed_order",
    "vorticity_relative_l2_error",
    "vorticity_observed_order",
    "kinetic_energy_relative_error",
    "kinetic_energy_observed_order",
    "divergence_rms",
    "max_mach",
    "max_density_deviation",
    "mass_drift_relative",
    "runtime_seconds",
    "stable",
    "validation_status",
    "validation_blocker",
    "min_velocity_observed_order",
    "passed_for_quantum_followup",
)


@dataclass(frozen=True, slots=True)
class D2Q9DiagnosticCase:
    """A periodic Taylor-Green case at controlled analytic decay."""

    grid_shape: tuple[int, int]
    tau: float
    steps: int
    amplitude: float
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT
    initial_condition: str = "taylor_green"

    def to_config(self) -> SimulationConfig:
        """Convert the diagnostic case into a solver config."""

        return SimulationConfig(
            grid_shape=self.grid_shape,
            steps=self.steps,
            tau=self.tau,
            initial_condition=self.initial_condition,
            sample_interval=None,
            amplitude=self.amplitude,
        )


@dataclass(frozen=True, slots=True)
class D2Q9DiagnosticRecord:
    """One Taylor-Green diagnostics row with optional adjacent-grid orders."""

    model: str
    grid_shape: tuple[int, int]
    grid_points: int
    grid_spacing: float
    steps: int
    tau: float
    amplitude: float
    target_decay_exponent: float
    actual_decay_exponent: float
    velocity_relative_l2_error: float
    velocity_observed_order: float | None
    vorticity_relative_l2_error: float
    vorticity_observed_order: float | None
    kinetic_energy_relative_error: float
    kinetic_energy_observed_order: float | None
    divergence_rms: float
    max_mach: float
    max_density_deviation: float
    mass_drift_relative: float
    runtime_seconds: float
    stable: bool
    validation_status: str = STATUS_INVESTIGATION_REQUIRED
    validation_blocker: str = "not_assessed"
    min_velocity_observed_order: float | None = None
    passed_for_quantum_followup: bool = False

    @classmethod
    def from_result(
        cls,
        case: D2Q9DiagnosticCase,
        result: SimulationResult,
    ) -> "D2Q9DiagnosticRecord":
        """Build diagnostics from a completed D2Q9 run."""

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

        base_density = np.full((nx, ny), result.config.base_density, dtype=float)
        kinetic_energy = mean_kinetic_energy(result.density, result.velocity)
        expected_kinetic_energy = mean_kinetic_energy(base_density, expected_velocity)
        kinetic_energy_error = relative_scalar_error(
            kinetic_energy,
            expected_kinetic_energy,
        )
        velocity_error = relative_l2_error(result.velocity, expected_velocity)
        vorticity_error = relative_l2_error(vorticity, expected_vorticity)
        divergence_rms = normalized_l2_norm(divergence)
        max_mach = max_mach_number(result.velocity)
        max_density_deviation = float(
            np.max(np.abs(result.density - result.config.base_density))
        )
        stable = bool(
            np.isfinite(velocity_error)
            and np.isfinite(vorticity_error)
            and np.isfinite(kinetic_energy_error)
            and np.isfinite(divergence_rms)
            and np.isfinite(max_mach)
            and max_mach < 0.1
            and divergence_rms < DEFAULT_DIVERGENCE_RMS_MAX
            and float(np.min(result.density)) > 0.0
            and max_density_deviation < DEFAULT_DENSITY_DEVIATION_MAX
            and result.metrics["mass_drift_relative"] < 1e-10
        )

        return cls(
            model=result.model,
            grid_shape=case.grid_shape,
            grid_points=int(np.prod(case.grid_shape)),
            grid_spacing=grid_spacing(case.grid_shape),
            steps=case.steps,
            tau=case.tau,
            amplitude=case.amplitude,
            target_decay_exponent=case.target_decay_exponent,
            actual_decay_exponent=taylor_green_decay_exponent(
                case.grid_shape,
                case.tau,
                case.steps,
            ),
            velocity_relative_l2_error=velocity_error,
            velocity_observed_order=None,
            vorticity_relative_l2_error=vorticity_error,
            vorticity_observed_order=None,
            kinetic_energy_relative_error=kinetic_energy_error,
            kinetic_energy_observed_order=None,
            divergence_rms=divergence_rms,
            max_mach=max_mach,
            max_density_deviation=max_density_deviation,
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
            "grid_spacing": self.grid_spacing,
            "steps": self.steps,
            "tau": self.tau,
            "amplitude": self.amplitude,
            "target_decay_exponent": self.target_decay_exponent,
            "actual_decay_exponent": self.actual_decay_exponent,
            "velocity_relative_l2_error": self.velocity_relative_l2_error,
            "velocity_observed_order": csv_optional(self.velocity_observed_order),
            "vorticity_relative_l2_error": self.vorticity_relative_l2_error,
            "vorticity_observed_order": csv_optional(self.vorticity_observed_order),
            "kinetic_energy_relative_error": self.kinetic_energy_relative_error,
            "kinetic_energy_observed_order": csv_optional(
                self.kinetic_energy_observed_order
            ),
            "divergence_rms": self.divergence_rms,
            "max_mach": self.max_mach,
            "max_density_deviation": self.max_density_deviation,
            "mass_drift_relative": self.mass_drift_relative,
            "runtime_seconds": self.runtime_seconds,
            "stable": self.stable,
            "validation_status": self.validation_status,
            "validation_blocker": self.validation_blocker,
            "min_velocity_observed_order": csv_optional(
                self.min_velocity_observed_order
            ),
            "passed_for_quantum_followup": self.passed_for_quantum_followup,
        }


@dataclass(frozen=True, slots=True)
class D2Q9DiagnosticAssessment:
    """Per-tau convergence assessment for follow-up decisions."""

    tau: float
    validation_status: str
    validation_blocker: str
    min_velocity_observed_order: float | None
    passed_for_quantum_followup: bool
    records_evaluated: int


def d2q9_diagnostic_cases(
    *,
    grids: tuple[tuple[int, int], ...] = D2Q9_DIAGNOSTIC_GRIDS,
    tau_values: tuple[float, ...] = D2Q9_DIAGNOSTIC_TAUS,
    amplitude: float = 0.02,
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT,
) -> list[D2Q9DiagnosticCase]:
    """Generate Taylor-Green diagnostic cases at fixed analytic decay."""

    return [
        D2Q9DiagnosticCase(
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


def run_d2q9_diagnostics(
    cases: list[D2Q9DiagnosticCase] | tuple[D2Q9DiagnosticCase, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> list[D2Q9DiagnosticRecord]:
    """Run diagnostic cases and attach adjacent-grid observed orders."""

    records = [
        D2Q9DiagnosticRecord.from_result(case, run_d2q9(case.to_config()))
        for case in cases
    ]
    return attach_observed_orders(records, min_velocity_order=min_velocity_order)


def attach_observed_orders(
    records: list[D2Q9DiagnosticRecord] | tuple[D2Q9DiagnosticRecord, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> list[D2Q9DiagnosticRecord]:
    """Attach observed orders within each tau group."""

    output: list[D2Q9DiagnosticRecord] = []
    for tau in sorted({record.tau for record in records}):
        subset = sorted(
            [record for record in records if record.tau == tau],
            key=lambda record: record.grid_spacing,
            reverse=True,
        )
        previous: D2Q9DiagnosticRecord | None = None
        with_orders: list[D2Q9DiagnosticRecord] = []
        for record in subset:
            velocity_order = None
            vorticity_order = None
            energy_order = None
            if previous is not None:
                velocity_order = observed_order(
                    coarse_spacing=previous.grid_spacing,
                    fine_spacing=record.grid_spacing,
                    coarse_error=previous.velocity_relative_l2_error,
                    fine_error=record.velocity_relative_l2_error,
                )
                vorticity_order = observed_order(
                    coarse_spacing=previous.grid_spacing,
                    fine_spacing=record.grid_spacing,
                    coarse_error=previous.vorticity_relative_l2_error,
                    fine_error=record.vorticity_relative_l2_error,
                )
                energy_order = observed_order(
                    coarse_spacing=previous.grid_spacing,
                    fine_spacing=record.grid_spacing,
                    coarse_error=previous.kinetic_energy_relative_error,
                    fine_error=record.kinetic_energy_relative_error,
                )
            with_orders.append(
                replace(
                    record,
                    velocity_observed_order=velocity_order,
                    vorticity_observed_order=vorticity_order,
                    kinetic_energy_observed_order=energy_order,
                )
            )
            previous = record
        assessment = assess_d2q9_diagnostics(
            with_orders,
            min_velocity_order=min_velocity_order,
        )
        output.extend(_with_assessment(record, assessment) for record in with_orders)
    return output


def assess_d2q9_diagnostics(
    records: list[D2Q9DiagnosticRecord] | tuple[D2Q9DiagnosticRecord, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> D2Q9DiagnosticAssessment:
    """Assess whether a diagnostics group is promotable for quantum follow-up."""

    if min_velocity_order <= 0.0:
        raise ValueError("min_velocity_order must be positive.")
    if not records:
        return D2Q9DiagnosticAssessment(
            tau=float("nan"),
            validation_status=STATUS_FAILED,
            validation_blocker="no_records",
            min_velocity_observed_order=None,
            passed_for_quantum_followup=False,
            records_evaluated=0,
        )

    ordered = sorted(records, key=lambda record: record.grid_spacing, reverse=True)
    tau = ordered[0].tau
    if any(not finite_record(record) or not record.stable for record in ordered):
        return D2Q9DiagnosticAssessment(
            tau=tau,
            validation_status=STATUS_FAILED,
            validation_blocker="unstable_or_nonfinite_case",
            min_velocity_observed_order=min_velocity_order_in(ordered),
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )

    velocity_orders = [
        record.velocity_observed_order
        for record in ordered
        if record.velocity_observed_order is not None
    ]
    if not velocity_orders:
        return D2Q9DiagnosticAssessment(
            tau=tau,
            validation_status=STATUS_INVESTIGATION_REQUIRED,
            validation_blocker="insufficient_refinement",
            min_velocity_observed_order=None,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    if any(not np.isfinite(order) for order in velocity_orders):
        return D2Q9DiagnosticAssessment(
            tau=tau,
            validation_status=STATUS_FAILED,
            validation_blocker="nonfinite_observed_order",
            min_velocity_observed_order=min_velocity_order_in(ordered),
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )

    min_order = float(min(velocity_orders))
    if any(
        fine.velocity_relative_l2_error > coarse.velocity_relative_l2_error
        for coarse, fine in zip(ordered, ordered[1:])
    ) or min_order < 0.0:
        return D2Q9DiagnosticAssessment(
            tau=tau,
            validation_status=STATUS_INVESTIGATION_REQUIRED,
            validation_blocker="velocity_error_increases_under_refinement",
            min_velocity_observed_order=min_order,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    if min_order < min_velocity_order:
        return D2Q9DiagnosticAssessment(
            tau=tau,
            validation_status=STATUS_INVESTIGATION_REQUIRED,
            validation_blocker=f"velocity_order_below_{min_velocity_order:g}",
            min_velocity_observed_order=min_order,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    return D2Q9DiagnosticAssessment(
        tau=tau,
        validation_status=STATUS_PASSED,
        validation_blocker="",
        min_velocity_observed_order=min_order,
        passed_for_quantum_followup=True,
        records_evaluated=len(ordered),
    )


def write_d2q9_diagnostics_csv(
    records: list[D2Q9DiagnosticRecord] | tuple[D2Q9DiagnosticRecord, ...],
    path: str | Path,
) -> Path:
    """Write D2Q9 diagnostics to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=D2Q9_DIAGNOSTIC_CSV_COLUMNS)
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


def grid_spacing(grid_shape: tuple[int, int]) -> float:
    """Return normalized grid spacing for a unit square periodic domain."""

    nx, ny = grid_shape
    if nx <= 0 or ny <= 0:
        raise ValueError("grid_shape values must be positive.")
    return 1.0 / float(max(nx, ny))


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


def observed_order(
    *,
    coarse_spacing: float,
    fine_spacing: float,
    coarse_error: float,
    fine_error: float,
) -> float:
    """Return p where error is approximately C * h**p."""

    if coarse_spacing <= 0.0 or fine_spacing <= 0.0:
        raise ValueError("grid spacings must be positive.")
    if coarse_spacing <= fine_spacing:
        raise ValueError("coarse_spacing must be larger than fine_spacing.")
    if coarse_error <= 0.0 or fine_error <= 0.0:
        raise ValueError("errors must be positive.")
    return float(np.log(coarse_error / fine_error) / np.log(coarse_spacing / fine_spacing))


def periodic_vorticity(
    velocity: np.ndarray,
    *,
    spacing: tuple[float, float] = (1.0, 1.0),
) -> np.ndarray:
    """Return scalar vorticity d(uy)/dx - d(ux)/dy with periodic differences."""

    ux = velocity[0]
    uy = velocity[1]
    dx, dy = validate_spacing(spacing)
    return central_periodic(uy, axis=0, spacing=dx) - central_periodic(
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
    dx, dy = validate_spacing(spacing)
    return central_periodic(ux, axis=0, spacing=dx) + central_periodic(
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


def central_periodic(field: np.ndarray, axis: int, *, spacing: float) -> np.ndarray:
    return 0.5 * (
        np.roll(field, shift=-1, axis=axis) - np.roll(field, shift=1, axis=axis)
    ) / spacing


def validate_spacing(spacing: tuple[float, float]) -> tuple[float, float]:
    dx, dy = spacing
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("spacing values must be positive.")
    return dx, dy


def relative_scalar_error(actual: float, expected: float) -> float:
    denominator = abs(expected)
    if denominator == 0.0:
        return abs(actual - expected)
    return abs(actual - expected) / denominator


def csv_optional(value: float | None) -> float | str:
    return "" if value is None else value


def finite_record(record: D2Q9DiagnosticRecord) -> bool:
    optional_orders = (
        record.velocity_observed_order,
        record.vorticity_observed_order,
        record.kinetic_energy_observed_order,
    )
    values = (
        record.velocity_relative_l2_error,
        record.vorticity_relative_l2_error,
        record.kinetic_energy_relative_error,
        record.divergence_rms,
        record.max_mach,
        record.max_density_deviation,
        record.mass_drift_relative,
        record.runtime_seconds,
    )
    return all(np.isfinite(value) for value in values) and all(
        value is None or np.isfinite(value) for value in optional_orders
    )


def min_velocity_order_in(
    records: list[D2Q9DiagnosticRecord] | tuple[D2Q9DiagnosticRecord, ...],
) -> float | None:
    orders = [
        record.velocity_observed_order
        for record in records
        if record.velocity_observed_order is not None
        and np.isfinite(record.velocity_observed_order)
    ]
    if not orders:
        return None
    return float(min(orders))


def _with_assessment(
    record: D2Q9DiagnosticRecord,
    assessment: D2Q9DiagnosticAssessment,
) -> D2Q9DiagnosticRecord:
    return replace(
        record,
        validation_status=assessment.validation_status,
        validation_blocker=assessment.validation_blocker,
        min_velocity_observed_order=assessment.min_velocity_observed_order,
        passed_for_quantum_followup=assessment.passed_for_quantum_followup,
    )
