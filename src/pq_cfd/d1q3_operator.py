"""D1Q3 classical operator emulation for the first quantum mapping step."""

from __future__ import annotations

from time import perf_counter

import numpy as np

from pq_cfd.d1q3 import (
    CS2,
    D1Q3_C,
    D1Q3_W,
    analytic_d1q3_density,
    _equilibrium,
    _initial_density,
    _sample,
    _stream_periodic,
)
from pq_cfd.metrics import mass_metrics, relative_l2_error
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult
from pq_cfd.validation import ensure_low_mach, validate_common


def run_d1q3_classical_operator_emulation(
    config: SimulationConfig,
) -> SimulationResult:
    """Run D1Q3 through explicit classical collision and streaming operators.

    This is not a quantum operator model: the collision matrix is dissipative and
    is not yet reversibly embedded, unitary, or block encoded.
    """

    (nx,) = validate_common(
        config,
        expected_dim=1,
        allowed_initial_conditions={"sinusoidal", "gaussian"},
        model_name="D1Q3-operator",
    )
    ensure_low_mach(config.advection_velocity, model_name="D1Q3-operator")

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
        distributions = apply_d1q3_operator_step(distributions, config)
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
        "classical_operator_emulation": 1.0,
        "quantum_ready": 0.0,
    }

    return SimulationResult(
        model="D1Q3-OPERATOR",
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


def run_d1q3_operator_model(config: SimulationConfig) -> SimulationResult:
    """Compatibility alias for classical operator emulation."""

    return run_d1q3_classical_operator_emulation(config)


def apply_d1q3_operator_step(
    distributions: np.ndarray,
    config: SimulationConfig,
) -> np.ndarray:
    """Apply one classical D1Q3 collision-plus-streaming operator step."""

    collision = d1q3_collision_matrix(config.tau, config.advection_velocity)
    post_collision = collision @ distributions
    return _stream_periodic(post_collision)


def d1q3_collision_matrix(
    tau: float,
    advection_velocity: float = 0.0,
) -> np.ndarray:
    """Return the local 3x3 dissipative collision matrix for fixed speed."""

    if tau <= 0.5:
        raise ValueError("tau must be greater than 0.5.")
    ensure_low_mach(advection_velocity, model_name="D1Q3-operator")
    equilibrium_coefficients = D1Q3_W * (1.0 + D1Q3_C * advection_velocity / CS2)
    omega = 1.0 / tau
    return (1.0 - omega) * np.eye(3) + omega * equilibrium_coefficients[:, None]


def flatten_d1q3_populations(distributions: np.ndarray) -> np.ndarray:
    """Flatten D1Q3 populations using velocity-major ordering."""

    if distributions.ndim != 2 or distributions.shape[0] != 3:
        raise ValueError("D1Q3 distributions must have shape (3, nx).")
    return distributions.reshape(-1).copy()


def unflatten_d1q3_populations(flattened: np.ndarray, nx: int) -> np.ndarray:
    """Restore velocity-major D1Q3 populations from a flat vector."""

    if nx <= 0:
        raise ValueError("nx must be positive.")
    if flattened.shape != (3 * nx,):
        raise ValueError(f"flattened populations must have shape ({3 * nx},).")
    return flattened.reshape((3, nx)).copy()


def d1q3_streaming_permutation(nx: int) -> np.ndarray:
    """Return the full dense streaming permutation for small operator tests."""

    if nx <= 0:
        raise ValueError("nx must be positive.")
    size = 3 * nx
    permutation = np.zeros((size, size), dtype=float)
    for velocity_index, speed in enumerate(D1Q3_C):
        for x in range(nx):
            source = velocity_index * nx + x
            target_x = (x + int(speed)) % nx
            target = velocity_index * nx + target_x
            permutation[target, source] = 1.0
    return permutation
