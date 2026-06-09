# Modular Resource Sandbox Report

Date: 2026-06-04

## Goal

Run a hands-on sandbox for the Qualtran + Bartiq/QREF modular resource path without adding project dependencies or making QCFD resource claims.

This report is a learning artifact. The formulas below are placeholder learning objects, not `QRE2` claims, not validated circuit costs, and not route commitments.

## Corpus And Tool Anchors

Project anchors:

- `QRE2`: Jennings bounded nonlinear LBM resource route.
- `QRE4`: Jennings/Airbus-PsiQuantum realistic-flow companion route.
- `IO4`, `IO5`, `IO7`, `IO8`: encoding, loading, and readout warnings.
- `PRIM5`: Qualtran as a logical-resource implementation substrate.

Tool sources checked:

- [Bartiq documentation](https://psiq.github.io/bartiq/latest/) and [Bartiq compilation notes](https://psiq.github.io/bartiq/latest/concepts/compilation/).
- [Bartiq PyPI](https://pypi.org/project/bartiq/).
- [QREF PyPI](https://pypi.org/project/qref/).
- [Qualtran fundamentals](https://qualtran.readthedocs.io/en/latest/bloq_infra.html).
- [Qualtran call graph protocol](https://qualtran.readthedocs.io/en/latest/resource_counting/call_graph.html).
- [Qualtran + QREF/Bartiq interop](https://qualtran.readthedocs.io/en/latest/qref_interop/bartiq_demo.html).
- [Qualtran PyPI](https://pypi.org/project/qualtran/).

## Scratch Location

Ignored scratch scripts were created under:

```text
.cache/tool_trials/modular_resources/
```

Scripts:

- `.cache/tool_trials/modular_resources/bartiq_qref_trial.py`
- `.cache/tool_trials/modular_resources/qualtran_trial.py`
- `.cache/tool_trials/modular_resources/qualtran_qref_interop_trial.py`

## Commands Run

Initial import/version probes:

```powershell
uv run --isolated --with bartiq --with qref --with sympy python -c "import importlib.metadata as m; import bartiq, qref, sympy; print('bartiq', m.version('bartiq')); print('qref', m.version('qref')); print('sympy', m.version('sympy')); print('bartiq_exports', [x for x in dir(bartiq) if not x.startswith('_')][:100]); print('qref_exports', [x for x in dir(qref) if not x.startswith('_')][:100])"
uv run --isolated --with qualtran --with sympy python -c "import importlib.metadata as m; import qualtran, sympy; print('qualtran', m.version('qualtran')); print('sympy', m.version('sympy')); print('qualtran_exports', [x for x in dir(qualtran) if not x.startswith('_')][:140])"
```

Scratch trials:

```powershell
uv run --isolated --with bartiq --with qref --with sympy python .cache\tool_trials\modular_resources\bartiq_qref_trial.py
uv run --isolated --with qualtran --with sympy python .cache\tool_trials\modular_resources\qualtran_trial.py
uv run --isolated --with qualtran --with bartiq --with qref --with sympy python .cache\tool_trials\modular_resources\qualtran_qref_interop_trial.py
```

Version-friction probes:

```powershell
uv run --isolated --with qualtran --with bartiq==0.17.0 --with qref --with sympy python -c "import importlib.metadata as m; print('qualtran', m.version('qualtran')); print('bartiq', m.version('bartiq')); print('qref', m.version('qref'))"
uv run --isolated --with qualtran==0.7.0 --with bartiq==0.17.0 --with qref --with sympy python -c "print('should not resolve')"
```

## Package Versions Observed

Standalone Bartiq/QREF environment:

- `bartiq`: `0.17.0`
- `qref`: `0.11.0`
- `sympy`: `1.14.0`

Standalone Qualtran environment:

- `qualtran`: `0.7.0`
- `sympy`: `1.14.0`

Qualtran + Bartiq/QREF interop environment:

- `qualtran`: `0.7.0`
- `bartiq`: `0.12.1`
- `qref`: `0.11.0`

Version-friction result:

- Forcing `bartiq==0.17.0` without pinning Qualtran backtracked Qualtran to `0.5.0`.
- Forcing both `qualtran==0.7.0` and `bartiq==0.17.0` failed resolution because `qualtran==0.7.0` depends on `bartiq==0.12.1`.

## What Worked

### Bartiq/QREF Official Minimal Workflow

The Bartiq quick-start alias-sampling JSON loaded through `qref.SchemaV1`, compiled with `bartiq.compile_routine`, and evaluated with `bartiq.evaluate`.

Observed output:

```text
official_quickstart.program alias_sampling
official_quickstart.resources ['T_gates', 'rotations']
official_quickstart.T_gates_symbolic compare.T_gates + qrom.T_gates + swap.T_gates + usp.T_gates
official_quickstart.T_gates_L100_mu10 O(log2(100)) + 832
```

This validates the documented workflow at a basic level.

### Bartiq/QREF Toy QCFD Routine Tree

The QREF tree accepted placeholder children:

- `load_state`
- `stream_collide_step`
- `observable_readout`

The parent routine accepted symbolic parameters:

- `N_sites`
- `N_timesteps`
- `b_load`
- `b_step`
- `b_readout`

Placeholder additive resource:

```text
toffoli = N_sites*N_timesteps*b_step + N_sites*b_load + N_timesteps*b_readout
```

Toy numeric assignment:

```text
N_sites = 16
N_timesteps = 3
b_load = 8
b_step = 5
b_readout = 4
```

Observed output:

```text
qcfd_placeholder.toffoli_transitive load_state.toffoli + observable_readout.toffoli + stream_collide_step.toffoli
qcfd_placeholder.toffoli_expanded N_sites*N_timesteps*b_step + N_sites*b_load + N_timesteps*b_readout
qcfd_placeholder.toffoli_numeric 380
qcfd_placeholder.logical_qubits_numeric 16
```

Important modeling note: if a parent additive resource is manually defined, Bartiq keeps the manual expression. To get automatic aggregation from children, omit that parent resource and let Bartiq introduce the additive resource from children.

### Qualtran Toy Call Graph

A custom symbolic `Bloq` hierarchy represented the same placeholder structure:

- `QCFDRoutePlaceholder`
- `LoadStatePlaceholder`
- `StreamCollideStepPlaceholder`
- `ObservableReadoutPlaceholder`
- `Toffoli` as the primitive leaf count

Observed output:

```text
qcfd_placeholder.graph_nodes 5
qcfd_placeholder.graph_edges 6
qcfd_placeholder.sigma_keys ['Toffoli']
qcfd_placeholder.toffoli_formula N_sites*N_timesteps*b_step + N_sites*b_load + N_timesteps*b_readout
qcfd_placeholder.toffoli_numeric 380
```

This shows that the Qualtran call-graph protocol can express symbolic placeholder child counts. It does not show that these placeholder Bloqs are real circuits.

### Qualtran To QREF To Bartiq Interop

The official Qualtran interop pattern worked on `StatePreparationAliasSampling`:

```text
interop.qref_program CompositeBloq
interop.qref_top_resources [('clifford', 'additive', 1770), ('rotations', 'additive', 2), ('t', 'additive', 307)]
interop.compiled_resource_names ['clifford', 'rotations', 't']
interop.compiled_resource.clifford 1770
interop.compiled_resource.rotations 2
interop.compiled_resource.t 307
```

This is useful evidence that Qualtran can export existing Bloqs to QREF and Bartiq can compile the exported resource fields. The current test did not attempt QCFD-specific custom Bloq export.

## What Failed Or Caused Friction

- The first isolated package probes timed out under short timeouts. Rerunning one at a time with longer limits worked.
- Qualtran `0.7.0` pins Bartiq to `0.12.1`, while standalone Bartiq currently resolves to `0.17.0`. This matters if we want both latest Bartiq behavior and latest Qualtran behavior in the same environment.
- Qualtran's PyPI page labels the package as an experimental preview with no backwards-compatibility guarantee. That is acceptable for sandboxing, but not enough for quiet dependency promotion.
- The Bartiq/QREF toy tree is easy to express, but it is also easy to create meaningless formulas. It needs route-note discipline before becoming more than a symbolic sketch.
- The Qualtran toy Bloqs used a fake one-qubit signature and `Toffoli` as a placeholder leaf. This is intentionally not a circuit model.
- Neither tool solves the hard QCFD assumptions by default: encoding, data loading/reloading, selected-observable sampling, normalization, success probability, and physical error-budget accounting still need separate route-note extraction.

## Side-By-Side Comparison

| Criterion | Bartiq/QREF | Qualtran |
| --- | --- | --- |
| Ease of expressing route notes | Strong for a route-note skeleton. QREF directly stores a hierarchical routine tree with children, resources, parameters, ports, and connections. | Strong once the route maps to Bloqs, but class definitions are heavier than a schema tree for early exploration. |
| Symbolic parameters | Worked cleanly with string expressions compiled to SymPy-backed expressions. | Worked cleanly with SymPy expressions in Bloq fields and symbolic child counts. |
| Subroutine hierarchy | Natural nested QREF children. Good fit for `load_state -> stream/collide -> readout` route-note sketches. | Natural Bloq call graph. Better fit when subroutines are meant to become quantum operations or decompositions. |
| Aggregation of logical resources | Additive child resources auto-propagate when the parent omits the resource. Manual parent formulas override this. Qubit aggregation needs explicit semantics. | `Bloq.call_graph()` gives leaf-count aggregation for primitive Bloqs. Custom logical metrics need either chosen primitive leaves or separate accounting. |
| Connections and dataflow | QREF supports ports and DAG connections. This was validated by the official alias-sampling example, not yet by the QCFD placeholder. | Qualtran supports signatures, registers, decomposition, and call graphs. The toy QCFD example did not validate real register flow. |
| Loading/readout/success probability gaps | Must be modeled explicitly as resources, derived resources, or child routines. No default QCFD interpretation. | Must be modeled explicitly in Bloqs or resource annotations. No default QCFD interpretation. |
| Best current sandbox role | Neutral symbolic route-note compiler. | Operation-grounded primitive and interop probe, especially for known quantum primitives. |
| Promotion risk | Lower if kept as schema-only scratch. Dependency promotion still needs version and API decision. | Higher because latest Qualtran and latest Bartiq currently conflict, and custom Bloq APIs may shift. |

## Provisional Recommendation

Recommendation only, not a project decision:

Use Bartiq/QREF first as a neutral sandbox for turning a route-note skeleton into a symbolic resource tree. Use Qualtran in parallel when a route component needs to become an operation-like primitive or when an existing Qualtran Bloq can be reused.

Do not add either package to `pyproject.toml` yet. Keep using isolated `uv run --isolated --with ...` trials until the route note defines:

- the exact benchmark and observable,
- the encoding and loading model,
- the reloading or timestep data-access model,
- the readout/sample complexity model,
- the normalization/success-probability model,
- the logical resource vocabulary to track.

## Open Questions For Project Owner

1. Should the next sandbox artifact be a QREF-style route skeleton independent of implementation, or a Qualtran Bloq-style route skeleton?
2. Should `toffoli`, `t`, `clifford`, `rotations`, `logical_qubits`, `active_volume`, `samples`, and `success_probability` be the first resource vocabulary, or should we copy QRE2's exact vocabulary first?
3. Are we willing to use Qualtran `0.7.0` with Bartiq `0.12.1` for interop trials, or do we prefer latest Bartiq `0.17.0` standalone until Qualtran catches up?
4. Should loading and readout be represented as sibling child routines, or should they wrap the timestep routine as repeated pre/post routines?
5. Should the first real route skeleton be periodic Taylor-Green only, or should it include `QRE4` boundary/forcing placeholders from the start?

## Next Options

Option A: Add Bartiq/QREF corpus IDs and source notes.

- What it teaches: creates durable traceability for the toolchain before more trials.
- Cost/risk: small docs work, but it promotes the tools in the bibliography before we have chosen them.

Option B: Build a QREF/Bartiq route-note skeleton for periodic `QRE2` Taylor-Green.

- What it teaches: whether the current route-note fields can become symbolic resources without real circuits.
- Cost/risk: easy to overfit placeholders unless every formula is labeled as a learning object.

Option C: Build a Qualtran custom-Bloq skeleton for the same route.

- What it teaches: whether route modules can later decompose toward real operations.
- Cost/risk: heavier Python class work and version friction with Bartiq.

Option D: Try Azure logical-count/resource-estimator integration next.

- What it teaches: whether an external estimator can consume a simplified logical model.
- Cost/risk: may be premature until QRE2 resource vocabulary and success-probability assumptions are extracted.

Option E: Inspect `qlbm` package fit.

- What it teaches: whether existing QLBM code offers reusable route primitives or examples.
- Cost/risk: likely more implementation-specific; may distract from QRE2 extraction.

Option F: Return to QRE2 route-note extraction before more tools.

- What it teaches: locks the real vocabulary and assumptions before tool experiments multiply.
- Cost/risk: slower tool exploration, but gives every future trial a better target.

## Promotion Gate

Before promoting any sandbox result into maintained package code or dependencies, require:

- a route note tied to `QRE2`, `QRE4`, `IO4`, `IO5`, `IO7`, `IO8`, and `PRIM5`,
- a benchmark card and observable,
- explicit encoding/loading/readout assumptions,
- a smallest classical/operator check,
- a resource vocabulary matching paper assumptions,
- tests for any maintained code,
- a decision on the Qualtran/Bartiq version mismatch.

No promotion happened in this sandbox.
