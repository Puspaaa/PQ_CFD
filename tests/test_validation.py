import pytest

from pq_cfd import SimulationConfig, run_d1q3, run_d2q9


def test_rejects_unstable_tau() -> None:
    with pytest.raises(ValueError, match="tau > 0.5"):
        run_d1q3(SimulationConfig(grid_shape=(16,), steps=1, tau=0.5))


def test_rejects_negative_grid_size() -> None:
    with pytest.raises(ValueError, match="positive integers"):
        run_d1q3(SimulationConfig(grid_shape=(-16,), steps=1, tau=0.8))


def test_rejects_unsupported_boundary_mode() -> None:
    with pytest.raises(ValueError, match="periodic"):
        run_d2q9(
            SimulationConfig(
                grid_shape=(16, 16),
                steps=1,
                tau=0.8,
                initial_condition="taylor_green",
                boundary_mode="bounce_back",
            )
        )


def test_rejects_out_of_regime_velocity() -> None:
    with pytest.raises(ValueError, match="low-Mach"):
        run_d1q3(
            SimulationConfig(
                grid_shape=(16,),
                steps=1,
                tau=0.8,
                advection_velocity=0.2,
            )
        )
