"""D1Q3 passive scalar lattice Boltzmann baseline."""

from __future__ import annotations

from time import perf_counter

import numpy as np

from pq_cfd.metrics import mass_metrics, relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult
from pq_cfd.validation import ensure_low_mach, validate_common

D1Q3_C = np.array([-1, 0, 1], dtype=int)
D1Q3_W = np.array([1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0], dtype=float)
CS2 = 1.0 / 3.0


def run_d1q3(config: SimulationConfig) -> SimulationResult:
    """Run a periodic D1Q3 advection-diffusion/diffusion LBM benchmark."""

    (nx,) = validate_common(
        config,
        expected_dim=1,
        allowed_initial_conditions={"sinusoidal", "gaussian"},
        model_name="D1Q3",
    )
    ensure_low_mach(config.advection_velocity, model_name="D1Q3")

    start_time = perf_counter()
    density = _initial_density(config, nx)
    velocity = np.full((1, nx), config.advection_velocity, dtype=float)
    distributions = _equilibrium(density, velocity[0])
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
        equilibrium = _equilibrium(density, velocity[0])
        post_collision = distributions - (distributions - equilibrium) / config.tau
        distributions = _stream_periodic(post_collision)
        density = np.sum(distributions, axis=0)
        velocity = np.full((1, nx), config.advection_velocity, dtype=float)
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

    expected_density = analytic_d1q3_density(config, nx, config.steps)
    diffusivity = CS2 * (config.tau - 0.5)
    metrics = {
        **mass_metrics(initial_mass, float(np.sum(density))),
        "diffusivity": diffusivity,
        "relative_l2_error_density": relative_l2_error(density, expected_density),
        "runtime_seconds": perf_counter() - start_time,
    }

    return SimulationResult(
        model="D1Q3",
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


def analytic_d1q3_density(
    config: SimulationConfig, nx: int, step: int
) -> np.ndarray:
    """Continuous periodic reference for the sinusoidal D1Q3 benchmark."""

    x = np.arange(nx, dtype=float)
    if config.initial_condition == "sinusoidal":
        wave_number = 2.0 * np.pi / nx
        diffusivity = CS2 * (config.tau - 0.5)
        advected_x = x - config.advection_velocity * step
        decay = np.exp(-diffusivity * wave_number**2 * step)
        return config.base_density + config.amplitude * decay * np.sin(
            wave_number * advected_x
        )
    if config.initial_condition == "gaussian":
        return _initial_density(config, nx)
    raise ValueError(f"Unsupported D1Q3 initial condition: {config.initial_condition!r}")


def _initial_density(config: SimulationConfig, nx: int) -> np.ndarray:
    x = np.arange(nx, dtype=float)
    if config.initial_condition == "sinusoidal":
        return config.base_density + config.amplitude * np.sin(2.0 * np.pi * x / nx)
    if config.initial_condition == "gaussian":
        center = 0.5 * nx
        sigma = 0.08 * nx
        periodic_distance = np.minimum(abs(x - center), nx - abs(x - center))
        return config.base_density + config.amplitude * np.exp(
            -0.5 * (periodic_distance / sigma) ** 2
        )
    raise ValueError(f"Unsupported D1Q3 initial condition: {config.initial_condition!r}")


def _equilibrium(density: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    return D1Q3_W[:, None] * density[None, :] * (
        1.0 + D1Q3_C[:, None] * velocity[None, :] / CS2
    )


def _stream_periodic(distributions: np.ndarray) -> np.ndarray:
    streamed = np.empty_like(distributions)
    for index, speed in enumerate(D1Q3_C):
        streamed[index] = np.roll(distributions[index], shift=int(speed), axis=0)
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
