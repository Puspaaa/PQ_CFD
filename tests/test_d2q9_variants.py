import numpy as np
import pytest

from pq_cfd import (
    D2Q9_SCHEMES,
    SimulationConfig,
    barred_from_physical_distribution,
    collide_d2q9_local,
    d2q9_mrt_inverse_moment_matrix,
    d2q9_mrt_moment_matrix,
    d2q9_mrt_relaxation_rates,
    d2q9_opposite_indices,
    physical_from_barred_distribution,
    run_d2q9,
    run_d2q9_barred_srt,
    run_d2q9_mrt,
    run_d2q9_scheme,
    run_d2q9_trt,
    trt_odd_relaxation_rate,
)
from pq_cfd.d2q9 import D2Q9_C, _equilibrium, _initial_taylor_green, _macroscopic


def test_first_wave_d2q9_schemes_return_core_metrics() -> None:
    config = SimulationConfig(
        grid_shape=(16, 16),
        steps=8,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=None,
        amplitude=0.02,
    )

    for scheme in D2Q9_SCHEMES:
        result = run_d2q9_scheme(config, scheme)

        assert result.density.shape == (16, 16)
        assert result.velocity.shape == (2, 16, 16)
        assert result.distributions.shape == (9, 16, 16)
        assert result.metrics["mass_drift_relative"] < 1e-12
        assert result.metrics["relative_l2_error_velocity"] < 0.2
        assert np.all(np.isfinite(result.density))
        assert np.all(np.isfinite(result.velocity))


def test_named_d2q9_variant_runners_are_available() -> None:
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=2,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=None,
        amplitude=0.02,
    )

    assert run_d2q9_barred_srt(config).model == "D2Q9-BARRED_SRT"
    assert run_d2q9_trt(config).model == "D2Q9-TRT"
    assert run_d2q9_mrt(config).model == "D2Q9-MRT"


def test_barred_transform_preserves_equilibrium_initialization() -> None:
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=1,
        tau=0.8,
        initial_condition="taylor_green",
        amplitude=0.02,
    )
    density, velocity = _initial_taylor_green(config, 8, 8)
    equilibrium = _equilibrium(density, velocity)

    barred = barred_from_physical_distribution(
        equilibrium,
        density,
        velocity,
        config.tau,
    )
    recovered = physical_from_barred_distribution(
        barred,
        density,
        velocity,
        config.tau,
    )

    np.testing.assert_allclose(barred, equilibrium)
    np.testing.assert_allclose(recovered, equilibrium)


def test_barred_transform_reconstructs_non_equilibrium_populations() -> None:
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=1,
        tau=0.8,
        initial_condition="taylor_green",
        amplitude=0.02,
    )
    density, velocity = _initial_taylor_green(config, 8, 8)
    equilibrium = _equilibrium(density, velocity)
    hydrodynamic_null_mode = np.array(
        [0.0, 1.0, -1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0]
    )
    perturbation = 1e-4 * hydrodynamic_null_mode[:, None, None]
    physical = equilibrium + perturbation

    barred = barred_from_physical_distribution(
        physical,
        density,
        velocity,
        config.tau,
    )
    recovered = physical_from_barred_distribution(
        barred,
        density,
        velocity,
        config.tau,
    )

    assert not np.allclose(barred, physical)
    np.testing.assert_allclose(recovered, physical, atol=1e-15)
    np.testing.assert_allclose(np.sum(perturbation, axis=0), 0.0)
    np.testing.assert_allclose(
        np.sum(D2Q9_C[:, 0, None, None] * perturbation, axis=0),
        0.0,
    )
    np.testing.assert_allclose(
        np.sum(D2Q9_C[:, 1, None, None] * perturbation, axis=0),
        0.0,
    )


def test_barred_srt_matches_bgk_for_unforced_equilibrium_taylor_green() -> None:
    config = SimulationConfig(
        grid_shape=(16, 16),
        steps=10,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=None,
        amplitude=0.02,
    )

    bgk = run_d2q9(config)
    barred = run_d2q9_barred_srt(config)

    np.testing.assert_allclose(barred.density, bgk.density, atol=1e-14)
    np.testing.assert_allclose(barred.velocity, bgk.velocity, atol=1e-14)


def test_trt_odd_relaxation_rate_validation() -> None:
    assert 0.0 < trt_odd_relaxation_rate(0.8) < 2.0

    with pytest.raises(ValueError):
        trt_odd_relaxation_rate(0.5)


def test_local_collision_conserves_mass_and_momentum_for_all_schemes() -> None:
    rng = np.random.default_rng(123)
    density = np.ones((3, 4))
    velocity = np.zeros((2, 3, 4))
    distributions = _equilibrium(density, velocity) + 1e-5 * rng.normal(
        size=(9, 3, 4)
    )
    density, velocity = _macroscopic(distributions)
    initial_mass, initial_momentum_x, initial_momentum_y = _moments(distributions)

    for scheme in D2Q9_SCHEMES:
        post = collide_d2q9_local(
            distributions,
            density,
            velocity,
            tau=0.8,
            scheme=scheme,
        )
        mass, momentum_x, momentum_y = _moments(post)

        np.testing.assert_allclose(mass, initial_mass, atol=1e-14)
        np.testing.assert_allclose(momentum_x, initial_momentum_x, atol=1e-14)
        np.testing.assert_allclose(momentum_y, initial_momentum_y, atol=1e-14)


def test_trt_even_and_odd_modes_relax_by_configured_rates() -> None:
    density = np.ones((1, 1))
    velocity = np.zeros((2, 1, 1))
    equilibrium = _equilibrium(density, velocity)
    delta = np.array(
        [0.0, 0.02, -0.01, -0.03, 0.04, 0.01, -0.02, 0.03, -0.04]
    )[:, None, None]
    distributions = equilibrium + delta
    post = collide_d2q9_local(distributions, density, velocity, 0.8, "trt")
    opposite = d2q9_opposite_indices()

    even_delta = 0.5 * (delta + delta[opposite])
    odd_delta = 0.5 * (delta - delta[opposite])
    post_delta = post - equilibrium
    post_even = 0.5 * (post_delta + post_delta[opposite])
    post_odd = 0.5 * (post_delta - post_delta[opposite])

    np.testing.assert_allclose(post_even, (1.0 - 1.0 / 0.8) * even_delta)
    np.testing.assert_allclose(
        post_odd,
        (1.0 - trt_odd_relaxation_rate(0.8)) * odd_delta,
    )


def test_mrt_moment_transform_round_trip_and_nonconserved_relaxation() -> None:
    moment_matrix = d2q9_mrt_moment_matrix()
    inverse_matrix = d2q9_mrt_inverse_moment_matrix()
    np.testing.assert_allclose(inverse_matrix @ moment_matrix, np.eye(9), atol=1e-14)

    density = np.ones((1, 1))
    velocity = np.zeros((2, 1, 1))
    equilibrium = _equilibrium(density, velocity)
    moment_perturbation = np.array(
        [0.0, 0.02, -0.01, 0.0, 0.015, 0.0, -0.012, 0.01, -0.02]
    )
    distributions = equilibrium.copy()
    distributions[:, 0, 0] += inverse_matrix @ moment_perturbation
    post = collide_d2q9_local(distributions, density, velocity, 0.8, "mrt")

    moments = moment_matrix @ distributions[:, 0, 0]
    equilibrium_moments = moment_matrix @ equilibrium[:, 0, 0]
    post_moments = moment_matrix @ post[:, 0, 0]
    rates = d2q9_mrt_relaxation_rates(0.8)

    expected = moments - rates * (moments - equilibrium_moments)
    np.testing.assert_allclose(post_moments, expected, atol=1e-14)


def _moments(distributions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mass = np.sum(distributions, axis=0)
    momentum_x = np.sum(D2Q9_C[:, 0, None, None] * distributions, axis=0)
    momentum_y = np.sum(D2Q9_C[:, 1, None, None] * distributions, axis=0)
    return mass, momentum_x, momentum_y
