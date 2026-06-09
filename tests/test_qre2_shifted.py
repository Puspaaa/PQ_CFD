import numpy as np

import pq_cfd
from pq_cfd import SimulationConfig, run_d2q9
from pq_cfd import _qre2_shifted as qre2
from pq_cfd.d2q9 import _initial_taylor_green, analytic_taylor_green_velocity
from pq_cfd.d2q9 import D2Q9_C, D2Q9_W
from pq_cfd.d2q9_diagnostics import max_mach_number
from pq_cfd.metrics import relative_l2_error


def test_qre2_shift_unshift_roundtrip_preserves_d2q9_layout() -> None:
    spatial_shape = (2, 3)
    delta_rho = np.full(spatial_shape, 0.01)
    velocity = np.zeros((2, *spatial_shape))
    velocity[0] = [[0.02, -0.01, 0.00], [0.01, -0.02, 0.03]]
    velocity[1] = [[0.01, 0.02, -0.01], [0.00, 0.01, -0.02]]
    g = qre2.shifted_equilibrium_from_moments(delta_rho, velocity)

    f_bar = qre2.unshift_to_fbar(g)
    recovered = qre2.shift_to_g(f_bar)

    assert f_bar.shape == (9, *spatial_shape)
    assert np.allclose(recovered, g)


def test_qre2_shifted_moments_recover_density_fluctuation_and_velocity() -> None:
    delta_rho = np.array([[0.01, -0.02, 0.00], [0.03, -0.01, 0.02]])
    velocity = np.zeros((2, *delta_rho.shape))
    velocity[0] = [[0.02, -0.01, 0.00], [0.01, -0.02, 0.03]]
    velocity[1] = [[0.01, 0.02, -0.01], [0.00, 0.01, -0.02]]
    g = _linear_shifted_state(delta_rho, velocity)

    recovered_delta, recovered_velocity = qre2.shifted_moments(g)

    assert np.allclose(recovered_delta, delta_rho, atol=1e-15)
    assert np.allclose(recovered_velocity, velocity, atol=1e-15)


def test_qre2_shifted_equilibrium_matches_explicit_paper_formula() -> None:
    delta_rho = np.array([[0.01, -0.02], [0.00, 0.03]])
    velocity = np.zeros((2, *delta_rho.shape))
    velocity[0] = [[0.02, -0.01], [0.01, 0.00]]
    velocity[1] = [[0.01, 0.02], [-0.01, 0.03]]
    g = _linear_shifted_state(delta_rho, velocity)

    actual = qre2.shifted_equilibrium(g)
    expected = _explicit_qre2_equilibrium(delta_rho, velocity)

    assert np.allclose(actual, expected, atol=1e-15)
    equilibrium_delta, equilibrium_velocity = qre2.shifted_moments(actual)
    assert np.allclose(equilibrium_delta, delta_rho, atol=1e-15)
    assert np.allclose(equilibrium_velocity, velocity, atol=1e-15)


def test_qre2_streaming_matrix_is_periodic_permutation() -> None:
    spatial_shape = (2, 3)
    rng = np.random.default_rng(7)
    g = rng.normal(scale=0.02, size=(9, *spatial_shape))

    streaming = qre2.build_streaming_matrix(spatial_shape)
    streamed_vector = streaming @ qre2.flatten_site_major(g)
    streamed = qre2.unflatten_site_major(streamed_vector, spatial_shape)

    assert streaming.shape == (54, 54)
    assert np.allclose(streaming.T @ streaming, np.eye(54))
    assert np.allclose(streamed, _manual_stream_periodic(g))


def test_qre2_polynomial_matrix_update_matches_direct_one_step() -> None:
    spatial_shape = (2, 2)
    tau_bar = 0.83
    g = _small_shifted_state(spatial_shape)
    f1, f2 = qre2.build_shifted_collision_terms(tau_bar, spatial_shape)
    streaming = qre2.build_streaming_matrix(spatial_shape)

    direct = qre2.step_shifted_direct(g, tau_bar)
    matrix = qre2.unflatten_site_major(
        qre2.step_shifted_matrix(qre2.flatten_site_major(g), streaming, f1, f2),
        spatial_shape,
    )

    assert f1.shape == (36, 36)
    assert f2.shape == (36, 36 * 36)
    assert np.allclose(matrix, direct, atol=1e-12)


def test_qre2_polynomial_matrix_trajectory_matches_direct_steps() -> None:
    spatial_shape = (2, 2)
    tau_bar = 0.91
    f1, f2 = qre2.build_shifted_collision_terms(tau_bar, spatial_shape)
    streaming = qre2.build_streaming_matrix(spatial_shape)
    direct = _small_shifted_state(spatial_shape)
    matrix_vector = qre2.flatten_site_major(direct)

    for _ in range(4):
        direct = qre2.step_shifted_direct(direct, tau_bar)
        matrix_vector = qre2.step_shifted_matrix(matrix_vector, streaming, f1, f2)

    matrix = qre2.unflatten_site_major(matrix_vector, spatial_shape)
    assert np.allclose(matrix, direct, atol=1e-12)


def test_qre2_global_f2_only_couples_same_site_pairs() -> None:
    spatial_shape = (2, 2)
    _, f2 = qre2.build_shifted_collision_terms(tau_bar=0.8, spatial_shape=spatial_shape)
    dimension = spatial_shape[0] * spatial_shape[1] * 9
    rows, cols = np.nonzero(f2)

    row_sites = rows // 9
    first_factor_sites = (cols // dimension) // 9
    second_factor_sites = (cols % dimension) // 9

    assert rows.size > 0
    assert np.all(row_sites == first_factor_sites)
    assert np.all(row_sites == second_factor_sites)


def test_qre2_shifted_taylor_green_zero_step_recovers_initial_moments() -> None:
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=0,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=1,
        amplitude=0.02,
        base_density=1.0,
    )

    result = qre2.run_shifted_taylor_green(config)
    expected_density, expected_velocity = _initial_taylor_green(config, 8, 8)
    shifted_delta, shifted_velocity = qre2.shifted_moments(result.distributions)

    assert result.model == "QRE2-shifted-D2Q9"
    assert result.density.shape == (8, 8)
    assert result.velocity.shape == (2, 8, 8)
    assert result.distributions.shape == (9, 8, 8)
    assert result.history.steps == (0,)
    assert np.allclose(result.density, expected_density, atol=1e-15)
    assert np.allclose(result.velocity, expected_velocity, atol=1e-15)
    assert np.allclose(1.0 + shifted_delta, expected_density, atol=1e-15)
    assert np.allclose(shifted_velocity, expected_velocity, atol=1e-15)


def test_qre2_shifted_taylor_green_history_shapes_and_short_run_metrics() -> None:
    config = SimulationConfig(
        grid_shape=(16, 16),
        steps=6,
        tau=0.85,
        initial_condition="taylor_green",
        sample_interval=3,
        amplitude=0.015,
        base_density=1.0,
    )

    result = qre2.run_shifted_taylor_green(config)

    assert result.density.shape == (16, 16)
    assert result.velocity.shape == (2, 16, 16)
    assert result.distributions.shape == (9, 16, 16)
    assert result.history.steps == (0, 3, 6)
    assert all(sample.shape == (16, 16) for sample in result.history.density)
    assert all(sample.shape == (2, 16, 16) for sample in result.history.velocity)
    assert np.isfinite(result.metrics["relative_l2_error_velocity"])
    assert np.isfinite(result.metrics["runtime_seconds"])
    assert result.metrics["mass_drift_relative"] < 1e-12
    assert result.metrics["viscosity"] == (1.0 / 3.0) * (config.tau - 0.5)


def test_qre2_shifted_taylor_green_keeps_private_api_private() -> None:
    assert "run_shifted_taylor_green" not in pq_cfd.__all__
    assert not hasattr(pq_cfd, "run_shifted_taylor_green")


def test_qre2_shifted_taylor_green_sweep_stays_finite_and_low_mach() -> None:
    for grid_shape in ((16, 16), (32, 32)):
        for tau in (0.7, 0.9):
            config = SimulationConfig(
                grid_shape=grid_shape,
                steps=10,
                tau=tau,
                initial_condition="taylor_green",
                sample_interval=None,
                amplitude=0.02,
                base_density=1.0,
            )
            classical = run_d2q9(config)
            shifted = qre2.run_shifted_taylor_green(config)
            expected_velocity = analytic_taylor_green_velocity(
                config,
                grid_shape[0],
                grid_shape[1],
                config.steps,
            )

            shifted_error = relative_l2_error(shifted.velocity, expected_velocity)
            classical_error = relative_l2_error(classical.velocity, expected_velocity)

            assert np.isfinite(shifted_error)
            assert np.isfinite(classical_error)
            assert abs(shifted_error - classical_error) < 1e-3
            assert max_mach_number(shifted.velocity) < 0.1
            assert shifted.metrics["mass_drift_relative"] < 1e-12


def _small_shifted_state(spatial_shape: tuple[int, int]) -> np.ndarray:
    nx, ny = spatial_shape
    x = np.arange(nx, dtype=float)[:, None]
    y = np.arange(ny, dtype=float)[None, :]
    delta_rho = 0.01 * np.cos(2.0 * np.pi * (x + y) / (nx + ny))
    velocity = np.zeros((2, nx, ny))
    velocity[0] = 0.02 * np.sin(2.0 * np.pi * (x + 1.0) / (nx + 1.0))
    velocity[1] = -0.015 * np.cos(2.0 * np.pi * (y + 1.0) / (ny + 1.0))
    return qre2.shifted_equilibrium_from_moments(delta_rho, velocity)


def _linear_shifted_state(delta_rho: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    g = np.empty((9, *delta_rho.shape))
    for index, (cx, cy) in enumerate(D2Q9_C):
        c_dot_u = cx * velocity[0] + cy * velocity[1]
        g[index] = D2Q9_W[index] * (delta_rho + 3.0 * c_dot_u)
    return g


def _explicit_qre2_equilibrium(delta_rho: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    equilibrium = np.empty((9, *delta_rho.shape))
    speed_squared = velocity[0] ** 2 + velocity[1] ** 2
    for index, (cx, cy) in enumerate(D2Q9_C):
        c_dot_u = cx * velocity[0] + cy * velocity[1]
        equilibrium[index] = D2Q9_W[index] * (
            delta_rho + 3.0 * c_dot_u + 4.5 * c_dot_u**2 - 1.5 * speed_squared
        )
    return equilibrium


def _manual_stream_periodic(distributions: np.ndarray) -> np.ndarray:
    streamed = np.empty_like(distributions)
    for index, (cx, cy) in enumerate(D2Q9_C):
        streamed[index] = np.roll(
            distributions[index],
            shift=(int(cx), int(cy)),
            axis=(0, 1),
        )
    return streamed
