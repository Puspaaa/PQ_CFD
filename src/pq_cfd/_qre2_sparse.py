"""Private sparse QRE2 shifted-D2Q9 validation helpers.

Corpus IDs: QRE2, QRE4, IO4, IO5, IO7, IO8, PRIM14, PRIM15.

These helpers replay the tiny dense QRE2 shifted-D2Q9 validation objects with
SciPy sparse matrices. They are classical operator checks only: no circuit,
oracle, block-encoding, loading, readout, or resource claim is implemented here.
"""

from __future__ import annotations

from itertools import product

import numpy as np
from scipy import sparse

from pq_cfd import _qre2_shifted as qre2
from pq_cfd.d2q9 import D2Q9_C, D2Q9_W

SparseArray = sparse.sparray


def build_sparse_streaming_matrix(spatial_shape: tuple[int, int]) -> SparseArray:
    """Build sparse QRE2 periodic streaming permutation (`eq:streaming`)."""

    spatial_shape = qre2._validate_spatial_shape(spatial_shape)
    shape_array = np.asarray(spatial_shape, dtype=int)
    site_count = int(np.prod(spatial_shape))
    dimension = site_count * qre2.Q
    rows: list[int] = []
    cols: list[int] = []

    for position in product(*[range(length) for length in spatial_shape]):
        source_site = qre2._site_index(position, spatial_shape)
        position_array = np.asarray(position, dtype=int)
        for velocity_index, velocity in enumerate(D2Q9_C):
            destination = tuple((position_array + velocity) % shape_array)
            destination_site = qre2._site_index(destination, spatial_shape)
            cols.append(source_site * qre2.Q + velocity_index)
            rows.append(destination_site * qre2.Q + velocity_index)

    data = np.ones(len(rows), dtype=float)
    return sparse.coo_array((data, (rows, cols)), shape=(dimension, dimension)).tocsr()


def build_sparse_shifted_collision_terms(
    tau_bar: float, spatial_shape: tuple[int, int] | None = None
) -> tuple[SparseArray, SparseArray]:
    """Build sparse QRE2 `F1` and `F2` collision terms."""

    f1_local, f2_local = qre2.build_shifted_collision_terms(tau_bar)
    f1_local_sparse = sparse.csr_array(f1_local)
    f2_local_sparse = sparse.csr_array(f2_local)

    if spatial_shape is None:
        return f1_local_sparse, f2_local_sparse

    spatial_shape = qre2._validate_spatial_shape(spatial_shape)
    site_count = int(np.prod(spatial_shape))
    dimension = site_count * qre2.Q
    f1 = sparse.kron(
        sparse.eye_array(site_count, format="csr"),
        f1_local_sparse,
        format="csr",
    )

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    local_rows, local_cols = np.nonzero(f2_local)
    for site in range(site_count):
        for local_row, local_col in zip(local_rows, local_cols, strict=True):
            m1, m2 = divmod(int(local_col), qre2.Q)
            rows.append(site * qre2.Q + int(local_row))
            cols.append((site * qre2.Q + m1) * dimension + (site * qre2.Q + m2))
            data.append(float(f2_local[local_row, local_col]))

    f2 = sparse.coo_array((data, (rows, cols)), shape=(dimension, dimension * dimension))
    return f1.tocsr(), f2.tocsr()


def step_shifted_sparse(
    g_vector: np.ndarray,
    streaming: SparseArray,
    f1: SparseArray,
    f2: SparseArray,
) -> np.ndarray:
    """Apply the sparse QRE2 polynomial update from `eq:LBE_col_shift_matrix`."""

    g_vector = np.asarray(g_vector)
    if g_vector.ndim != 1:
        raise ValueError(f"g_vector must be one-dimensional; got {g_vector.shape}")
    dimension = g_vector.shape[0]
    _validate_sparse_shape(streaming, (dimension, dimension), "streaming")
    _validate_sparse_shape(f1, (dimension, dimension), "f1")
    _validate_sparse_shape(f2, (dimension, dimension * dimension), "f2")

    quadratic = np.kron(g_vector, g_vector)
    collision = g_vector + f1 @ g_vector + f2 @ quadratic
    return np.asarray(streaming @ collision).reshape(-1)


def _validate_sparse_shape(matrix: SparseArray, shape: tuple[int, int], name: str) -> None:
    if not sparse.issparse(matrix):
        raise TypeError(f"{name} must be a SciPy sparse array; got {type(matrix)!r}")
    if matrix.shape != shape:
        raise ValueError(f"{name} must have shape {shape}; got {matrix.shape}")
