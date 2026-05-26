# PQ CFD

Classical lattice Boltzmann baselines for a stepwise quantum CFD research project.

The first milestone focuses on reproducible classical simulations that can later be mirrored as quantum-state emulations, explicit circuits, and resource estimates.

## Setup

```powershell
uv sync --all-extras --group dev
```

The project pins Python 3.12 through `.python-version` because scientific and quantum packages are usually better supported there than on bleeding-edge Python releases.

## Quick Start

```powershell
uv run pytest
```

```python
from pq_cfd import SimulationConfig, run_d1q3, run_d2q9

d1 = run_d1q3(SimulationConfig(grid_shape=(128,), steps=100, tau=0.8))
d2 = run_d2q9(
    SimulationConfig(
        grid_shape=(64, 64),
        steps=100,
        tau=0.8,
        initial_condition="taylor_green",
    )
)

print(d1.metrics)
print(d2.metrics)
```

The notebook `notebooks/baseline_lbm.ipynb` runs both benchmarks and plots the density/velocity fields.

## Classical Analysis

```python
from pq_cfd import default_sweep_cases, run_sweep, write_sweep_csv

records = run_sweep(default_sweep_cases(amplitude=0.02))
write_sweep_csv(records, ".cache/benchmarks/classical_sweep.csv")
```

The notebook `notebooks/classical_analysis.ipynb` runs the default D1Q3 and D2Q9 sweeps, writes CSV outputs, and plots accuracy, mass drift, and runtime.

`notebooks/d2q9_order_study.ipynb` audits observed D2Q9 Taylor-Green convergence order before changing the solver.

## End-to-End Study Framework

The study framework keeps CFD accuracy, quantum mapping assumptions, and resource estimates in one comparable schema.

```python
from pq_cfd import (
    SimulationConfig,
    controlled_decay_scheme_comparison_cases,
    default_algorithm_registry,
    default_quantum_operator_specs,
    default_scheme_comparison_cases,
    run_d1q3_classical_operator_emulation,
    run_scheme_comparison,
    validate_algorithm_registry,
)

registry = validate_algorithm_registry(default_algorithm_registry())

scheme_records = run_scheme_comparison(
    controlled_decay_scheme_comparison_cases(grids=((16, 16), (32, 32), (64, 64)))
)

operator_result = run_d1q3_classical_operator_emulation(
    SimulationConfig(grid_shape=(128,), steps=80, tau=0.8)
)

operator_specs = default_quantum_operator_specs()
```

The first-wave D2Q9 comparison includes BGK/SRT, barred-variable SRT, TRT, and MRT. The D1Q3 operator layer is classical operator emulation: it exposes flattened populations, a local dissipative collision matrix, and streaming as a permutation-like update, but it is not yet reversible, unitary, or block encoded.

Logical resource estimates must explicitly record conditioning, block-encoding normalization, postselection success probability, precision/error budget, observable tolerance, nonlinear treatment, and classical-comparison assumptions. Physical estimates are represented separately for Azure-style quantities such as physical qubits, runtime, code distance, T factories, T states, and failure budget.

D2Q9 order studies and scheme comparisons now carry validation-gate fields such as `validation_status`, `validation_blocker`, and `passed_for_quantum_followup`. If velocity convergence worsens under refinement, the framework reports `investigation_required`; this blocks circuit and resource-estimation work until the numerical issue is understood or a simpler validated target is chosen.
