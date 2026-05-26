import csv

import pytest

from pq_cfd import (
    D2Q9DiagnosticCase,
    d2q9_diagnostic_cases,
    run_d2q9_diagnostics,
    steps_for_decay_exponent,
    write_d2q9_diagnostics_csv,
)
from pq_cfd.d2q9_diagnostics import (
    D2Q9_DIAGNOSTIC_CSV_COLUMNS,
    D2Q9DiagnosticRecord,
    STATUS_FAILED,
    STATUS_INVESTIGATION_REQUIRED,
    STATUS_PASSED,
    assess_d2q9_diagnostics,
    attach_observed_orders,
    observed_order,
)


def test_d2q9_diagnostic_case_generation() -> None:
    cases = d2q9_diagnostic_cases(
        grids=((16, 16), (32, 32)),
        tau_values=(0.8,),
        amplitude=0.02,
    )

    assert len(cases) == 2
    assert [case.grid_shape for case in cases] == [(16, 16), (32, 32)]
    assert all(case.steps > 0 for case in cases)


def test_steps_increase_with_grid_refinement_for_fixed_decay() -> None:
    coarse_steps = steps_for_decay_exponent((16, 16), 0.8)
    fine_steps = steps_for_decay_exponent((32, 32), 0.8)

    assert fine_steps > coarse_steps


def test_observed_order_on_synthetic_second_order_data() -> None:
    order = observed_order(
        coarse_spacing=0.5,
        fine_spacing=0.25,
        coarse_error=0.25,
        fine_error=0.0625,
    )

    assert order == pytest.approx(2.0)


def test_attach_observed_orders_on_synthetic_records() -> None:
    coarse = _synthetic_record((16, 16), velocity_error=4.0)
    fine = _synthetic_record((32, 32), velocity_error=1.0)

    records = attach_observed_orders([coarse, fine])

    assert len(records) == 2
    assert records[0].velocity_observed_order is None
    assert records[1].velocity_observed_order == pytest.approx(2.0)
    assert all(record.validation_status == STATUS_PASSED for record in records)
    assert all(record.passed_for_quantum_followup for record in records)


def test_assessment_marks_negative_order_for_investigation() -> None:
    coarse = _synthetic_record((16, 16), velocity_error=1.0)
    fine = _synthetic_record((32, 32), velocity_error=2.0)

    records = attach_observed_orders([coarse, fine])
    assessment = assess_d2q9_diagnostics(records)

    assert assessment.validation_status == STATUS_INVESTIGATION_REQUIRED
    assert assessment.validation_blocker == "velocity_error_increases_under_refinement"
    assert not assessment.passed_for_quantum_followup


def test_assessment_marks_unstable_or_nonfinite_as_failed() -> None:
    coarse = _synthetic_record((16, 16), velocity_error=1.0)
    fine = _synthetic_record((32, 32), velocity_error=float("nan"), stable=False)

    records = attach_observed_orders([coarse, fine])
    assessment = assess_d2q9_diagnostics(records)

    assert assessment.validation_status == STATUS_FAILED
    assert assessment.validation_blocker == "unstable_or_nonfinite_case"


def test_tiny_diagnostics_run_has_finite_metrics() -> None:
    records = run_d2q9_diagnostics(
        [
            D2Q9DiagnosticCase(
                grid_shape=(8, 8),
                tau=0.8,
                steps=4,
                amplitude=0.02,
            ),
            D2Q9DiagnosticCase(
                grid_shape=(16, 16),
                tau=0.8,
                steps=8,
                amplitude=0.02,
            ),
        ]
    )

    assert len(records) == 2
    assert records[0].velocity_observed_order is None
    assert records[1].velocity_observed_order is not None
    for record in records:
        assert record.velocity_relative_l2_error >= 0.0
        assert record.vorticity_relative_l2_error >= 0.0
        assert record.kinetic_energy_relative_error >= 0.0
        assert record.max_mach < 0.1
        assert record.stable
        assert record.validation_status in {
            STATUS_PASSED,
            STATUS_INVESTIGATION_REQUIRED,
            STATUS_FAILED,
        }


def test_write_diagnostics_csv_round_trip(tmp_path) -> None:
    records = run_d2q9_diagnostics(
        [
            D2Q9DiagnosticCase(
                grid_shape=(8, 8),
                tau=0.8,
                steps=4,
                amplitude=0.02,
            )
        ]
    )

    output_path = write_d2q9_diagnostics_csv(records, tmp_path / "diagnostics.csv")

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == D2Q9_DIAGNOSTIC_CSV_COLUMNS
    assert rows[0]["model"] == "D2Q9"
    assert rows[0]["grid_shape"] == "8x8"


def _synthetic_record(
    grid_shape: tuple[int, int],
    *,
    velocity_error: float,
    stable: bool = True,
) -> D2Q9DiagnosticRecord:
    spacing = 1.0 / max(grid_shape)
    return D2Q9DiagnosticRecord(
        model="D2Q9",
        grid_shape=grid_shape,
        grid_points=grid_shape[0] * grid_shape[1],
        grid_spacing=spacing,
        steps=1,
        tau=0.8,
        amplitude=0.02,
        target_decay_exponent=0.1,
        actual_decay_exponent=0.1,
        velocity_relative_l2_error=velocity_error,
        velocity_observed_order=None,
        vorticity_relative_l2_error=velocity_error,
        vorticity_observed_order=None,
        kinetic_energy_relative_error=velocity_error,
        kinetic_energy_observed_order=None,
        divergence_rms=0.0,
        max_mach=0.01,
        max_density_deviation=0.0,
        mass_drift_relative=0.0,
        runtime_seconds=0.0,
        stable=stable,
    )
