"""D2Q9 BGK lattice Boltzmann baseline."""

from __future__ import annotations

from time import perf_counter

import numpy as np

from pq_cfd.metrics import mass_metrics, relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult
from pq_cfd.validation import ensure_low_mach, validate_common

D2Q9_C = np.array(
    [
        [0, 0],
        [1, 0],
        [0, 1],
        [-1, 0],
        [0, -1],
        [1, 1],
        [-1, 1],
        [-1, -1],
        [1, -1],
    ],
    dtype=int,
)
D2Q9_W = np.array(
    [4.0 / 9.0]
    + [1.0 / 9.0] * 4
    + [1.0 / 36.0] * 4,
    dtype=float,
)
CS2 = 1.0 / 3.0


def run_d2q9(config: SimulationConfig) -> SimulationResult:
    """Run a periodic D2Q9 Taylor-Green vortex LBM benchmark."""

    nx, ny = validate_common(
        config,
        expected_dim=2,
        allowed_initial_conditions={"taylor_green"},
        model_name="D2Q9",
    )
    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    y_scale = kx / ky
    ensure_low_mach(config.amplitude * max(1.0, abs(y_scale)), model_name="D2Q9")

    start_time = perf_counter()
    density, velocity = _initial_taylor_green(config, nx, ny)
    distributions = _equilibrium(density, velocity)
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
        equilibrium = _equilibrium(density, velocity)
        post_collision = distributions - (distributions - equilibrium) / config.tau
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
    }

    return SimulationResult(
        model="D2Q9",
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


def analytic_taylor_green_velocity(
    config: SimulationConfig, nx: int, ny: int, step: int
) -> np.ndarray:
    """Low-Mach incompressible Taylor-Green velocity reference."""

    _, velocity0 = _initial_taylor_green(config, nx, ny)
    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    viscosity = CS2 * (config.tau - 0.5)
    decay = np.exp(-viscosity * (kx**2 + ky**2) * step)
    return velocity0 * decay


def _initial_taylor_green(
    config: SimulationConfig, nx: int, ny: int
) -> tuple[np.ndarray, np.ndarray]:
    x = np.arange(nx, dtype=float)[:, None]
    y = np.arange(ny, dtype=float)[None, :]
    kx = 2.0 * np.pi / nx
    ky = 2.0 * np.pi / ny
    y_scale = kx / ky

    ux = config.amplitude * np.sin(kx * x) * np.cos(ky * y)
    uy = -config.amplitude * y_scale * np.cos(kx * x) * np.sin(ky * y)
    velocity = np.stack((ux, uy), axis=0)

    pressure = -0.25 * config.base_density * config.amplitude**2 * (
        np.cos(2.0 * kx * x) + y_scale**2 * np.cos(2.0 * ky * y)
    )
    density = config.base_density + pressure / CS2
    return density, velocity


def _equilibrium(density: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    ux = velocity[0]
    uy = velocity[1]
    speed_squared = ux**2 + uy**2
    equilibrium = np.empty((9, *density.shape), dtype=float)
    for index, (cx, cy) in enumerate(D2Q9_C):
        c_dot_u = cx * ux + cy * uy
        equilibrium[index] = D2Q9_W[index] * density * (
            1.0 + 3.0 * c_dot_u + 4.5 * c_dot_u**2 - 1.5 * speed_squared
        )
    return equilibrium


def _macroscopic(distributions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    density = np.sum(distributions, axis=0)
    momentum_x = np.sum(D2Q9_C[:, 0, None, None] * distributions, axis=0)
    momentum_y = np.sum(D2Q9_C[:, 1, None, None] * distributions, axis=0)
    velocity = np.stack((momentum_x / density, momentum_y / density), axis=0)
    return density, velocity


def _stream_periodic(distributions: np.ndarray) -> np.ndarray:
    streamed = np.empty_like(distributions)
    for index, (cx, cy) in enumerate(D2Q9_C):
        streamed[index] = np.roll(
            distributions[index],
            shift=(int(cx), int(cy)),
            axis=(0, 1),
        )
    return streamed


def _sample(
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
