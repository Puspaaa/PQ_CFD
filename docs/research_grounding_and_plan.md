# Research Bibliography And Corpus

Latest scan date: 2026-05-26

Project objective: estimate the logical and physical resources needed to run computational fluid dynamics workloads on fault-tolerant quantum computers. Every implementation step must be tied to a concrete paper-backed method, CFD benchmark, operator construction, observable/readout path, and fault-tolerance model.

This is the canonical bibliography and corpus analysis document. It is intentionally latest-first because quantum CFD is moving quickly. Older papers remain only when they define a primitive, proof technique, benchmark, or fault-tolerance assumption that current papers still rely on.

Companion documents:

- `docs/qcfd_landscape_map.md`: start-here route-map wiki with Mermaid diagrams.
- `docs/implementation_plan.md`: dependency-ordered implementation plan and acceptance gates.
- `docs/research_mind_map.html`: optional interactive branch map of the active papers.

## Decision Rules

1. No quantum implementation starts from an informal idea. It must name the route label and cite the paper-backed departure point.
2. Every route must specify benchmark, state encoding, evolution operator, nonlinearity treatment, boundary model, readout path, and error budget before resource estimates are produced.
3. Full-field readout is a negative-control baseline unless a paper justifies it. Prefer selected observables, force/lift/drag, moments, norms, spectra, structure functions, or amplitude-estimation-compatible quantities.
4. Claims of advantage must include time stepping, condition number, block-encoding normalization, postselection/success probability, precision, state preparation, data loading, and data extraction costs.
5. Peer-reviewed papers can seed implementation. Preprints can seed experiments, but the maturity label must remain visible.
6. Classical baselines stay lean. They exist to validate benchmarks and observables, not to grow into a scheme registry.

## Literature Scan Protocol

Scan date: 2026-05-26.

Primary sweep:

- arXiv categories: `quant-ph`, `physics.flu-dyn`, `physics.comp-ph`, `math.NA`, `cs.NA`, `math-ph`.
- CFD terms: `Navier-Stokes`, `fluid dynamics`, `CFD`, `lattice Boltzmann`, `LBM`, `Boltzmann`, `advection-diffusion`, `Burgers`, `Poisson`, `pressure`, `incompressible`, `turbulence`, `vorticity`, `SPH`.
- Quantum/resource terms: `quantum`, `fault-tolerant`, `resource estimation`, `HHL`, `QLSA`, `block encoding`, `QSVT`, `Carleman`, `data loading`, `readout`, `tomography`, `QST`, `shadow tomography`, `amplitude estimation`.

Procedure:

1. Sweep arXiv metadata for category and keyword combinations, sorted by submission date.
2. Force-check exact arXiv IDs named by the project owner or found through related-paper trails.
3. Cross-check publisher pages when a paper has a journal version.
4. Put every relevant hit into one of four bins: core, adjacent, foundation, or excluded/watch.
5. Promote a paper to core only if it changes route selection, benchmark choice, data loading, readout, or resource-estimation assumptions.

Known scan limitation: the arXiv API can rate-limit broad query loops. The sweep therefore records both the query protocol and a curated appendix so future updates can be rerun and compared.

## Miss Audit

The corpus is maintained with an explicit miss audit because this field is moving too quickly for one-shot keyword search to be reliable.

Miss patterns already observed:

- Encoding papers were missed until `encoding`, `amplitude encoding`, `basis encoding`, and `qubit encoding` were promoted to first-class terms. This is why `IO4` Kosel and `IO5` Rathore were added after the first sweep.
- Collision/operator papers can be missed when they do not include `resource estimation` or `Navier-Stokes` in the title. This is why `LBM8` Duong was restored after the role-label rewrite.
- Realistic-flow companion papers can be missed when they share authors with an already-included resource paper. This is why `QRE4` Jennings/Airbus-PsiQuantum is now included separately from `QRE2`.
- Turbulence papers can be missed when they use linear turbulence models rather than full Navier-Stokes wording. This is why `QRE5` Meng is now included for rapidly distorted turbulence and LCHS resource accounting.
- No-reinitialization and dynamic-circuit QLBM papers can be missed when they are framed as ADE improvements instead of CFD resource papers. This is why `LBM10` Wawrzyniak and `LBM11` Nagel are now included.
- Warning/foundation papers can be missed by latest-first scans. This is why `CAR9` Lin is kept as a required failure-mode checklist for Carleman and Koopman-von Neumann routes.
- Adjacent nonlinear-dynamics papers can be missed when they say `stochastic differential equations`, `homotopy`, or `flow problems` rather than CFD. This is why `CAR10` Li and `CAR11` Bharadwaj are included.
- API rate limiting can truncate broad arXiv sweeps. Exact arXiv IDs named by the project owner or found through citation trails must always be force-checked.

Additional recurring search terms:

- `encoding`, `amplitude encoding`, `basis encoding`, `qubit encoding`, `tensor network encoding`.
- `homotopy`, `flow problems`, `nonlinear PDE`, `stochastic differential equation`, `Koopman`, `KvN`.
- `collision operator`, `denoising collision`, `surrogate collision`, `dynamic circuits`, `irreversible`, `reinitialization`, `no reinitialization`, `observable extraction`.
- `rapidly distorted turbulence`, `Reynolds stress`, `velocity spectrum`, `non-trivial incompressible flows`, `flow past a cylinder`, `inlets`, `outlets`, `external forcing`.

## Labeling And Priority Scheme

The stable ID prefix is only a citation handle, not a complete classification. Papers must also carry multi-label tags so that one paper can be filtered as, for example, `LBM`, `FTQC`, `Resource-Estimation`, `Encoding-Strategy`, and `Readout` at the same time. The user's `Carlman` label is normalized to `Carleman`; keep `Carlman` only as a search alias, not as a canonical tag.

Role labels:

- `QRE*`: full-stack resource estimates, resource-warning papers, or explicit advantage claims.
- `LBM*`: LBM, QLBM, OSSLBM, ADE, time-marching, and boundary-condition LBM routes.
- `CAR*`: Carleman, Schrodingerization, Koopman-von Neumann, and nonlinear embedding routes.
- `QLSA*`: HHL, pressure-Poisson, QLSA, and linear-system CFD subroutines.
- `IO*`: data loading, readout, tomography, shadow tomography, selected observables.
- `PRIM*`: foundations such as QSVT, block encoding, linear ODE/PDE algorithms, and surface-code assumptions.
- `SURV*`: reviews and taxonomies.
- `WATCH*`: adjacent papers worth tracking but not yet central to FTQC CFD resource estimation.

Canonical multi-label vocabulary:

- Formulation labels: `LBM`, `QLBM`, `LBE`, `ADE`, `Navier-Stokes`, `Pressure-Poisson`, `Boltzmann`, `Lattice-Gas`, `Lattice-Kinetic-Scheme`, `SPH`, `Vortex`, `Vortex-Method`, `Turbulence`, `Rapid-Distortion-Theory`, `Spectral`, `D2Q9`, `Streamfunction-Vorticity`, `PDE`, `ODE`, `Stochastic-PDE`.
- Method labels: `Carleman`, `Schrodinger-Navier-Stokes`, `Koopman-von-Neumann`, `LCHS`, `QLSA`, `HHL`, `QSVT`, `QAE`, `QST`, `QPE`, `Homotopy`, `Stochastic`, `Noisy-Dynamics`, `Dynamic-Circuit`, `Mid-Circuit-Measurement`, `Denoising-Collision`, `Projector-Collision`, `Surrogate-Collision`, `Linearized-Collision`, `Linear-Collision`, `OSSLBM`, `Fractional-Step`, `Linearization`, `SVD`, `LCU`, `PREP-SELECT`, `Approximate-Loading`, `Amplitude-Amplification`, `Global-Time-System`, `Tensor-Network`, `VQLS`.
- Resource and hardware labels: `FTQC`, `FTQC-Emulator`, `Near-Term-Hardware`, `Hybrid`, `Trapped-Ion`, `Superconducting`, `Resource-Estimation`, `Resource-Reduction`, `Logical-Resources`, `Physical-Resources`, `Gate-Counts`, `Error-Correction`, `Surface-Code`, `T-Count`, `Circuit-Depth`.
- Input/output labels: `Encoding-Strategy`, `Amplitude-Encoding`, `Basis-Encoding`, `Qubit-Encoding`, `Tensor-Encoding`, `Spatiotemporal-Encoding`, `Data-Loading`, `State-Preparation`, `Readout`, `Observable-Selection`, `Tomography-Avoidance`, `Shadow-Tomography`, `No-Reinitialization`, `Data-Reloading`, `Boundary-Conditions`.
- Benchmark and observable labels: `Taylor-Green`, `Lid-Driven-Cavity`, `Flow-Past-Cylinder`, `Poiseuille`, `Couette`, `Drag`, `Velocity-Moments`, `Structure-Functions`, `Reynolds-Stress`, `Velocity-Spectrum`, `Vorticity`, `Natural-Convection`, `External-Forcing`, `Linear-Acoustics`, `Moderate-Re`, `Low-Mach`.
- Status labels: `Core`, `Adjacent`, `Foundation`, `Watch`, `Review`, `Tooling`, `Warning`, `Peer-Reviewed`, `Preprint`.

When a repeated tag is missing from this vocabulary, add it here before using it broadly in the matrix.

Priority labels:

- `P0`: read now; latest core paper that changes route choice, resources, data loading, readout, or feasibility.
- `P1`: read before implementing the corresponding route.
- `P2`: read when testing a specific benchmark or alternative.
- `P3`: older foundation/reference; read only when needed by a route.
- `Watch`: adjacent/latest paper that may matter later but does not yet change the FTQC CFD roadmap.

## First Reading Path

Read in this order before adding new code:

1. Full-stack claims and warnings: `QRE1`, `QRE2`, `QRE3`, `QRE4`, `QRE5`.
2. Latest LBM family: `LBM1`, `LBM2`, `LBM3`, `LBM4`, `LBM5`, `LBM8`, `LBM9`, `LBM10`, `LBM11`, `LBM12`.
3. Input/output bottlenecks: `IO1`, `IO2`, `IO3`, `IO4`, `IO5`.
4. Alternative nonlinear embeddings: `CAR1`, `CAR2`, `CAR3`, `CAR4`, `CAR10`, `CAR11`, with `CAR9` as the warning paper.
5. Pressure-Poisson/QLSA route: `QLSA1`.
6. Foundations only as needed: `PRIM1`, `PRIM2`, `PRIM3`, `PRIM4`.

## Core And Reference Matrix

| ID | Lead author + title | Date / revision | Maturity | Priority | Route role | What we extract | Risks | Supersedes or challenges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QRE1 | Zhuang 2025 - [A Pathway to Practical Quantum Advantage in Solving Navier-Stokes Equations](https://arxiv.org/abs/2509.08807) | arXiv submitted 2025-09-10. | Preprint | P0 | Full-stack FTQC Navier-Stokes resource claim. | Spectral I/O strategy, synthesized circuit, optimized error-correction protocol, concrete physical-qubit/runtime claim. | Very large claim; must be compared against independent bottleneck papers and its I/O assumptions. | Challenges the pessimism of QRE3; must be checked against QRE2 and drag/readout costs. |
| QRE2 | Jennings 2025 - [An end-to-end quantum algorithm for nonlinear fluid dynamics with bounded quantum advantage](https://arxiv.org/abs/2512.03758) | arXiv submitted 2025-12-03. | Preprint | P0 | Constructive but bounded nonlinear LBM resource route. | End-to-end accounting, Reynolds scaling, gate-count template, selected-observable framing. | New preprint; advantage is bounded and high-error-tolerance dependent. | Challenges broad exponential-speedup narratives; complements QRE1 with a more cautious bound. |
| QRE3 | Penuel 2024 - [Detailed assessment of calculating drag force with quantum computers](https://arxiv.org/abs/2406.06323) | arXiv submitted 2024-06-10; revised 2025-12-08. | Preprint | P0 | Drag-force QRE and bottleneck audit. | Cost categories for grid, timestep, block encoding, drag readout, T gates, and logical qubits. | Specific route and observable, not a universal no-go result. | Challenges QRE1-style advantage claims unless I/O and timestep costs are explicit. |
| QRE4 | Jennings 2025/2026 - [Simulating non-trivial incompressible flows with a quantum lattice Boltzmann algorithm](https://arxiv.org/abs/2512.05781) | arXiv submitted 2025-12-05; AIAA SciTech 2026 paper. | Preprint / conference paper | P0 | Realistic-flow companion to the bounded LBM resource route. | Walls, inlets, outlets, external forcing, driven Taylor-Green, lid-driven cavity, flow past a cylinder, and complexity-cost preservation. | Companion to QRE2 rather than independent validation; constants and physical resource implications still need extraction. | Promotes boundary/forcing handling from future work to a core requirement for QLBM route cards. |
| QRE5 | Meng 2025/2026 - [Toward end-to-end quantum simulation of rapidly distorted turbulence](https://arxiv.org/abs/2511.18802) | arXiv submitted 2025-11-24; Journal of Computational Physics online 2026-03-27. | Peer reviewed / in press | P0 | End-to-end turbulence statistics and resource route via LCHS. | Initial turbulent-state preparation, LCHS evolution, Reynolds-stress and velocity-spectrum measurements, qubit/depth resource estimates. | Rapid distortion theory is linear and not full Navier-Stokes turbulence; applicability to nonlinear turbulence must be bounded. | Adds a turbulence-specific route that is not LBM, Carleman, or pressure-Poisson. |
| IO1 | Demirdjian 2026 - [Quantum Data Loading for Carleman Linearized Systems: Application to the Lattice-Boltzmann Equation](https://arxiv.org/abs/2605.00302) | arXiv submitted 2026-05-01; revised 2026-05-15. | Preprint | P0 | Data loading and LCU construction for Carleman-linearized LBE. | LCNU-to-LCU framework, PREP/SELECT T-cost estimates, dependence on Carleman order and velocity count. | Very new; must test whether loading cost fits chosen CFD benchmark. | Promotes data loading to a first-class gate for all Carleman/LBE resource claims. |
| IO4 | Kosel 2026 - [Resource Implications of Different Encodings for Quantum Computational Fluid Dynamics](https://arxiv.org/abs/2604.05577) | arXiv submitted 2026-04-07. | Preprint | P0 | Encoding/resource comparison for quantum CFD. | Tradeoffs among amplitude, basis, and qubit encodings; initialization/readout cost framing; QLBM encoding implications. | Encoding analysis must be tied to an actual benchmark and observable before resource claims. | Challenges any route that assumes state encoding is a minor implementation detail. |
| IO5 | Rathore 2026 - [Encoding strategies for quantum enhanced fluid simulations: opportunities and challenges](https://arxiv.org/abs/2604.24694) | arXiv submitted 2026-04-27. | Preprint / perspective | P0 | Encoding taxonomy for quantum fluid simulation. | Basis, amplitude, tensor-network, and hybrid encoding tradeoffs; near-term and FTQC opportunity/risk map. | Perspective-style paper; may not provide enough circuit-level cost for implementation by itself. | Supersedes the older Rathore context row for encoding decisions; `SURV3` remains broad HPC background. |
| LBM1 | Ray 2026 - [Quantum Lattice Boltzmann Solutions for Transport under 3D Spatially Varying Advection on Trapped Ion Hardware](https://arxiv.org/abs/2604.28121) | arXiv submitted 2026-04-30. | Preprint / hardware demo | P0 | Hardware-oriented QLBM for nonuniform 3D advection. | Readout/reloading bottleneck, MPS shadow tomography idea, wall-boundary method. | Near-term hardware route, not automatically FTQC advantage. | Challenges earlier QLBM work to handle realistic velocity fields and scalable readout. |
| LBM2 | Bastida-Zamora 2026 - [Quantum algorithm for the lattice Boltzmann method with applications on real quantum devices](https://arxiv.org/abs/2603.02127) (OSSLBM) | arXiv submitted 2026-03-02. | Preprint | P0 | One-Step Simplified LBM route. | OSSLBM operator decomposition, linear acoustics case, hybrid nonlinear Navier-Stokes loop. | Hybrid and not yet a full FTQC resource estimate. | Challenges older QLBM designs by making the one-step formulation explicit and modular. |
| LBM3 | Xiao 2026 - [A Stable and General Quantum Fractional-Step Lattice Boltzmann Method for Incompressible Flows](https://arxiv.org/abs/2603.00558) | arXiv submitted 2026-02-28. | Preprint | P0 | Fractional-step QLBM for incompressible and thermal flows. | Quantum predictor/classical corrector split, high-Re stability comparison, 3D benchmark set. | Hybrid corrector complicates fault-tolerant advantage claims. | Challenges fixed-relaxation QLBM and the earlier LKS instability at high Reynolds number. |
| LBM4 | He 2026 - [Time-marching representation based quantum algorithms for the LBM of ADE](https://arxiv.org/abs/2602.09799) | arXiv submitted 2026-02-10. | Preprint | P0 | Measurement-free ADE/LBM time-marching framework. | Sequential evolution route, global linear-system route, low-Mach stability proof. | Linear ADE only; resource effects depend on normalization and readout. | Challenges measurement/reinitialization-heavy QLBM workflows. |
| LBM5 | Chen 2026 - [Quantum circuits for the advection-diffusion equation with boundary conditions based on LCHS](https://arxiv.org/abs/2605.17542) | arXiv submitted 2026-05-17. | Preprint | P1 | Boundary-condition and LCHS route for ADE. | Robin, Dirichlet, Neumann, and periodic boundary circuit construction; fault-tolerant emulator validation. | Linear PDE route, not nonlinear CFD by itself. | Challenges ADE papers without explicit boundary-condition handling. |
| LBM6 | Xiao 2025 - [Quantum Lattice Kinetic Scheme for Solving Two-dimensional and Three-dimensional Incompressible Flows](https://arxiv.org/abs/2505.10883) | arXiv submitted 2025-05-16. | Preprint | P1 | Earlier LKS route for adjustable viscosity. | Modified equilibrium distribution with adjustable viscosity, TGV and cavity-flow benchmarks. | Superseded in stability by LBM3 according to the later authors. | Kept because LBM3 explicitly builds on and critiques it. |
| LBM7 | Liu 2026 - [Quantum Lattice Boltzmann Method based on linear equilibrium distribution functions](https://www.frontiersin.org/journals/mechanical-engineering/articles/10.3389/fmech.2025.1717775/full) | Received 2025-10-02; accepted 2025-11-05; published 2026-01-16. | Peer reviewed | P1 | Linear-equilibrium QLBM with SVD/LCU collision. | D2Q9 register layout, SVD/LCU collision, bounce-back boundaries, Couette/Poiseuille benchmarks. | Linear equilibrium simplification may limit nonlinear/high-Re claims. | Challenges any route that ignores explicit boundary and collision circuit construction. |
| LBM8 | Duong 2026 - [Quantum Lattice Boltzmann with Denoising Collision Operators](https://arxiv.org/abs/2604.09997) | arXiv submitted 2026-04-11. | Preprint | P0 | Denoising/projector collision route for QLBM. | Projector collision, coherent multi-timestep motivation, reference-state sensitivity tests. | Hydrodynamic validity and FTQC resource cost still need reproduction. | Challenges QLBM routes that rely on tomography or reinitialization to handle irreversible collision effects. |
| LBM9 | Wang 2025 - [Quantum lattice Boltzmann method for simulating nonlinear fluid dynamics](https://arxiv.org/abs/2502.16568) | arXiv submitted 2025-02-23; npj Quantum Information published 2025-12-13. | Peer reviewed | P1 | Nonlinear QLBM via node-level ensemble lattice-gas description. | Linear collision treatment for nonlinear fluid dynamics, H-step stabilization, vortex-pair and decaying-turbulence benchmarks. | Resource estimates and FTQC I/O accounting are not the paper's main deliverable. | Forces comparison between ensemble/lattice-gas QLBM and the QRE2 bounded-incompressible-LBM route. |
| LBM10 | Wawrzyniak 2025 - [Dynamic Circuits for the Quantum Lattice-Boltzmann Method](https://arxiv.org/abs/2502.02131) / linearized QLBM for ADE | arXiv submitted 2025-02-04; Computer Physics Communications published 2025-12. | Peer reviewed | P1 | Dynamic-circuit ADE/QLBM route with reduced reinitialization. | Mid-circuit measurements, adaptive collision, deterministic unitary collision, arbitrary velocity-set extension, no probabilistic LCU failure. | Dynamic circuits and mid-circuit measurement assumptions must be translated carefully into FTQC resource models. | Challenges measurement/reinitialization-heavy ADE routes and should be compared with LBM4 and LBM11. |
| LBM11 | Nagel 2025/2026 - [Quantum Lattice Boltzmann Method for Multiple Time Steps Without Reinitialization for Linear Advection-Diffusion Problems](https://arxiv.org/abs/2510.05965) | arXiv submitted 2025-10-07; Computer Physics Communications published 2026-01-18. | Peer reviewed | P1 | Multi-timestep QLBM without intermediate state extraction. | Time-qubit construction, periodic ADE circuits, amplitude-decay discussion, final-only sampling strategy. | Linear ADE and periodic boundaries only; probability decay and final readout still need route-specific accounting. | Makes `No-Reinitialization` a core label for LBM/ADE route comparisons. |
| LBM12 | Zeng 2026 - [A quantum lattice Boltzmann method for solving the Navier-Stokes systems with a linearized non-equilibrium collision operator and modular circuit](https://www.sciengine.com/doi/10.1007/s10409-025-25741-x) | Published 2026-05-05. | Peer reviewed | P1 | Latest modular QLBM for Navier-Stokes with linearized non-equilibrium collision. | Adjustable relaxation, unitary-friendly collision treatment, lid-driven cavity, natural convection, modular circuit structure. | Linearized collision and hybrid/state-reinitialization assumptions may restrict high-Re or FTQC claims. | Adds a latest peer-reviewed Navier-Stokes QLBM route that must be compared against LBM3, LBM7, and LBM9. |
| LBM13 | Lee 2024/2026 - [A multiple-circuit approach to quantum resource reduction with application to the quantum lattice Boltzmann method](https://arxiv.org/abs/2401.12248) | arXiv submitted 2024-01-22; Future Generation Computer Systems 2026. | Peer reviewed | P2 | QLBM-frugal resource-reduction route. | Stream-function/vorticity split, two-circuit Navier-Stokes strategy, CX/gate-depth reduction, lid-driven cavity benchmark. | Still depends on tomography/readout and near-term resource measures; not a full FTQC estimate. | Useful resource-reduction comparator for LBM2, LBM3, and QLSA pressure routes. |
| LBM14 | Lacatus 2025/2026 - [Surrogate Quantum Circuit Design for the Lattice Boltzmann Collision Operator](https://arxiv.org/abs/2507.12256) | arXiv submitted 2025-07-16; International Journal for Numerical Methods in Engineering published 2026. | Peer reviewed | P2 | Learned surrogate circuit for BGK collision. | Low-depth local D2Q9 collision circuit, mass/symmetry constraints, Taylor-Green and lid-driven-cavity validation. | QML surrogate route; current integration still needs measurement/reinitialization and does not prove FTQC advantage. | Important collision-operator alternative to denoising, LCU, and Carleman collision routes. |
| IO2 | Goldack 2026 - [Computing Statistical Properties of Velocity Fields on Current Quantum Hardware](https://arxiv.org/abs/2601.10166) | arXiv submitted 2026-01-15. | Preprint / hardware demo | P0 | Observable/readout for velocity-field statistics. | Central moments, structure functions, ansatz-based statistical readout, tomography avoidance. | 1D proof of concept; near-term mitigation does not equal FTQC resource estimate. | Challenges full-state readout defaults and supports selected statistical observables. |
| IO3 | Zhang 2026 - [AQER: a scalable and efficient data loader for digital quantum computers](https://arxiv.org/abs/2602.02165) | arXiv submitted 2026-02-02; ICLR 2026 reference. | Conference preprint | P1 | Adjacent approximate data-loading framework. | Entanglement-based loading bounds, approximate loader tradeoffs, fidelity/gate-efficiency language. | Not CFD-specific; relevance depends on whether CFD states have exploitable structure. | Challenges exact-loading assumptions; complements IO1. |
| WATCH1 | Zhao 2026 - [Exponential quantum advantage in processing massive classical data](https://arxiv.org/abs/2604.07639) | arXiv submitted 2026-04-08. | Preprint | Watch | Adjacent classical-data access/readout alternative. | Oracle sketching and classical-shadows language for avoiding loading/readout bottlenecks. | Machine-learning setting, not CFD simulation. | Watch for ideas that may transfer to compressed CFD observables. |
| WATCH2 | Meng 2025/2026 - [Simulating fluid vortex interactions on a superconducting quantum processor](https://arxiv.org/abs/2506.04023) | arXiv submitted 2025-06-04; Nature Communications published 2026. | Peer reviewed / hardware demo | Watch | Vortex-method hardware evidence. | Spatiotemporal encoding, leapfrogging vortex experiment, vortex-level observables, superconducting hardware constraints. | Data-driven vortex model, tomography, and small coherent-vortex setting; not a grid-CFD FTQC estimate. | Watch if the project adds vortex/Lagrangian reduced-order benchmarks. |
| CAR1 | Cappelli 2026 - [Schrodinger-Navier-Stokes Equation for the Quantum Simulation of Navier-Stokes Flows](https://arxiv.org/abs/2604.11113) | arXiv submitted 2026-04-13. | Preprint | P0 | SNS/Hamilton-Jacobi/Carleman tensor-network route. | Why the SNS dissipator is hard, Hamilton-Jacobi workaround, tensor-network Carleman embedding. | New route; classical emulation evidence must be reproduced. | Challenges LBM-only planning by adding a genuine Navier-Stokes formulation route. |
| CAR2 | Cappelli 2026 - [Lowest order Carleman linearization for steady state fluid flow simulations](https://arxiv.org/abs/2605.23380) | arXiv submitted 2026-05-22. | Preprint | P1 | Latest steady-state Carleman improvement. | Evidence that second-order truncation can capture steady states for moderate-Re 2D flows. | Very new; steady-state focus may not cover transient observables. | Challenges the assumption that low-order Carleman only captures early transients. |
| CAR3 | Jemcov 2026 - [Unitary discretization of the Koopman-von Neumann equation for quantum simulation of fluid and plasma dynamics](https://arxiv.org/abs/2605.19187) | arXiv submitted 2026-05-18. | Preprint | P1 | KvN unitary embedding for fluid/plasma dynamics. | Weyl-ordered generator, summation-by-parts discretization, absorbing layer, triad validations. | Measurement-stage limitations remain; spectrally truncated setting. | Challenges Carleman-only nonlinear embeddings and adds a unitary PDF route. |
| CAR4 | Bravyi 2025 - [Quantum simulation of a noisy classical nonlinear dynamics](https://arxiv.org/abs/2507.06198) | arXiv submitted 2025-07-08; revised 2025-10-03. | Preprint | P1 | Noisy dissipative nonlinear-dynamics route. | Kolmogorov PDE route, noise assumptions, BQP-completeness, 2D Navier-Stokes vortex experiment. | Runtime depends on noise and inverse relative-error parameters. | Challenges noiseless nonlinear-DE framing; adds noise as a tractability condition. |
| CAR5 | Wang 2026 - [Quantum Algorithms for Nonlinear Differential Equations via Pivot-Shifted Carleman Linearization](https://arxiv.org/abs/2605.20071) | arXiv submitted 2026-05-19. | Preprint | P2 | Latest general Carleman improvement. | Pivot selection, shifted coordinates, stability assumptions. | Not yet vetted for CFD discretizations. | Challenges older Carleman convergence limits but must be mapped to CFD. |
| CAR6 | Liu 2021 - [Efficient quantum algorithm for dissipative nonlinear differential equations](https://arxiv.org/abs/2011.03185) | Published online 2021-08-26; arXiv revised 2021-10-16; SI correction 2026-05-20. | Peer reviewed | P3 | Foundational Carleman algorithm. | Dissipative quadratic ODE assumptions, Carleman truncation, QLSA structure. | Older and not CFD-specific. | Kept because newer Carleman papers still depend on this primitive. |
| CAR7 | Sanavio 2024 - [Lattice Boltzmann-Carleman quantum algorithm and circuit for fluid flows at moderate Reynolds number](https://arxiv.org/abs/2310.17973) | Published online 2024-04-22; arXiv revised 2024-01-09. | Peer reviewed | P2 | Carleman-LBM route. | Moderate-Re D2Q9 assumptions, second-order truncation, circuit-depth warning. | Multi-step viability remains hard. | Kept because IO1 and QRE3 directly relate to Carleman-LBM resource accounting. |
| CAR8 | Sanavio 2024 - [Three Carleman routes to the quantum simulation of classical fluids](https://arxiv.org/abs/2402.16686) | Published issue 2024-05-01; online 2024-05-23. | Peer reviewed | P2 | Carleman route comparison. | Comparison among LBM, Navier-Stokes, and Grad formulations. | Conceptual route paper, not an end-to-end estimate. | Kept for route taxonomy; challenged by CAR1-CAR3 latest routes. |
| CAR9 | Lin 2022 - [Challenges for quantum computation of nonlinear dynamical systems using linear representations](https://arxiv.org/abs/2202.02188) | arXiv submitted 2022-02-04; revised 2024-07-08. | Preprint / warning paper | P3 | Foundation/warning for Koopman and Carleman-style linear representations. | Conditions where linear representations become exponentially inefficient; observable/readout caveats. | Not CFD-specific and older than the latest route papers. | Kept because `CAR3`, Carleman, and KvN-style routes need this failure-mode checklist. |
| CAR10 | Li 2026 - [Efficient Quantum Simulation for Nonlinear Stochastic Differential Equations](https://arxiv.org/abs/2603.12398) | arXiv submitted 2026-03-12. | Preprint | P1 | Stochastic nonlinear-DE route. | Probabilistic Carleman linearization, stochastic LCHS ideas, scaling with noise/time/precision. | Not CFD-specific; relevance depends on stochastic-flow or noisy-dynamics formulation. | Complements `CAR4` by making stochastic nonlinear simulation a separate route instead of only a caveat. |
| CAR11 | Bharadwaj 2025 - [A Quantum Homotopy Algorithm for Solving Nonlinear PDEs and Flow Problems](https://arxiv.org/abs/2512.21033) | arXiv submitted 2025-12-24. | Preprint | P0 | Homotopy route for nonlinear PDEs and flow problems. | Homotopy continuation strategy, Burgers/flow benchmarks, query/gate complexity accounting. | New and broad; must be tested against concrete CFD discretizations and readout costs. | Challenges the roadmap to include non-Carleman nonlinear PDE routes, not only LBM and linearization. |
| QLSA1 | Inger 2026 - [An HHL-Based Quantum-Classical Solver for the Incompressible Navier-Stokes Equations with Approximate QST](https://arxiv.org/abs/2603.18222) | arXiv submitted 2026-03-18; revised 2026-04-16. | Preprint | P1 | HHL pressure-Poisson and approximate-QST CFD route. | Hybrid pressure solve, lid-driven cavity and TGV benchmarks, Chebyshev/QAE approximate QST readout. | HHL route depends on sparsity, conditioning, and readout practicality. | Challenges LBM-only roadmap and belongs in pressure-Poisson/QLSA comparison, not default core implementation. |
| QLSA2 | Williams 2025 - [Quantum Iterative Methods for Solving Differential Equations with Application to CFD](https://arxiv.org/abs/2404.08605) | arXiv submitted 2024-04-12; journal publication 2025-10-24. | Peer reviewed | P2 | Quantum iterative/multigrid-like route. | Jacobi, Gauss-Seidel, Woodbury/resolvent decomposition, CFD benchmark framing. | Not yet an end-to-end FTQC CFD resource estimate. | Kept as a non-HHL linear-solver alternative. |
| SURV1 | Tennie 2025 - [Quantum computing for nonlinear differential equations and turbulence](https://www.nature.com/articles/s42254-024-00799-w) | Published online 2025-01-22. | Published review | P1 | Nonlinear-DE and turbulence taxonomy. | Terminology, bottleneck map, nonlinear route categories. | Review, not implementation authority. | Kept as orientation only; latest route papers decide implementation. |
| SURV2 | Malinverno 2025 - [A Review of the Current State-of-the-Art of Quantum Computing for CFD](https://link.springer.com/article/10.1007/s42496-025-00269-1) | Published online 2025-06-12; print issue 2026-04. | Published review | P1 | CFD-specific quantum-computing survey. | CFD route taxonomy and limitations. | Broad survey; can lag fast 2026 preprints. | Kept for orientation; latest scan supersedes its paper list. |
| SURV3 | Au-Yeung 2024 - [Quantum algorithms for scientific computing](https://arxiv.org/abs/2312.14904) | arXiv submitted 2023-12-22; published 2024-11-01; arXiv revised 2025-09-24. | Peer-reviewed review | P2 | Scientific-computing/HPC context; includes O. Rathore. | HPC motivation, CFD context, broad quantum algorithm constraints. | Not CFD-resource specific. | Kept to cover the Rathore context and broader scientific-computing framing. |
| SURV4 | Amaral 2025 - [Quantum machine learning and quantum-inspired methods applied to computational fluid dynamics: a short review](https://arxiv.org/abs/2510.14099) | arXiv submitted 2025-10-15. | Preprint review | Watch | QML and quantum-inspired CFD survey. | VQA, QPINN/QNN, tensor-network CFD, surrogate-modeling context. | Mostly not FTQC solver/resource work. | Keep as orientation only; do not let QML/surrogate papers displace solver-resource routes. |
| PRIM1 | Gilyen 2019 - [Quantum singular value transformation and beyond](https://arxiv.org/abs/1806.01838) | arXiv submitted 2018-06-05; STOC published 2019-06-23. | Foundational | P3 | QSVT/block-encoding primitive. | Matrix-function, inverse, and block-encoding vocabulary. | Not CFD-specific. | Kept because QRE, QLSA, LCHS, and block-encoding routes depend on it. |
| PRIM2 | Berry 2017 - [Quantum algorithm for linear differential equations](https://arxiv.org/abs/1701.03684) | arXiv revised 2017-02-17; published online 2017-10-07. | Peer reviewed | P3 | Global-in-time linear ODE primitive. | Time-encoded linear-system construction and precision scaling. | State output and condition-number costs remain. | Kept because LBM4 and QLSA-style time-trajectory methods depend on it. |
| PRIM3 | Childs 2021 - [High-precision quantum algorithms for partial differential equations](https://arxiv.org/abs/2002.07868) | arXiv revised 2021-11-04; published online 2021-11-10. | Peer reviewed | P3 | Linear PDE primitive. | Finite-difference/spectral error and condition-number accounting. | Linear PDE focus. | Kept because ADE, pressure-Poisson, and spectral I/O routes need PDE cost baselines. |
| PRIM4 | Fowler 2012 - [Surface codes: Towards practical large-scale quantum computation](https://arxiv.org/abs/1208.0928) | Published online 2012-09-18; arXiv revised 2012-10-27. | Peer reviewed | P3 | Surface-code baseline. | Logical-to-physical intuition, code distance, T-state overhead concepts. | Older architecture model. | Kept because modern estimators still encode surface-code assumptions. |
| PRIM5 | Harrigan 2024 - [Expressing and Analyzing Quantum Algorithms with Qualtran](https://arxiv.org/abs/2409.04643) | arXiv submitted 2024-09-06. | Tool preprint | P1 | Logical resource-estimation framework. | Bloq/component resource tables and diagrams. | Custom CFD blocks need careful modeling. | Kept as the preferred logical-resource implementation substrate. |
| PRIM6 | van Dam 2023 - [Azure Quantum Resource Estimator paper](https://arxiv.org/abs/2311.05801) and [Microsoft docs](https://learn.microsoft.com/en-us/azure/quantum/learn-how-the-resource-estimator-works) | Paper submitted 2023-11-10; revised 2024-05-06. Docs last updated 2026-01-29. | Tool paper / official docs | P1 | Physical resource-estimation stack. | Error budget, QEC scheme, logical layout, T factories, runtime/physical qubits. | Tool assumptions can change. | Kept as the physical-estimate backend once logical circuit costs exist. |

## Quick Paper Key

Roadmap labels use HTML `abbr` tooltips where the renderer supports them. This table is the fallback reminder when hover text is unavailable.

| ID | Reminder |
| --- | --- |
| QRE1 | Zhuang 2025; Practical Quantum Advantage for Navier-Stokes; 2025-09-10; P0; full-stack FTQC resource claim. |
| QRE2 | Jennings 2025; End-to-end nonlinear fluid dynamics with bounded advantage; 2025-12-03; P0; bounded QLBM resource route. |
| QRE3 | Penuel 2024/2025; drag-force QRE warning; revised 2025-12-08; P0; bottleneck audit. |
| QRE4 | Jennings 2025/2026; non-trivial incompressible QLBM flows; 2025-12-05 / AIAA 2026; P0; realistic boundary/forcing companion to QRE2. |
| QRE5 | Meng 2025/2026; rapidly distorted turbulence via LCHS; JCP 2026; P0; turbulence statistics and resource route. |
| IO1 | Demirdjian 2026; data loading for Carleman-linearized LBE; revised 2026-05-15; P0; loading/LCU cost. |
| IO4 | Kosel 2026; encoding resources for quantum CFD; 2026-04-07; P0; encoding/resource tradeoffs. |
| IO5 | Rathore 2026; encoding strategies for quantum fluid simulation; 2026-04-27; P0; encoding taxonomy. |
| LBM1 | Ray 2026; trapped-ion QLBM with 3D spatially varying advection; 2026-04-30; P0; readout/reloading bottleneck. |
| LBM2 | Bastida-Zamora 2026; OSSLBM and real-device LBM applications; 2026-03-02; P0; one-step LBM. |
| LBM3 | Xiao 2026; fractional-step QLBM; 2026-02-28; P0; stable incompressible/thermal route. |
| LBM4 | He 2026; time-marching LBM for ADE; 2026-02-10; P0; measurement-free/global-system alternatives. |
| LBM5 | Chen 2026; LCHS ADE with boundary conditions; 2026-05-17; P1; boundary-aware linear PDE route. |
| LBM6 | Xiao 2025; quantum LKS; 2025-05-16; P1; adjustable viscosity predecessor. |
| LBM7 | Liu 2026; linear-equilibrium QLBM; 2026-01-16; P1; SVD/LCU collision and bounce-back. |
| LBM8 | Duong 2026; denoising collision operators; 2026-04-11; P0; coherent collision route. |
| LBM9 | Wang 2025; nonlinear QLBM via ensemble lattice gas; 2025-12-13; P1; peer-reviewed nonlinear QLBM. |
| LBM10 | Wawrzyniak 2025; dynamic-circuit QLBM for ADE; 2025-12; P1; no-reinitialization collision route. |
| LBM11 | Nagel 2025/2026; multi-step QLBM without reinitialization; 2026-01-18; P1; final-only sampling ADE route. |
| LBM12 | Zeng 2026; modular Navier-Stokes QLBM with linearized non-equilibrium collision; 2026-05-05; P1; latest peer-reviewed collision route. |
| LBM13 | Lee 2024/2026; multiple-circuit QLBM resource reduction; 2026; P2; QLBM-frugal comparator. |
| LBM14 | Lacatus 2025/2026; surrogate quantum circuit for BGK collision; 2026; P2; learned collision route. |
| IO2 | Goldack 2026; statistical velocity-field readout; 2026-01-15; P0; moments and structure functions. |
| IO3 | Zhang 2026; AQER data loader; 2026-02-02; P1; approximate loading bounds. |
| WATCH1 | Zhao 2026; massive classical-data advantage; 2026-04-08; Watch; oracle sketching/shadows. |
| WATCH2 | Meng 2025/2026; vortex interactions on superconducting processor; 2026; Watch; vortex-method hardware evidence. |
| CAR1 | Cappelli 2026; Schrodinger-Navier-Stokes; 2026-04-13; P0; SNS/HJ/Carleman route. |
| CAR2 | Cappelli 2026; lowest-order Carleman steady-state fluids; 2026-05-22; P1; steady-state Carleman. |
| CAR3 | Jemcov 2026; unitary KvN discretization; 2026-05-18; P1; fluid/plasma PDF route. |
| CAR4 | Bravyi 2025; noisy nonlinear dynamics; revised 2025-10-03; P1; noisy dissipative nonlinear route. |
| CAR5 | Wang 2026; pivot-shifted Carleman; 2026-05-19; P2; general nonlinear-DE improvement. |
| CAR6 | Liu 2021; dissipative nonlinear DE via Carleman; SI correction 2026-05-20; P3; foundation. |
| CAR7 | Sanavio 2024; Carleman-LBM; 2024-04-22; P2; moderate-Re D2Q9 Carleman. |
| CAR8 | Sanavio 2024; three Carleman routes; 2024-05-23; P2; route taxonomy. |
| CAR9 | Lin 2022/2024; challenges for linear representations; revised 2024-07-08; P3; warning paper. |
| CAR10 | Li 2026; nonlinear stochastic differential equations; 2026-03-12; P1; stochastic nonlinear route. |
| CAR11 | Bharadwaj 2025; quantum homotopy for nonlinear PDEs and flow; 2025-12-24; P0; homotopy route. |
| QLSA1 | Inger 2026; HHL Navier-Stokes with approximate QST; revised 2026-04-16; P1; pressure-Poisson route. |
| QLSA2 | Williams 2025; quantum iterative CFD methods; 2025-10-24; P2; Jacobi/Gauss-Seidel alternatives. |
| SURV1 | Tennie 2025; nonlinear DE and turbulence review; 2025-01-22; P1; orientation. |
| SURV2 | Malinverno 2025; quantum CFD review; 2025-06-12; P1; CFD taxonomy. |
| SURV3 | Au-Yeung 2024 with O. Rathore; scientific-computing review; revised 2025-09-24; P2; HPC context. |
| SURV4 | Amaral 2025; QML and quantum-inspired CFD review; 2025-10-15; Watch; surrogate/tensor-network orientation. |
| PRIM1 | Gilyen 2019; QSVT; 2019-06-23; P3; block-encoding primitive. |
| PRIM2 | Berry 2017; linear ODE algorithm; 2017-10-07; P3; global-time primitive. |
| PRIM3 | Childs 2021; high-precision PDE algorithms; 2021-11-10; P3; linear PDE primitive. |
| PRIM4 | Fowler 2012; surface codes; 2012-09-18; P3; QEC baseline. |
| PRIM5 | Harrigan 2024; Qualtran; 2024-09-06; P1; logical resources. |
| PRIM6 | van Dam 2023 / Microsoft docs; Azure Resource Estimator; docs 2026-01-29; P1; physical resources. |

## Paper Multi-Label Matrix

Use this table for filtering. The ID remains stable even when a paper receives many tags.

| ID | Multi-label tags |
| --- | --- |
| QRE1 | `FTQC`; `Resource-Estimation`; `Physical-Resources`; `Navier-Stokes`; `Spectral`; `Encoding-Strategy`; `State-Preparation`; `Readout`; `Error-Correction`; `Circuit-Depth`; `Core`; `Preprint` |
| QRE2 | `FTQC`; `Resource-Estimation`; `Logical-Resources`; `LBM`; `QLBM`; `Navier-Stokes`; `Turbulence`; `Observable-Selection`; `Readout`; `Gate-Counts`; `Core`; `Preprint` |
| QRE3 | `FTQC`; `Resource-Estimation`; `Drag`; `LBM`; `QLBM`; `Carleman`; `Data-Loading`; `Readout`; `T-Count`; `Logical-Resources`; `Warning`; `Core`; `Preprint` |
| QRE4 | `FTQC`; `LBM`; `QLBM`; `Navier-Stokes`; `Boundary-Conditions`; `Flow-Past-Cylinder`; `Lid-Driven-Cavity`; `Taylor-Green`; `External-Forcing`; `Resource-Estimation`; `Core`; `Preprint` |
| QRE5 | `FTQC`; `Resource-Estimation`; `Turbulence`; `LCHS`; `State-Preparation`; `Observable-Selection`; `Reynolds-Stress`; `Velocity-Spectrum`; `Circuit-Depth`; `Core`; `Peer-Reviewed` |
| IO1 | `Data-Loading`; `Carleman`; `LBM`; `LBE`; `LCU`; `PREP-SELECT`; `T-Count`; `Resource-Estimation`; `Core`; `Preprint` |
| IO2 | `Readout`; `Observable-Selection`; `Near-Term-Hardware`; `Velocity-Moments`; `Structure-Functions`; `Tomography-Avoidance`; `Hybrid`; `Core`; `Preprint` |
| IO3 | `Data-Loading`; `State-Preparation`; `Approximate-Loading`; `Encoding-Strategy`; `Hybrid`; `Adjacent`; `Preprint` |
| IO4 | `Encoding-Strategy`; `Amplitude-Encoding`; `Basis-Encoding`; `Qubit-Encoding`; `Readout`; `Resource-Estimation`; `LBM`; `QLBM`; `Core`; `Preprint` |
| IO5 | `Encoding-Strategy`; `Amplitude-Encoding`; `Basis-Encoding`; `Tensor-Encoding`; `Hybrid`; `FTQC`; `Near-Term-Hardware`; `Review`; `Core`; `Preprint` |
| LBM1 | `LBM`; `QLBM`; `ADE`; `Near-Term-Hardware`; `Trapped-Ion`; `Boundary-Conditions`; `Readout`; `Data-Reloading`; `Shadow-Tomography`; `Core`; `Preprint` |
| LBM2 | `LBM`; `QLBM`; `OSSLBM`; `Near-Term-Hardware`; `Hybrid`; `Navier-Stokes`; `Linear-Acoustics`; `Circuit-Depth`; `Gate-Counts`; `Core`; `Preprint` |
| LBM3 | `LBM`; `QLBM`; `Fractional-Step`; `Hybrid`; `Navier-Stokes`; `Thermal-Flow`; `Taylor-Green`; `Lid-Driven-Cavity`; `Core`; `Preprint` |
| LBM4 | `LBM`; `QLBM`; `ADE`; `No-Reinitialization`; `No-Repeated-Measurement`; `Global-Time-System`; `Low-Mach`; `Hybrid`; `Core`; `Preprint` |
| LBM5 | `LBM`; `ADE`; `LCHS`; `Boundary-Conditions`; `Dirichlet`; `Neumann`; `Robin`; `FTQC-Emulator`; `Adjacent`; `Preprint` |
| LBM6 | `LBM`; `QLBM`; `Lattice-Kinetic-Scheme`; `Navier-Stokes`; `Adjustable-Viscosity`; `Taylor-Green`; `Lid-Driven-Cavity`; `Adjacent`; `Preprint` |
| LBM7 | `LBM`; `QLBM`; `Linearization`; `Linear-Equilibrium`; `SVD`; `LCU`; `Boundary-Conditions`; `Poiseuille`; `Couette`; `Adjacent`; `Peer-Reviewed` |
| LBM8 | `LBM`; `QLBM`; `Denoising-Collision`; `Projector-Collision`; `No-Reinitialization`; `Boundary-Conditions`; `Observable-Selection`; `Core`; `Preprint` |
| LBM9 | `LBM`; `QLBM`; `Lattice-Gas`; `Nonlinear-Fluid-Dynamics`; `Turbulence`; `Linear-Collision`; `Vortex`; `Core`; `Peer-Reviewed` |
| LBM10 | `LBM`; `QLBM`; `ADE`; `Dynamic-Circuit`; `No-Reinitialization`; `Mid-Circuit-Measurement`; `Linearization`; `Circuit-Depth`; `Adjacent`; `Peer-Reviewed` |
| LBM11 | `LBM`; `QLBM`; `ADE`; `No-Reinitialization`; `State-Preparation`; `Readout`; `Amplitude-Amplification`; `Circuit-Depth`; `Adjacent`; `Peer-Reviewed` |
| LBM12 | `LBM`; `QLBM`; `Navier-Stokes`; `Linearization`; `Linearized-Collision`; `Boundary-Conditions`; `Lid-Driven-Cavity`; `Natural-Convection`; `Hybrid`; `Peer-Reviewed` |
| LBM13 | `LBM`; `QLBM`; `Resource-Estimation`; `Resource-Reduction`; `Gate-Counts`; `Circuit-Depth`; `Streamfunction-Vorticity`; `Lid-Driven-Cavity`; `Adjacent`; `Peer-Reviewed` |
| LBM14 | `LBM`; `QLBM`; `Surrogate-Collision`; `QML`; `BGK`; `Taylor-Green`; `Lid-Driven-Cavity`; `Circuit-Depth`; `Watch`; `Peer-Reviewed` |
| WATCH1 | `Classical-Data`; `Shadow-Tomography`; `Readout`; `Data-Loading`; `Oracle-Access`; `Watch`; `Preprint` |
| WATCH2 | `Vortex`; `Near-Term-Hardware`; `Superconducting`; `Spatiotemporal-Encoding`; `QST`; `Readout`; `Hybrid`; `Watch`; `Peer-Reviewed` |
| CAR1 | `Schrodinger-Navier-Stokes`; `Carleman`; `Hamilton-Jacobi`; `Tensor-Network`; `Navier-Stokes`; `FTQC`; `Core`; `Preprint` |
| CAR2 | `Carleman`; `Navier-Stokes`; `Steady-State`; `Linearization`; `Taylor-Green`; `Lid-Driven-Cavity`; `Adjacent`; `Preprint` |
| CAR3 | `Koopman-von-Neumann`; `Unitary-Embedding`; `Fluid-Dynamics`; `Plasma`; `PDF`; `Observable-Selection`; `Adjacent`; `Preprint` |
| CAR4 | `Noisy-Dynamics`; `Stochastic`; `Kolmogorov-PDE`; `Navier-Stokes`; `BQP-Completeness`; `Foundation`; `Preprint` |
| CAR5 | `Carleman`; `Pivot-Shifted`; `Nonlinear-ODE`; `Linearization`; `Foundation`; `Preprint` |
| CAR6 | `Carleman`; `Nonlinear-ODE`; `Dissipative`; `QLSA`; `Foundation`; `Peer-Reviewed` |
| CAR7 | `Carleman`; `LBM`; `QLBM`; `D2Q9`; `Moderate-Re`; `Circuit-Depth`; `Foundation`; `Peer-Reviewed` |
| CAR8 | `Carleman`; `LBM`; `Navier-Stokes`; `Grad`; `Route-Taxonomy`; `Foundation`; `Peer-Reviewed` |
| CAR9 | `Linearization`; `Carleman`; `Koopman`; `Readout`; `Conditioning`; `Warning`; `Foundation`; `Preprint` |
| CAR10 | `Stochastic`; `Carleman`; `LCHS`; `Nonlinear-SDE`; `Noisy-Dynamics`; `Adjacent`; `Preprint` |
| CAR11 | `Homotopy`; `Nonlinear-PDE`; `Flow-Problems`; `Resource-Estimation`; `Burgers`; `Core`; `Preprint` |
| QLSA1 | `QLSA`; `HHL`; `Pressure-Poisson`; `Navier-Stokes`; `Approximate-QST`; `QAE`; `Lid-Driven-Cavity`; `Taylor-Green`; `Hybrid`; `Preprint` |
| QLSA2 | `QLSA`; `Quantum-Iterative`; `Jacobi`; `Gauss-Seidel`; `CFD`; `Resource-Estimation`; `Adjacent`; `Peer-Reviewed` |
| SURV1 | `Review`; `Nonlinear-ODE`; `Turbulence`; `Carleman`; `Stochastic`; `Foundation`; `Peer-Reviewed` |
| SURV2 | `Review`; `Quantum-CFD`; `LBM`; `QLSA`; `Near-Term-Hardware`; `Foundation`; `Peer-Reviewed` |
| SURV3 | `Review`; `Scientific-Computing`; `HPC`; `Quantum-Algorithms`; `Foundation`; `Peer-Reviewed` |
| SURV4 | `Review`; `QML`; `Quantum-Inspired`; `Tensor-Network`; `CFD`; `Surrogate`; `Watch`; `Preprint` |
| PRIM1 | `QSVT`; `Block-Encoding`; `QLSA`; `Matrix-Functions`; `Foundation`; `Peer-Reviewed` |
| PRIM2 | `Linear-ODE`; `Global-Time-System`; `QLSA`; `Foundation`; `Peer-Reviewed` |
| PRIM3 | `Linear-PDE`; `Spectral`; `Finite-Difference`; `Conditioning`; `Foundation`; `Peer-Reviewed` |
| PRIM4 | `Error-Correction`; `Surface-Code`; `Physical-Resources`; `FTQC`; `Foundation`; `Peer-Reviewed` |
| PRIM5 | `Tooling`; `Qualtran`; `Logical-Resources`; `Gate-Counts`; `T-Count`; `Circuit-Depth`; `Foundation`; `Preprint` |
| PRIM6 | `Tooling`; `Azure-Resource-Estimator`; `Physical-Resources`; `Error-Correction`; `Surface-Code`; `T-Factories`; `Foundation` |

## Cross-Document Usage

Use `docs/qcfd_landscape_map.md` first to understand the QCFD route landscape. Use this bibliography for paper-level detail and inclusion status. Use `docs/implementation_plan.md` when deciding what to build next, and use `docs/research_mind_map.html` as an optional interactive paper explorer.

## Candidate Appendix

### Included In Core

- `QRE1` Zhuang 2025: core because it makes a concrete full-stack FTQC Navier-Stokes advantage claim.
- `QRE2` Jennings 2025: core because it gives an end-to-end nonlinear LBM route with bounded advantage.
- `QRE3` Penuel 2024/2025: core because it audits drag-force resources and exposes bottlenecks.
- `QRE4` Jennings 2025/2026: core because it extends the bounded QLBM route to walls, inlets, outlets, forcing, cavity flow, and cylinder flow.
- `QRE5` Meng 2025/2026: core because it is an end-to-end turbulence-statistics route with concrete resource accounting.
- `IO1` Demirdjian 2026: core because data loading can dominate Carleman/LBE routes.
- `IO4` Kosel 2026: core because encoding choice changes resource estimates before circuits exist.
- `IO5` Rathore 2026: core because it is the latest fluid-simulation encoding taxonomy.
- `LBM1` Ray 2026: core because it identifies readout/reloading bottlenecks in realistic QLBM transport.
- `LBM2` Bastida-Zamora 2026 OSSLBM: core because OSSLBM is a latest implementable LBM route.
- `LBM3` Xiao 2026 FS-LBM: core because it targets stability and 3D incompressible/thermal flows.
- `LBM4` He 2026: core because it directly addresses measurement-free time marching.
- `LBM8` Duong 2026: core because collision irreversibility/tomography is one of the main QLBM blockers.
- `LBM9` Wang 2025 nonlinear QLBM: core because it is a peer-reviewed nonlinear QLBM route with turbulence-scale benchmarks.
- `IO2` Goldack 2026: core because readout of statistical velocity properties is central.
- `CAR1` Cappelli 2026 SNS: core because it offers a genuine Navier-Stokes alternative to LBM.
- `CAR11` Bharadwaj 2025: core because homotopy gives a separate nonlinear PDE and flow route.

### Included As Adjacent

- `LBM5` Chen 2026 LCHS boundary ADE: adjacent because it is linear, but boundary handling matters.
- `LBM6` Xiao 2025 LKS: adjacent because the 2026 FS-LBM route builds on and critiques it.
- `LBM7` Liu 2026 linear-equilibrium QLBM: adjacent because it is peer-reviewed and circuit-explicit, but linearized.
- `LBM10` Wawrzyniak 2025 dynamic-circuit QLBM: adjacent/core-candidate because it reduces reinitialization for ADE but uses mid-circuit dynamics that need FTQC translation.
- `LBM11` Nagel 2025/2026 no-reinitialization QLBM: adjacent/core-candidate for ADE time marching because it directly removes intermediate full-state sampling.
- `LBM12` Zeng 2026 linearized-collision QLBM: adjacent/core-candidate because it is the latest peer-reviewed Navier-Stokes QLBM collision route.
- `LBM13` Lee 2024/2026 QLBM-frugal: adjacent because it gives circuit-depth/gate-count reduction evidence for split streamfunction-vorticity workflows.
- `LBM14` Lacatus 2025/2026 surrogate collision: adjacent/watch because it addresses BGK collision cost but uses a learned surrogate and still needs route-level FTQC accounting.
- `IO3` Zhang 2026 AQER: adjacent because approximate loading may transfer if CFD states are compressible.
- `WATCH1` Zhao 2026 massive classical data: adjacent because oracle sketching/shadows may inspire I/O strategy, but it is not a CFD solver.
- `WATCH2` Meng 2025/2026 vortex hardware paper: adjacent/watch because it is a vortex-method hardware demonstration, not a grid-CFD FTQC resource route.
- `CAR2` Cappelli 2026 lowest-order Carleman: adjacent/core-candidate for steady-state flows.
- `CAR3` Jemcov 2026 KvN: adjacent/core-candidate for probability-density formulations.
- `CAR10` Li 2026 stochastic nonlinear DEs: adjacent because it may matter for noisy/stochastic flow formulations.
- `QLSA1` Inger 2026 HHL/QST: adjacent route for pressure-Poisson solves; not default until conditioning/readout costs are clear.
- `QLSA2` Williams 2025 iterative methods: adjacent alternative to HHL.

### Foundation Only

- `CAR6` Liu 2021 dissipative nonlinear DE: foundation because newer Carleman routes depend on the technique.
- `CAR7` Sanavio 2024 Carleman-LBM: foundation/route reference for D2Q9 Carleman.
- `CAR8` Sanavio 2024 three Carleman routes: foundation for comparing CLB/CNS/Grad.
- `CAR9` Lin 2022/2024 linear-representation challenges: foundation because Carleman and KvN routes need its failure-mode checklist.
- `PRIM1` Gilyen 2019 QSVT: foundation for block-encoded matrix functions.
- `PRIM2` Berry 2017 linear ODE: foundation for global-in-time linear systems.
- `PRIM3` Childs 2021 PDE algorithms: foundation for linear PDE cost accounting.
- `PRIM4` Fowler 2012 surface codes: foundation for QEC intuition; modern estimates should use `PRIM6`.
- `PRIM5` Qualtran and `PRIM6` Azure Resource Estimator: foundation/tooling required for resource estimates.

### Excluded For Now

- `SURV4` Amaral 2025 QML/quantum-inspired CFD review: excluded from the implementation path because it is orientation for surrogate/tensor-network work, not an FTQC CFD resource route.
- Hsain 2025 quantum generative models for CFD latent spaces: excluded from the core because it is a surrogate/generative modeling route, not FTQC CFD simulation or resource estimation.
- Li 2026 quantum kernel networks on SPH: excluded from core because it is a hybrid QML/SPH model, not a fault-tolerant CFD solver; keep on watch if SPH becomes a project route.
- Au-Yeung 2025 quantum SPH via quantum walks: excluded from core because it is a small SPH/advection proof of concept; revisit only if meshfree CFD becomes a route.
- Broad QML data-encoding papers such as shot-based quantum encoding: excluded unless they connect to CFD state preparation, observable extraction, or FTQC resource estimates.
- Classical CFD ML/generative reconstruction papers: excluded because they are useful classical context but not quantum resource-estimation routes.

## Implementation Policy

Before any new implementation, create a small route note that answers:

1. Which labels from this document justify the work?
2. What benchmark and observable are used?
3. What data loading and readout assumptions are made?
4. What is the smallest classical operator or matrix representation to validate first?
5. What resource quantities will be produced, and which papers will they be compared against?

If a proposed task cannot answer these questions, it remains literature review, not implementation.
