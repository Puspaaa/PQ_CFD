# Review Packet

Date: 2026-06-04

This is the suggested review order for the current batch of work. The goal is
to help you review concepts first, not to force implementation decisions while
you are still learning the tools.

## Short Answer

Review first before we promote more route logic. The environment work is now in
good enough shape that the next major choices are research choices, not setup
chores.

I can still do low-risk support work in parallel, such as polishing docs,
running verification, and preparing small microbenchmarks, but I should not
commit us to a new scientific route without discussing it with you.

## Read In This Order

1. `docs/research_partner_workflow.md`

   This explains the collaboration philosophy: explore broadly, prototype in
   sandboxes, then promote only after discussion.

2. `docs/bartiq_qref_route_skeleton.md`

   Read this before the longer sandbox report. It is the beginner-friendly
   explanation of what Bartiq/QREF is doing and why the formulas are only
   placeholders.

3. `docs/modular_resource_sandbox_report.md`

   This is the evidence log. It is more technical. Use it to see what worked,
   what failed, and why Qualtran stayed sandbox-only for now.

4. `docs/psiqdk_fit_note.md`

   This explains where PsiQDK fits: not as a first symbolic model, but as a
   later FTQC-native subroutine sandbox after the operator/resource boxes are
   clearer.

5. `docs/wsl_research_environment.md`

   This is the practical environment note. It tells future us how to run WSL,
   Pixi, Jupyter notebooks, and PsiQDK.

6. `docs/environment_decision_note.md`

   This explains why local WSL is the primary environment and GitHub Codespaces
   is a fallback.

7. `notebooks/qre2_sparse_streaming.ipynb`

   This is a small Jupyter learning notebook. It is meant to make one sparse
   streaming operator visible; it is not a route claim or resource estimate.

## Decisions To Discuss

### Decision 1: Bartiq/QREF Promotion Level

Question: Should Bartiq/QREF become our main symbolic bookkeeping layer for the
next route-note work?

Default recommendation: Yes, for private symbolic route bookkeeping only.

What would change this: if you find the Bartiq skeleton confusing, too abstract,
or not helpful for learning the route.

### Decision 2: Next Scientific Microbenchmark

Question: What should we test next after the sparse streaming/collision replay?

Options:

- Keep extracting `QRE2` route-note boxes into Bartiq.
- Try a tiny PsiQDK state-preparation or QROM/data-loading primitive.
- Inspect QLBM/qlbm tooling as a separate sandbox.
- Return to the classical sparse operator path and make the QRE2 matrix objects
  easier to understand.

Default recommendation: one tiny PsiQDK state-preparation or QROM trial, but
only after you are comfortable with what the Bartiq placeholders mean.

### Decision 3: Notebook Role

Question: Should Jupyter become the main learning notebook style?

Default recommendation: yes. Jupyter is now the main learning notebook style.
The active notebooks are `.ipynb` files so Bartiq/QREF and future Qualtran
visualizations can use normal IPython display behavior.

What would change this: if a future route dashboard needs app-like interaction
more than IPython display compatibility.

### Decision 4: Codespaces Role

Question: Should we use GitHub Codespaces regularly?

Default recommendation: no. Keep it as fallback/review/demo infrastructure.
Local WSL is better for long-running experiments and large sandbox installs.

## What I Can Do Without More Input

- Keep WSL/Pixi/PsiQDK verification green.
- Improve beginner explanations in the existing notes.
- Add small one-concept Jupyter notebooks that do not change the route.
- Prepare option briefs for the next scientific decision.
- Clean up command docs and environment friction.

## What Should Wait For Discussion

- Making Bartiq/QREF public API.
- Claiming any formula is a `QRE2` resource estimate.
- Adding Qualtran, Qiskit, qlbm, Azure resource-estimator code, or PsiQDK to
  tracked runtime dependencies.
- Choosing the next route family beyond the current `QRE2`/Taylor-Green path.
- Converting existing notebooks wholesale to another notebook/app format.

## Current Verification Commands

Windows:

```powershell
uv run pytest
```

WSL:

```bash
cd ~/PQ_CFD
pixi run test
PYTHONPATH=src .cache/psiqdk-uv-venv/bin/python -m pytest -q
```
