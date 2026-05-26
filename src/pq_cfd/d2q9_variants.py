"""D2Q9 collision variants for first-wave scheme comparisons."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

import numpy as np

from pq_cfd.d2q9 import (
    CS2,
    D2Q9_C,
    analytic_taylor_green_velocity,
    _equilibrium,
    _initial_taylor_green,
    _macroscopic,
    _sample,
    _stream_periodic,
)
from pq_cfd.metrics import mass_metrics, relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult
from pq_cfd.validation import ensure_low_mach, validate_common

D2Q9_SCHEMES = ("bgk_srt", "barred_srt", "trt", "mrt")
TRT_MAGIC_PARAMETER = 3.0 / 16.0

_OPPOSITE = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6], dtype=int)
_MRT_M = np.array(
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [-4, -1, -1, -1, -1, 2, 2, 2, 2],
        [4, -2, -2, -2, -2, 1, 1, 1, 1],
        [0, 1, 0, -1, 0, 1, -1, -1, 1],
        [0, -2, 0, 2, 0, 1, -1, -1, 1],
        [0, 0, 1, 0, -1, 1, 1, -1, -1],
        [0, 0, -2, 0, 2, 1, 1, -1, -1],
        [0, 1, -1, 1, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, -1, 1, -1],
    ],
    dtype=float,
)
_MRT_M_INV = np.linalg.inv(_MRT_M)


def run_d2q9_scheme(config: SimulationConfig, scheme: str) -> SimulationResult:
    """Run a D2Q9 Taylor-Green benchmark with a selected collision scheme."""

    normalized = normalize_d2q9_scheme(scheme)
    if normalized == "bgk_srt":
        return _run_d2q9_with_collision(
            config,
            scheme=normalized,
            collision=_collide_bgk_srt,
        )
    if normalized == "barred_srt":
        return _run_d2q9_with_collision(
            config,
            scheme=normalized,
            collision=_collide_barred_srt,
            initialize=_initialize_barred_srt,
        )
    if normalized == "trt":
        return _run_d2q9_with_collision(
            config,
            scheme=normalized,
            collision=_collide_trt,
        )
    if normalized == "mrt":
        return _run_d2q9_with_collision(
            config,
            scheme=normalized,
            collision=_collide_mrt,
        )
    raise ValueError(f"Unsupported D2Q9 scheme: {scheme!r}")


def run_d2q9_barred_srt(config: SimulationConfig) -> SimulationResult:
    """Run D2Q9 using the transformed barred-variable SRT update."""

    return run_d2q9_scheme(config, "barred_srt")


def run_d2q9_trt(config: SimulationConfig) -> SimulationResult:
    """Run D2Q9 using a two-relaxation-time collision operator."""

    return run_d2q9_scheme(config, "trt")


def run_d2q9_mrt(config: SimulationConfig) -> SimulationResult:
    """Run D2Q9 using a raw-moment MRT collision operator."""

    return run_d2q9_scheme(config, "mrt")


def collide_d2q9_local(
    distributions: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
    scheme: str,
) -> np.ndarray:
    """Apply one local D2Q9 collision step without streaming."""

    normalized = normalize_d2q9_scheme(scheme)
    if normalized == "bgk_srt":
        return _collide_bgk_srt(distributions, density, velocity, tau)
    if normalized == "barred_srt":
        return _collide_barred_srt(distributions, density, velocity, tau)
    if normalized == "trt":
        return _collide_trt(distributions, density, velocity, tau)
    if normalized == "mrt":
        return _collide_mrt(distributions, density, velocity, tau)
    raise ValueError(f"Unsupported D2Q9 scheme: {scheme!r}")


def normalize_d2q9_scheme(scheme: str) -> str:
    """Return the canonical D2Q9 collision scheme identifier."""

    normalized = scheme.lower().replace("-", "_")
    aliases = {
        "srt": "bgk_srt",
        "bgk": "bgk_srt",
        "standard": "bgk_srt",
        "barred": "barred_srt",
        "second_order_srt": "barred_srt",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in D2Q9_SCHEMES:
        raise ValueError(f"Unsupported D2Q9 scheme: {scheme!r}")
    return normalized


def barred_from_physical_distribution(
    physical_distribution: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    """Transform physical populations to barred populations for trapezoidal SRT."""

    continuous_tau = _continuous_relaxation_time(tau)
    equilibrium = _equilibrium(density, velocity)
    return physical_distribution + 0.5 * (
        physical_distribution - equilibrium
    ) / continuous_tau


def physical_from_barred_distribution(
    barred_distribution: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    """Recover physical populations from barred populations for SRT diagnostics."""

    continuous_tau = _continuous_relaxation_time(tau)
    equilibrium = _equilibrium(density, velocity)
    numerator = barred_distribution + equilibrium / (2.0 * continuous_tau)
    denominator = 1.0 + 1.0 / (2.0 * continuous_tau)
    return numerator / denominator


def trt_odd_relaxation_rate(
    tau: float,
    *,
    magic_parameter: float = TRT_MAGIC_PARAMETER,
) -> float:
    """Return the odd-mode TRT relaxation rate from the standard magic parameter."""

    if tau <= 0.5:
        raise ValueError("tau must be greater than 0.5.")
    if magic_parameter <= 0.0:
        raise ValueError("magic_parameter must be positive.")
    return 1.0 / (0.5 + magic_parameter / (tau - 0.5))


def d2q9_opposite_indices() -> np.ndarray:
    """Return D2Q9 opposite velocity indices."""

    return _OPPOSITE.copy()


def d2q9_mrt_moment_matrix() -> np.ndarray:
    """Return the raw-moment matrix used by the MRT collision operator."""

    return _MRT_M.copy()


def d2q9_mrt_inverse_moment_matrix() -> np.ndarray:
    """Return the inverse raw-moment matrix used by MRT."""

    return _MRT_M_INV.copy()


def d2q9_mrt_relaxation_rates(tau: float) -> np.ndarray:
    """Return MRT relaxation rates for public tests and diagnostics."""

    return _mrt_relaxation_rates(tau).copy()


def _run_d2q9_with_collision(
    config: SimulationConfig,
    *,
    scheme: str,
    collision: Callable[[np.ndarray, np.ndarray, np.ndarray, float], np.ndarray],
    initialize: Callable[[np.ndarray, np.ndarray, float], np.ndarray] | None = None,
) -> SimulationResult:
    nx, ny = validate_common(
        config,
        expected_dim=2,
        allowed_initial_conditions={"taylor_green"},
        model_name=f"D2Q9-{scheme}",
    )
    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    y_scale = kx / ky
    ensure_low_mach(config.amplitude * max(1.0, abs(y_scale)), model_name="D2Q9")

    start_time = perf_counter()
    density, velocity = _initial_taylor_green(config, nx, ny)
    physical_distribution = _equilibrium(density, velocity)
    if initialize is None:
        distributions = physical_distribution
    else:
        distributions = initialize(physical_distribution, velocity, config.tau)
    initial_mass = float(np.sum(density))

    sampled_steps: list[int] = []
    sampled_density: list[np.ndarray] = []
    sampled_velocity: list[np.ndarray] = []
    _sample(
        0,
        config,
        sampled_steps,
        sampled_density,
        sampled_velocity,
        density,
        velocity,
    )

    for step in range(1, config.steps + 1):
        post_collision = collision(distributions, density, velocity, config.tau)
        distributions = _stream_periodic(post_collision)
        density, velocity = _macroscopic(distributions)
        _sample(
            step,
            config,
            sampled_steps,
            sampled_density,
            sampled_velocity,
            density,
            velocity,
        )

    _sample(
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
        "collision_scheme": scheme,
    }
    if scheme == "barred_srt":
        metrics["continuous_relaxation_time"] = config.tau - 0.5
        metrics["barred_relaxation_time"] = config.tau
    if scheme == "trt":
        metrics["trt_even_relaxation_rate"] = 1.0 / config.tau
        metrics["trt_odd_relaxation_rate"] = trt_odd_relaxation_rate(config.tau)
    if scheme == "mrt":
        metrics["mrt_shear_relaxation_rate"] = 1.0 / config.tau

    return SimulationResult(
        model=f"D2Q9-{scheme.upper()}",
        config=config,
        density=density,
        velocity=velocity,
        distributions=distributions,
        history=SimulationHistory(
            steps=tuple(sampled_steps),
            density=tuple(sampled_density),
            velocity=tuple(sampled_velocity),
        ),
        metrics=metrics,
    )


def _initialize_barred_srt(
    physical_distribution: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    density = np.sum(physical_distribution, axis=0)
    return barred_from_physical_distribution(
        physical_distribution,
        density,
        velocity,
        tau,
    )


def _collide_bgk_srt(
    distributions: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    equilibrium = _equilibrium(density, velocity)
    return distributions - (distributions - equilibrium) / tau


def _collide_barred_srt(
    barred_distributions: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    equilibrium = _equilibrium(density, velocity)
    return barred_distributions - (barred_distributions - equilibrium) / tau


def _collide_trt(
    distributions: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    equilibrium = _equilibrium(density, velocity)
    delta = distributions - equilibrium
    opposite_delta = delta[_OPPOSITE]
    even_delta = 0.5 * (delta + opposite_delta)
    odd_delta = 0.5 * (delta - opposite_delta)
    even_rate = 1.0 / tau
    odd_rate = trt_odd_relaxation_rate(tau)
    return distributions - even_rate * even_delta - odd_rate * odd_delta


def _collide_mrt(
    distributions: np.ndarray,
    density: np.ndarray,
    velocity: np.ndarray,
    tau: float,
) -> np.ndarray:
    moments = np.tensordot(_MRT_M, distributions, axes=(1, 0))
    equilibrium_moments = _mrt_equilibrium_moments(density, velocity)
    rates = _mrt_relaxation_rates(tau)
    post_moments = moments - rates[:, None, None] * (
        moments - equilibrium_moments
    )
    return np.tensordot(_MRT_M_INV, post_moments, axes=(1, 0))


def _mrt_equilibrium_moments(
    density: np.ndarray,
    velocity: np.ndarray,
) -> np.ndarray:
    ux = velocity[0]
    uy = velocity[1]
    speed_squared = ux**2 + uy**2
    moments = np.empty((9, *density.shape), dtype=float)
    moments[0] = density
    moments[1] = -2.0 * density + 3.0 * density * speed_squared
    moments[2] = density - 3.0 * density * speed_squared
    moments[3] = density * ux
    moments[4] = -density * ux
    moments[5] = density * uy
    moments[6] = -density * uy
    moments[7] = density * (ux**2 - uy**2)
    moments[8] = density * ux * uy
    return moments


def _mrt_relaxation_rates(tau: float) -> np.ndarray:
    shear_rate = 1.0 / tau
    return np.array(
        [0.0, 1.64, 1.54, 0.0, 1.9, 0.0, 1.9, shear_rate, shear_rate],
        dtype=float,
    )


def _continuous_relaxation_time(tau: float) -> float:
    if tau <= 0.5:
        raise ValueError("tau must be greater than 0.5.")
    return tau - 0.5
