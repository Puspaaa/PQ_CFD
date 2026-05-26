import csv

import numpy as np

from pq_cfd import d2q9_validation_cases, run_d2q9_validation, write_d2q9_validation_csv
from pq_cfd.d2q9_validation import (
    D2Q9_VALIDATION_CSV_COLUMNS,
    D2Q9ValidationCase,
    grid_spacings,
    normalized_l2_norm,
    periodic_divergence,
    periodic_vorticity,
    steps_for_decay_exponent,
)


def test_validation_case_generation_count_and_steps() -> None:
    cases = d2q9_validation_cases(
        grids=((16, 16), (32, 32)),
        tau_values=(0.6, 0.8),
        amplitude=0.02,
    )

    assert len(cases) == 4
    assert all(case.steps > 0 for case in cases)


def test_steps_increase_with_grid_refinement_for_fixed_tau() -> None:
    coarse = steps_for_decay_exponent((16, 16), 0.8)
    medium = steps_for_decay_exponent((32, 32), 0.8)
    fine = steps_for_decay_exponent((64, 64), 0.8)

    assert coarse < medium < fine


def test_periodic_vorticity_and_divergence_shapes_and_finite_values() -> None:
    x = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)[:, None]
    y = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)[None, :]
    velocity = np.stack((np.sin(x) * np.cos(y), -np.cos(x) * np.sin(y)), axis=0)

    spacing = grid_spacings((16, 16))
    vorticity = periodic_vorticity(velocity, spacing=spacing)
    divergence = periodic_divergence(velocity, spacing=spacing)

    assert vorticity.shape == (16, 16)
    assert divergence.shape == (16, 16)
    assert np.all(np.isfinite(vorticity))
    assert np.all(np.isfinite(divergence))
    assert normalized_l2_norm(divergence) >= 0.0


def test_grid_scaled_derivatives_change_with_spacing() -> None:
    x = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)[:, None]
    y = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)[None, :]
    velocity = np.stack((np.sin(x) * np.cos(y), -np.cos(x) * np.sin(y)), axis=0)

    lattice_vorticity = periodic_vorticity(velocity)
    scaled_vorticity = periodic_vorticity(velocity, spacing=grid_spacings((16, 16)))

    assert np.linalg.norm(scaled_vorticity) > np.linalg.norm(lattice_vorticity)


def test_d2q9_validation_record_fields_and_finite_metrics() -> None:
    records = run_d2q9_validation(
        [
            D2Q9ValidationCase(
                grid_shape=(16, 16),
                tau=0.8,
                steps=8,
                amplitude=0.02,
            )
        ]
    )

    assert len(records) == 1
    record = records[0]
    row = record.as_dict()

    assert tuple(row.keys()) == D2Q9_VALIDATION_CSV_COLUMNS
    assert record.model == "D2Q9"
    assert record.velocity_relative_l2_error >= 0.0
    assert record.vorticity_relative_l2_error >= 0.0
    assert record.kinetic_energy > 0.0
    assert record.expected_kinetic_energy > 0.0
    assert record.kinetic_energy_relative_error >= 0.0
    assert record.grid_spacing_x > 0.0
    assert record.grid_spacing_y > 0.0
    assert record.density_weighted_kinetic_energy > 0.0
    assert record.incompressible_kinetic_energy > 0.0
    assert record.expected_incompressible_kinetic_energy > 0.0
    assert record.incompressible_kinetic_energy_relative_error >= 0.0
    assert record.divergence_l2_norm >= 0.0
    assert record.divergence_rms >= 0.0
    assert record.max_mach < 0.1
    assert record.min_density > 0.0
    assert record.stable


def test_write_d2q9_validation_csv_round_trip(tmp_path) -> None:
    records = run_d2q9_validation(
        [
            D2Q9ValidationCase(
                grid_shape=(8, 8),
                tau=0.8,
                steps=4,
                amplitude=0.02,
            )
        ]
    )

    output_path = write_d2q9_validation_csv(records, tmp_path / "validation.csv")

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == D2Q9_VALIDATION_CSV_COLUMNS
    assert rows[0]["model"] == "D2Q9"
    assert rows[0]["grid_shape"] == "8x8"
