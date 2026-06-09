import numpy as np
import pytest

import pq_cfd
from pq_cfd import _qre2_carleman as carleman
from pq_cfd import _qre2_shifted as qre2


def test_qre2_carleman_block_dimensions_and_dense_shapes() -> None:
    """Corpus IDs: QRE2, CAR7."""

    dimension = 3
    f1 = np.zeros((dimension, dimension))
    f2 = np.zeros((dimension, dimension * dimension))
    streaming = np.eye(dimension)

    assert carleman.carleman_block_dimensions(dimension, order=1) == (3,)
    assert carleman.carleman_block_dimensions(dimension, order=2) == (3, 9)
    assert carleman.carleman_dimension(dimension, order=2) == 12

    collision_1 = carleman.build_carleman_collision(f1, f2, order=1)
    collision_2 = carleman.build_carleman_collision(f1, f2, order=2)
    streaming_2 = carleman.build_carleman_streaming(streaming, order=2)
    propagator_2 = carleman.build_carleman_propagator(
        streaming, f1, f2, order=2
    )

    assert collision_1.shape == (3, 3)
    assert collision_2.shape == (12, 12)
    assert streaming_2.shape == (12, 12)
    assert propagator_2.shape == (12, 12)


def test_qre2_carleman_lift_uses_qre2_f2_tensor_ordering() -> None:
    """Corpus IDs: QRE2, IO1, CAR15."""

    g_vector = np.array([1.0, 2.0, 3.0])
    lifted = carleman.lift_shifted_state(g_vector, order=2)

    assert np.allclose(lifted[:3], g_vector)
    assert np.allclose(lifted[3:], np.kron(g_vector, g_vector))


def test_qre2_carleman_nc2_first_block_matches_one_shifted_step() -> None:
    """Corpus IDs: QRE2, CAR7."""

    spatial_shape = (2, 2)
    tau_bar = 0.83
    g_vector = qre2.flatten_site_major(_small_shifted_state(spatial_shape))
    f1, f2 = qre2.build_shifted_collision_terms(tau_bar, spatial_shape)
    streaming = qre2.build_streaming_matrix(spatial_shape)
    propagator = carleman.build_carleman_propagator(
        streaming, f1, f2, order=2
    )

    lifted_next = propagator @ carleman.lift_shifted_state(g_vector, order=2)
    actual = carleman.extract_first_block(lifted_next, g_vector.size)
    expected = qre2.step_shifted_matrix(g_vector, streaming, f1, f2)

    assert np.allclose(actual, expected, atol=1e-12)


def test_qre2_carleman_nc2_short_run_improves_over_nc1_baseline() -> None:
    """Corpus IDs: QRE2, CAR7, CAR9, CAR19."""

    spatial_shape = (1, 3)
    tau_bar = 0.83
    steps = 6
    initial = qre2.flatten_site_major(_small_shifted_state(spatial_shape))
    f1, f2 = qre2.build_shifted_collision_terms(tau_bar, spatial_shape)
    streaming = qre2.build_streaming_matrix(spatial_shape)

    nc1_error = _first_block_error(initial, streaming, f1, f2, order=1, steps=steps)
    nc2_error = _first_block_error(initial, streaming, f1, f2, order=2, steps=steps)

    assert np.isfinite(nc1_error)
    assert np.isfinite(nc2_error)
    assert nc2_error < nc1_error
    assert nc2_error < 1e-2


def test_qre2_carleman_dense_dimension_guard_rejects_oversized_lifts() -> None:
    """Corpus IDs: QRE2, IO1, CAR15."""

    dimension = 12
    f1 = np.zeros((dimension, dimension))
    f2 = np.zeros((dimension, dimension * dimension))
    streaming = np.eye(dimension)

    with pytest.raises(ValueError, match="refused dimension"):
        carleman.build_carleman_collision(
            f1, f2, order=2, max_dimension=dimension
        )
    with pytest.raises(ValueError, match="refused dimension"):
        carleman.build_carleman_streaming(
            streaming, order=2, max_dimension=dimension
        )
    with pytest.raises(ValueError, match="refused dimension"):
        carleman.build_carleman_propagator(
            streaming, f1, f2, order=2, max_dimension=dimension
        )


def test_qre2_carleman_scope_and_public_api_stay_private() -> None:
    """Corpus IDs: QRE2, IO4, IO5, IO7, IO8."""

    with pytest.raises(ValueError, match="N_C=1 and N_C=2"):
        carleman.carleman_dimension(3, order=3)

    assert "_qre2_carleman" not in pq_cfd.__all__
    assert "build_carleman_propagator" not in pq_cfd.__all__
    assert not hasattr(pq_cfd, "build_carleman_propagator")


def _first_block_error(
    initial: np.ndarray,
    streaming: np.ndarray,
    f1: np.ndarray,
    f2: np.ndarray,
    *,
    order: int,
    steps: int,
) -> float:
    direct = initial.copy()
    lifted = carleman.lift_shifted_state(initial, order=order)
    propagator = carleman.build_carleman_propagator(
        streaming, f1, f2, order=order
    )
    for _ in range(steps):
        direct = qre2.step_shifted_matrix(direct, streaming, f1, f2)
        lifted = propagator @ lifted
    approximate = carleman.extract_first_block(lifted, initial.size)
    return float(np.linalg.norm(approximate - direct) / np.linalg.norm(direct))


def _small_shifted_state(spatial_shape: tuple[int, int]) -> np.ndarray:
    nx, ny = spatial_shape
    x = np.arange(nx, dtype=float)[:, None]
    y = np.arange(ny, dtype=float)[None, :]
    delta_rho = 0.01 * np.cos(2.0 * np.pi * (x + y) / (nx + ny))
    velocity = np.zeros((2, nx, ny))
    velocity[0] = 0.02 * np.sin(2.0 * np.pi * (x + 1.0) / (nx + 1.0))
    velocity[1] = -0.015 * np.cos(2.0 * np.pi * (y + 1.0) / (ny + 1.0))
    return qre2.shifted_equilibrium_from_moments(delta_rho, velocity)
