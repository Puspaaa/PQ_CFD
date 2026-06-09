# PQ CFD

Classical lattice Boltzmann baselines for a research-grounded project on resource estimation for computational fluid dynamics on fault-tolerant quantum computers.

The repo is intentionally lean. It keeps validated classical solvers and diagnostics only; quantum algorithms and resource estimates should be added only after a route note passes the benchmark, encoding, loading, and readout gates in `docs/implementation_plan.md`.

Future agents should start with `AGENTS.md`.

## Setup

```powershell
uv sync --all-extras --group dev
```

The project targets Python 3.12 through `.python-version`.

## Tests

```powershell
uv run pytest
```

## Baseline Solvers

```python
from pq_cfd import SimulationConfig, run_d1q3, run_d2q9

d1 = run_d1q3(
    SimulationConfig(
        grid_shape=(128,),
        steps=100,
        tau=0.8,
        initial_condition="sinusoidal",
        sample_interval=20,
        amplitude=0.02,
    )
)

d2 = run_d2q9(
    SimulationConfig(
        grid_shape=(32, 32),
        steps=30,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=10,
        amplitude=0.02,
    )
)

print(d1.metrics)
print(d2.metrics)
```

## Sweeps

```python
from pq_cfd import default_sweep_cases, run_sweep, write_sweep_csv

records = run_sweep(
    default_sweep_cases(
        d1_grids=(32, 64),
        d2_grids=((16, 16), (32, 32)),
        d1_tau_values=(0.8,),
        d2_tau_values=(0.8,),
    )
)
write_sweep_csv(records, ".cache/benchmarks/classical_sweep.csv")
```

## D2Q9 Diagnostics

```python
from pq_cfd import d2q9_diagnostic_cases, run_d2q9_diagnostics

cases = d2q9_diagnostic_cases(
    grids=((16, 16), (32, 32)),
    tau_values=(0.8,),
    amplitude=0.02,
)
records = run_d2q9_diagnostics(cases)

for record in records:
    print(record.grid_shape, record.validation_status, record.validation_blocker)
```

Diagnostics use a controlled-decay Taylor-Green setup, adjacent-grid observed order, and validation gates. A non-passing gate blocks quantum follow-up until the benchmark, operator, readout, and resource assumptions are explicit.

## Jupyter Notebooks

`notebooks/baseline_lbm.ipynb` is a quick-run Jupyter notebook for the D1Q3
and D2Q9 baselines. The QRE2 handoff notebooks are also kept as `.ipynb`
files so Bartiq/QREF and future quantum-tool visualizations can use normal
IPython display behavior. Install the notebook extra if needed:

```powershell
uv sync --extra notebook
```

Then open JupyterLab:

```powershell
uv run --extra notebook jupyter lab
```

From the WSL/Pixi environment:

```bash
pixi run jupyter-lab
pixi run notebook-execute
```

## Research Roadmap

Research material is split by purpose:

- `AGENTS.md`: operating instructions for future agents.
- `docs/implementation_plan.md`: roadmap, next milestones, route-note template, benchmark-card template, and gates.
- `docs/research_grounding_and_plan.md`: human-readable bibliography/corpus.
- `docs/research_landscape_data.js`: structured paper graph and canonical tags/relationships.
- `docs/research_mind_map.html`: official interactive visualization.
- `docs/qcfd_landscape_map.md`: static route-family map with Mermaid diagrams.

Future quantum/resource work starts with a route note, not with exploratory package layers.
