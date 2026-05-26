import csv

from pq_cfd import (
    SCHEME_COMPARISON_CSV_COLUMNS,
    controlled_decay_scheme_comparison_cases,
    default_scheme_comparison_cases,
    run_scheme_comparison,
    write_scheme_comparison_csv,
)
from pq_cfd.d2q9_order import (
    ORDER_STATUS_FAILED,
    ORDER_STATUS_INVESTIGATION_REQUIRED,
    ORDER_STATUS_PASSED,
)


def test_scheme_comparison_runs_first_wave_cases() -> None:
    cases = default_scheme_comparison_cases(
        grid_shape=(8, 8),
        steps=2,
        tau=0.8,
        amplitude=0.02,
    )
    records = run_scheme_comparison(cases)

    assert len(records) == 4
    assert {record.scheme for record in records} == {
        "bgk_srt",
        "barred_srt",
        "trt",
        "mrt",
    }
    for record in records:
        row = record.as_dict()
        assert tuple(row.keys()) == SCHEME_COMPARISON_CSV_COLUMNS
        assert record.velocity_relative_l2_error >= 0.0
        assert record.vorticity_relative_l2_error >= 0.0
        assert record.grid_spacing_x > 0.0
        assert record.grid_spacing_y > 0.0
        assert record.density_weighted_kinetic_energy > 0.0
        assert record.incompressible_kinetic_energy > 0.0
        assert record.expected_incompressible_kinetic_energy > 0.0
        assert record.kinetic_energy_relative_error >= 0.0
        assert record.incompressible_kinetic_energy_relative_error >= 0.0
        assert record.divergence_l2_norm >= 0.0
        assert record.divergence_rms >= 0.0
        assert record.max_mach < 0.1
        assert record.max_density_deviation >= 0.0
        assert record.stable
        assert record.stability_blocker == ""
        assert record.validation_status == ORDER_STATUS_INVESTIGATION_REQUIRED
        assert record.validation_blocker == "insufficient_refinement"


def test_write_scheme_comparison_csv_round_trip(tmp_path) -> None:
    records = run_scheme_comparison(
        default_scheme_comparison_cases(
            schemes=("bgk_srt",),
            grid_shape=(8, 8),
            steps=2,
            tau=0.8,
            amplitude=0.02,
        )
    )

    output = write_scheme_comparison_csv(records, tmp_path / "schemes.csv")

    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == SCHEME_COMPARISON_CSV_COLUMNS
    assert rows[0]["scheme"] == "bgk_srt"


def test_controlled_decay_scheme_comparison_produces_order_status_fields() -> None:
    records = run_scheme_comparison(
        controlled_decay_scheme_comparison_cases(
            schemes=("bgk_srt", "trt"),
            grids=((8, 8), (16, 16)),
            tau=0.8,
            amplitude=0.02,
        )
    )

    assert len(records) == 4
    for record in records:
        assert record.validation_status in {
            ORDER_STATUS_PASSED,
            ORDER_STATUS_INVESTIGATION_REQUIRED,
            ORDER_STATUS_FAILED,
        }
        assert record.validation_blocker != "not_assessed"
        assert record.max_density_deviation >= 0.0
        assert record.divergence_rms >= 0.0
    assert any(record.velocity_observed_order is not None for record in records)
