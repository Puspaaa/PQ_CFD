# QRE2 Migration Audit From QCFD_3

Latest audit date: 2026-06-02

This document records what can be reused from
`C:/Users/NishchayVORA/Documents/QCFD_3` for the first paper-anchored route in
this repository. The authority order is:

1. Corpus IDs in `docs/research_grounding_and_plan.md` and
   `docs/research_landscape_data.js`.
2. Exact paper sections and equation labels from `QRE2`.
3. `QCFD_3` code and tests as engineering evidence only.

The immediate target is a private shifted-D2Q9 operator validation for `QRE2`,
followed only by the smallest dense `N_C=2` discrete Carleman validation.
Linear-system, quantum-circuit, and resource-estimation code remains deferred
until the lifted recurrence is validated against the paper and the periodic
D2Q9 Taylor-Green benchmark card.

## Paper Anchors

| Topic | Corpus IDs | Paper anchor |
| --- | --- | --- |
| Shifted variable | `QRE2` | Problem formulation, shifted incompressible LBE, `sec:shifted`, `eq:g` |
| Shifted collision and streaming | `QRE2` | `sec:shifted`, `eq:LBE_col_shift`, `eq:LBE_str_shift` |
| Shifted incompressible equilibrium | `QRE2` | `sec:shifted`, `eq:eq_shift`, `eq:eq_shift_incompressible`, `eq:eq_shift_explicit` |
| Polynomial collision matrices | `QRE2` | `sec:shifted`, `eq:LBE_col_shift_matrix`, `eq:F1`, `eq:F2`, `eq:F1_loc`, `eq:F2_loc` |
| Periodic streaming matrix | `QRE2` | `sec:shifted`, `eq:LBE_str_shift_matrix`, `eq:streaming` |
| Discrete Carleman lift | `QRE2`, comparator `CAR7` | Discrete Carleman embedding, `sec:discrete_carleman`, `eq:Ckl`, `eq:carl_evol_d`, `eq:LBE_recurrence` |
| Linear systems | `QRE2` | Linear system formulation, `sec:linear_system`, `eq:linearHistory`, `eq:linearFinal` |
| Encoding and block encodings | `QRE2`, warnings `IO4`, `IO5`, `IO7`, `IO8` | Quantum algorithm implementation, `sec:encoding`, `sec:block_encodings` |
| QLSA and measurements | `QRE2`, warnings `IO4`, `IO5`, `IO7`, `IO8` | `sec:QLS`, `sec:measurement` |
| Boundary/realistic-flow extensions | `QRE4` | Defer until periodic shifted operator is validated |
| Surrogate collision alternative | `LBM14` | Comparator only; do not implement before QRE2 shifted operator gate |

## Migration Decisions

| QCFD_3 artifact | Paper anchor | Decision | PQ_CFD target | Required validation |
| --- | --- | --- | --- | --- |
| `docs/paper_understanding.md` | `QRE2`, especially `sec:shifted`, `sec:discrete_carleman`, `sec:linear_system`, `sec:encoding`, `sec:measurement` | Adapt as audit evidence, not as source of truth | This document plus route notes in `docs/implementation_plan.md` | Every adopted claim must carry a corpus ID and paper anchor |
| `src/lbe_quantum/shifted.py::shift_to_g`, `unshift_to_fbar` | `QRE2 sec:shifted`, `eq:g` | Adopt concept, rewrite layout | Private shifted module only | Shift/unshift round trip on D2Q9 arrays shaped `(9, nx, ny)` |
| `src/lbe_quantum/shifted.py::shifted_moments` | `QRE2 sec:shifted`, `eq:eq_shift_incompressible` | Adopt concept, rewrite layout | Private shifted module only | Recover density fluctuation and incompressible velocity from constructed shifted populations |
| `src/lbe_quantum/shifted.py::shifted_equilibrium` | `QRE2 sec:shifted`, `eq:eq_shift_incompressible`, `eq:eq_shift_explicit` | Adopt formula, rewrite layout | Private shifted module only | Match an independently computed D2Q9 equilibrium expression |
| `src/lbe_quantum/shifted.py::build_F1_F2` | `QRE2 sec:shifted`, `eq:LBE_col_shift_matrix`, `eq:F1`, `eq:F2`, `eq:F1_loc`, `eq:F2_loc` | Adapt; keep dense matrices tiny | Private shifted module only | Local/global shapes and one-step direct-vs-polynomial equality |
| `src/lbe_quantum/shifted.py::build_streaming_matrix` | `QRE2 sec:shifted`, `eq:streaming` | Adapt to current D2Q9 ordering | Private shifted module only | Matrix is a permutation and matches periodic `np.roll` streaming |
| `src/lbe_quantum/shifted.py::step_shifted_direct`, `step_shifted_matrix` | `QRE2 sec:shifted`, `eq:LBE_col_shift`, `eq:LBE_str_shift`, `eq:LBE_col_shift_matrix` | Adopt behavior, rewrite layout | Private shifted module only | One-step and short-trajectory equality between direct and matrix forms |
| `src/lbe_quantum/carleman.py` | `QRE2 sec:discrete_carleman`, `eq:Ckl`, `eq:carl_evol_d`, `eq:LBE_recurrence`; comparator `CAR7`; warnings `IO1`, `CAR15`, `CAR9`, `CAR19`, `IO4`, `IO5`, `IO7`, `IO8` | Adapt only the dense `N_C=1/2` recurrence idea; rewrite layout and guards | Private `_qre2_carleman` module only | First lifted block must recover the shifted polynomial update for one step, stay finite on a short tiny-grid run, and improve over the `N_C=1` linear-control baseline |
| `src/lbe_quantum/linear_systems.py` | `QRE2 sec:linear_system`, `eq:linearHistory`, `eq:linearFinal` | Defer | Future linear-system validation only after Carleman lift | Dense solve must reproduce recurrence before any QLSA discussion |
| `src/lbe_quantum/readout.py` | `QRE2 sec:measurement`; warnings `IO4`, `IO5`, `IO7`, `IO8` | Defer and re-audit | Future observable/readout note | Selected observable cost must be stated; full-field readout remains a negative control |
| `src/lbe_quantum/quantum.py` | `QRE2 sec:encoding`, `sec:block_encodings`, `sec:QLS`; warnings `IO4`, `IO5`, `IO7`, `IO8` | Reject for now | None | No Qiskit, block-encoding, QLSA, or resource code before gates pass |
| `src/lbe_quantum/__init__.py` broad exports | No direct paper authority | Reject | None | `pq_cfd.__all__` remains limited to baseline and diagnostic APIs |
| QCFD_3 notebooks | `QRE2` narrative support | Defer | Future pedagogical notebook only after tests pass | Notebook must explain equations, observables, numerical checks, and research reason |

## First Implementation Boundary

The first allowed code migration was only:

- corpus ID: `QRE2`;
- benchmark surface: periodic D2Q9 Taylor-Green from `docs/implementation_plan.md`;
- module visibility: private internal Python module, no public API export;
- operator: shifted D2Q9 direct stream-collide and equivalent dense polynomial
  matrix form on tiny grids;
- validation: direct update equals the `F1`/`F2` polynomial matrix update for
  one step and several steps.

Everything else remains deferred:

- `QRE2` linear systems, state encoding, block encodings, QLSA, measurement
  extraction, and T-gate estimates;
- `QRE2` Carleman lifts beyond dense guarded `N_C=2` validation;
- `QRE4` wall, inlet, outlet, forcing, cavity, and cylinder extensions;
- `CAR7` comparator implementation;
- `LBM14` surrogate collision implementation;
- Qiskit, Qualtran, qlbm tooling, Azure estimator code, and custom circuit APIs.

## Second Implementation Boundary

The second allowed code migration is only:

- corpus IDs: `QRE2`, with comparator/warning IDs `CAR7`, `IO1`, `CAR15`,
  `CAR9`, `CAR19`, `IO4`, `IO5`, `IO7`, and `IO8`;
- benchmark surface: the same periodic D2Q9 Taylor-Green surface from
  `docs/implementation_plan.md`;
- module visibility: private internal Python module, no public API export;
- operator: dense direct-sum Carleman state `y=[g, g^{otimes 2}]`, dense
  collision lift, dense streaming lift, and dense propagator on tiny grids;
- validation: the lifted first block matches the shifted polynomial update for
  one step, and the `N_C=2` short-run first-block error improves over the
  `N_C=1` linear-control baseline.

## Compatibility Notes

- `QCFD_3` stores D2Q9 populations with velocity as the last axis; current
  `PQ_CFD` stores D2Q9 populations as `(9, nx, ny)`. Direct array copying would
  silently change indexing, so all adopted code must be rewritten around the
  current layout.
- Dense global `F2` matrices scale as `d x d^2`. They are validation objects
  for tiny grids, not scalable implementation objects.
- The shifted incompressible LBE is not algebraically identical to the existing
  standard BGK `run_d2q9` update. Its role here is to validate the QRE2 operator
  route, then compare observables against the existing classical diagnostics.
