"""First-wave D2Q9 scheme comparison harness."""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from pq_cfd.analysis import format_grid_shape
from pq_cfd.d2q9 import analytic_taylor_green_velocity
from pq_cfd.d2q9_order import (
    DEFAULT_MIN_VELOCITY_ORDER,
    ORDER_STATUS_FAILED,
    ORDER_STATUS_INVESTIGATION_REQUIRED,
    ORDER_STATUS_PASSED,
    grid_spacing,
    observed_order,
)
from pq_cfd.d2q9_validation import (
    DEFAULT_DECAY_EXPONENT,
    DEFAULT_DENSITY_DEVIATION_MAX,
    DEFAULT_DIVERGENCE_RMS_MAX,
    grid_spacings,
    max_mach_number,
    mean_kinetic_energy,
    normalized_l2_norm,
    periodic_divergence,
    periodic_vorticity,
    steps_for_decay_exponent,
)
from pq_cfd.d2q9_variants import D2Q9_SCHEMES, normalize_d2q9_scheme, run_d2q9_scheme
from pq_cfd.metrics import relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationResult

SCHEME_COMPARISON_CSV_COLUMNS = (
    "algorithm_id",
    "scheme",
    "model",
    "grid_shape",
    "grid_points",
    "steps",
    "tau",
    "amplitude",
    "grid_spacing_x",
    "grid_spacing_y",
    "velocity_relative_l2_error",
    "velocity_observed_order",
    "vorticity_relative_l2_error",
    "density_weighted_kinetic_energy",
    "incompressible_kinetic_energy",
    "expected_incompressible_kinetic_energy",
    "kinetic_energy_relative_error",
    "incompressible_kinetic_energy_relative_error",
    "divergence_l2_norm",
    "divergence_rms",
    "max_mach",
    "max_density_deviation",
    "mass_drift_relative",
    "runtime_seconds",
    "stable",
    "stability_blocker",
    "validation_status",
    "validation_blocker",
    "min_velocity_observed_order",
    "passed_for_quantum_followup",
)


@dataclass(frozen=True, slots=True)
class SchemeComparisonCase:
    """One D2Q9 first-wave collision-scheme comparison case."""

    scheme: str
    grid_shape: tuple[int, int]
    steps: int
    tau: float
    amplitude: float
    initial_condition: str = "taylor_green"

    @property
    def algorithm_id(self) -> str:
        """Return the algorithm registry id for this scheme."""

        return f"d2q9_{normalize_d2q9_scheme(self.scheme)}"

    def to_config(self) -> SimulationConfig:
        """Convert the case to a solver config."""

        return SimulationConfig(
            grid_shape=self.grid_shape,
            steps=self.steps,
            tau=self.tau,
            initial_condition=self.initial_condition,
            sample_interval=None,
            amplitude=self.amplitude,
        )


@dataclass(frozen=True, slots=True)
class SchemeComparisonRecord:
    """Stable diagnostics for one first-wave D2Q9 scheme run."""

    algorithm_id: str
    scheme: str
    model: str
    grid_shape: tuple[int, int]
    grid_points: int
    steps: int
    tau: float
    amplitude: float
    grid_spacing_x: float
    grid_spacing_y: float
    velocity_relative_l2_error: float
    velocity_observed_order: float | None
    vorticity_relative_l2_error: float
    density_weighted_kinetic_energy: float
    incompressible_kinetic_energy: float
    expected_incompressible_kinetic_energy: float
    kinetic_energy_relative_error: float
    incompressible_kinetic_energy_relative_error: float
    divergence_l2_norm: float
    divergence_rms: float
    max_mach: float
    max_density_deviation: float
    mass_drift_relative: float
    runtime_seconds: float
    stable: bool
    stability_blocker: str
    validation_status: str = ORDER_STATUS_INVESTIGATION_REQUIRED
    validation_blocker: str = "not_assessed"
    min_velocity_observed_order: float | None = None
    passed_for_quantum_followup: bool = False

    @classmethod
    def from_result(
        cls,
        case: SchemeComparisonCase,
        result: SimulationResult,
        *,
        divergence_rms_max: float = DEFAULT_DIVERGENCE_RMS_MAX,
        density_deviation_max: float = DEFAULT_DENSITY_DEVIATION_MAX,
    ) -> "SchemeComparisonRecord":
        """Create comparison diagnostics from one solver result."""

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
        kinetic_energy_error = _relative_scalar_error(
            density_weighted_kinetic_energy,
            expected_incompressible_kinetic_energy,
        )
        incompressible_kinetic_energy_error = _relative_scalar_error(
            incompressible_kinetic_energy,
            expected_incompressible_kinetic_energy,
        )
        divergence = periodic_divergence(result.velocity, spacing=spacing)
        mach = max_mach_number(result.velocity)
        max_density_deviation = float(
            np.max(np.abs(result.density - result.config.base_density))
        )
        velocity_error = relative_l2_error(result.velocity, expected_velocity)
        vorticity_error = relative_l2_error(vorticity, expected_vorticity)
        divergence_rms = normalized_l2_norm(divergence)
        stability_blocker = _stability_blocker(
            velocity_error=velocity_error,
            vorticity_error=vorticity_error,
            kinetic_energy_error=kinetic_energy_error,
            incompressible_kinetic_energy_error=incompressible_kinetic_energy_error,
            mach=mach,
            min_density=float(np.min(result.density)),
            max_density_deviation=max_density_deviation,
            divergence_rms=divergence_rms,
            mass_drift_relative=float(result.metrics["mass_drift_relative"]),
            divergence_rms_max=divergence_rms_max,
            density_deviation_max=density_deviation_max,
        )
        stable = stability_blocker == ""
        scheme = normalize_d2q9_scheme(case.scheme)

        return cls(
            algorithm_id=f"d2q9_{scheme}",
            scheme=scheme,
            model=result.model,
            grid_shape=case.grid_shape,
            grid_points=int(np.prod(case.grid_shape)),
            steps=case.steps,
            tau=case.tau,
            amplitude=case.amplitude,
            grid_spacing_x=spacing[0],
            grid_spacing_y=spacing[1],
            velocity_relative_l2_error=velocity_error,
            velocity_observed_order=None,
            vorticity_relative_l2_error=vorticity_error,
            density_weighted_kinetic_energy=density_weighted_kinetic_energy,
            incompressible_kinetic_energy=incompressible_kinetic_energy,
            expected_incompressible_kinetic_energy=(
                expected_incompressible_kinetic_energy
            ),
            kinetic_energy_relative_error=kinetic_energy_error,
            incompressible_kinetic_energy_relative_error=(
                incompressible_kinetic_energy_error
            ),
            divergence_l2_norm=float(np.linalg.norm(divergence.ravel())),
            divergence_rms=divergence_rms,
            max_mach=mach,
            max_density_deviation=max_density_deviation,
            mass_drift_relative=float(result.metrics["mass_drift_relative"]),
            runtime_seconds=float(result.metrics["runtime_seconds"]),
            stable=stable,
            stability_blocker=stability_blocker,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a CSV-friendly row with stable columns."""

        return {
            "algorithm_id": self.algorithm_id,
            "scheme": self.scheme,
            "model": self.model,
            "grid_shape": format_grid_shape(self.grid_shape),
            "grid_points": self.grid_points,
            "steps": self.steps,
            "tau": self.tau,
            "amplitude": self.amplitude,
            "grid_spacing_x": self.grid_spacing_x,
            "grid_spacing_y": self.grid_spacing_y,
            "velocity_relative_l2_error": self.velocity_relative_l2_error,
            "velocity_observed_order": _csv_optional(self.velocity_observed_order),
            "vorticity_relative_l2_error": self.vorticity_relative_l2_error,
            "density_weighted_kinetic_energy": self.density_weighted_kinetic_energy,
            "incompressible_kinetic_energy": self.incompressible_kinetic_energy,
            "expected_incompressible_kinetic_energy": (
                self.expected_incompressible_kinetic_energy
            ),
            "kinetic_energy_relative_error": self.kinetic_energy_relative_error,
            "incompressible_kinetic_energy_relative_error": (
                self.incompressible_kinetic_energy_relative_error
            ),
            "divergence_l2_norm": self.divergence_l2_norm,
            "divergence_rms": self.divergence_rms,
            "max_mach": self.max_mach,
            "max_density_deviation": self.max_density_deviation,
            "mass_drift_relative": self.mass_drift_relative,
            "runtime_seconds": self.runtime_seconds,
            "stable": self.stable,
            "stability_blocker": self.stability_blocker,
            "validation_status": self.validation_status,
            "validation_blocker": self.validation_blocker,
            "min_velocity_observed_order": _csv_optional(
                self.min_velocity_observed_order
            ),
            "passed_for_quantum_followup": self.passed_for_quantum_followup,
        }


def default_scheme_comparison_cases(
    *,
    schemes: tuple[str, ...] = D2Q9_SCHEMES,
    grid_shape: tuple[int, int] = (32, 32),
    steps: int = 32,
    tau: float = 0.8,
    amplitude: float = 0.02,
) -> list[SchemeComparisonCase]:
    """Return first-wave D2Q9 scheme comparison cases."""

    return [
        SchemeComparisonCase(
            scheme=scheme,
            grid_shape=grid_shape,
            steps=steps,
            tau=tau,
            amplitude=amplitude,
        )
        for scheme in schemes
    ]


def controlled_decay_scheme_comparison_cases(
    *,
    schemes: tuple[str, ...] = D2Q9_SCHEMES,
    grids: tuple[tuple[int, int], ...] = ((16, 16), (32, 32), (64, 64)),
    tau: float = 0.8,
    amplitude: float = 0.02,
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT,
) -> list[SchemeComparisonCase]:
    """Return controlled-decay first-wave D2Q9 scheme comparison cases."""

    return [
        SchemeComparisonCase(
            scheme=scheme,
            grid_shape=grid,
            steps=steps_for_decay_exponent(
                grid,
                tau,
                target_decay_exponent=target_decay_exponent,
            ),
            tau=tau,
            amplitude=amplitude,
        )
        for scheme in schemes
        for grid in grids
    ]


def run_scheme_comparison(
    cases: list[SchemeComparisonCase] | tuple[SchemeComparisonCase, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
    divergence_rms_max: float = DEFAULT_DIVERGENCE_RMS_MAX,
    density_deviation_max: float = DEFAULT_DENSITY_DEVIATION_MAX,
) -> list[SchemeComparisonRecord]:
    """Run first-wave D2Q9 scheme comparisons."""

    records: list[SchemeComparisonRecord] = []
    for case in cases:
        result = run_d2q9_scheme(case.to_config(), case.scheme)
        records.append(
            SchemeComparisonRecord.from_result(
                case,
                result,
                divergence_rms_max=divergence_rms_max,
                density_deviation_max=density_deviation_max,
            )
        )
    return attach_scheme_observed_orders(records, min_velocity_order=min_velocity_order)


def attach_scheme_observed_orders(
    records: list[SchemeComparisonRecord] | tuple[SchemeComparisonRecord, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> list[SchemeComparisonRecord]:
    """Attach per-scheme observed orders and validation status."""

    output: list[SchemeComparisonRecord] = []
    for scheme in sorted({record.scheme for record in records}):
        subset = sorted(
            [record for record in records if record.scheme == scheme],
            key=lambda record: grid_spacing(record.grid_shape),
            reverse=True,
        )
        with_orders: list[SchemeComparisonRecord] = []
        previous: SchemeComparisonRecord | None = None
        for record in subset:
            velocity_order = None
            if previous is not None:
                velocity_order = observed_order(
                    coarse_spacing=grid_spacing(previous.grid_shape),
                    fine_spacing=grid_spacing(record.grid_shape),
                    coarse_error=previous.velocity_relative_l2_error,
                    fine_error=record.velocity_relative_l2_error,
                )
            with_orders.append(replace(record, velocity_observed_order=velocity_order))
            previous = record
        assessment = _assess_scheme_records(
            with_orders,
            min_velocity_order=min_velocity_order,
        )
        output.extend(
            replace(
                record,
                validation_status=assessment["validation_status"],
                validation_blocker=assessment["validation_blocker"],
                min_velocity_observed_order=assessment["min_velocity_observed_order"],
                passed_for_quantum_followup=assessment["passed_for_quantum_followup"],
            )
            for record in with_orders
        )
    return sorted(
        output,
        key=lambda record: (record.scheme, grid_spacing(record.grid_shape)),
        reverse=True,
    )


def write_scheme_comparison_csv(
    records: list[SchemeComparisonRecord] | tuple[SchemeComparisonRecord, ...],
    path: str | Path,
) -> Path:
    """Write first-wave scheme comparison records to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCHEME_COMPARISON_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return output_path


def _relative_scalar_error(actual: float, expected: float) -> float:
    denominator = abs(expected)
    if denominator == 0.0:
        return abs(actual - expected)
    return abs(actual - expected) / denominator


def _stability_blocker(
    *,
    velocity_error: float,
    vorticity_error: float,
    kinetic_energy_error: float,
    incompressible_kinetic_energy_error: float,
    mach: float,
    min_density: float,
    max_density_deviation: float,
    divergence_rms: float,
    mass_drift_relative: float,
    divergence_rms_max: float,
    density_deviation_max: float,
) -> str:
    if not all(
        np.isfinite(value)
        for value in (
            velocity_error,
            vorticity_error,
            kinetic_energy_error,
            incompressible_kinetic_energy_error,
            mach,
            min_density,
            max_density_deviation,
            divergence_rms,
            mass_drift_relative,
        )
    ):
        return "nonfinite_metric"
    if mach >= 0.1:
        return "mach_limit_exceeded"
    if min_density <= 0.0:
        return "nonpositive_density"
    if divergence_rms >= divergence_rms_max:
        return "divergence_rms_exceeded"
    if max_density_deviation >= density_deviation_max:
        return "density_deviation_exceeded"
    if mass_drift_relative >= 1e-10:
        return "mass_drift_exceeded"
    return ""


def _assess_scheme_records(
    records: list[SchemeComparisonRecord],
    *,
    min_velocity_order: float,
) -> dict[str, Any]:
    if not records:
        return {
            "validation_status": ORDER_STATUS_FAILED,
            "validation_blocker": "no_records",
            "min_velocity_observed_order": None,
            "passed_for_quantum_followup": False,
        }
    if any(not record.stable for record in records):
        return {
            "validation_status": ORDER_STATUS_FAILED,
            "validation_blocker": "unstable_or_nonfinite_case",
            "min_velocity_observed_order": _min_velocity_observed_order(records),
            "passed_for_quantum_followup": False,
        }
    velocity_orders = [
        record.velocity_observed_order
        for record in records
        if record.velocity_observed_order is not None
    ]
    if not velocity_orders:
        return {
            "validation_status": ORDER_STATUS_INVESTIGATION_REQUIRED,
            "validation_blocker": "insufficient_refinement",
            "min_velocity_observed_order": None,
            "passed_for_quantum_followup": False,
        }
    if any(not np.isfinite(order) for order in velocity_orders):
        return {
            "validation_status": ORDER_STATUS_FAILED,
            "validation_blocker": "nonfinite_observed_order",
            "min_velocity_observed_order": _min_velocity_observed_order(records),
            "passed_for_quantum_followup": False,
        }
    min_order = float(min(velocity_orders))
    if any(
        fine.velocity_relative_l2_error > coarse.velocity_relative_l2_error
        for coarse, fine in zip(records, records[1:])
    ) or min_order < 0.0:
        return {
            "validation_status": ORDER_STATUS_INVESTIGATION_REQUIRED,
            "validation_blocker": "velocity_error_increases_under_refinement",
            "min_velocity_observed_order": min_order,
            "passed_for_quantum_followup": False,
        }
    if min_order < min_velocity_order:
        return {
            "validation_status": ORDER_STATUS_INVESTIGATION_REQUIRED,
            "validation_blocker": f"velocity_order_below_{min_velocity_order:g}",
            "min_velocity_observed_order": min_order,
            "passed_for_quantum_followup": False,
        }
    return {
        "validation_status": ORDER_STATUS_PASSED,
        "validation_blocker": "",
        "min_velocity_observed_order": min_order,
        "passed_for_quantum_followup": True,
    }


def _min_velocity_observed_order(
    records: list[SchemeComparisonRecord],
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


def _csv_optional(value: float | None) -> float | str:
    return "" if value is None else value
