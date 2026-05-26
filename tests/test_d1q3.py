import numpy as np

from pq_cfd import SimulationConfig, run_d1q3


def test_d1q3_mass_conservation_shapes_and_accuracy() -> None:
    config = SimulationConfig(
        grid_shape=(128,),
        steps=80,
        tau=0.8,
        initial_condition="sinusoidal",
        sample_interval=20,
        amplitude=0.02,
    )

    result = run_d1q3(config)

    assert result.density.shape == (128,)
    assert result.velocity.shape == (1, 128)
    assert result.distributions.shape == (3, 128)
    assert result.density.dtype == np.float64
    assert result.velocity.dtype == np.float64
    assert result.distributions.dtype == np.float64
    assert result.history.steps == (0, 20, 40, 60, 80)
    assert result.metrics["mass_drift_relative"] < 1e-12
    assert result.metrics["relative_l2_error_density"] < 2e-3
