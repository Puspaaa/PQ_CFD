import numpy as np
from scipy import sparse

import pq_cfd
from pq_cfd import _qre2_shifted as qre2
from pq_cfd import _qre2_sparse as qre2_sparse
from pq_cfd.d2q9 import D2Q9_C, D2Q9_W


def test_qre2_sparse_streaming_matches_dense_periodic_permutation() -> None:
    spatial_shape = (2, 3)
    dense_streaming = qre2.build_streaming_matrix(spatial_shape)
    sparse_streaming = qre2_sparse.build_sparse_streaming_matrix(spatial_shape)

    assert sparse.issparse(sparse_streaming)
    assert sparse_streaming.shape == dense_streaming.shape
    assert sparse_streaming.nnz == dense_streaming.shape[0]
    assert np.allclose(sparse_streaming.toarray(), dense_streaming)


def test_qre2_sparse_collision_terms_match_dense_terms() -> None:
    spatial_shape = (2, 2)
    tau_bar = 0.83
    dense_f1, dense_f2 = qre2.build_shifted_collision_terms(tau_bar, spatial_shape)
    sparse_f1, sparse_f2 = qre2_sparse.build_sparse_shifted_collision_terms(
        tau_bar,
        spatial_shape,
    )

    assert sparse.issparse(sparse_f1)
    assert sparse.issparse(sparse_f2)
    assert sparse_f1.shape == dense_f1.shape
    assert sparse_f2.shape == dense_f2.shape
    assert np.allclose(sparse_f1.toarray(), dense_f1)
    assert np.allclose(sparse_f2.toarray(), dense_f2)


def test_qre2_sparse_update_matches_direct_one_step() -> None:
    spatial_shape = (2, 2)
    tau_bar = 0.83
    g = _small_shifted_state(spatial_shape)
    sparse_f1, sparse_f2 = qre2_sparse.build_sparse_shifted_collision_terms(
        tau_bar,
        spatial_shape,
    )
    sparse_streaming = qre2_sparse.build_sparse_streaming_matrix(spatial_shape)

    direct = qre2.step_shifted_direct(g, tau_bar)
    sparse_vector = qre2_sparse.step_shifted_sparse(
        qre2.flatten_site_major(g),
        sparse_streaming,
        sparse_f1,
        sparse_f2,
    )
    sparse_result = qre2.unflatten_site_major(sparse_vector, spatial_shape)

    assert np.allclose(sparse_result, direct, atol=1e-12)


def test_qre2_sparse_update_matches_direct_short_trajectory() -> None:
    spatial_shape = (2, 2)
    tau_bar = 0.91
    sparse_f1, sparse_f2 = qre2_sparse.build_sparse_shifted_collision_terms(
        tau_bar,
        spatial_shape,
    )
    sparse_streaming = qre2_sparse.build_sparse_streaming_matrix(spatial_shape)
    direct = _small_shifted_state(spatial_shape)
    sparse_vector = qre2.flatten_site_major(direct)

    for _ in range(4):
        direct = qre2.step_shifted_direct(direct, tau_bar)
        sparse_vector = qre2_sparse.step_shifted_sparse(
            sparse_vector,
            sparse_streaming,
            sparse_f1,
            sparse_f2,
        )

    sparse_result = qre2.unflatten_site_major(sparse_vector, spatial_shape)
    assert np.allclose(sparse_result, direct, atol=1e-12)


def test_qre2_sparse_helpers_stay_private() -> None:
    assert "_qre2_sparse" not in pq_cfd.__all__
    assert not hasattr(pq_cfd, "build_sparse_streaming_matrix")


def _small_shifted_state(spatial_shape: tuple[int, int]) -> np.ndarray:
    nx, ny = spatial_shape
    x = np.arange(nx, dtype=float)[:, None]
    y = np.arange(ny, dtype=float)[None, :]
    delta_rho = 0.01 * np.cos(2.0 * np.pi * (x + y) / (nx + ny))
    velocity = np.zeros((2, nx, ny))
    velocity[0] = 0.02 * np.sin(2.0 * np.pi * (x + 1.0) / (nx + 1.0))
    velocity[1] = -0.015 * np.cos(2.0 * np.pi * (y + 1.0) / (ny + 1.0))
    return _explicit_qre2_equilibrium(delta_rho, velocity)


def _explicit_qre2_equilibrium(delta_rho: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    equilibrium = np.empty((9, *delta_rho.shape))
    speed_squared = velocity[0] ** 2 + velocity[1] ** 2
    for index, (cx, cy) in enumerate(D2Q9_C):
        c_dot_u = cx * velocity[0] + cy * velocity[1]
        equilibrium[index] = D2Q9_W[index] * (
            delta_rho + 3.0 * c_dot_u + 4.5 * c_dot_u**2 - 1.5 * speed_squared
        )
    return equilibrium
