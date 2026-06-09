# Tooling Exploration And Options

Latest exploration date: 2026-06-08

This memo is a research-partner discussion artifact, not a dependency adoption
decision. It separates tools worth learning from tools worth sandboxing and
from tools that should be promoted into maintained project code only after a
route note and benchmark gate justify them.

Project anchors:

- Current repo state: runtime dependencies are `numpy`, `scipy`, `bartiq`, and
  `qref`; notebooks use Jupyter/IPython, matplotlib, and seaborn extras; tests use
  `pytest`.
- Current benchmark surface: periodic D2Q9 Taylor-Green, tied to `QRE2`,
  `QRE4`, `LBM14`, and `CAR7`.
- Current I/O gates: `IO4`, `IO5`, `IO7`, and `IO8`.
- Current resource/tooling corpus anchors: `PRIM14` for Bartiq, `PRIM15` for
  QREF, `PRIM16` for PsiQDK, `PRIM5` for Qualtran, `PRIM6` for
  Azure/Microsoft resource estimation, and `PRIM8` for qlbm.
- Sandbox trials are allowed when chosen for learning. Promotion into tracked
  dependencies, public APIs, or project claims still requires route gates.

## How To Use This Memo

Use this as a discussion menu.

- "Learn" means read docs, examples, papers, and maybe reproduce a tiny toy.
- "Sandbox" means run an isolated trial under `.cache/`, a temporary branch, or
  a task-scoped agent thread.
- "Promote" means add to maintained repo dependencies, public APIs, notebooks,
  route notes, or resource claims.

The important research habit is: do not ask "should this be in the project?"
before asking "what would this tool teach us?"

## Evidence Tiers

The atlas uses evidence tiers so that broad learning does not quietly become
dependency promotion.

| Tier | Meaning | Current Examples | Allowed Output |
| --- | --- | --- | --- |
| Tier 1: live now | The repo already has the dependency or a working local sandbox. | NumPy, SciPy sparse, Bartiq, QREF, WSL PsiQDK. | Tracked notebook demos and `.cache/tooling_atlas/` outputs. |
| Tier 2: isolated sandbox | The tool is relevant enough to trial, but should not enter maintained dependencies yet. | Qualtran, qlbm, Qiskit, Cirq, Azure QDK/QRE, PennyLane resources, PyZX, Stim, PyMatching. | Optional notebook cells, `.cache/` env notes, and blocked-demo records if absent. |
| Tier 3: scout/watch | The tool has interesting claims, recent activity, or adjacent capability, but the QCFD fit is not yet proven. | pyLIQTR, CUDA-Q, pytket, BQSKit/BQSKit-FT, MQT QMAP/QCEC, Bench-Q, Classiq, Qrisp, OpenFermion, JAX, Dedalus, FEniCSx, OpenFOAM, Qamomile, QURI Parts. | Source-backed capability cards and optional scout tasks. |

Promotion remains a separate decision. A working demo can move a tool from
Tier 3 to Tier 2, but it cannot move a tool into maintained dependencies,
public APIs, or route claims without the gates in `docs/implementation_plan.md`.

## Tool Register

`Corpus ID` uses existing IDs when the corpus already tracks the tool. New
entries stay `WATCH-TOOL` until we decide they deserve curated corpus entries.

| Tool | Layer | Corpus ID | Recent Activity / Release | Promised Capability | Demo Feasibility | QCFD Fit | Cannot Do | Install Friction | Promotion Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NumPy | Classical arrays | Foundation | Active scientific Python stack. | Dense arrays, vectorized diagnostics, reference states. | Tier 1 live. | Core baseline and notebook checks. | Sparse/operator scaling by itself. | Low; already installed. | Promoted runtime. |
| SciPy sparse | Classical sparse operators | Foundation | Current docs recommend sparse array APIs for new sparse work. | CSR/COO sparse operators, Kronecker products, matrix-vector validation. | Tier 1 live. | Validates streaming/collision objects before quantum routes. | Quantum circuit or loading model. | Low; already installed. | Promoted runtime for private validation. |
| Bartiq | Symbolic resource aggregation | `PRIM14` | Official docs and PyPI track current symbolic QRE workflow. | Compile nested subroutine costs into global symbolic costs. | Tier 1 live. | Route-note bookkeeping for `QRE2/QRE4`. | Circuit implementation or formula truth. | Low; already installed. | Promoted private bookkeeping. |
| QREF | Resource-estimation schema | `PRIM15` | PyPI `0.11.0` release provides schema validation and rendering utilities. | Store algorithms as hierarchical DAG/routine trees. | Tier 1 live. | Exchange format for route skeletons and possible Qualtran interop. | Resource evidence without paper-backed formulas. | Low; already installed. | Promoted private schema. |
| PsiQuantum Construct | FTQC platform | `PRIM16` | Construct is open access and includes PsiQDK, Circuit Designer, and Resource Analyzer. | Platform for FTQC circuit design, resource analysis, and algorithm optimization. | Tier 1/3: source-backed plus WSL PsiQDK where local. | Helps understand PsiQuantum workflow and resource hotspots. | Native Windows dependency or QCFD route proof. | Medium; browser/cloud/platform plus WSL for SDK. | Sandbox/watch. |
| PsiQDK / Workbench | FTQC SDK | `PRIM16` | PyPI `2.0.0`; local WSL sandbox verified. | Python FTQC programming, Workbench algorithms, visualization, logical resource reports. | Tier 1 in WSL, blocked on native Windows. | Candidate backend after operator/resource boxes are clear. | Cheap loading/readout assumptions. | Medium/high; WSL/Linux only here. | WSL sandbox only. |
| Qualtran | Logical-resource IR | `PRIM5` | PyPI `0.7.0`; docs warn experimental preview/no compatibility guarantee. | Bloqs, registers, call graphs, symbolic resource counting. | Tier 2 sandbox. | Strong candidate for logical route components. | Stable maintained dependency or CFD-specific Bloqs by default. | Medium; version friction with Bartiq history. | Sandbox. |
| qlbm | QLBM domain package | `PRIM8` | PyPI `0.0.6`; docs target QLBM research acceleration. | QLBM circuit components, lattices/geometry, Qiskit/Tket/Qulacs integration. | Tier 2 sandbox. | Directly relevant for QLBM family comparison. | Guarantee match to Jennings `QRE2/QRE4`. | Medium; quantum-stack deps. | Sandbox. |
| Qiskit | Circuit SDK/transpiler | WATCH-TOOL | PyPI latest observed `2.4.1`; IBM docs cover circuits, primitives, transpilation. | Build, visualize, transpile, and execute circuits across IBM ecosystem. | Tier 2 sandbox. | Best general pedagogy for tiny circuits and Azure/QDK interop examples. | FTQC resource estimate by itself. | Medium; manageable optional env. | Sandbox. |
| Cirq | Circuit SDK/simulator | WATCH-TOOL | Google Quantum AI docs current; simulator and circuit APIs maintained. | Circuit construction, simulation, Google-style workflows. | Tier 2 sandbox. | Natural around Qualtran/pyLIQTR/OpenFermion examples. | Physical resources or CFD route assumptions. | Medium. | Sandbox. |
| Azure QDK / Microsoft QRE | Physical resource estimator | `PRIM6` | Docs now point to `qdk.qre`/QDK Python and `LogicalCounts`. | Convert circuits or known logical counts into physical qubits/runtime under QEC assumptions. | Tier 2 sandbox; no Azure account required for estimator path. | Main physical-estimate candidate after logical counts exist. | Produce logical counts or validate CFD encodings. | Medium; docs/API transition. | Sandbox. |
| PennyLane resources | Logical resource cross-check | WATCH-TOOL | `qp.estimator` docs describe resource estimates from operators/resource operators. | Quick resource estimates and differentiable quantum workflow context. | Tier 2 sandbox. | Cross-check for simple primitives, not main FTQC route. | QCFD-specific route accounting. | Medium. | Sandbox/watch. |
| PyZX | Circuit optimization/verification | WATCH-TOOL | Docs describe ZX-calculus simplification and equality checks. | Optimize and compare circuits through ZX diagrams. | Tier 2 sandbox. | Sanity-check concrete tiny circuits after they exist. | Choose route or estimate physical resources. | Low/medium. | Sandbox/watch. |
| Stim / sinter | QEC stabilizer simulation | WATCH-TOOL | Quantumlib Stim is a high-performance stabilizer/QEC circuit tool. | Sample stabilizer circuits, detector-error models, QEC Monte Carlo workflows. | Tier 2 sandbox. | Teaches QEC assumptions under physical estimators. | Non-Clifford algorithm resources or CFD logic. | Low/medium. | Sandbox/watch. |
| PyMatching | QEC decoder | WATCH-TOOL | PyMatching v2 sparse-blossom work supports fast MWPM decoding. | Decode detector graphs and surface-code-style syndromes. | Tier 2 sandbox. | Decoder intuition for QEC/resource skepticism. | Logical algorithm costs. | Low/medium. | Sandbox/watch. |
| pyLIQTR | Clifford+T/resource analysis | WATCH-TOOL | Docs expose resource-analysis functions for Cirq-style circuits. | Clifford/T/rotation counts for algorithm-derived circuits. | Tier 3 scout. | Useful once a selected primitive needs concrete decomposition counts. | Route notes or physical qubits by itself. | Medium/high; ecosystem-specific. | Watch. |
| CUDA-Q | Hybrid quantum-classical SDK | WATCH-TOOL | Latest NVIDIA docs target CPU/GPU/QPU heterogeneous programming. | Python/C++ kernels, simulators, GPU acceleration, hybrid workflows. | Tier 3 scout. | Interesting for scalable simulations and heterogeneous demos. | QCFD FTQC resources by itself. | High on Windows/WSL if GPU stack needed. | Watch. |
| pytket | Optimizing compiler | WATCH-TOOL | Quantinuum docs describe platform-agnostic circuit compilation. | Circuit optimization, routing, interop with Qiskit/Cirq/others. | Tier 3 scout. | Compare compiler effects on tiny primitives. | Logical/physical resource claims. | Medium. | Watch. |
| BQSKit / BQSKit-FT | Compiler/synthesis | WATCH-TOOL | LBNL docs promise gate-set/topology portable compilation and FT extensions. | Synthesis, routing, Clifford+T-oriented compilation extensions. | Tier 3 scout. | Useful after concrete circuits exist. | Algorithm route modeling or loading/readout. | Medium/high. | Watch. |
| MQT QMAP / QCEC | Mapping/equivalence | WATCH-TOOL | MQT QMAP docs current at 3.6.x and include Qiskit-compatible mapping. | Circuit mapping, synthesis, equivalence checking in MQT stack. | Tier 3 scout. | Good for compiler and verification comparisons. | Resource model for QCFD routes. | Medium. | Watch. |
| Bench-Q | FT resource workflow | WATCH-TOOL | Bench-Q provides graph-state compilation, distillation, architecture models. | Hardware-resource benchmarking for FTQC workflows. | Tier 3 scout. | Interesting physical-estimation comparator. | Easy lightweight install or QCFD route proof. | High; optional Julia/Rust components. | Watch. |
| Classiq | High-level synthesis/platform | WATCH-TOOL | Classiq docs and 1.0 messaging emphasize high-level quantum programming and analysis. | Model-level synthesis, program analysis, application examples including QLBM material. | Tier 3 scout; account/platform may gate. | Useful for supervisor-friendly QLBM/circuit synthesis comparison. | Open local reproducibility unless account/env works. | Medium/high. | Watch. |
| Qrisp | High-level quantum programming | WATCH-TOOL | Active high-level programming project. | Pythonic quantum variables, high-level algorithm construction. | Tier 3 scout. | Pedagogical programming intuition. | FTQC resource authority. | Medium. | Watch. |
| OpenFermion | Quantum chemistry/Hamiltonians | WATCH-TOOL | Google Quantum AI docs position it for fermionic systems and chemistry. | Fermionic operators, transforms, Hamiltonian simulation tooling. | Tier 3 scout. | Only if CFD route becomes Hamiltonian/Pauli-sum-like. | Native LBM/CFD route modeling. | Medium. | Watch. |
| JAX | Accelerated arrays | WATCH-TOOL | Docs describe accelerator-oriented arrays; sparse module remains experimental. | JIT/vectorized sweeps, autodiff, accelerators. | Tier 3 scout. | Scaling classical sweeps or differentiable validation. | Quantum resources or stable sparse backbone. | Medium/high. | Watch. |
| Dedalus | Spectral PDE framework | WATCH-TOOL | Active v3 spectral PDE framework. | Spectral PDE benchmarks and custom equations. | Tier 3 scout. | Useful if spectral/PDE route becomes central. | LBM/QCFD resource estimates. | High; MPI/compiled stack. | Watch. |
| FEniCSx | FEM PDE framework | WATCH-TOOL | Current docs for finite-element PDE stack. | Weak-form/FEM PDE reference problems. | Tier 3 scout. | Useful for pressure/Poisson or FEM comparators. | QLBM route modeling. | High. | Watch. |
| OpenFOAM | Industrial CFD | WATCH-TOOL | Mature industrial CFD ecosystem. | High-fidelity classical CFD context. | Tier 3 scout. | Context/comparator for future realistic flows. | Quantum route/resource model. | High; non-Python stack. | Watch. |
| Qamomile / QURI Parts | Emerging SDK/IR | WATCH-TOOL | Recent PyPI/docs suggest typed kernels, resource estimates, SDK transpilation, and QURI ecosystem interop. | Emerging IR/resource/transpilation patterns. | Tier 3 scout only. | Watch for design ideas and interop, not first route work. | Established QCFD evidence. | Unknown/medium. | Watch. |

## PsiQuantum Stack Clarification

This is the supervisor-facing distinction to keep straight.

Construct is the umbrella platform. PsiQuantum describes Construct as its
open-access software platform for fault-tolerant quantum algorithm design,
circuit design, resource estimation, and algorithm optimization. In practice,
Construct is not one monolithic package we install into this repository. It is
the entry point for several tools:

- Circuit Designer: a web/canvas tool for drawing and sharing circuit diagrams.
- QDK with Workbench: the Python SDK/runtime path for writing FTQC programs.
- Resource Analyzer: a web/app path for visualizing and comparing resource
  estimates.
- Documentation, education material, and community support.

PsiQDK is the Python SDK inside that Construct ecosystem. The Construct QDK page
describes PsiQDK as including Workbench, the FTQC-native runtime, plus
Workbench Algorithms. Workbench is the programming/runtime layer: it lets us
write FTQC programs, simulate them, compile/optimize operations, and emit
logical resource estimates from the API.

QREF and Bartiq are more specialized and lighter-weight:

- QREF is a resource-estimation data format/schema. It represents a quantum
  algorithm as a hierarchical directed acyclic graph of routines, ports,
  connections, and resources. QREF can be written as JSON/YAML even before a
  circuit exists.
- Bartiq is a symbolic resource-estimation compiler/evaluator. It takes routine
  trees with local symbolic costs and propagates them into global symbolic
  costs such as T-count, Toffolis, active volume, and qubits.

For this QCFD project, the practical split is:

| Need | Best PsiQuantum Tool | Why |
| --- | --- | --- |
| Explain the ecosystem to supervisors | Construct web platform | It is the umbrella and has Circuit Designer, QDK/Workbench, and Resource Analyzer entry points. |
| Draw or inspect teaching circuits | Circuit Designer or Workbench visualization | Useful for communication, not route validation. |
| Write PsiQuantum-native FTQC toy programs | PsiQDK / Workbench in WSL | Native Windows is not the supported path in this workspace; the WSL sandbox works. |
| Express route-note boxes before circuits exist | QREF | It is a schema for hierarchical resource-estimation structure. |
| Aggregate symbolic route costs | Bartiq | It compiles local symbolic formulas into global formulas without requiring a full circuit. |
| Compare final estimates visually | Resource Analyzer, after we have estimates | It is useful only after logical estimates and assumptions exist. |

Why not install "all of Construct"? Because Construct is not a single
repo-local dependency. The web tools are better used through the browser, while
the installable Python path is PsiQDK/Workbench. PsiQDK is also heavier and
platform-sensitive here: it works in the WSL/Linux sandbox, but it is not a
native Windows dependency for this repo. Bartiq and QREF are small enough and
directly useful for the current route-note bookkeeping, so they remain the only
PsiQuantum tools promoted into the maintained Python dependencies.

Supervisor-ready summary:

> Construct is PsiQuantum's umbrella software platform for fault-tolerant
> quantum algorithm design, resource estimation, and optimization. PsiQDK and
> Workbench are the Python SDK/runtime inside that ecosystem for writing and
> analyzing FTQC programs. QREF is a schema for expressing resource-estimation
> routine trees, while Bartiq is a symbolic compiler/evaluator that aggregates
> local resource formulas into global costs. For this project, Bartiq/QREF are
> lightweight enough for maintained symbolic bookkeeping, while PsiQDK is
> better treated as a WSL sandbox until a QCFD route requires
> PsiQuantum-native primitives.

Sources:

- [PsiQuantum Construct](https://construct.psiquantum.com/)
- [PsiQDK / Workbench](https://construct.psiquantum.com/qdk)
- [Bartiq documentation](https://psiq.github.io/bartiq/latest/)
- [QREF PyPI](https://pypi.org/project/qref/)

## Big Picture

The other agent's suggested stack is not wrong. The problem is that it mixes
several different jobs:

1. Classical CFD and operator grounding.
2. Pedagogical and exploratory interfaces.
3. Quantum algorithm intermediate representations.
4. Circuit materialization and small-instance simulation.
5. Symbolic logical resource estimation.
6. Physical fault-tolerant resource estimation.
7. QEC and compiler sanity checks.

For this project, the more useful framing is not "best tool overall" but "which
tool answers which research question at which stage?"

## Tool Landscape By Layer

| Layer | Tools | What They Could Teach Us | Current Fit |
| --- | --- | --- | --- |
| Project environment | `uv`, `pixi` | Whether Python-only reproducibility is enough, or whether conda-forge/system packages become painful. | `uv` is already enough. `pixi` becomes interesting only if PDE/quantum packages need non-Python binaries. |
| Interactive research | Jupyter, Quarto, lightweight dashboards | Whether explanations are easier as classic notebooks, polished reports, or small app-like views. | Jupyter is the current learning notebook default because Bartiq/QREF and future Qualtran visualizations fit IPython display behavior. Quarto is for final report polish. |
| Classical arrays | NumPy, SciPy sparse, JAX | Dense validation, sparse operator construction, accelerated sweeps, differentiable experiments. | NumPy and SciPy sparse are current. JAX is a sandbox for scale/sweeps, not first needed. |
| Symbolic/operator algebra | SymPy, NetworkX, Pydantic/dataclasses, xarray | Symbolic resource formulas, subroutine graphs, typed route specs, multidimensional sweep data. | SymPy and NetworkX are plausible once symbolic resource models begin. Prefer dataclasses before Pydantic unless validation gets complex. |
| CFD/PDE frameworks | Dedalus, FiPy, FEniCSx, OpenFOAM | Spectral, finite-volume, FEM, or industrial CFD reference behavior. | Learn only. Promote only if a route/benchmark needs that exact formulation. |
| Quantum algorithm IR | Qualtran, qlbm, Qrisp | Bloq/call-graph resource models, QLBM-specific circuit abstractions, high-level quantum programming ergonomics. | Qualtran and qlbm deserve sandbox trials. Qrisp is for learning high-level quantum programming, not route authority yet. |
| Circuit prototyping | Qiskit, Cirq, Qiskit Aer | Tiny circuit sanity checks, drawings, transpilation, simulator-backed examples, Azure interop. | Sandbox after a selected primitive. Qiskit is strongest pedagogically and for Azure examples; Cirq is strongest near Qualtran/pyLIQTR. |
| Logical resources | Qualtran, pyLIQTR, Bartiq/QREF, PennyLane estimator | Bloq counts, Clifford+T/T-count estimates, symbolic modular aggregation, cross-checks. | Bartiq/QREF are current for private route bookkeeping. Qualtran and pyLIQTR remain sandbox/cross-check candidates. PennyLane is a cross-check or learning tool. |
| Physical resources | Azure/Microsoft QDK resource estimator, Bench-Q, Construct | Logical-to-physical qubits/runtime, architecture/QEC sensitivity, graph-state or vendor-specific resource analysis. | Azure is corpus-backed and should be sandboxed with toy logical counts. Bench-Q/Construct are learn/watch until their assumptions matter. |
| QEC sanity checks | Stim, sinter, PyMatching | Surface-code or decoder assumptions below resource-estimator formulas. | Learn/sandbox only if QEC assumptions become a research question. |
| Circuit optimization/verification | PyZX, MQT QMAP/QCEC, Qiskit transpiler | Gate simplification, mapping, equivalence checking, and small-circuit compiler effects. | Sandbox only after circuits exist. Do not infer asymptotic CFD resource claims from small optimized circuits. |
| Large simulation | Qiskit Aer, Cirq/qsim, quimb/cotengra | Statevector/noisy/tensor-network simulation of small or structured quantum circuits. | Learn. Use only to debug small circuits or tensor structure, not as the main estimator. |

## Tools Worth Discussing First

### 1. SciPy Sparse

Why it matters:

- The current QRE2 dense Carleman objects are intentionally tiny.
- The next natural classical validation step will likely need sparse streaming,
  collision, lifted-block, or oracle-like matrix summaries.
- SciPy's current docs recommend sparse array objects for new work and document
  CSR/CSC/COO formats, sparse Kronecker products, sparse linear algebra, and
  sparse matrix-vector products.

What it teaches:

- How the QRE2 shifted and Carleman operators scale before any quantum package.
- Whether sparsity patterns line up with block-encoding/oracle assumptions from
  `QRE2`, `IO1`, and `CAR15`.

Sandbox question:

- Can we reproduce the tiny dense QRE2 streaming/collision checks using sparse
  arrays and get the same one-step validations?

Promotion trigger:

- Already promoted for private QRE2 sparse operator validation. Public APIs or
  notebook-facing claims still need a route decision.

Sources:

- [SciPy sparse arrays](https://docs.scipy.org/doc/scipy/reference/sparse.html)
- [NumPy documentation](https://numpy.org/doc/stable/)

### 2. Qualtran

Why it matters:

- `PRIM5` already records Qualtran as the preferred logical-resource substrate.
- Qualtran represents algorithms through `Bloq`, `Register`, and
  `CompositeBloq` objects and exposes call-graph based resource counting.
- Qualtran also has documented interop with QREF/Bartiq and Microsoft resource
  estimation.

What it teaches:

- Whether a QCFD route can be represented as composable subroutines without
  materializing huge circuits.
- Whether symbolic placeholders can represent CFD-specific pieces while the
  route note is still being refined.

Sandbox question:

- Can a toy "QRE2 timestep skeleton" Bloq report symbolic qubits/T-like counts
  without pretending to implement encoding/loading/readout?

Promotion trigger:

- A route note names the operator, observable, precision target, loading model,
  success probability, and comparison papers.

Sources:

- [Qualtran fundamentals](https://qualtran.readthedocs.io/en/latest/bloq_infra.html)
- [Qualtran call graph protocol](https://qualtran.readthedocs.io/en/latest/resource_counting/call_graph.html)
- [Qualtran + QREF and Bartiq](https://qualtran.readthedocs.io/en/latest/qref_interop/bartiq_demo.html)

### 3. Bartiq And QREF

Why they matter:

- Bartiq is explicitly built for compiling symbolic resource costs for
  fault-tolerant quantum algorithms.
- QREF is the serialization/data format used by Bartiq and supported by
  Qualtran interop examples.
- This is very close to the project need: compare modular route costs before
  committing to one SDK or materializing circuits.

What they teach:

- Whether Jennings-style resource accounting can be represented as a routine
  tree with symbolic local costs.
- Whether route notes can become executable resource models without becoming
  circuit code too early.

Sandbox question:

- Can we encode a route-note skeleton with children like loading, timestep,
  observable measurement, and amplitude-estimation/readout into QREF, then use
  Bartiq to aggregate symbolic counts?

Promotion trigger:

- Already promoted for private symbolic route bookkeeping. Public APIs,
  notebook-facing claims, or real resource estimates still need route gates.

Sources:

- [Bartiq documentation](https://psiq.github.io/bartiq/latest/)
- [QREF PyPI page](https://pypi.org/project/qref/)
- [Qualtran + QREF and Bartiq](https://qualtran.readthedocs.io/en/latest/qref_interop/bartiq_demo.html)

### 4. Azure/Microsoft Resource Estimator

Why it matters:

- `PRIM6` already anchors this as the physical resource backend.
- Current Microsoft docs say the resource estimator is part of QDK, can model
  architecture/QEC assumptions, supports Qiskit and Q#, and can accept known
  logical counts.
- The docs also show an important transition: pages mention the newer `qdk.qre`
  module while API pages still expose/re-export `qdk.estimator` and
  `qsharp.estimator`. That should be verified in a sandbox before relying on
  examples.

What it teaches:

- How sensitive physical qubits/runtime are to QEC scheme, qubit parameters,
  error budget, and T-factory assumptions.
- What exact logical-count fields the project must produce before physical
  resource estimation is meaningful.

Sandbox question:

- Can toy logical counts from a pretend QRE2 subroutine be converted into
  physical qubits/runtime using `LogicalCounts`, without any circuit code?

Promotion trigger:

- Logical estimates exist for a route and the physical-estimate assumptions are
  ready to be discussed.

Sources:

- [Azure resource-estimator introduction](https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation)
- [Known estimates and LogicalCounts](https://learn.microsoft.com/en-us/azure/quantum/resource-estimator-known-estimates)
- [qdk.estimator API](https://learn.microsoft.com/en-us/python/qdk/qdk.estimator?view=qsharp-py)
- [QDK GitHub repository](https://github.com/microsoft/qdk)

### 5. qlbm

Why it matters:

- `PRIM8` already tracks qlbm as QLBM software framework context.
- Its docs say its goal is to accelerate QLBM research, with modules for
  amplitude-based circuits, QLGA circuits, lattices/geometry, and
  infrastructure integrating Tket, Qiskit, and Qulacs.
- It currently supports CQLBM, STQLBM, and LQLGA families, which may or may not
  match the Jennings/QRE2 route assumptions.

What it teaches:

- Whether there is reusable QLBM circuit/geometry machinery that can help us
  understand basis-state or amplitude-based QLBM approaches.
- Whether qlbm is a fit for the current Taylor-Green/QRE2 route or belongs as a
  comparator for a different QLBM family.

Sandbox question:

- Can we instantiate and inspect the smallest qlbm tutorial circuit, then map
  its encoding, streaming, collision, and readout assumptions against `QRE2`,
  `QRE4`, `IO4`, `IO5`, `IO7`, and `IO8`?

Promotion trigger:

- The route note explicitly selects a qlbm-supported algorithm family or uses
  it as a named comparator.

Sources:

- [qlbm documentation](https://qcfd-lab.github.io/qlbm/)
- [qlbm CPC paper page](https://www.sciencedirect.com/science/article/pii/S0010465525002012)

### 6. pyLIQTR

Why it matters:

- pyLIQTR is built for circuits derived from quantum algorithms and
  Clifford+T resource estimates.
- Its best-practices docs describe resource analysis over Cirq circuits and
  utilities for T, qubit, Clifford counts, decomposition, and Clifford+T
  transforms.

What it teaches:

- Whether a selected primitive can be decomposed into Clifford+T estimates more
  concretely than a purely symbolic route model.
- How much detail is lost between symbolic Qualtran/Bartiq models and concrete
  decomposition estimates.

Sandbox question:

- Can pyLIQTR estimate resources for a tiny Cirq circuit or primitive related
  to loading, SELECT/PREPARE, arithmetic, or basis shift?

Promotion trigger:

- Add pyLIQTR as a corpus/tool ID first; then promote only for a selected
  primitive where Clifford+T counts are needed.

Sources:

- [pyLIQTR documentation](https://isi-usc-edu.github.io/pyLIQTR/)
- [pyLIQTR resource analysis API](https://isi-usc-edu.github.io/pyLIQTR/_build/html/generated/src.pyLIQTR.utils.resource_analysis.html)
- [pyLIQTR best practices](https://isi-usc-edu.github.io/pyLIQTR/_build/html/best_practice.html)

### 7. Qiskit And Cirq

Why they matter:

- Qiskit is the strongest general-purpose Python circuit SDK for pedagogy,
  drawings, transpilation, primitives, and Azure QRE examples.
- Cirq is the natural circuit language around parts of the Google/Qualtran and
  pyLIQTR ecosystem.
- Both are useful for tiny circuit sanity checks, but neither should become the
  project architecture by itself.

What they teach:

- How a small primitive looks at circuit level.
- Whether resource estimates are stable under basic decomposition/transpilation.
- How easy it is to explain a primitive visually.

Sandbox question:

- Which one makes the smallest selected primitive easiest to inspect and
  compare against Qualtran/pyLIQTR/Azure?

Promotion trigger:

- A selected primitive needs actual circuit inspection or simulator-backed
  validation.

Sources:

- [Qiskit API documentation](https://docs.quantum.ibm.com/api/qiskit)
- [Qiskit Aer simulator docs](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- [Cirq documentation](https://quantumai.google/cirq)
- [Cirq simulation docs](https://quantumai.google/cirq/simulate/simulation)

### 8. Jupyter/IPython Notebooks

Why it matters:

- Bartiq/QREF examples and future Qualtran diagrams fit the Jupyter/IPython
  display model more naturally than a reactive app notebook.
- `.ipynb` files can preserve explanatory markdown, plots, SVG/HTML display,
  and executed review artifacts while keeping generated outputs in `.cache/`.

What it teaches:

- Whether route assumptions, package outputs, and resource plots are clear
  enough as executable pedagogical notebooks.

Sandbox question:

- Can a clean Jupyter notebook expose benchmark size, route family, encoding
  assumption, and placeholder logical counts without hiding state or outputs?

Promotion trigger:

- The notebook clearly improves research discussion, cites corpus IDs, and
  executes into `.cache/notebooks/` without changing maintained package APIs.

Sources:

- [Jupyter documentation](https://docs.jupyter.org/)
- [IPython display documentation](https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html)

## Tooling Atlas Notebook Series

The teaching artifact is a layer-based notebook series rather than one notebook
per tool. The notebooks are intentionally allowed to contain blocked-demo
cells: if a sandbox package is absent, the notebook records the missing package
and keeps executing.

| Notebook | Purpose | Live Scope |
| --- | --- | --- |
| `notebooks/tooling_00_atlas_index.ipynb` | Map layers, vocabulary, tiers, and objectives. | Current notebook dependencies only. |
| `notebooks/tooling_01_classical_operator_backbone.ipynb` | Show why NumPy/SciPy sparse validation comes before quantum packages. | NumPy, SciPy sparse, private `QRE2` helpers. |
| `notebooks/tooling_02_psiquantum_stack.ipynb` | Separate Construct, PsiQDK/Workbench, QREF, and Bartiq roles. | Bartiq/QREF live on Windows; PsiQDK live only in WSL sandbox. |
| `notebooks/tooling_03_qcfd_domain_tools.ipynb` | Compare qlbm/Classiq/PsiQDK/Qiskit domain fit against `QRE2/QRE4`. | Source-backed matrix, optional imports. |
| `notebooks/tooling_04_logical_resource_models.ipynb` | Compare Bartiq/QREF with Qualtran, pyLIQTR, and PennyLane resource shapes. | Bartiq/QREF live, optional sandbox imports. |
| `notebooks/tooling_05_circuits_and_compilers.ipynb` | Compare circuit SDK and compiler roles through a tiny primitive. | NumPy fallback live, optional Qiskit/Cirq/etc. imports. |
| `notebooks/tooling_06_physical_qec_estimators.ipynb` | Teach physical-resource and QEC-estimator input/output shapes. | Explicit toy model live, optional Azure/Stim/PyMatching/Bench-Q imports. |
| `notebooks/tooling_07_decision_matrix.ipynb` | Turn the atlas into an objective-by-tool decision aid. | Current notebook dependencies only. |
| `notebooks/tooling_08_live_demo_comparison.ipynb` | Run the installed sandbox demos and convert outputs into a supervisor-facing choice analysis. | Main env, WSL PsiQDK, and `.cache/tooling_atlas/` sandbox Python environments. |

Each notebook must contain a compact object or equation, one visual, one
falsifiable check, and one explicit "what this cannot prove" boundary.

## Live Demo Comparison Synthesis

`notebooks/tooling_08_live_demo_comparison.ipynb` is the current comparison
hub. It writes `.cache/tooling_atlas/live_demo_results.json` and records which
installed tools passed, failed, or remain blocked. The notebook is designed to
be supervisor-facing: it shows the shared shifted-D2Q9/QRE2-style learning
object, a pass/fail evidence table, a tool-by-objective heatmap, and a short
choice narrative.

Current interpretation:

- Use NumPy/SciPy sparse first for `QRE2/QRE4` operator validation.
- Use QREF/Bartiq now for route-box and symbolic-resource bookkeeping.
- Use PsiQDK/Workbench only for PsiQuantum-native primitive trials; Construct
  is the broader cloud/platform layer, not a package to promote wholesale.
- Use qlbm as the strongest live QLBM-family comparator, while checking its
  assumptions against the shifted-D2Q9 benchmark route.
- Use Qualtran when a specific QCFD primitive can be expressed as an
  operation-level bloq/call graph.
- Use Qiskit/Cirq/PennyLane/PyZX/pytket/BQSKit/MQT for teaching, circuit sanity,
  decomposition, and compiler comparisons after a meaningful primitive exists.
- Use Azure QDK/QRE only after logical counts exist, because it can study
  physical-resource sensitivity but cannot validate those logical counts.
- Use Stim/PyMatching/sinter for QEC and decoder intuition, not as a full
  application-level resource estimator.

The comparison is still not a route claim. The promotion gate remains a route
note that fixes benchmark, observable, encoding, loading/reloading, readout,
primitive decomposition, and comparison papers.

Current local run, 2026-06-09:

- Passed live demos: promoted NumPy/SciPy + Bartiq/QREF, WSL PsiQDK/Workbench,
  qlbm, Qualtran, Qiskit/Cirq/PennyLane/PyZX/OpenFermion, Stim/PyMatching,
  Azure QDK/QRE, and watch-stack imports for pytket/BQSKit/MQT QMAP/pyLIQTR/
  Qrisp/Classiq/Qamomile/QURI Parts/JAX/FiPy/sinter.
- Blocked or not locally importable: Bench-Q, CUDA-Q, Dedalus, and FEniCSx/
  dolfinx. These remain scout items, not failed QCFD choices.
- Machine-readable output:
  `.cache/tooling_atlas/live_demo_results.json`.

## Installed Sandbox Environments

These environments live under `.cache/tooling_atlas/` and are intentionally
ignored by git. They are for live demos and comparison only; they do not change
the maintained project dependency set.

| Environment | Jupyter kernel | Main packages currently importable | Notes |
| --- | --- | --- | --- |
| `.cache/tooling_atlas/env-general` | `Tooling Atlas General` | Qiskit `2.4.1`, Qiskit Aer `0.17.2`, Cirq `1.6.1`, PennyLane `0.45.0`, PyZX `0.10.3`, Stim `1.16.0`, PyMatching `2.4.0`, OpenFermion `1.7.1`, quimb `1.14.0`, cotengra `0.8.0`, `pq-cfd`. | General circuits, simulators, QEC sanity checks, and tensor-network demos. |
| `.cache/tooling_atlas/env-logical` | `Tooling Atlas qlbm` | qlbm `0.0.6`, Qiskit `2.4.1`, pytket `2.18.0`, Qulacs `0.6.13`, `pq-cfd`. | QLBM/domain-tool demos. |
| `.cache/tooling_atlas/env-qualtran` | `Tooling Atlas Qualtran` | Qualtran `0.7.0`, Bartiq `0.12.1`, QREF `0.11.0`, QDK/Q# `1.29.1`. | Kept separate because Qualtran's current dependency set is not compatible with the maintained Bartiq `0.17.0` route-bookkeeping environment. |
| `.cache/tooling_atlas/env-azure` | `Tooling Atlas Azure QDK` | QDK `1.29.1`, Q# `1.29.1`, qsharp-widgets `1.29.1`. | Physical-estimator and `LogicalCounts` demos. |
| `.cache/tooling_atlas/env-watch` | `Tooling Atlas Watch` | pytket `2.18.0`, BQSKit `1.2.1`, MQT QMAP `3.6.0`, pyLIQTR `1.4.2`, Qrisp `0.8.2`, Classiq `1.15.0`, Qamomile `0.12.5`, QURI Parts `0.25.1`, Qualtran `0.4.0`, Bartiq `0.17.0`, QREF `0.11.0`, sinter `1.16.0`, JAX `0.7.1`, FiPy `4.0.2`, `pq-cfd`. | Watch/compiler/emerging-tool demos plus lightweight PDE/QEC scouts. |
| WSL `.cache/tooling_atlas/env-cudaq` | not registered | `cudaq` metadata package `0.14.2`, but no importable `cudaq` module. | CUDA-Q backend install (`cuda-quantum-cu13`) timed out; keep CUDA-Q as WSL/Linux/GPU-stack scout for now. |

Install attempts that remain blocked:

- Bench-Q: blocked on Python 3.12 because its Orquestra/Ray dependency chain
  requires Ray wheels that are not available for this Python ABI in the needed
  range.
- Dedalus: Windows build failed without MPI/FFTW paths and because the native
  compiler rejected a GCC-style flag. Treat as WSL/Pixi/system-package work.
- FEniCSx/dolfinx: `fenics-dolfinx` is not available from the package registry
  in this environment. Treat as conda/WSL/system-package work.
- OpenFOAM: not a Python package; requires a system installation if selected.

The detailed machine-readable audit is
`.cache/tooling_atlas/installed_packages_report.json`.

## Tools To Learn But Not Prioritize Yet

### JAX

Use when sweeps, differentiability, GPU/TPU acceleration, or vectorized
experiments become the bottleneck. JAX is powerful, but it adds a new array
semantics layer and is not required for the current tiny dense/sparse operator
validations.

Sources:

- [JAX documentation](https://docs.jax.dev/en/latest/)

### Dedalus, FiPy, FEniCSx, OpenFOAM

These are serious PDE/CFD tools, but they answer classical PDE reference
questions rather than quantum-resource questions.

- Dedalus is attractive if a spectral route or `QRE1`-style spectral benchmark
  becomes central.
- FiPy is attractive for finite-volume PDE baselines.
- FEniCSx is attractive for FEM/weak-form PDE work.
- OpenFOAM is attractive for industrial CFD context, but it is far from the
  current LBM/operator-resource abstraction.

Sources:

- [Dedalus project](https://dedalus-project.org/index.html)
- [FiPy documentation](https://pages.nist.gov/fipy/en/stable/generated/fipy.html)
- [FEniCSx documentation](https://docs.fenicsproject.org/)
- [OpenFOAM documentation overview](https://www.openfoam.com/documentation/overview)

### OpenFermion

OpenFermion is excellent for fermionic systems and chemistry-style Hamiltonian
operator workflows. It may be useful only if a CFD route is recast into Pauli
sums or Hamiltonian simulation primitives in a way that genuinely resembles its
native domain. Otherwise, it is likely a distraction.

Sources:

- [OpenFermion documentation](https://quantumai.google/openfermion)

### PennyLane Estimator And Qrisp

PennyLane's estimator can be useful as a resource-estimation cross-check, and
Qrisp can be useful for high-level quantum programming intuition. Neither is
currently anchored in this QCFD corpus, so they should be learning tools unless
a specific route points to them.

Sources:

- [PennyLane resource module](https://docs.pennylane.ai/en/stable/code/qml_resource.html)
- [PennyLane estimator module](https://docs.pennylane.ai/en/stable/code/qp_estimator.html)
- [Qrisp documentation](https://www.qrisp.eu/)

### Stim, sinter, PyMatching

These are useful if we go below resource-estimator formulas and want to test
surface-code or decoder assumptions directly. They are not needed for the first
QCFD route comparison, but they are important background for physical-resource
skepticism.

Sources:

- [Stim GitHub repository](https://github.com/quantumlib/Stim)
- [PyMatching documentation](https://pymatching.readthedocs.io/en/latest/index.html)

### PyZX And MQT

These help with circuit optimization, mapping, and equivalence checking after
circuits exist. They should not drive route choice. Their useful role is to
debug and sanity-check concrete small circuits.

Sources:

- [PyZX documentation](https://pyzx.readthedocs.io/)
- [MQT QMAP documentation](https://mqt.readthedocs.io/projects/qmap/en/stable/index.html)

### quimb And cotengra

These are useful when tensor-network circuit simulation is a better fit than
statevector simulation. They are not an estimator, but they can help debug
structured circuits or data encodings.

Sources:

- [quimb tensor circuit documentation](https://quimb.readthedocs.io/en/latest/tensor-circuit.html)

### Bench-Q And Construct

Bench-Q and PsiQuantum Construct are worth learning about because they address
fault-tolerant resource workflows, architecture assumptions, and resource
hotspots. For this project they are watch/sandbox candidates unless their
modeling assumptions line up with the selected QCFD route.

Sources:

- [Bench-Q GitHub repository](https://github.com/zapatacomputing/benchq)
- [PsiQuantum Construct](https://www.psiquantum.com/construct)

## Suggested Sandbox Trials

These are not implementation decisions. They are evidence-gathering options.

| Trial | Tools | Question | Output |
| --- | --- | --- | --- |
| Sparse operator replay | SciPy sparse | Can sparse arrays reproduce existing QRE2 tiny dense operator checks? | `.cache/tooling_atlas/scipy_sparse_qre2_notes.md` plus small scratch script. |
| Symbolic route tree | QREF/Bartiq, maybe Qualtran export | Can a route note become a symbolic resource tree? | QREF JSON/YAML and aggregated symbolic counts in `.cache/tooling_atlas/`. |
| Qualtran skeleton | Qualtran | Can a placeholder QCFD timestep Bloq expose call-graph counts without false implementation claims? | Tiny Bloq experiment and notes in `.cache/tooling_atlas/`. |
| Azure logical-counts | QDK resource estimator | Can toy logical counts become physical resource estimates with explicit QEC assumptions? | One notebook/script and parameter table in `.cache/tooling_atlas/`. |
| qlbm reconnaissance | qlbm, Qiskit/Tket/Qulacs if needed | Do qlbm algorithms match or differ from the QRE2/QRE4 route? | Assumption comparison table in `.cache/tooling_atlas/`. |
| Jupyter route dashboard | Jupyter widgets or notebook controls | Is a small interactive notebook better for discussing route/resource tradeoffs? | Tiny notebook with controls and placeholder formulas. |

## Option Brief: First Tool Sandbox

### Decision

Which tool sandbox should we run first?

### Why It Matters

The first trial should teach us something useful without committing the project
to a package stack. It should also help decide what the next real route note or
prototype needs.

### Options

| Option | What It Teaches | Cost/Risk | Best Use |
| --- | --- | --- | --- |
| SciPy sparse replay | Operator scaling and sparse structure before quantum tools. | Low risk, less exciting. | Grounding `QRE2`/Carleman assumptions. |
| Qualtran skeleton | Whether QCFD subroutines can become Bloq call graphs. | Medium install/API risk; may need placeholders. | Logical-resource IR exploration. |
| Bartiq/QREF route tree | Whether route notes can become symbolic resource estimates. | Easy to make meaningless placeholders unless every formula is labeled. | Modular Jennings-style accounting. |
| Azure logical-counts | What physical estimator inputs/outputs look like. | API docs appear in transition; toy counts can mislead. | Learning physical-resource sensitivity. |
| qlbm reconnaissance | Whether a domain package helps QLBM circuit intuition. | May not match Jennings/QRE2 route. | Comparing QLBM families and encodings. |
| Jupyter dashboard | Whether interaction improves research discussion. | Interface polish can distract from substance. | Making option comparison intuitive. |

### Recommendation

My current recommendation is to start with the latest-Bartiq/QREF route tree
alone, because it directly tests the current need: modular algorithmic logic to
symbolic resource accounting without requiring circuit code. Qualtran remains a
later option when a route component needs operation-level grounding. This is a
recommendation, not a decision.

### Evidence That Would Change The Decision

- If we want more classical grounding first, run SciPy sparse replay.
- If physical resource intuition is the immediate priority, run Azure
  logical-counts first.
- If the goal is to learn QLBM software quickly, run qlbm reconnaissance first.
- If the priority is making discussion easier, run the Jupyter dashboard first.

## Open Discussion Questions

1. Do we want the first hands-on trial to maximize learning excitement or to
   reduce route risk?
2. Do we want to add missing tool IDs for pyLIQTR now, or only after a sandbox
   shows it matters?
3. Should sandbox trials live only in `.cache/`, or should we make a dedicated
   untracked/ignored `experiments/` or `scratch/` convention?
4. Should we use task-scoped scout agents for separate tool investigations, or
   keep the first round in the main thread?
5. Should the next route discussion focus on `QRE2`/Jennings, qlbm-supported
   QLBM families, or physical-estimator inputs?
