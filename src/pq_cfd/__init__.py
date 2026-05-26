"""Classical LBM baselines for the PQ CFD project."""

from pq_cfd.analysis import (
    SweepCase,
    SweepRecord,
    default_d1q3_sweep_cases,
    default_d2q9_sweep_cases,
    default_sweep_cases,
    run_sweep,
    write_sweep_csv,
)
from pq_cfd.d1q3 import run_d1q3
from pq_cfd.d2q9 import run_d2q9
from pq_cfd.d2q9_diagnostics import (
    D2Q9DiagnosticAssessment,
    D2Q9DiagnosticCase,
    D2Q9DiagnosticRecord,
    assess_d2q9_diagnostics,
    d2q9_diagnostic_cases,
    observed_order,
    run_d2q9_diagnostics,
    steps_for_decay_exponent,
    write_d2q9_diagnostics_csv,
)
from pq_cfd.types import SimulationConfig, SimulationHistory, SimulationResult

__all__ = [
    "D2Q9DiagnosticAssessment",
    "D2Q9DiagnosticCase",
    "D2Q9DiagnosticRecord",
    "SimulationConfig",
    "SimulationHistory",
    "SimulationResult",
    "SweepCase",
    "SweepRecord",
    "assess_d2q9_diagnostics",
    "d2q9_diagnostic_cases",
    "default_d1q3_sweep_cases",
    "default_d2q9_sweep_cases",
    "default_sweep_cases",
    "observed_order",
    "run_d1q3",
    "run_d2q9",
    "run_d2q9_diagnostics",
    "run_sweep",
    "steps_for_decay_exponent",
    "write_d2q9_diagnostics_csv",
    "write_sweep_csv",
]
