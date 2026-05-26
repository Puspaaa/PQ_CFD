import csv

import pytest

from pq_cfd import d2q9_order_cases, run_d2q9_order_study, write_d2q9_order_csv
from pq_cfd.d2q9_order import (
    D2Q9_ORDER_CSV_COLUMNS,
    ORDER_STATUS_FAILED,
    ORDER_STATUS_INVESTIGATION_REQUIRED,
    ORDER_STATUS_PASSED,
    attach_observed_orders,
    assess_order_records,
    observed_order,
)
from pq_cfd.d2q9_validation import D2Q9ValidationCase, D2Q9ValidationRecord


def test_d2q9_order_case_generation() -> None:
    cases = d2q9_order_cases(
        grids=((16, 16), (32, 32)),
        tau_values=(0.8,),
        amplitude=0.02,
    )

    assert len(cases) == 2
    assert all(case.steps > 0 for case in cases)
    assert [case.grid_shape for case in cases] == [(16, 16), (32, 32)]


def test_observed_order_on_synthetic_second_order_data() -> None:
    order = observed_order(
        coarse_spacing=0.5,
        fine_spacing=0.25,
        coarse_error=0.25,
        fine_error=0.0625,
    )

    assert order == pytest.approx(2.0)


def test_attach_observed_orders_on_synthetic_records() -> None:
    coarse = _synthetic_validation_record((16, 16), velocity_error=4.0)
    fine = _synthetic_validation_record((32, 32), velocity_error=1.0)

    records = attach_observed_orders([coarse, fine])

    assert len(records) == 2
    assert records[0].velocity_observed_order is None
    assert records[1].velocity_observed_order == pytest.approx(2.0)
    assert all(record.validation_status == ORDER_STATUS_PASSED for record in records)
    assert all(record.passed_for_quantum_followup for record in records)


def test_order_assessment_marks_negative_order_for_investigation() -> None:
    coarse = _synthetic_validation_record((16, 16), velocity_error=1.0)
    fine = _synthetic_validation_record((32, 32), velocity_error=2.0)

    records = attach_observed_orders([coarse, fine])
    assessment = assess_order_records(records)

    assert assessment.validation_status == ORDER_STATUS_INVESTIGATION_REQUIRED
    assert assessment.validation_blocker == "velocity_error_increases_under_refinement"
    assert not assessment.passed_for_quantum_followup


def test_order_assessment_marks_unstable_or_nonfinite_as_failed() -> None:
    coarse = _synthetic_validation_record((16, 16), velocity_error=1.0)
    fine = _synthetic_validation_record(
        (32, 32),
        velocity_error=float("nan"),
        stable=False,
    )

    records = attach_observed_orders([coarse, fine])
    assessment = assess_order_records(records)

    assert assessment.validation_status == ORDER_STATUS_FAILED
    assert assessment.validation_blocker == "unstable_or_nonfinite_case"


def test_tiny_order_study_has_finite_metrics() -> None:
    records = run_d2q9_order_study(
        [
            D2Q9ValidationCase(
                grid_shape=(8, 8),
                tau=0.8,
                steps=4,
                amplitude=0.02,
            ),
            D2Q9ValidationCase(
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
            ORDER_STATUS_PASSED,
            ORDER_STATUS_INVESTIGATION_REQUIRED,
            ORDER_STATUS_FAILED,
        }


def test_default_order_study_surfaces_negative_order_blocker_if_present() -> None:
    records = run_d2q9_order_study(d2q9_order_cases())

    negative_order_present = any(
        record.velocity_observed_order is not None
        and record.velocity_observed_order < 0.0
        for record in records
    )
    if negative_order_present:
        assert any(
            record.validation_status == ORDER_STATUS_INVESTIGATION_REQUIRED
            for record in records
        )
        assert not any(record.passed_for_quantum_followup for record in records)


def test_write_d2q9_order_csv_round_trip(tmp_path) -> None:
    records = run_d2q9_order_study(
        [
            D2Q9ValidationCase(
                grid_shape=(8, 8),
                tau=0.8,
                steps=4,
                amplitude=0.02,
            )
        ]
    )

    output_path = write_d2q9_order_csv(records, tmp_path / "order.csv")

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == D2Q9_ORDER_CSV_COLUMNS
    assert rows[0]["model"] == "D2Q9"
    assert rows[0]["grid_shape"] == "8x8"


def _synthetic_validation_record(
    grid_shape: tuple[int, int],
    *,
    velocity_error: float,
    stable: bool = True,
) -> D2Q9ValidationRecord:
    return D2Q9ValidationRecord(
        model="D2Q9",
        grid_shape=grid_shape,
        grid_points=grid_shape[0] * grid_shape[1],
        steps=1,
        tau=0.8,
        amplitude=0.02,
        initial_condition="taylor_green",
        grid_spacing_x=1.0 / grid_shape[0],
        grid_spacing_y=1.0 / grid_shape[1],
        target_decay_exponent=0.1,
        actual_decay_exponent=0.1,
        velocity_relative_l2_error=velocity_error,
        vorticity_relative_l2_error=velocity_error,
        kinetic_energy=1.0,
        expected_kinetic_energy=1.0,
        kinetic_energy_relative_error=velocity_error,
        density_weighted_kinetic_energy=1.0,
        incompressible_kinetic_energy=1.0,
        expected_incompressible_kinetic_energy=1.0,
        incompressible_kinetic_energy_relative_error=velocity_error,
        divergence_l2_norm=0.0,
        divergence_rms=0.0,
        max_mach=0.01,
        min_density=1.0,
        max_density_deviation=0.0,
        mass_drift_absolute=0.0,
        mass_drift_relative=0.0,
        runtime_seconds=0.0,
        stable=stable,
    )
