# QCFD Implementation Roadmap

Latest roadmap date: 2026-06-02

This file is the practical handoff for both the project owner and future agents. It explains what to build next, what must be explained in notebooks, and what gates block quantum/resource code. Paper metadata lives in `docs/research_grounding_and_plan.md`; structured paper IDs, tags, reading statuses, and relationships live in `docs/research_landscape_data.js`; the official visual explorer is `docs/research_mind_map.html`.

The paper-anchored migration audit for selectively reusing the previous
`QCFD_3` attempt is `docs/qre2_migration_audit.md`. Treat that audit as the
traceability ledger for the first `QRE2` shifted-D2Q9 operator work: `QCFD_3`
is engineering evidence, while `QRE2` section and equation anchors are the
authority.

Project philosophy: keep technical depth high and cognitive load low. For each
new route concept, prefer one exact paper anchor, one compact equation, one
visual/operator object, and one falsifiable numerical check before adding
broader code structure.

## Current State

- The repository is intentionally lean: D1Q3 passive scalar LBM, D2Q9 BGK Taylor-Green LBM, benchmark sweeps, D2Q9 diagnostics, private QRE2 operator validation helpers, private SciPy sparse replays, and private Bartiq/QREF route bookkeeping.
- Tests currently cover public API stability, validation, solver accuracy, sweeps, and diagnostics.
- `notebooks/baseline_lbm.ipynb` is the pedagogical Jupyter entrypoint for the classical baseline. It explains D1Q3, D2Q9, Taylor-Green observables, and the diagnostic gate. The package code and tests remain the source of truth for implementation behavior.
- `notebooks/qre2_shifted_operator_handoff.ipynb` is the Jupyter supervision handoff for the private `QRE2` shifted-D2Q9 operator. It explains the `QCFD_3` adaptation, paper anchors, layout change, validation checks, and dependency/public-API guards.
- `docs/qre2_migration_audit.md` records which `QCFD_3` components can be adopted, adapted, deferred, or rejected for the first `QRE2` route, with paper anchors and validation requirements.
- Bartiq/QREF are promoted only for private symbolic bookkeeping, and SciPy sparse is promoted only for classical operator validation. No circuit code, public resource-estimation API, PsiQDK dependency, or route claim should be added before a route note passes the benchmark, encoding, loading, and readout gates below.

## QRE2 Pre-Carleman Gate

Current decision: the private `QRE2` shifted-D2Q9 route may advance to the
smallest dense `N_C=2` Carleman lift only after the following pre-Carleman
checks pass.

Validated scope:

- Corpus ID: `QRE2`; route is anchored to `sec:shifted`, `eq:g`,
  `eq:eq_shift_incompressible`, `eq:eq_shift_explicit`,
  `eq:LBE_col_shift_matrix`, `eq:F1`, `eq:F2`, and `eq:streaming`.
- Operator story: shifted moments, shifted equilibrium, direct collision and
  streaming, polynomial `F1/F2` matrix form, and periodic streaming permutation.
- Matrix checks: `S.T @ S = I`, direct shifted update equals polynomial
  matrix update on tiny D2Q9 states, and global `F2` couples same-site pairs
  only.
- Benchmark checks: selected Taylor-Green observables remain finite and
  low-Mach over a small sweep of `16x16`, `32x32`, `64x64` grids and
  `tau=0.7,0.8,0.9`.
- Notebook gate: `notebooks/qre2_shifted_operator_handoff.ipynb` executes in
  Jupyter, shows the operator equations, object ledger, sparsity visuals, local
  collision storyboard, and selected-observable sweep, while generated outputs
  stay in `.cache/notebooks/`.

Remaining caveats:

- This is a route-behavior comparison against the standard BGK D2Q9 baseline,
  not a claim that the shifted incompressible QRE2 update is algebraically
  identical to the baseline solver.
- No Carleman, linear-system, encoding, block-encoding, QLSA, measurement,
  resource-estimation, or circuit code is included in this gate.
- The next implementation step is a tiny dense Carleman lift validation, still
  private/internal and still without quantum packages.

## QRE2 Dense Carleman Lift Gate

Current implementation boundary: add only the private dense `N_C=2` discrete
Carleman lift for the validated shifted-D2Q9 polynomial map.

Allowed scope:

- Corpus IDs: `QRE2` for `sec:discrete_carleman`, `eq:Ckl`,
  `eq:carl_evol_d`, and `eq:LBE_recurrence`; `CAR7` as the D2Q9
  Carleman-LBM comparator; warnings `IO1`, `CAR15`, `CAR9`, `CAR19`, `IO4`,
  `IO5`, `IO7`, and `IO8`.
- Operator story: form the lifted state `y=[g, g^{otimes 2}]`, dense collision
  block matrix `C`, dense streaming block matrix `S_C=diag(S,S^{otimes 2})`,
  and dense propagator `P=S_C C` for tiny validation grids.
- Matrix checks: `N_C=1` recovers the linear-control stream-collide update;
  `N_C=2` first block matches the direct shifted polynomial update for one
  step and improves over `N_C=1` on a short tiny-grid run.
- Allocation guard: dense lifted matrices are refused above an explicit maximum
  dimension before allocation.

Remaining caveats:

- The first block of the truncated lift is a classical validation object, not a
  circuit, block encoding, QLSA solve, or resource estimate.
- No loading, oracle, normalization, success-probability, or measurement claim
  may be inferred from this gate. Those remain blocked by `IO1`, `CAR15`,
  `CAR9`, `CAR19`, `IO4`, `IO5`, `IO7`, and `IO8`.
- `CAR7` is route provenance and comparison context here, not a standalone
  implementation route.

## Milestone Status

Completed in the 2026-05-28 reset:

- Added root `AGENTS.md` with durable operating instructions.
- Rewrote this file as the implementation roadmap.
- Trimmed `docs/research_grounding_and_plan.md` back to a corpus document.
- Kept `docs/research_mind_map.html` as the official visualization.
- Updated `notebooks/baseline_lbm.ipynb` as a pedagogical Jupyter classical baseline.
- Completed the notebook handoff explaining D1Q3, D2Q9, Taylor-Green observables, diagnostics, and why route notes must precede quantum/resource code.

Next active work:

1. Write and compare the first route notes against the periodic D2Q9 Taylor-Green benchmark card.
   - Active route-note IDs: bounded/realistic QLBM resources (`QRE2`, `QRE4`), Carleman-LBM comparator (`CAR7`), and surrogate BGK collision comparator (`LBM14`).
   - Required I/O and encoding warning IDs: `IO4`, `IO5`, `IO7`, and `IO8`.
   - Gate: no route can advance to circuit or resource-estimation code until it states operator/update form, encoding, loading/reloading, selected readout observables, smallest classical validation, resource quantities, comparison papers, blockers, and an advance/defer decision.

2. Use the first benchmark/observable card as the common comparison surface: periodic D2Q9 Taylor-Green.
   - Candidate paper IDs: `QRE2`, `QRE4`, `LBM14`, `CAR7`.
   - Current classical reference: `run_d2q9` plus `run_d2q9_diagnostics`.
   - Observables: velocity field error, vorticity error, kinetic-energy error, divergence RMS, max Mach, mass drift.
   - Gate: a route cannot advance from this card unless it states encoding, data loading, readout, and resource-comparison assumptions.

3. Keep LBM/QLBM route comparison document-first.
   - First compare route notes, not packages.
   - Start with route families that can be tied to the D2Q9/ADE baseline: bounded QLBM resources (`QRE2`, `QRE4`), ADE/time marching (`LBM4`, `LBM10`, `LBM11`, `LBM18`), collision alternatives (`LBM8`, `LBM12`, `LBM14`, `LBM23`), and basis/streaming primitives (`PRIM7`, `PRIM8`, `LBM24`).
   - Only after this comparison choose the smallest implementation route.

4. Add resource tooling only after a route is concrete.
   - Qualtran, Azure Resource Estimator, Qiskit, qlbm tooling, or custom circuit libraries can be introduced only when the selected route note identifies the operator, observable, precision target, loading model, success probability, and comparison papers.

## Benchmark Card Template

Use this template before implementing or extending a benchmark.

```markdown
### Benchmark: <name>

- Corpus IDs:
- Purpose:
- Classical reference:
- Grid and domain:
- Timestep/steps:
- Fluid parameters: tau, viscosity/diffusivity, Mach/Re regime if applicable
- Initial condition:
- Boundary condition:
- Observables:
- Validation metrics and tolerances:
- Candidate route IDs:
- Encoding candidates:
- Data-loading assumption:
- Readout/sample assumption:
- Quantum follow-up gate:
- Current status:
```

### Benchmark: Periodic D2Q9 Taylor-Green

- Corpus IDs: `QRE2`, `QRE4`, `LBM14`, `CAR7`.
- Purpose: first 2D incompressible-flow baseline for comparing LBM/QLBM and Carleman-LBM route assumptions.
- Classical reference: `pq_cfd.run_d2q9`, `pq_cfd.run_d2q9_diagnostics`, and the analytic low-Mach Taylor-Green decay model.
- Grid and domain: periodic square lattice, currently tested on refinement sets such as `16x16`, `32x32`, `64x64`, and `128x128`.
- Timestep/steps: diagnostics choose steps to match a controlled analytic decay exponent.
- Fluid parameters: `tau > 0.5`; lattice viscosity is `c_s^2 (tau - 1/2)` with `c_s^2 = 1/3`; low-Mach amplitudes only.
- Initial condition: Taylor-Green vortex velocity with pressure-compatible density perturbation.
- Boundary condition: periodic.
- Observables: velocity relative L2 error, vorticity relative L2 error, kinetic-energy relative error, divergence RMS, max Mach, density deviation, mass drift.
- Validation metrics and tolerances: use `run_d2q9_diagnostics`; non-passing diagnostics block quantum follow-up.
- Candidate route IDs: bounded/realistic QLBM resources (`QRE2`, `QRE4`), surrogate BGK collision (`LBM14`), and Carleman-LBM comparison (`CAR7`).
- Encoding candidates: unresolved; must compare amplitude, basis/qubit, and route-specific encodings with `IO4`, `IO5`, `IO7`, and `IO8` before circuit work.
- Data-loading assumption: unresolved; full field loading is not assumed cheap.
- Readout/sample assumption: selected observables only; full-field readout remains a negative control.
- Quantum follow-up gate: route note must specify operator form, encoding, data loading/reloading, readout, normalization/success probability if relevant, and resource quantities.
- Current status: classical solver and diagnostics exist; notebook explanation is complete; first route-note comparison is the active milestone.

## Route Note Template

Use this template before adding quantum algorithms, resource estimators, or route-specific packages.

```markdown
### Route: <name>

- Corpus IDs:
- Reading status:
- Benchmark card:
- Route family:
- What evolves: field, distribution, lifted polynomial state, stochastic observable, pressure solve, or statistic
- Operator/update form:
- Nonlinearity treatment:
- Boundary/forcing treatment:
- Encoding:
- Data loading and reloading:
- Readout and sample complexity:
- Normalization/success probability:
- Error budget and tolerance:
- Smallest classical validation:
- Resource quantities to estimate:
- Comparison papers:
- Main blockers:
- Decision:
```

### Route: Bounded And Realistic QLBM Resources

- Corpus IDs: `QRE2`, `QRE4`, with encoding/readout checks from `IO4`, `IO5`, `IO7`, and `IO8`.
- Reading status: `QRE2` is Read First; `QRE4` is Read With; `IO4` and `IO5` are Read First; `IO7` and `IO8` are Read With for encoding and fluid-data resource warnings.
- Benchmark card: Periodic D2Q9 Taylor-Green.
- Route family: LBM/QLBM fault-tolerant resource route.
- What evolves: D2Q9 distribution populations and their low-Mach macroscopic velocity/density moments.
- Operator/update form: stream-collide LBM-style timestep; route note must extract the exact update, resource-count template, and selected-observable path from `QRE2`, then record which boundary/forcing extensions from `QRE4` are out of scope for the periodic first card.
- Nonlinearity treatment: treat nonlinear incompressible-flow terms only through the bounded assumptions stated by `QRE2`; do not generalize to arbitrary Navier-Stokes without a separate note.
- Boundary/forcing treatment: periodic boundaries only for the first card; walls, inlets, outlets, forcing, cavity flow, and cylinder flow remain `QRE4` comparison items.
- Encoding: unresolved; compare amplitude, basis/qubit, and route-specific encodings using `IO4`, `IO5`, `IO7`, and `IO8` before choosing a circuit representation.
- Data loading and reloading: unresolved and not assumed cheap; record whether the route needs initial-state loading only, repeated field reloading, or oracle/block-encoding access.
- Readout and sample complexity: selected observables only: velocity moments/error proxies, vorticity, kinetic energy, divergence RMS, max Mach, density deviation, and mass drift; full-field readout is a negative-control baseline.
- Normalization/success probability: unresolved; extract any block-encoding normalization, postselection, amplification, or failure-probability assumptions from `QRE2`.
- Error budget and tolerance: start from the existing D2Q9 diagnostic pass/fail gates and add route-specific precision only after `QRE2` resource tolerances are extracted.
- Smallest classical validation: construct no quantum code yet; first validate a tiny classical D2Q9 stream-collide operator or matrix representation against `run_d2q9` for one and several low-Mach Taylor-Green steps.
- Resource quantities to estimate: logical qubits, gate count, T count/depth if applicable, circuit depth, timestep scaling, loading cost, readout/sample count, and later physical qubits/runtime only after a logical route is explicit.
- Comparison papers: compare directly against `CAR7` and `LBM14` on the same benchmark; use `QRE3` only as an I/O/readout warning comparator if drag or force observables enter scope.
- Main blockers: unresolved encoding, data loading/reloading, normalization/success probability, selected-observable sample cost, and whether `QRE4` boundary/forcing constants affect the periodic case.
- Decision: advance only as a route-note extraction task; defer all packages, circuits, and resource-estimator code.

### Route: Carleman-LBM Comparator

- Corpus IDs: `CAR7`, with loading/readout warnings from `IO4`, `IO5`, `IO7`, and `IO8`.
- Reading status: `CAR7` is Reference Only/Foundation for moderate-Re D2Q9 Carleman-LBM; read only the sections needed for formulas, truncation, and circuit-depth warnings unless this comparator becomes active.
- Benchmark card: Periodic D2Q9 Taylor-Green.
- Route family: Carleman-linearized LBM comparison route.
- What evolves: a lifted polynomial state built from D2Q9 distribution variables.
- Operator/update form: second-order or otherwise explicitly stated Carleman truncation of the LBM update; route note must identify the smallest lifted update matrix before implementation.
- Nonlinearity treatment: nonlinearity is represented by finite-order Carleman lifting; truncation order, dimension growth, and moderate-Re assumptions are blockers rather than implementation details.
- Boundary/forcing treatment: periodic first; no boundary extension until the periodic lifted operator is specified and compared with `QRE4` assumptions.
- Encoding: unresolved; compare lifted-state amplitude encoding against basis/qubit alternatives using `IO4`, `IO5`, `IO7`, and `IO8`.
- Data loading and reloading: first-class blocker; do not assume loading the lifted state or matrix access oracle is cheap.
- Readout and sample complexity: selected Taylor-Green observables only; full lifted-state or full-field reconstruction is a negative-control baseline.
- Normalization/success probability: unresolved; the note must record matrix norm, block-encoding normalization, condition/success assumptions, and any amplification requirements before resource work.
- Error budget and tolerance: classical diagnostic tolerances apply first; add truncation and linear-solver precision only after the lifted operator is written down.
- Smallest classical validation: build no quantum code yet; first write a tiny classical lifted D2Q9 update for a minimal periodic grid and compare one-step and short-time moment evolution to `run_d2q9`.
- Resource quantities to estimate: lifted dimension, sparsity/oracle assumptions, normalization, logical qubits, T/gate counts if block encoding is chosen, timestep scaling, loading cost, and selected-observable readout cost.
- Comparison papers: compare against bounded QLBM (`QRE2`, `QRE4`) and surrogate collision (`LBM14`); bring in data-loading papers only when the lifted state access model is explicit.
- Main blockers: lifted dimension blowup, truncation validity, conditioning/normalization, repeated loading, and readout cost.
- Decision: keep as comparator; defer implementation until the QLBM route note exposes a concrete operator to compare against.

### Route: Surrogate BGK Collision Comparator

- Corpus IDs: `LBM14`, with encoding/readout checks from `IO4`, `IO5`, `IO7`, and `IO8`.
- Reading status: `LBM14` is Watch/P2; read it only as a collision-cost alternative unless learned surrogate collision becomes central.
- Benchmark card: Periodic D2Q9 Taylor-Green.
- Route family: collision-alternative QLBM route.
- What evolves: local D2Q9 distribution populations through a learned/surrogate BGK collision component, paired conceptually with a streaming step.
- Operator/update form: surrogate local collision circuit or classical surrogate map for the BGK collision; the route note must separate local collision approximation from lattice streaming and boundary handling.
- Nonlinearity treatment: nonlinearity is approximated in the collision surrogate; mass, symmetry, stability, and low-Mach validity constraints must be documented from `LBM14`.
- Boundary/forcing treatment: periodic first; lid-driven cavity and other validations from `LBM14` stay comparison context, not first implementation scope.
- Encoding: unresolved; local population encoding must be compared against route-level field/state encoding using `IO4`, `IO5`, `IO7`, and `IO8`.
- Data loading and reloading: unresolved; a low-depth collision circuit does not remove the cost of preparing local populations or reloading the global state.
- Readout and sample complexity: selected Taylor-Green diagnostics only; do not use full-field tomography as the default validation path.
- Normalization/success probability: unresolved; record whether the surrogate is unitary, approximate, postselected, variational, or otherwise requiring normalization/resource overhead before code.
- Error budget and tolerance: separate surrogate collision approximation error from D2Q9 discretization and diagnostic tolerances.
- Smallest classical validation: build no quantum code yet; first test a classical local collision surrogate or explicit local collision matrix on D2Q9 populations and verify mass/symmetry constraints plus Taylor-Green diagnostic observables.
- Resource quantities to estimate: collision circuit depth/gates, qubits per node or local register, streaming overhead, loading/reloading cost, surrogate training/selection assumptions, and selected-observable readout samples.
- Comparison papers: compare against bounded QLBM (`QRE2`, `QRE4`) and Carleman-LBM (`CAR7`) only after the local collision and global streaming assumptions are separated.
- Main blockers: learned-circuit scope, integration with global streaming, measurement/reinitialization assumptions, loading/readout cost, and absence of an end-to-end FTQC resource claim.
- Decision: watch/comparator only; defer implementation unless collision cost becomes the dominant blocker after the bounded QLBM note.

## Gates

- Benchmark gate: do not implement a route until the benchmark and observable are named.
- Encoding gate: do not trust a speedup claim until the state representation and initialization/readout costs are explicit.
- Readout gate: full-field readout is a negative control unless the cited route justifies it.
- Route-comparison gate: compare at least two plausible routes on the same benchmark before committing to one.
- Tooling gate: beyond the current private SciPy sparse and Bartiq/QREF bookkeeping helpers, do not add Qiskit, Qualtran, qlbm tooling, Azure estimator code, PsiQDK, or custom circuit layers until a route note identifies exactly why that tool is needed.

## Verification Routine

- Run `uv run pytest` after code or notebook-facing API changes.
- Execute notebooks into `.cache/notebooks/` for verification instead of committing outputs.
- Run the corpus/graph ID consistency check after corpus edits.
- Confirm `pq_cfd.__all__` remains small unless the roadmap explicitly calls for a public API change.

## Working Defaults

- Prefer short, explicit documents over parallel planning files.
- Prefer explanatory notebooks for research understanding and tested package code for reusable behavior.
- Prefer selected observables over reconstructing whole velocity or density fields.
- Treat newer papers as route-setting only when they change a benchmark, observable, encoding, loading, readout, or resource estimate.
