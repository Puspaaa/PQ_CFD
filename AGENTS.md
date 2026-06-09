# PQ CFD Agent Instructions

This repository is for a research-grounded study of quantum computational fluid dynamics (QCFD): estimating logical and physical resources for computational fluid dynamics workloads on fault-tolerant quantum computers. The project should move as a research partnership: explore rapidly, discuss options explicitly, then promote only the pieces that survive paper, benchmark, and tooling scrutiny.

## Collaboration Rules

- Treat the project owner as a research partner, not a downstream reviewer. When the task is exploratory, strategic, architectural, or tool-selection oriented, do not silently narrow the option space.
- Before significant implementation, dependency adoption, route commitment, public-API expansion, or public-facing conclusion, present an option brief and ask the project owner to choose.
- An option brief should state the decision, why it matters, the viable options, what each option teaches, cost/risk, a recommendation clearly labeled as a recommendation, and what evidence would change the decision.
- Separate learning from promotion. Broad paper and tool exploration is encouraged in sandboxes, `.cache/`, separate branches, or separate task-scoped agent threads; promotion into maintained code, dependencies, notebooks, or claims requires the gates below.
- Use task-scoped sub-agents only when the project owner explicitly authorizes parallel scouting or delegated work. Keep the main thread as the place where options are synthesized and decisions are made together.

## Operating Rules

- Keep promoted workspace state lean. Do not add registries, framework layers, or speculative packages to maintained code just because they may become useful later; exploratory sandboxes are allowed when clearly labeled and isolated.
- Every implementation step must cite corpus IDs from `docs/research_grounding_and_plan.md` or `docs/research_landscape_data.js`.
- Every notebook must be pedagogical: explain the equation, observable, numerical check, and research reason for the step. The project owner is a theoretical researcher, so clarity is part of the deliverable.
- Optimize for technical depth with minimal cognitive load: prefer one explicit equation, one visual, and one falsifiable check per concept over long prose or broad framework scaffolding.
- Full-field readout is a negative-control baseline unless a paper justifies it. Prefer named observables such as velocity moments, vorticity, energy, drag/lift, spectra, norms, or structure functions.
- Bartiq/QREF and SciPy are promoted for private symbolic bookkeeping and sparse classical validation. Do not promote Qiskit, Qualtran, QLBM tooling, Azure resource-estimation code, PsiQDK, or another quantum package into tracked dependencies or maintained APIs until a route note passes the benchmark, encoding, loading, and readout gates in `docs/implementation_plan.md`. Sandbox trials are allowed when the project owner has chosen that exploration path.
- Keep Python APIs small and tested by default for maintained package code. This default is not a reason to suppress research exploration; it is a promotion criterion for reusable code.

## Source-Of-Truth Map

- `docs/implementation_plan.md`: roadmap, current state, next milestones, route-note template, benchmark-card template, and notebook expectations.
- `docs/research_partner_workflow.md`: collaboration workflow for broad exploration, option briefs, sandbox prototypes, and promotion decisions.
- `docs/tooling_exploration_and_options.md`: current tool landscape, sandbox options, sources, and discussion questions for QCFD tooling.
- `docs/bartiq_qref_route_skeleton.md`: beginner-friendly latest-Bartiq/QREF route skeleton for periodic `QRE2` Taylor-Green resource bookkeeping.
- `docs/psiqdk_fit_note.md`: PsiQDK fit note and WSL/Linux-only sandbox commands.
- `docs/wsl_research_environment.md`: WSL-first execution workflow, Pixi trial status, Jupyter notebook command notes, and environment roles.
- `docs/environment_decision_note.md`: local WSL versus GitHub Codespaces decision note and current environment recommendation.
- `docs/review_packet.md`: suggested review order, pending decisions, and what should wait for project-owner discussion.
- `docs/viewing_files_in_vscode.md`: workspace editor behavior for Markdown and Jupyter notebooks.
- `docs/research_grounding_and_plan.md`: human-readable bibliography/corpus with paper metadata, scan logic, reading statuses, and paper labels.
- `docs/research_landscape_data.js`: canonical structured graph for IDs, aliases, citation keys, tags, reading statuses, and paper relations.
- `docs/research_mind_map.html`: official interactive visualization for exploring the research landscape.
- `docs/qcfd_landscape_map.md`: static route-family map and Mermaid diagrams.
- `notebooks/baseline_lbm.ipynb`: pedagogical Jupyter notebook for the current D1Q3/D2Q9 classical baseline.

The untracked overlap HTML files are non-authoritative unless the project owner explicitly promotes them.

## Current State

- The codebase currently exposes only D1Q3 and D2Q9 LBM baselines, benchmark sweeps, and D2Q9 diagnostics.
- Runtime dependencies include NumPy, SciPy sparse, Bartiq, and QREF. SciPy/Bartiq/QREF helpers are private and do not make route claims.
- WSL-first execution is available through a synced `~/PQ_CFD` checkout. Mirrored WSL networking is configured in `%USERPROFILE%/.wslconfig`; Pixi 0.70.1 has a generated `pixi.lock` and tasks `imports`, `test`, `notebook-smoke`, and `notebook-execute`.
- PsiQDK 2.0.0 is staged for WSL/Linux use in the ignored WSL-local `.cache/psiqdk-uv-venv/` environment. It is not a native Windows dependency; from `~/PQ_CFD`, use `PYTHONPATH=src .cache/psiqdk-uv-venv/bin/python -m pytest -q`.
- `uv run pytest` is the basic verification command.
- The first quantum-relevant benchmark card is the periodic D2Q9 Taylor-Green case, tied to `QRE2`, `QRE4`, `LBM14`, and `CAR7`.
- Raw `References/` PDFs and BibTeX files are intentionally not the working source of truth; the curated corpus and graph are.

## Before Adding Code

For promoted route code or claims, create or update a route note that answers:

1. Which corpus IDs justify the work?
2. What benchmark and observable are used?
3. What encoding, data-loading, reloading, and readout assumptions are made?
4. What is the smallest classical operator or matrix representation to validate first?
5. Which resource quantities will eventually be produced, and which papers are comparison targets?

If those answers are not available, the task is still research grounding or sandbox prototyping, not promoted implementation.
