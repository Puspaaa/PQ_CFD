import csv

import pytest

from pq_cfd import (
    SweepCase,
    default_sweep_cases,
    run_sweep,
    write_sweep_csv,
)
from pq_cfd.analysis import SWEEP_CSV_COLUMNS


def test_run_sweep_record_count_and_required_fields() -> None:
    cases = [
        SweepCase(
            model="D1Q3",
            grid_shape=(32,),
            steps=16,
            tau=0.8,
            amplitude=0.02,
            initial_condition="sinusoidal",
        ),
        SweepCase(
            model="D2Q9",
            grid_shape=(16, 16),
            steps=8,
            tau=0.8,
            amplitude=0.02,
            initial_condition="taylor_green",
        ),
    ]

    records = run_sweep(cases)

    assert len(records) == len(cases)
    for record in records:
        row = record.as_dict()
        assert tuple(row.keys()) == SWEEP_CSV_COLUMNS
        assert row["model"] in {"D1Q3", "D2Q9"}
        assert row["grid_points"] > 0
        assert row["relative_error"] >= 0.0
        assert row["mass_drift_relative"] >= 0.0
        assert row["runtime_seconds"] >= 0.0


def test_write_sweep_csv_round_trip(tmp_path) -> None:
    records = run_sweep(
        [
            SweepCase(
                model="D1Q3",
                grid_shape=(16,),
                steps=8,
                tau=0.8,
                amplitude=0.02,
                initial_condition="sinusoidal",
            )
        ]
    )

    output_path = write_sweep_csv(records, tmp_path / "sweep.csv")

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == SWEEP_CSV_COLUMNS
    assert rows[0]["model"] == "D1Q3"
    assert rows[0]["grid_shape"] == "16"


def test_invalid_sweep_case_propagates_solver_validation() -> None:
    with pytest.raises(ValueError, match="tau > 0.5"):
        run_sweep(
            [
                SweepCase(
                    model="D1Q3",
                    grid_shape=(16,),
                    steps=8,
                    tau=0.5,
                    amplitude=0.02,
                    initial_condition="sinusoidal",
                )
            ]
        )


def test_small_default_sweep_cases_complete() -> None:
    cases = default_sweep_cases(
        d1_grids=(16,),
        d2_grids=((8, 8),),
        d1_tau_values=(0.8,),
        d2_tau_values=(0.8,),
        amplitude=0.02,
    )

    records = run_sweep(cases)

    assert len(records) == 2
    assert {record.model for record in records} == {"D1Q3", "D2Q9"}
