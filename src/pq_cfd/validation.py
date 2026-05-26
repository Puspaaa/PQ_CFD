"""Input validation for baseline solvers."""

from __future__ import annotations

from collections.abc import Iterable

from pq_cfd.types import SimulationConfig

LOW_MACH_MAX_SPEED = 0.1


def validate_common(
    config: SimulationConfig,
    *,
    expected_dim: int,
    allowed_initial_conditions: Iterable[str],
    model_name: str,
) -> tuple[int, ...]:
    """Validate common LBM configuration and return a normalized grid shape."""

    shape = tuple(config.grid_shape)
    if len(shape) != expected_dim:
        raise ValueError(
            f"{model_name} expects a {expected_dim}D grid_shape, got {shape}."
        )
    if any(not isinstance(size, int) or size <= 0 for size in shape):
        raise ValueError(f"{model_name} grid sizes must be positive integers.")
    if config.steps < 0:
        raise ValueError(f"{model_name} steps must be non-negative.")
    if config.tau <= 0.5:
        raise ValueError(
            f"{model_name} requires tau > 0.5 for positive viscosity/diffusivity."
        )
    if config.boundary_mode != "periodic":
        raise ValueError(
            f"{model_name} currently supports only periodic boundaries, "
            f"got {config.boundary_mode!r}."
        )
    if config.initial_condition not in set(allowed_initial_conditions):
        raise ValueError(
            f"{model_name} unsupported initial condition "
            f"{config.initial_condition!r}."
        )
    if config.sample_interval is not None and config.sample_interval <= 0:
        raise ValueError(f"{model_name} sample_interval must be positive or None.")
    if config.amplitude < 0.0:
        raise ValueError(f"{model_name} amplitude must be non-negative.")
    if config.base_density <= 0.0:
        raise ValueError(f"{model_name} base_density must be positive.")
    return shape


def ensure_low_mach(speed: float, *, model_name: str) -> None:
    """Reject configurations outside the intentionally conservative first regime."""

    if abs(speed) >= LOW_MACH_MAX_SPEED:
        raise ValueError(
            f"{model_name} is limited to |speed| < {LOW_MACH_MAX_SPEED} "
            "for this first low-Mach baseline."
        )
