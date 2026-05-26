import numpy as np

from pq_cfd import SimulationConfig, run_d2q9


def test_d2q9_mass_conservation_shapes_and_taylor_green_accuracy() -> None:
    config = SimulationConfig(
        grid_shape=(32, 32),
        steps=30,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=10,
        amplitude=0.02,
    )

    result = run_d2q9(config)

    assert result.density.shape == (32, 32)
    assert result.velocity.shape == (2, 32, 32)
    assert result.distributions.shape == (9, 32, 32)
    assert result.density.dtype == np.float64
    assert result.velocity.dtype == np.float64
    assert result.distributions.dtype == np.float64
    assert result.history.steps == (0, 10, 20, 30)
    assert result.metrics["mass_drift_relative"] < 1e-12
    assert result.metrics["relative_l2_error_velocity"] < 8e-2
