import numpy as np
import pytest

from pq_cfd import (
    SimulationConfig,
    apply_d1q3_operator_step,
    d1q3_collision_matrix,
    d1q3_streaming_permutation,
    default_quantum_operator_specs,
    flatten_d1q3_populations,
    run_d1q3,
    run_d1q3_classical_operator_emulation,
    run_d1q3_operator_model,
    unflatten_d1q3_populations,
)
from pq_cfd.d1q3 import _equilibrium, _initial_density


def test_d1q3_operator_model_matches_baseline_solver() -> None:
    config = SimulationConfig(
        grid_shape=(64,),
        steps=20,
        tau=0.8,
        initial_condition="sinusoidal",
        sample_interval=10,
        amplitude=0.02,
    )

    baseline = run_d1q3(config)
    operator = run_d1q3_classical_operator_emulation(config)
    compatibility = run_d1q3_operator_model(config)

    np.testing.assert_allclose(operator.density, baseline.density, atol=1e-14)
    np.testing.assert_allclose(
        operator.distributions,
        baseline.distributions,
        atol=1e-14,
    )
    np.testing.assert_allclose(compatibility.density, operator.density, atol=1e-14)
    assert operator.history.steps == baseline.history.steps
    assert operator.metrics["classical_operator_emulation"] == 1.0
    assert operator.metrics["quantum_ready"] == 0.0


def test_d1q3_quantum_operator_spec_marks_missing_quantum_work() -> None:
    spec = default_quantum_operator_specs()[0]

    assert spec.algorithm_id == "d1q3_classical_operator_emulation"
    assert not spec.circuit_ready
    assert "no reversible dilation or block encoding" in spec.known_gaps


def test_apply_d1q3_operator_step_matches_one_baseline_step() -> None:
    config = SimulationConfig(
        grid_shape=(16,),
        steps=1,
        tau=0.8,
        initial_condition="sinusoidal",
        sample_interval=None,
        amplitude=0.02,
    )
    density = _initial_density(config, 16)
    distributions = _equilibrium(density, np.zeros(16))

    stepped = apply_d1q3_operator_step(distributions, config)
    baseline = run_d1q3(config)

    np.testing.assert_allclose(stepped, baseline.distributions, atol=1e-14)


def test_d1q3_collision_matrix_and_streaming_permutation_shapes() -> None:
    collision = d1q3_collision_matrix(0.8)
    streaming = d1q3_streaming_permutation(8)

    assert collision.shape == (3, 3)
    assert streaming.shape == (24, 24)
    np.testing.assert_allclose(streaming.sum(axis=0), np.ones(24))
    np.testing.assert_allclose(streaming.sum(axis=1), np.ones(24))


def test_d1q3_flatten_round_trip_and_validation() -> None:
    distributions = np.arange(12, dtype=float).reshape(3, 4)
    flattened = flatten_d1q3_populations(distributions)

    np.testing.assert_allclose(
        unflatten_d1q3_populations(flattened, 4),
        distributions,
    )

    with pytest.raises(ValueError):
        flatten_d1q3_populations(np.zeros((4, 3)))
    with pytest.raises(ValueError):
        unflatten_d1q3_populations(flattened, 5)
