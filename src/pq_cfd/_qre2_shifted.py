"""Private QRE2 shifted-D2Q9 operator validation helpers.

Corpus ID: QRE2. This module implements only the shifted incompressible LBE
operator pieces from the paper's shifted LBE section (`sec:shifted`), especially
`eq:g`, `eq:eq_shift_incompressible`, `eq:eq_shift_explicit`,
`eq:LBE_col_shift_matrix`, `eq:F1`, `eq:F2`, and `eq:streaming`.

These helpers are intentionally private and dense-matrix based. They are for
tiny classical validation before any Carleman, quantum, or resource code.
"""

from __future__ import annotations

from itertools import product
from time import perf_counter

import numpy as np

from pq_cfd.d2q9 import CS2, D2Q9_C, D2Q9_W, _initial_taylor_green
from pq_cfd.d2q9 import analytic_taylor_green_velocity
from pq_cfd.metrics import mass_metrics, relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult
from pq_cfd.validation import ensure_low_mach, validate_common

Q = 9


def shift_to_g(f_bar: np.ndarray) -> np.ndarray:
    """Return QRE2 shifted populations `g = f_bar - w` (`eq:g`)."""

    f_bar = _validate_d2q9_state(f_bar, name="f_bar")
    return f_bar - _weights_field()


def unshift_to_fbar(g: np.ndarray) -> np.ndarray:
    """Undo the QRE2 shifted variable transformation (`eq:g`)."""

    g = _validate_d2q9_state(g, name="g")
    return g + _weights_field()


def shifted_moments(g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return density fluctuation and incompressible velocity for QRE2."""

    g = _validate_d2q9_state(g, name="g")
    delta_rho = np.sum(g, axis=0)
    velocity_x = np.sum(D2Q9_C[:, 0, None, None] * g, axis=0)
    velocity_y = np.sum(D2Q9_C[:, 1, None, None] * g, axis=0)
    velocity = np.stack((velocity_x, velocity_y), axis=0)
    return delta_rho, velocity


def shifted_equilibrium(g: np.ndarray) -> np.ndarray:
    """QRE2 shifted incompressible equilibrium from `eq:eq_shift_explicit`."""

    delta_rho, velocity = shifted_moments(g)
    return shifted_equilibrium_from_moments(delta_rho, velocity)


def shifted_equilibrium_from_moments(
    delta_rho: np.ndarray, velocity: np.ndarray
) -> np.ndarray:
    """Build QRE2 shifted equilibrium from density fluctuation and velocity."""

    delta_rho = np.asarray(delta_rho)
    velocity = np.asarray(velocity)
    if velocity.shape != (2, *delta_rho.shape):
        raise ValueError(
            "velocity must have shape (2, *delta_rho.shape); "
            f"got {velocity.shape} for delta_rho {delta_rho.shape}"
        )

    speed_squared = velocity[0] ** 2 + velocity[1] ** 2
    equilibrium = np.empty((Q, *delta_rho.shape), dtype=np.result_type(delta_rho, velocity, float))
    for index, (cx, cy) in enumerate(D2Q9_C):
        c_dot_u = cx * velocity[0] + cy * velocity[1]
        equilibrium[index] = D2Q9_W[index] * (
            delta_rho + 3.0 * c_dot_u + 4.5 * c_dot_u**2 - 1.5 * speed_squared
        )
    return equilibrium


def step_shifted_direct(g: np.ndarray, tau_bar: float) -> np.ndarray:
    """One direct QRE2 shifted collision-streaming step.

    This is the direct form of `eq:LBE_col_shift` followed by
    `eq:LBE_str_shift`, before any Carleman lifting.
    """

    _validate_tau_bar(tau_bar)
    g = _validate_d2q9_state(g, name="g")
    collision = g + (shifted_equilibrium(g) - g) / tau_bar
    return _stream_periodic(collision)


def run_shifted_taylor_green(config: SimulationConfig) -> SimulationResult:
    """Run the private QRE2 shifted-D2Q9 route on Taylor-Green moments.

    Corpus ID: QRE2. This helper validates the shifted incompressible LBE route
    on the existing periodic Taylor-Green benchmark surface. It is a route
    behavior comparison against the classical D2Q9 baseline, not a claim that
    the shifted incompressible update is algebraically identical to standard
    BGK D2Q9.
    """

    nx, ny = validate_common(
        config,
        expected_dim=2,
        allowed_initial_conditions={"taylor_green"},
        model_name="QRE2 shifted D2Q9",
    )
    if not np.isclose(config.base_density, 1.0):
        raise ValueError("QRE2 shifted D2Q9 currently requires base_density=1.0.")

    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    y_scale = kx / ky
    ensure_low_mach(
        config.amplitude * max(1.0, abs(y_scale)),
        model_name="QRE2 shifted D2Q9",
    )

    start_time = perf_counter()
    density, velocity = _initial_taylor_green(config, nx, ny)
    g = shifted_equilibrium_from_moments(density - config.base_density, velocity)
    initial_mass = float(np.sum(density))

    sampled_steps: list[int] = []
    sampled_density: list[np.ndarray] = []
    sampled_velocity: list[np.ndarray] = []
    _sample_shifted(
        0,
        config,
        sampled_steps,
        sampled_density,
        sampled_velocity,
        density,
        velocity,
    )

    for step in range(1, config.steps + 1):
        g = step_shifted_direct(g, config.tau)
        delta_rho, velocity = shifted_moments(g)
        density = config.base_density + delta_rho
        _sample_shifted(
            step,
            config,
            sampled_steps,
            sampled_density,
            sampled_velocity,
            density,
            velocity,
        )

    _sample_shifted(
        config.steps,
        config,
        sampled_steps,
        sampled_density,
        sampled_velocity,
        density,
        velocity,
        force=True,
    )

    expected_velocity = analytic_taylor_green_velocity(config, nx, ny, config.steps)
    viscosity = CS2 * (config.tau - 0.5)
    metrics = {
        **mass_metrics(initial_mass, float(np.sum(density))),
        "viscosity": viscosity,
        "relative_l2_error_velocity": relative_l2_error(velocity, expected_velocity),
        "runtime_seconds": perf_counter() - start_time,
    }

    return SimulationResult(
        model="QRE2-shifted-D2Q9",
        config=config,
        density=density,
        velocity=velocity,
        distributions=g,
        history=SimulationHistory(
            steps=tuple(sampled_steps),
            density=tuple(sampled_density),
            velocity=tuple(sampled_velocity),
        ),
        metrics=metrics,
    )


def build_shifted_collision_terms(
    tau_bar: float, spatial_shape: tuple[int, int] | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Build QRE2 `F1` and `F2` collision terms.

    With ``spatial_shape=None``, return local D2Q9 velocity-space matrices from
    `eq:F1_loc` and `eq:F2_loc`. With a spatial shape, return dense global
    matrices acting on site-major flattened states. The dense global form is for
    tiny validation only.
    """

    _validate_tau_bar(tau_bar)
    gram = D2Q9_C @ D2Q9_C.T
    f1_local = np.zeros((Q, Q), dtype=float)
    f2_local = np.zeros((Q, Q * Q), dtype=float)
    for m in range(Q):
        for m1 in range(Q):
            f1_local[m, m1] = (
                D2Q9_W[m] + 3.0 * D2Q9_W[m] * gram[m, m1] - float(m == m1)
            ) / tau_bar
            for m2 in range(Q):
                f2_local[m, m1 * Q + m2] = (
                    D2Q9_W[m]
                    * (4.5 * gram[m, m1] * gram[m, m2] - 1.5 * gram[m1, m2])
                    / tau_bar
                )

    if spatial_shape is None:
        return f1_local, f2_local

    spatial_shape = _validate_spatial_shape(spatial_shape)
    site_count = int(np.prod(spatial_shape))
    dimension = site_count * Q
    f1 = np.kron(np.eye(site_count), f1_local)
    f2 = np.zeros((dimension, dimension * dimension), dtype=float)
    for site in range(site_count):
        rows = slice(site * Q, (site + 1) * Q)
        for m1 in range(Q):
            for m2 in range(Q):
                global_col = (site * Q + m1) * dimension + (site * Q + m2)
                local_col = m1 * Q + m2
                f2[rows, global_col] = f2_local[:, local_col]
    return f1, f2


def build_streaming_matrix(spatial_shape: tuple[int, int]) -> np.ndarray:
    """Build the QRE2 periodic streaming permutation (`eq:streaming`)."""

    spatial_shape = _validate_spatial_shape(spatial_shape)
    site_count = int(np.prod(spatial_shape))
    dimension = site_count * Q
    streaming = np.zeros((dimension, dimension), dtype=float)
    for position in product(*[range(length) for length in spatial_shape]):
        source_site = _site_index(position, spatial_shape)
        for m, velocity in enumerate(D2Q9_C):
            destination = tuple((np.asarray(position) + velocity) % spatial_shape)
            destination_site = _site_index(destination, spatial_shape)
            source = source_site * Q + m
            dest = destination_site * Q + m
            streaming[dest, source] = 1.0
    return streaming


def flatten_site_major(g: np.ndarray) -> np.ndarray:
    """Flatten `(9, nx, ny)` populations as `(site, velocity)` for QRE2 matrices."""

    g = _validate_d2q9_state(g, name="g")
    return np.moveaxis(g, 0, -1).reshape(-1)


def unflatten_site_major(g_vector: np.ndarray, spatial_shape: tuple[int, int]) -> np.ndarray:
    """Undo `flatten_site_major` for a QRE2 shifted D2Q9 vector."""

    spatial_shape = _validate_spatial_shape(spatial_shape)
    g_vector = np.asarray(g_vector)
    expected = int(np.prod(spatial_shape)) * Q
    if g_vector.shape != (expected,):
        raise ValueError(
            f"g_vector must have shape ({expected},) for spatial_shape {spatial_shape}; "
            f"got {g_vector.shape}"
        )
    return np.moveaxis(g_vector.reshape((*spatial_shape, Q)), -1, 0)


def step_shifted_matrix(
    g_vector: np.ndarray, streaming: np.ndarray, f1: np.ndarray, f2: np.ndarray
) -> np.ndarray:
    """Apply the dense QRE2 polynomial update from `eq:LBE_col_shift_matrix`."""

    g_vector = np.asarray(g_vector)
    if g_vector.ndim != 1:
        raise ValueError(f"g_vector must be one-dimensional; got {g_vector.shape}")
    dimension = g_vector.shape[0]
    if streaming.shape != (dimension, dimension):
        raise ValueError(
            f"streaming must have shape {(dimension, dimension)}; got {streaming.shape}"
        )
    if f1.shape != (dimension, dimension):
        raise ValueError(f"f1 must have shape {(dimension, dimension)}; got {f1.shape}")
    if f2.shape != (dimension, dimension * dimension):
        raise ValueError(
            f"f2 must have shape {(dimension, dimension * dimension)}; got {f2.shape}"
        )

    identity = np.eye(dimension, dtype=np.result_type(g_vector, f1, f2, streaming, float))
    collision = (identity + f1) @ g_vector + f2 @ np.kron(g_vector, g_vector)
    return streaming @ collision


def _stream_periodic(distributions: np.ndarray) -> np.ndarray:
    streamed = np.empty_like(distributions)
    for index, (cx, cy) in enumerate(D2Q9_C):
        streamed[index] = np.roll(
            distributions[index],
            shift=(int(cx), int(cy)),
            axis=(0, 1),
        )
    return streamed


def _weights_field() -> np.ndarray:
    return D2Q9_W[:, None, None]


def _site_index(position: tuple[int, int], spatial_shape: tuple[int, int]) -> int:
    return int(np.ravel_multi_index(position, spatial_shape))


def _validate_d2q9_state(state: np.ndarray, *, name: str) -> np.ndarray:
    state = np.asarray(state)
    if state.ndim != 3 or state.shape[0] != Q:
        raise ValueError(f"{name} must have shape (9, nx, ny); got {state.shape}")
    return state


def _validate_spatial_shape(spatial_shape: tuple[int, int]) -> tuple[int, int]:
    if len(spatial_shape) != 2:
        raise ValueError(f"spatial_shape must be two-dimensional; got {spatial_shape}")
    nx, ny = (int(spatial_shape[0]), int(spatial_shape[1]))
    if nx <= 0 or ny <= 0:
        raise ValueError(f"spatial_shape entries must be positive; got {spatial_shape}")
    return nx, ny


def _validate_tau_bar(tau_bar: float) -> None:
    if not np.isfinite(tau_bar) or tau_bar <= 0.0:
        raise ValueError(f"tau_bar must be positive and finite; got {tau_bar}")


def _sample_shifted(
    step: int,
    config: SimulationConfig,
    sampled_steps: list[int],
    sampled_density: list[np.ndarray],
    sampled_velocity: list[np.ndarray],
    density: np.ndarray,
    velocity: np.ndarray,
    *,
    force: bool = False,
) -> None:
    if config.sample_interval is None and not force:
        return
    should_sample = force or step == 0 or step % int(config.sample_interval) == 0
    if not should_sample:
        return
    if sampled_steps and sampled_steps[-1] == step:
        return
    sampled_steps.append(step)
    sampled_density.append(density.copy())
    sampled_velocity.append(velocity.copy())
