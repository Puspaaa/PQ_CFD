# Quantum CFD Research Log

This log captures the starting research choices for the project. It should be updated whenever we compare algorithmic options, choose a benchmark, or change the implementation path.

## Starting Decision

Selected route:

1. Classical D1Q3 LBM baseline.
2. Classical D2Q9 Taylor-Green LBM baseline.
3. Quantum-style statevector emulation of the same update rules.
4. Explicit Qiskit/QLBM circuit design.
5. Fault-tolerant resource estimation.

The first milestone intentionally excludes quantum circuits and resource estimation. The goal is to build trustworthy classical references before adding quantum-specific assumptions.

## Option Comparison

### Direct Navier-Stokes Quantum Algorithms

Direct Navier-Stokes algorithms are attractive because they target the governing equations directly, but current proposals tend to rely on strong assumptions, oracle access, linearization, amplitude amplification, or restricted flows. Gaitan's Navier-Stokes algorithm demonstrated a nozzle-flow test case, but it is not a general industrial CFD workflow.

Source: https://www.nature.com/articles/s41534-020-00291-0

### Quantum Lattice Boltzmann Method

QLBM is the best initial implementation target because classical LBM already decomposes into local collision and streaming steps. Those operations are easier to reason about as reversible/permutation-like components than a full finite-volume Navier-Stokes solver. The `qlbm` framework is also an active software reference for QLBM circuit generation and benchmarking.

Sources:
- https://arxiv.org/abs/2411.19439
- https://qcfd-lab.github.io/qlbm/

### Carleman-LBM

Carleman-linearized LBM is one of the more serious fault-tolerant quantum CFD routes because it trades nonlinearity for a larger linear system. Recent work argues for potential advantage in specific regimes, but follow-up end-to-end analyses emphasize convergence, condition-number, time-stepping, and readout bottlenecks. We should treat Carleman-LBM as a later research branch after the basic LBM reference solvers are validated.

Sources:
- https://arxiv.org/abs/2303.16550
- https://arxiv.org/abs/2512.03758

### Hybrid Quantum-Classical Pressure Solves

Hybrid schemes that use quantum linear solvers for pressure Poisson or related linear subproblems are closer to near-term hardware, especially with variational solvers. Their main risk is that state preparation, repeated readout, optimizer cost, and noise can dominate any benefit. These are useful later as a comparison branch, not the first baseline.

Context source: https://link.springer.com/article/10.1007/s42496-025-00269-1

### Resource Estimation

Resource estimation should wait until we have concrete circuits or reliable logical operation counts. Microsoft Quantum Resource Estimator is the planned first tool because it can estimate logical qubits, physical qubits, runtime, T factories, and related fault-tolerance quantities.

Source: https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation

## Current Assumptions

- Prioritize clarity and validation over speed.
- Use periodic boundaries first.
- Use low-Mach, stable regimes only.
- Use D1Q3 to expose the minimal update rule and D2Q9 to expose a meaningful 2D fluid benchmark.
- Keep all benchmarks small enough to run in local tests and notebooks.

## Milestone 2 Decision: Classical Characterization First

The next milestone is a classical analysis harness rather than quantum emulation. Recent QLBM work identifies practical obstacles around data encoding, observable readout, repeated timesteps, and circuit depth. These issues cannot be evaluated responsibly unless the underlying classical benchmark behavior is already quantified.

The analysis harness records accuracy, mass conservation, runtime, grid size, relaxation time, and initial condition for D1Q3 and D2Q9 cases. D1Q3 remains the minimal target for later reversible/statevector mapping. D2Q9 remains the first physically meaningful 2D fluid benchmark.

Relevant sources:

- Algorithmic Advances Towards a Realizable Quantum Lattice Boltzmann Method: https://arxiv.org/abs/2504.10870
- qlbm documentation: https://qcfd-lab.github.io/qlbm/
- Quantum lattice Boltzmann method for simulating nonlinear fluid dynamics: https://arxiv.org/abs/2502.16568
- End-to-end quantum algorithm analysis for nonlinear fluid dynamics: https://www.sciencestack.ai/paper/2512.03758

## Milestone 3 Decision: D2Q9 Taylor-Green Validation

Before quantum emulation, the D2Q9 baseline needs a stronger convergence protocol. The Taylor-Green vortex is periodic and has a closed-form low-Mach reference, so it isolates solver accuracy without introducing boundary-condition choices. The validation suite compares grid refinements at a controlled viscous decay exponent rather than at an arbitrary shared timestep count.

The validation diagnostics now track velocity error, vorticity error, kinetic-energy error, divergence, Mach number, density range, mass drift, runtime, and a stability flag. This is the classical evidence we will use when deciding whether a later quantum formulation is still solving the intended flow problem.

Relevant sources:

- Taylor-Green vortex as a closed-form periodic validation case: https://docs.aerosim.io/nassu/validation/cases/00_taylor_green_vortex/index.html
- Taylor-Green vortex as a standard validation benchmark with exact Navier-Stokes solution: https://pmc.ncbi.nlm.nih.gov/articles/PMC9988764/
- D2Q9 LBM model reference: https://docs.tclb.io/models/flow/d2q9/d2q9/

## Next Operator Design Note

The next mapping milestone starts with D1Q3 classical operator emulation, not Qiskit circuits. The state is represented as flattened populations, streaming is represented as a permutation-like classical update, and collision is represented as a local linear dissipative matrix. This is useful for step-by-step equivalence, but it is not yet a quantum operator model because it has no reversible embedding, block encoding, fixed-point arithmetic model, success probability, or readout model.

## Milestone 4 Decision: Formal D2Q9 Accuracy Audit

The current D2Q9 BGK solver is already the standard periodic SRT/BGK LBM form with the usual second-order equilibrium expansion and viscosity relation. Rather than replace it immediately, the project now audits the observed order of accuracy on Taylor-Green refinements.

Candidate solver variants remain on the table:

- Current SRT/BGK D2Q9: simplest reference and easiest future quantum comparison.
- Incompressible He-Luo style equilibrium: can reduce compressibility artifacts when density fluctuations dominate.
- TRT/MRT collision: improves stability and can reduce non-hydrodynamic mode errors, but complicates the later quantum operator model.
- Boundary-focused second-order schemes: important for Couette, Poiseuille, cavity, and obstacle flows, but not relevant to the current periodic Taylor-Green benchmark.

The recommendation is to implement a variant only after the order audit identifies the dominant error source.

## Milestone 5 Decision: End-to-End Study Framework

The project now uses an evidence ladder so broad exploration does not drift away from the fault-tolerant resource-estimation objective:

1. literature card,
2. classical benchmark,
3. operator/state emulation,
4. explicit circuit,
5. logical resource counts,
6. physical fault-tolerant estimate,
7. end-to-end comparison against classical CFD cost.

The new registry records comparable study cards for classical LBM variants, QLBM routes, Carleman-LBM, direct Navier-Stokes algorithms, hybrid pressure-Poisson solvers, and spectral transport. Every card has a status, evidence stage, benchmark target, resource assumptions, and sources. This keeps advanced options visible without forcing every option into implementation.

The first implemented comparison wave is deliberately narrow:

- D2Q9 BGK/SRT remains the reference.
- D2Q9 barred-variable SRT makes the trapezoidal transformed-distribution formulation explicit. For the current unforced, equilibrium-initialized Taylor-Green benchmark it is expected to be algebraically equivalent to standard SRT when matched to the same viscosity, but it is the correct bookkeeping model for later forcing, boundary, and non-equilibrium initialization studies.
- D2Q9 TRT adds the smallest useful extra collision freedom through even/odd relaxation.
- D2Q9 MRT adds raw-moment relaxation and exposes the cost of moment transforms.
- D1Q3 operator emulation is the first bridge toward quantum-state and circuit mapping.

The registry also includes literature-card placeholders for incompressible-equilibrium, central-moment/cumulant, and entropic/regularized LBM variants. These are not implemented in the first wave because they add extra local transforms or nonlinear stabilization choices; they should be promoted only if BGK/barred/TRT/MRT diagnostics show a specific accuracy or stability bottleneck they are designed to address.

Resource estimates are also staged. The internal schema is intentionally expanded in Milestone 6 to include conditioning, normalization, postselection, precision, readout, nonlinear treatment, and classical-comparison assumptions. External tools such as Azure Quantum Resource Estimator and Qualtran should only be used after a method has either concrete circuits or defensible logical-count formulas.

Relevant sources:

- qlbm framework: https://arxiv.org/abs/2411.19439
- qlbm documentation: https://qcfd-lab.github.io/qlbm/
- QLBM end-to-end bottleneck analysis: https://arxiv.org/abs/2512.03758
- Carleman-LBM: https://arxiv.org/abs/2303.16550
- Azure Quantum Resource Estimator output metrics: https://learn.microsoft.com/en-us/azure/quantum/overview-resource-estimator-output-data
- Qualtran resource-counting documentation: https://qualtran.readthedocs.io/en/latest/resource_counting/qubit_counts.html
- central-moment MRT comparison context: https://www.sciencedirect.com/science/article/pii/S0045793018301889
- entropic LBM review: https://www.sciencedirect.com/science/article/pii/S0045793023001093

## Milestone 6 Decision: Correct Framework Before Circuits

An independent supervisor review found that the study framework risked premature confidence: it stored quantum-resource-looking fields before modeling the bottlenecks that dominate fault-tolerant QCFD estimates. The correction milestone tightens the framework before any circuit work.

Changes made:

- D1Q3 is now described as classical operator emulation. The old `run_d1q3_operator_model` name remains as a compatibility alias, but the preferred API is `run_d1q3_classical_operator_emulation`.
- A `QuantumOperatorSpec` records whether an operator has reversible embedding, block encoding, normalization, success probability, fixed-point arithmetic, readout model, and known gaps. The current D1Q3 spec is explicitly not circuit-ready.
- `LogicalResourceEstimate` now requires condition number, block-encoding normalization, postselection success probability, nonlinear treatment, Carleman truncation order when relevant, precision bits, error budget, observable tolerance, classical baseline cost, timestep count, and observable repetitions.
- `PhysicalResourceEstimate` separates Azure-style physical outputs: physical qubits, logical qubits, runtime, code distance, T factories, T states, and failure budget.
- D2Q9 diagnostics now include explicit grid spacing, grid-scaled vorticity/divergence, divergence RMS, density-weighted kinetic energy, and incompressible-reference kinetic energy.
- TRT/MRT/SRT tests now include local conservation and prescribed relaxation checks. Barred SRT now has non-equilibrium transform/reconstruction tests, but remains labeled as BGK-equivalent for the current unforced Taylor-Green benchmark.
- Algorithm cards are now literature cards with source date, core claim, assumptions, benchmark relevance, bottlenecks, caveats, and promotion blockers. No-reinitialization QLBM is scoped to D1Q3-style linear transport until evidence supports nonlinear D2Q9.

This correction keeps the project aligned with the resource-estimation objective: circuits remain blocked until a method has a defensible quantum operator specification and resource assumptions that include conditioning, normalization, success probability, precision, readout, and classical comparison.

Relevant sources:

- End-to-end nonlinear fluid bottleneck analysis: https://arxiv.org/abs/2512.03758
- Realizable QLBM concerns: https://arxiv.org/abs/2504.10870
- No-reinitialization QLBM scope: https://arxiv.org/abs/2510.05965
- Azure Resource Estimator output data: https://learn.microsoft.com/en-us/azure/quantum/overview-resource-estimator-output-data
- Qualtran resource counting: https://qualtran.readthedocs.io/en/latest/resource_counting/qubit_counts.html

## Milestone 7 Decision: Validation Gates and Readiness Guardrails

A second supervisor review found that remaining issues were now concentrated in two places: D2Q9 convergence was still non-passing at fine refinement, and the framework still allowed some unknown quantum/resource quantities to look definite. This milestone adds guardrails rather than circuits.

Changes made:

- D2Q9 order studies now attach validation fields to each row: `validation_status`, `validation_blocker`, `min_velocity_observed_order`, and `passed_for_quantum_followup`.
- The default order gate marks a study as `investigation_required` when velocity error increases under refinement or adjacent velocity order is negative. A study is `passed` only when all tested velocity orders meet the default threshold of `1.5`.
- First-wave D2Q9 scheme comparisons now support controlled-decay grid sweeps for BGK/SRT, barred SRT, TRT, and MRT, and they carry the same convergence-style status fields.
- Stability decisions now include divergence RMS and maximum density deviation thresholds, so stable finite outputs are no longer treated as sufficient validation evidence by themselves.
- `QuantumOperatorSpec` now leaves normalization and success probability as unknown when block encoding is incomplete. Circuit readiness requires complete reversible embedding, block encoding, fixed-point arithmetic, readout model, error-budget status, known normalization, known success probability, and no known gaps.
- Logical resource estimates are rejected unless the algorithm card has reached `logical_resource_counts`; physical estimates are rejected unless a logical estimate is present and the card has reached `physical_ft_estimate`.
- Physical estimates now require positive physical/logical qubits, positive runtime, positive code distance, valid failure probability, estimator provenance, and logical-estimate provenance.

Current implication:

- D2Q9 remains a classical-diagnosis target, not a validated quantum follow-up target, until the velocity-convergence blocker is resolved.
- D1Q3 remains the simpler fallback for operator-emulation research, but it is still classical operator emulation until a reversible or block-encoded construction exists.
- Unknown quantum quantities must remain `None`/unknown rather than being filled with optimistic defaults.

This keeps the project aligned with the fault-tolerant resource-estimation objective by making non-passing validation states explicit before circuit work begins.
