# Chronological Implementation Plan

Latest plan date: 2026-05-27

This plan is chronological by dependency order, not by paper publication date. The bibliography in `docs/research_grounding_and_plan.md` is the source of truth for paper metadata and inclusion status. The structured graph in `docs/research_landscape_data.js` is the source of truth for canonical IDs, aliases, citation keys, reading statuses, multi-label tags, and paper-to-paper relations. The landscape wiki in `docs/qcfd_landscape_map.md` is the source of truth for branch-level relationships; `docs/research_mind_map.html` is the local interactive explorer.

## Stage 0: Literature Governance And Lean Classical Baseline

Goal: keep the repository lean while making future work traceable to papers.

Required papers:

- `QRE1` Zhuang: full-stack FTQC Navier-Stokes claim to compare against.
- `QRE2` Jennings: bounded nonlinear LBM resource route.
- `QRE3` Penuel: drag-force resource warning and bottleneck audit.
- `QRE4` Jennings/Airbus-PsiQuantum: realistic incompressible-flow extension of the bounded LBM route.
- `QRE5` Meng: end-to-end rapidly-distorted-turbulence route with resource accounting.
- `SURV1`, `SURV2`, `SURV3`: orientation only, not implementation authority.

Reading-status rule:

- Start from the `Minimum Reading Path` in `docs/research_mind_map.html`.
- Treat `Read First` and `Read With` papers as decision inputs.
- Treat `Read If Building` papers as route-specific work, not general onboarding.
- Treat `Covered By Newer`, `Reference Only`, and `Watch` papers as dimmed unless a route card explicitly needs them.

Implementation scope:

- Keep the existing D1Q3 and D2Q9 baselines.
- Keep D2Q9 controlled-decay diagnostics.
- Do not add quantum/resource package APIs until a route card passes Stage 1 and Stage 2.

Acceptance gate:

- Classical solver and diagnostics tests pass.
- Any proposed task cites canonical bibliography IDs or short aliases and states whether it is bibliography work, route-card work, operator work, readout work, or resource-estimation work.
- Route-card work preserves reading status, tags, and `coveredBy` / `dependsOn` / `readBefore` metadata when it introduces or reclassifies a paper.

## Stage 1: Benchmark And Observable Cards

Goal: choose benchmarks and observables before choosing algorithms.

Benchmark cards to create:

- Linear ADE with boundaries: `LBM4`, `LBM5`.
- Periodic D2Q9 Taylor-Green decay: `QRE2`, `QRE4`, `LBM14`, `CAR7`.
- Incompressible pressure-Poisson or cavity-flow card: `QLSA1`, `QLSA2`.
- Drag or force toy benchmark: `QRE3`, `QRE4`, `IO2`.
- Nonlinear PDE/flow benchmark card: `CAR11`, `CAR1`, `CAR4`, `LBM9`, `LBM12`.
- Rapidly distorted turbulence statistics card: `QRE5`, `IO2`, `SURV1`.

Each card must specify:

- grid, timestep, viscosity/tau, Mach/Re regime, boundary condition;
- initial condition and classical reference;
- selected observable and tolerance;
- state encoding candidates;
- data-loading assumption;
- readout assumption;
- candidate route IDs.

Acceptance gate:

- At least two route alternatives exist for each benchmark before implementation.
- Full-field readout is marked as a negative control unless a cited paper justifies it.
- Every `P0` route is either tied to a benchmark card or explicitly deferred with a reason.

## Stage 2: Encoding, Data Loading, And Readout Gate

Goal: make I/O and encoding choices blockers before operator implementation.

Required papers:

- `IO4` Kosel: compare encoding/resource implications for quantum CFD.
- `IO5` Rathore: fluid-simulation encoding taxonomy.
- `IO1` Demirdjian: data loading for Carleman-linearized LBE.
- `IO2` Goldack: statistical velocity-field readout.
- `IO3` Zhang: approximate data loading, if CFD state structure supports it.
- `WATCH1` Zhao: watch only for compressed classical-data ideas.
- `QLSA1` Inger: approximate QST assumptions for pressure-Poisson route.

Implementation scope:

- Add a route-card section for encoding: amplitude, basis, qubit, tensor-network, and hybrid.
- Add explicit loading/readout line items to every route card.
- Build no circuit until the card states normalization, success probability, and observable extraction.

Acceptance gate:

- Every active route states why its encoding is chosen.
- Every active route lists loading cost and readout/sample cost.
- Any route requiring repeated reloading is compared against `LBM1` and `LBM4`.

## Stage 3: ADE And LBM Route Comparison

Goal: compare modern LBM-family routes in a small, modular way before committing to one.

Candidate routes:

- `LBM2` Bastida-Zamora OSSLBM: one-step simplified LBM.
- `LBM3` Xiao fractional-step QLBM: stable incompressible/thermal route.
- `LBM8` Duong denoising collision: projector/denoising collision route.
- `LBM9` Wang nonlinear QLBM: node-level ensemble/lattice-gas route.
- `LBM10` Wawrzyniak dynamic-circuit QLBM: ADE no-reinitialization route with mid-circuit adaptation.
- `LBM11` Nagel no-reinitialization QLBM: multi-timestep ADE without intermediate state extraction.
- `LBM12` Zeng linearized-collision QLBM: latest modular Navier-Stokes collision route.
- `LBM13` Lee QLBM-frugal: streamfunction/vorticity multi-circuit resource reduction.
- `LBM14` Lacatus surrogate BGK collision: learned local collision circuit route.
- `LBM1` Ray trapped-ion QLBM: nonuniform 3D advection and readout/reloading bottleneck.
- `LBM4` He time-marching ADE/LBM: measurement-free and global linear-system alternatives.
- `LBM5` Chen LCHS ADE: boundary-condition circuits.
- `LBM6` Xiao LKS: predecessor retained because `LBM3` critiques it.
- `LBM7` Liu linear-equilibrium QLBM: SVD/LCU collision and bounce-back details.

Implementation order:

1. Build classical matrix/operator representations for ADE and D2Q9 toy cases.
2. Write an operator note for each route: state dimension, update form, normalization, success probability, and observable path.
3. Compare route notes before adding circuit code.
4. Implement only the smallest route that passes Stage 2 and has a clear benchmark card.

Acceptance gate:

- At least two LBM-family alternatives are compared on the same benchmark.
- Hybrid classical steps are labeled and included in runtime/resource accounting.
- Denoising/reinitialization/tomography assumptions are explicit.
- Every route card includes multi-label tags from the bibliography, including at least one formulation tag, one method tag, one I/O tag, and one resource/hardware maturity tag.

## Stage 4: Nonlinear Routes Beyond LBM

Goal: compare nonlinear alternatives without mixing their assumptions.

Candidate routes:

- `QRE5` Meng: rapidly distorted turbulence through LCHS and selected statistics.
- `CAR11` Bharadwaj: homotopy algorithm for nonlinear PDEs and flow problems.
- `CAR1` Cappelli SNS: Schrodinger-Navier-Stokes and Hamilton-Jacobi/Carleman route.
- `CAR2` Cappelli steady-state Carleman: lowest-order steady-state route.
- `CAR3` Jemcov KvN: unitary PDF route for fluid/plasma dynamics.
- `CAR4` Bravyi: noisy dissipative nonlinear dynamics.
- `CAR10` Li: nonlinear stochastic differential equations.
- `CAR5` Wang: pivot-shifted Carleman.
- `CAR6`, `CAR7`, `CAR8`: Carleman foundations and route comparisons.
- `CAR9` Lin: warning checklist for linear-representation failure modes.

Implementation order:

1. For each route, state whether it evolves fields, distributions, polynomial lifts, stochastic observables, or steady states.
2. Apply `CAR9` as a failure-mode checklist to all Carleman/KvN-like routes.
3. Compare nonlinear route cards on dimension blowup, convergence condition, conditioning, and observable extraction.
4. Implement only a toy nonlinear operator after Stage 2 and Stage 3 results identify a route worth resource-estimating.

Acceptance gate:

- The route states how nonlinearity is represented.
- Dimension blowup and convergence assumptions are explicit.
- The route is compared against `QRE1`, `QRE2`, and `QRE3` before resource work.

## Stage 5: Resource-Estimation Stack

Goal: produce reproducible logical and physical resource estimates only after the route, operator, and observable are explicit.

Required papers/tools:

- `QRE1`, `QRE2`, `QRE3`: comparison targets.
- `QRE4`, `QRE5`: latest realistic-flow and turbulence-statistics comparison targets.
- `PRIM5` Qualtran: logical resource representation.
- `PRIM6` Azure Quantum Resource Estimator: physical resources.
- `PRIM1` QSVT, `PRIM2` linear ODE, `PRIM3` PDE algorithms, `PRIM4` surface code: primitives used only when invoked by a route.

Implementation order:

1. Express the chosen operator as a logical resource model.
2. Record block-encoding normalization, precision, failure budget, and success probability.
3. Produce logical qubits, T count, T depth, and circuit depth.
4. Convert to physical qubits and runtime under documented QEC assumptions.
5. Compare against `QRE1`, `QRE2`, and `QRE3`.

Acceptance gate:

- Resource output lists logical qubits, T count/depth, circuit depth, normalization, success probability, error budget, physical qubits, runtime, and readout/sample count.
- The estimate names which assumptions are inherited from papers and which are project choices.

## Stage 6: Route Selection And Comparative Report

Goal: choose the next implementation route based on evidence, not novelty alone.

Required outputs:

- one benchmark card per active route;
- one operator/readout note per route;
- one resource-estimation note for any route that reaches Stage 5;
- a comparative report ranking routes by implementability, resource credibility, and risk.

Decision rule:

- A newer paper gets priority only when it changes a route, benchmark, observable, encoding, readout, or resource estimate.
- An older paper remains active only when it provides a primitive or warning that a newer route depends on.
- No route advances if it cannot state its data-loading, readout, and resource-estimation assumptions.
