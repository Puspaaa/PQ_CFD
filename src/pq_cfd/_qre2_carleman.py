"""Private dense QRE2 discrete Carleman validation helpers.

Corpus IDs: QRE2, CAR7, IO1, CAR15, CAR9, CAR19, IO4, IO5, IO7, IO8.

This module implements only the tiny classical `N_C=1/2` validation objects for
the QRE2 shifted-D2Q9 polynomial map. The paper anchors are QRE2
`sec:discrete_carleman`, `eq:Ckl`, `eq:carl_evol_d`, and `eq:LBE_recurrence`.

The helpers are intentionally private and dense. They do not implement loading,
matrix oracles, block encodings, QLSA, measurement extraction, circuits, or
resource estimates.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np

SUPPORTED_ORDERS = {1, 2}
DEFAULT_MAX_DIMENSION = 2500


def carleman_block_dimensions(dimension: int, order: int) -> tuple[int, ...]:
    """Return dense direct-sum block sizes `(d, d**2)` through `N_C=2`.

    Corpus ID: QRE2 (`eq:carl_evol_d`).
    """

    dimension, order = _validate_dimension_order(dimension, order)
    return tuple(dimension**power for power in range(1, order + 1))


def carleman_dimension(dimension: int, order: int) -> int:
    """Return the total dense Carleman vector dimension through `N_C=2`.

    Corpus ID: QRE2 (`eq:carl_evol_d`).
    """

    return int(sum(carleman_block_dimensions(dimension, order)))


def lift_shifted_state(g_vector: np.ndarray, order: int) -> np.ndarray:
    """Return `y=[g, g tensor g]` through the requested supported order.

    Corpus ID: QRE2 (`eq:LBE_recurrence`). The tensor ordering follows
    `np.kron(g, g)`, matching the existing QRE2 dense `F2` column convention.
    """

    g_vector = _validate_vector(g_vector, name="g_vector")
    _validate_dimension_order(g_vector.size, order)
    return np.concatenate(
        [_kron_power_vector(g_vector, power) for power in range(1, order + 1)]
    )


def build_carleman_collision(
    f1: np.ndarray,
    f2: np.ndarray,
    order: int,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
) -> np.ndarray:
    """Build the dense truncated QRE2 Carleman collision matrix.

    Corpus ID: QRE2 (`eq:Ckl`). This is a tiny validation matrix only.
    """

    f1, f2 = _validate_collision_terms(f1, f2)
    dimension = f1.shape[0]
    order = _validate_order(order)
    slices = _guarded_block_slices(
        dimension,
        order,
        max_dimension=max_dimension,
        object_name="dense Carleman collision",
    )
    dtype = np.result_type(f1, f2, float)
    linear = np.eye(dimension, dtype=dtype) + f1
    total = slices[-1].stop
    collision = np.zeros((total, total), dtype=dtype)

    for row_order in range(1, order + 1):
        row_slice = slices[row_order - 1]
        for quadratic_count in range(0, min(row_order, order - row_order) + 1):
            col_order = row_order + quadratic_count
            col_slice = slices[col_order - 1]
            block = np.zeros(
                (dimension**row_order, dimension**col_order),
                dtype=dtype,
            )
            for quadratic_positions in combinations(
                range(row_order), quadratic_count
            ):
                factors = [
                    f2 if position in quadratic_positions else linear
                    for position in range(row_order)
                ]
                block += _kron_all_matrices(factors)
            collision[row_slice, col_slice] = block

    return collision


def build_carleman_streaming(
    streaming: np.ndarray,
    order: int,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
) -> np.ndarray:
    """Build the dense block-diagonal streaming lift `diag(S, S tensor S)`.

    Corpus ID: QRE2 (`eq:carl_evol_d`).
    """

    streaming = _validate_streaming(streaming)
    dimension = streaming.shape[0]
    order = _validate_order(order)
    slices = _guarded_block_slices(
        dimension,
        order,
        max_dimension=max_dimension,
        object_name="dense Carleman streaming",
    )
    dtype = np.result_type(streaming, float)
    total = slices[-1].stop
    lifted = np.zeros((total, total), dtype=dtype)
    for power, block_slice in enumerate(slices, start=1):
        lifted[block_slice, block_slice] = _kron_power_matrix(streaming, power)
    return lifted


def build_carleman_propagator(
    streaming: np.ndarray,
    f1: np.ndarray,
    f2: np.ndarray,
    order: int,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
) -> np.ndarray:
    """Build the dense QRE2 Carleman propagator `P = S_C C`.

    Corpus ID: QRE2 (`eq:carl_evol_d`, `eq:LBE_recurrence`).
    """

    streaming = _validate_streaming(streaming)
    f1, f2 = _validate_collision_terms(f1, f2)
    if streaming.shape[0] != f1.shape[0]:
        raise ValueError(
            "streaming, f1, and f2 must use the same base dimension; "
            f"got streaming {streaming.shape[0]} and f1/f2 {f1.shape[0]}"
        )
    _guarded_block_slices(
        f1.shape[0],
        order,
        max_dimension=max_dimension,
        object_name="dense Carleman propagator",
    )
    return build_carleman_streaming(
        streaming, order, max_dimension=max_dimension
    ) @ build_carleman_collision(f1, f2, order, max_dimension=max_dimension)


def extract_first_block(y: np.ndarray, dimension: int) -> np.ndarray:
    """Return the physical shifted-state block from a lifted state.

    Corpus ID: QRE2 (`eq:LBE_recurrence`).
    """

    y = _validate_vector(y, name="y")
    dimension = _validate_dimension(dimension)
    if y.size < dimension:
        raise ValueError(
            f"y must contain at least {dimension} entries; got {y.size}"
        )
    return y[:dimension]


def _validate_dimension_order(dimension: int, order: int) -> tuple[int, int]:
    return _validate_dimension(dimension), _validate_order(order)


def _validate_dimension(dimension: int) -> int:
    dimension = int(dimension)
    if dimension <= 0:
        raise ValueError(f"dimension must be positive; got {dimension}")
    return dimension


def _validate_order(order: int) -> int:
    order = int(order)
    if order not in SUPPORTED_ORDERS:
        raise ValueError(
            "QRE2 dense Carleman validation supports only N_C=1 and N_C=2; "
            f"got {order}"
        )
    return order


def _validate_max_dimension(max_dimension: int) -> int:
    max_dimension = int(max_dimension)
    if max_dimension <= 0:
        raise ValueError(f"max_dimension must be positive; got {max_dimension}")
    return max_dimension


def _validate_vector(vector: np.ndarray, *, name: str) -> np.ndarray:
    vector = np.asarray(vector)
    if vector.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional; got {vector.shape}")
    if vector.size == 0:
        raise ValueError(f"{name} must be non-empty")
    return vector


def _validate_collision_terms(
    f1: np.ndarray, f2: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    f1 = np.asarray(f1)
    f2 = np.asarray(f2)
    if f1.ndim != 2 or f1.shape[0] != f1.shape[1]:
        raise ValueError(f"f1 must be square; got {f1.shape}")
    dimension = f1.shape[0]
    expected_f2_shape = (dimension, dimension * dimension)
    if f2.shape != expected_f2_shape:
        raise ValueError(f"f2 must have shape {expected_f2_shape}; got {f2.shape}")
    return f1, f2


def _validate_streaming(streaming: np.ndarray) -> np.ndarray:
    streaming = np.asarray(streaming)
    if streaming.ndim != 2 or streaming.shape[0] != streaming.shape[1]:
        raise ValueError(f"streaming must be square; got {streaming.shape}")
    return streaming


def _guarded_block_slices(
    dimension: int,
    order: int,
    *,
    max_dimension: int,
    object_name: str,
) -> list[slice]:
    dimension, order = _validate_dimension_order(dimension, order)
    max_dimension = _validate_max_dimension(max_dimension)
    block_sizes = carleman_block_dimensions(dimension, order)
    total_dimension = int(sum(block_sizes))
    if total_dimension > max_dimension:
        raise ValueError(
            f"{object_name} refused dimension={total_dimension}; "
            f"max_dimension={max_dimension}. Use a smaller grid or order."
        )
    offsets = np.cumsum([0, *block_sizes])
    return [
        slice(int(offsets[index]), int(offsets[index + 1]))
        for index in range(order)
    ]


def _kron_power_vector(vector: np.ndarray, power: int) -> np.ndarray:
    result = np.asarray([1.0], dtype=np.result_type(vector, float))
    for _ in range(power):
        result = np.kron(result, vector)
    return result


def _kron_power_matrix(matrix: np.ndarray, power: int) -> np.ndarray:
    return _kron_all_matrices([matrix] * power)


def _kron_all_matrices(matrices: list[np.ndarray]) -> np.ndarray:
    if not matrices:
        return np.asarray([[1.0]])
    result = matrices[0]
    for matrix in matrices[1:]:
        result = np.kron(result, matrix)
    return result
