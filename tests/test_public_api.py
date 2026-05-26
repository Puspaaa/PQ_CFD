import importlib

import pytest

import pq_cfd


def test_public_api_keeps_only_baseline_and_diagnostics_surface() -> None:
    expected = {
        "SimulationConfig",
        "SimulationHistory",
        "SimulationResult",
        "SweepCase",
        "SweepRecord",
        "run_d1q3",
        "run_d2q9",
        "run_sweep",
        "default_sweep_cases",
        "default_d1q3_sweep_cases",
        "default_d2q9_sweep_cases",
        "write_sweep_csv",
        "D2Q9DiagnosticCase",
        "D2Q9DiagnosticRecord",
        "D2Q9DiagnosticAssessment",
        "d2q9_diagnostic_cases",
        "run_d2q9_diagnostics",
        "assess_d2q9_diagnostics",
        "steps_for_decay_exponent",
        "observed_order",
        "write_d2q9_diagnostics_csv",
    }

    assert set(pq_cfd.__all__) == expected


@pytest.mark.parametrize(
    "name",
    [
        "run_d1q3_operator_model",
        "run_d2q9_scheme",
        "run_scheme_comparison",
        "default_algorithm_registry",
        "LogicalResourceEstimate",
    ],
)
def test_removed_experimental_symbols_are_not_exported(name: str) -> None:
    assert not hasattr(pq_cfd, name)


@pytest.mark.parametrize(
    "module_name",
    [
        "pq_cfd.d1q3_operator",
        "pq_cfd.d2q9_variants",
        "pq_cfd.scheme_comparison",
        "pq_cfd.study",
    ],
)
def test_removed_experimental_modules_are_gone(module_name: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)
