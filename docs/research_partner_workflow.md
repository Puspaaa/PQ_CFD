# Research Partner Workflow

This document records how agents should work with the project owner on QCFD strategy, tools, route selection, and implementation. It complements `AGENTS.md` and keeps the project open to fast-moving research without turning every experiment into maintained project state.

## Core Principle

Separate learning from promotion.

Learning means broad exploration of papers, tools, packages, APIs, examples, and speculative workflows. It can be fast, comparative, and messy when it is isolated.

Promotion means adding something to maintained code, tracked dependencies, notebooks, route notes, public APIs, or project claims. Promotion requires explicit discussion, corpus anchors, tests where relevant, and the gates in `docs/implementation_plan.md`.

Current corpus anchors for near-term examples include `QRE2`, `QRE4`, `LBM14`, and `CAR7` for the Taylor-Green route comparison; `IO4`, `IO5`, `IO7`, and `IO8` for encoding/readout gates; and `PRIM14`, `PRIM15`, `PRIM16`, `PRIM5`, `PRIM6`, and `PRIM8` for Bartiq, QREF, PsiQDK, Qualtran, Azure resource estimation, and qlbm-style tooling context.

## Explore

Use exploration when the goal is to understand the landscape, compare promises, or discover what could make the research easier.

- Scan papers, docs, examples, packages, and current tool capabilities broadly.
- Report options instead of prematurely choosing one path.
- Record what each option is good for, what assumptions it hides, and what would make it worth prototyping.
- Use corpus IDs when a tool or method is connected to a project route, gate, or comparison target.
- Treat external tool claims as hypotheses until checked against benchmark, encoding, loading, readout, and resource assumptions.

Exploration output should usually be an option brief, a decision memo, or a short comparison table, not a dependency change.

## Prototype

Use prototypes when exploration needs hands-on evidence.

- Put throwaway trials in `.cache/`, an isolated environment, a separate branch, or a separate task-scoped agent thread.
- Keep prototypes small enough to answer one question: installation friction, API fit, resource-count shape, circuit export, notebook ergonomics, or compatibility with a tiny QCFD operator.
- Do not treat a successful prototype as a decision to adopt the tool.
- Do not update tracked dependencies, public APIs, notebooks, or roadmap claims unless the project owner has chosen that promotion step.
- Capture what the prototype taught and what remains unknown.

Prototype examples:

- Qualtran trial under `PRIM5`: can a tiny operator or placeholder Bloq express the resource quantities needed by a route note?
- Azure/QDK resource-estimator trial under `PRIM6`: can toy logical counts be converted into physical qubits/runtime without hiding QEC assumptions?
- qlbm reconnaissance under `PRIM8`: do its abstractions match the QRE2/QRE4 route assumptions or only a different QLBM family?

## Promote

Use promotion when a tool, method, or implementation becomes part of the maintained project.

- Confirm the project owner chose the option after seeing tradeoffs.
- Add or cite corpus IDs from `docs/research_grounding_and_plan.md` or `docs/research_landscape_data.js`.
- State the benchmark, observable, encoding, loading/reloading, readout, normalization or success-probability assumptions, and comparison papers.
- Keep APIs and dependencies as small as the promoted scope allows.
- Add tests or notebook checks proportional to the risk and user-facing surface.
- Run `uv run pytest` after maintained code or dependency changes.

Promotion is the point where the stricter route and tooling gates apply.

## Option Brief Template

Use this before significant implementation, dependency, architecture, route, tooling, or public-facing research decisions.

```markdown
### Decision

What are we deciding?

### Why It Matters

What changes depending on this choice?

### Options

| Option | What it teaches | Cost/risk | Best use |
| --- | --- | --- | --- |
| A |  |  |  |
| B |  |  |  |
| C |  |  |  |

### Recommendation

My recommendation is <option>, because <reason>. This is a recommendation, not a decision.

### Evidence That Would Change The Decision

What result, paper detail, prototype outcome, or constraint would make another option better?
```

## Agent Support

The main thread should remain the research-partner discussion space.

Task-scoped sub-agents can be useful for parallel scouting when the project owner explicitly authorizes them. They are not persistent custom research personalities. Use them for bounded investigations such as current Qualtran capabilities, Bartiq/QREF workflow, qlbm package fit, or Azure resource-estimator inputs. Bring their results back to the main thread as options and evidence.

Do not use sub-agents to bypass the discussion loop. Their role is to gather evidence faster, not to make strategic decisions independently.
