"""Formal D2Q9 Taylor-Green order-of-accuracy study."""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from pq_cfd.analysis import format_grid_shape
from pq_cfd.d2q9_validation import (
    DEFAULT_DECAY_EXPONENT,
    D2Q9ValidationCase,
    D2Q9ValidationRecord,
    d2q9_validation_cases,
    run_d2q9_validation,
)

D2Q9_ORDER_GRIDS = ((16, 16), (32, 32), (64, 64), (128, 128))
D2Q9_ORDER_TAUS = (0.8,)
DEFAULT_MIN_VELOCITY_ORDER = 1.5
ORDER_STATUS_PASSED = "passed"
ORDER_STATUS_INVESTIGATION_REQUIRED = "investigation_required"
ORDER_STATUS_FAILED = "failed"

D2Q9_ORDER_CSV_COLUMNS = (
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
    "divergence_l2_norm",
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
class D2Q9OrderAssessment:
    """Per-tau convergence assessment for downstream promotion decisions."""

    tau: float
    validation_status: str
    validation_blocker: str
    min_velocity_observed_order: float | None
    passed_for_quantum_followup: bool
    records_evaluated: int

    def as_dict(self) -> dict[str, Any]:
        """Return a CSV/JSON-friendly assessment row."""

        return {
            "tau": self.tau,
            "validation_status": self.validation_status,
            "validation_blocker": self.validation_blocker,
            "min_velocity_observed_order": _csv_optional(
                self.min_velocity_observed_order
            ),
            "passed_for_quantum_followup": self.passed_for_quantum_followup,
            "records_evaluated": self.records_evaluated,
        }


@dataclass(frozen=True, slots=True)
class D2Q9OrderRecord:
    """One order-study row with diagnostics and adjacent-grid slopes."""

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
    divergence_l2_norm: float
    max_mach: float
    max_density_deviation: float
    mass_drift_relative: float
    runtime_seconds: float
    stable: bool
    validation_status: str = ORDER_STATUS_INVESTIGATION_REQUIRED
    validation_blocker: str = "not_assessed"
    min_velocity_observed_order: float | None = None
    passed_for_quantum_followup: bool = False

    @classmethod
    def from_validation_record(
        cls,
        record: D2Q9ValidationRecord,
        *,
        velocity_observed_order: float | None = None,
        vorticity_observed_order: float | None = None,
        kinetic_energy_observed_order: float | None = None,
    ) -> "D2Q9OrderRecord":
        """Create an order-study row from validation diagnostics."""

        return cls(
            model=record.model,
            grid_shape=record.grid_shape,
            grid_points=record.grid_points,
            grid_spacing=grid_spacing(record.grid_shape),
            steps=record.steps,
            tau=record.tau,
            amplitude=record.amplitude,
            target_decay_exponent=record.target_decay_exponent,
            actual_decay_exponent=record.actual_decay_exponent,
            velocity_relative_l2_error=record.velocity_relative_l2_error,
            velocity_observed_order=velocity_observed_order,
            vorticity_relative_l2_error=record.vorticity_relative_l2_error,
            vorticity_observed_order=vorticity_observed_order,
            kinetic_energy_relative_error=record.kinetic_energy_relative_error,
            kinetic_energy_observed_order=kinetic_energy_observed_order,
            divergence_l2_norm=record.divergence_l2_norm,
            max_mach=record.max_mach,
            max_density_deviation=record.max_density_deviation,
            mass_drift_relative=record.mass_drift_relative,
            runtime_seconds=record.runtime_seconds,
            stable=record.stable,
            validation_status=ORDER_STATUS_INVESTIGATION_REQUIRED,
            validation_blocker="not_assessed",
            min_velocity_observed_order=None,
            passed_for_quantum_followup=False,
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
            "velocity_observed_order": _csv_optional(self.velocity_observed_order),
            "vorticity_relative_l2_error": self.vorticity_relative_l2_error,
            "vorticity_observed_order": _csv_optional(self.vorticity_observed_order),
            "kinetic_energy_relative_error": self.kinetic_energy_relative_error,
            "kinetic_energy_observed_order": _csv_optional(
                self.kinetic_energy_observed_order
            ),
            "divergence_l2_norm": self.divergence_l2_norm,
            "max_mach": self.max_mach,
            "max_density_deviation": self.max_density_deviation,
            "mass_drift_relative": self.mass_drift_relative,
            "runtime_seconds": self.runtime_seconds,
            "stable": self.stable,
            "validation_status": self.validation_status,
            "validation_blocker": self.validation_blocker,
            "min_velocity_observed_order": _csv_optional(
                self.min_velocity_observed_order
            ),
            "passed_for_quantum_followup": self.passed_for_quantum_followup,
        }


def d2q9_order_cases(
    *,
    grids: tuple[tuple[int, int], ...] = D2Q9_ORDER_GRIDS,
    tau_values: tuple[float, ...] = D2Q9_ORDER_TAUS,
    amplitude: float = 0.02,
    target_decay_exponent: float = DEFAULT_DECAY_EXPONENT,
) -> list[D2Q9ValidationCase]:
    """Generate D2Q9 Taylor-Green cases for an order study."""

    return d2q9_validation_cases(
        grids=grids,
        tau_values=tau_values,
        amplitude=amplitude,
        target_decay_exponent=target_decay_exponent,
    )


def run_d2q9_order_study(
    cases: list[D2Q9ValidationCase] | tuple[D2Q9ValidationCase, ...],
) -> list[D2Q9OrderRecord]:
    """Run validation cases and attach adjacent-grid observed orders."""

    validation_records = run_d2q9_validation(cases)
    return attach_observed_orders(validation_records)


def attach_observed_orders(
    records: list[D2Q9ValidationRecord] | tuple[D2Q9ValidationRecord, ...],
    *,
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> list[D2Q9OrderRecord]:
    """Attach observed orders within each tau group."""

    output: list[D2Q9OrderRecord] = []
    for tau in sorted({record.tau for record in records}):
        subset = sorted(
            [record for record in records if record.tau == tau],
            key=lambda record: grid_spacing(record.grid_shape),
            reverse=True,
        )
        previous: D2Q9ValidationRecord | None = None
        for record in subset:
            velocity_order = None
            vorticity_order = None
            energy_order = None
            if previous is not None:
                velocity_order = observed_order(
                    coarse_spacing=grid_spacing(previous.grid_shape),
                    fine_spacing=grid_spacing(record.grid_shape),
                    coarse_error=previous.velocity_relative_l2_error,
                    fine_error=record.velocity_relative_l2_error,
                )
                vorticity_order = observed_order(
                    coarse_spacing=grid_spacing(previous.grid_shape),
                    fine_spacing=grid_spacing(record.grid_shape),
                    coarse_error=previous.vorticity_relative_l2_error,
                    fine_error=record.vorticity_relative_l2_error,
                )
                energy_order = observed_order(
                    coarse_spacing=grid_spacing(previous.grid_shape),
                    fine_spacing=grid_spacing(record.grid_shape),
                    coarse_error=previous.kinetic_energy_relative_error,
                    fine_error=record.kinetic_energy_relative_error,
                )
            output.append(
                D2Q9OrderRecord.from_validation_record(
                    record,
                    velocity_observed_order=velocity_order,
                    vorticity_observed_order=vorticity_order,
                    kinetic_energy_observed_order=energy_order,
                )
            )
            previous = record
        assessment = assess_order_records(output_for_tau(output, tau), min_velocity_order)
        output = [
            _with_assessment(record, assessment) if record.tau == tau else record
            for record in output
        ]
    return output


def output_for_tau(records: list[D2Q9OrderRecord], tau: float) -> list[D2Q9OrderRecord]:
    """Return records for a tau group sorted from coarse to fine."""

    return sorted(
        [record for record in records if record.tau == tau],
        key=lambda record: record.grid_spacing,
        reverse=True,
    )


def assess_order_records(
    records: list[D2Q9OrderRecord] | tuple[D2Q9OrderRecord, ...],
    min_velocity_order: float = DEFAULT_MIN_VELOCITY_ORDER,
) -> D2Q9OrderAssessment:
    """Assess whether an order-study group is promotable for quantum follow-up."""

    if min_velocity_order <= 0.0:
        raise ValueError("min_velocity_order must be positive.")
    if not records:
        return D2Q9OrderAssessment(
            tau=float("nan"),
            validation_status=ORDER_STATUS_FAILED,
            validation_blocker="no_records",
            min_velocity_observed_order=None,
            passed_for_quantum_followup=False,
            records_evaluated=0,
        )

    ordered = sorted(records, key=lambda record: record.grid_spacing, reverse=True)
    tau = ordered[0].tau
    if any(not _finite_record(record) or not record.stable for record in ordered):
        return D2Q9OrderAssessment(
            tau=tau,
            validation_status=ORDER_STATUS_FAILED,
            validation_blocker="unstable_or_nonfinite_case",
            min_velocity_observed_order=_min_velocity_order(ordered),
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )

    velocity_orders = [
        record.velocity_observed_order
        for record in ordered
        if record.velocity_observed_order is not None
    ]
    if not velocity_orders:
        return D2Q9OrderAssessment(
            tau=tau,
            validation_status=ORDER_STATUS_INVESTIGATION_REQUIRED,
            validation_blocker="insufficient_refinement",
            min_velocity_observed_order=None,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    if any(not np.isfinite(order) for order in velocity_orders):
        return D2Q9OrderAssessment(
            tau=tau,
            validation_status=ORDER_STATUS_FAILED,
            validation_blocker="nonfinite_observed_order",
            min_velocity_observed_order=_min_velocity_order(ordered),
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )

    min_order = float(min(velocity_orders))
    if any(
        fine.velocity_relative_l2_error > coarse.velocity_relative_l2_error
        for coarse, fine in zip(ordered, ordered[1:])
    ) or min_order < 0.0:
        return D2Q9OrderAssessment(
            tau=tau,
            validation_status=ORDER_STATUS_INVESTIGATION_REQUIRED,
            validation_blocker="velocity_error_increases_under_refinement",
            min_velocity_observed_order=min_order,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    if min_order < min_velocity_order:
        return D2Q9OrderAssessment(
            tau=tau,
            validation_status=ORDER_STATUS_INVESTIGATION_REQUIRED,
            validation_blocker=f"velocity_order_below_{min_velocity_order:g}",
            min_velocity_observed_order=min_order,
            passed_for_quantum_followup=False,
            records_evaluated=len(ordered),
        )
    return D2Q9OrderAssessment(
        tau=tau,
        validation_status=ORDER_STATUS_PASSED,
        validation_blocker="",
        min_velocity_observed_order=min_order,
        passed_for_quantum_followup=True,
        records_evaluated=len(ordered),
    )


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


def grid_spacing(grid_shape: tuple[int, int]) -> float:
    """Return normalized grid spacing for a unit square periodic domain."""

    nx, ny = grid_shape
    if nx <= 0 or ny <= 0:
        raise ValueError("grid_shape values must be positive.")
    return 1.0 / float(max(nx, ny))


def write_d2q9_order_csv(
    records: list[D2Q9OrderRecord],
    path: str | Path,
) -> Path:
    """Write order-study records to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=D2Q9_ORDER_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return output_path


def _csv_optional(value: float | None) -> float | str:
    return "" if value is None else value


def _with_assessment(
    record: D2Q9OrderRecord,
    assessment: D2Q9OrderAssessment,
) -> D2Q9OrderRecord:
    return replace(
        record,
        validation_status=assessment.validation_status,
        validation_blocker=assessment.validation_blocker,
        min_velocity_observed_order=assessment.min_velocity_observed_order,
        passed_for_quantum_followup=assessment.passed_for_quantum_followup,
    )


def _finite_record(record: D2Q9OrderRecord) -> bool:
    optional_orders = (
        record.velocity_observed_order,
        record.vorticity_observed_order,
        record.kinetic_energy_observed_order,
    )
    values = (
        record.velocity_relative_l2_error,
        record.vorticity_relative_l2_error,
        record.kinetic_energy_relative_error,
        record.divergence_l2_norm,
        record.max_mach,
        record.max_density_deviation,
        record.mass_drift_relative,
        record.runtime_seconds,
    )
    return all(np.isfinite(value) for value in values) and all(
        value is None or np.isfinite(value) for value in optional_orders
    )


def _min_velocity_order(
    records: list[D2Q9OrderRecord] | tuple[D2Q9OrderRecord, ...],
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
