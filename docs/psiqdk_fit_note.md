# PsiQDK Fit Note

Date: 2026-06-04

This note records where PsiQDK fits in the project after the SciPy sparse and
Bartiq/QREF promotion, plus the working WSL setup created on 2026-06-04.

## Short Answer

PsiQDK is relevant, but it is not a native Windows dependency.

Use it as a WSL/Linux sandbox for PsiQuantum-native FTQC subroutine trials:

```text
validated classical operator
  -> Bartiq/QREF symbolic resource boxes
  -> PsiQDK Workbench/Algorithms microbenchmark
  -> optional Azure or other physical-resource cross-check
```

## Why It Matters

PsiQDK bundles:

- Workbench for FTQC-oriented program construction and resource reports.
- Algorithms for reusable primitives such as state preparation, QROM/data
  loading, arithmetic, phase estimation, and Hamiltonian simulation.
- Visualize for circuit and resource-estimate inspection.
- Bartiq and QREF in pinned compatible versions.

That matches likely QCFD bottlenecks: loading, arithmetic, block encodings,
success probability, and selected-observable readout.

## Current Setup Status

WSL2 Ubuntu is available in this workspace. The preferred execution checkout is:

```text
~/PQ_CFD
```

The current clean PsiQDK environment is a WSL-local `uv` virtual environment:

```text
~/PQ_CFD/.cache/psiqdk-uv-venv/
```

It was installed directly from PyPI inside WSL after enabling mirrored WSL
networking. This directory is ignored by git and keeps PsiQDK outside the
native Windows dependency set.

The Windows user-level WSL networking fix used:

```text
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
```

Verified WSL imports:

```text
psiqdk 2.0.0
psiqdk-workbench 4.45.0
psiqdk-algorithms 1.22.3
psiqdk-visualize 0.97.2
workbench-sim-native 0.2.1
bartiq 0.17.0
qref 0.11.0
```

The project test suite also runs from WSL with the PsiQDK target active:

```bash
cd ~/PQ_CFD
PYTHONPATH=src .cache/psiqdk-uv-venv/bin/python -m pytest -q
```

Observed result:

```text
53 passed
```

## Why It Is Not Added To `pyproject.toml`

The native Windows install fails because `psiqdk==2.0.0` depends on
`workbench-sim-native==0.2.1`, which currently has Linux/macOS wheels but no
Windows wheel. PyPI also states that Windows is not supported and recommends WSL.

So PsiQDK should be used through WSL/Linux, not installed into the current
native Windows project environment.

## Working Setup Commands

The current WSL setup uses Linux `uv`:

```bash
cd ~/PQ_CFD
curl -LsSf https://astral.sh/uv/install.sh | sh
rm -rf .cache/psiqdk-uv-venv
~/.local/bin/uv venv .cache/psiqdk-uv-venv --python /usr/bin/python3
~/.local/bin/uv pip install \
  --python .cache/psiqdk-uv-venv/bin/python \
  psiqdk==2.0.0 \
  "pytest>=8.3"
```

Then run from the WSL-side checkout:

```bash
cd ~/PQ_CFD
PYTHONPATH=src .cache/psiqdk-uv-venv/bin/python -m pytest -q
```

Use the Python entrypoint for CLI checks:

```bash
cd ~/PQ_CFD
.cache/psiqdk-uv-venv/bin/python - <<'PY'
import sys
from psiqdk.cli import main

sys.argv = ["psiqdk", "--version"]
raise SystemExit(main())
PY
```

## API Inventory

Initial imports show these likely starting points:

- `psiqdk.algorithms`: state preparation, alias sampling, QROM/data lookup,
  arithmetic, LCU, QPE, amplitude amplification, and block-encoding components.
- `psiqdk.workbench`: FTQC-oriented quantum data types, QPU/program machinery,
  QRE, arithmetic, comparators, rotations, QFT, simulation, and utility filters.
- `psiqdk.visualize`: `CallGraph`, `FlameGraph`, and `Circuit` viewers.

## First Microbenchmarks To Try

Start small. Do not port the full Jennings/QRE2 route first.

1. State preparation for a tiny real-amplitude vector.
2. QROM/data-loading cost for a tiny lookup table.
3. Fixed-point arithmetic for a product or square term.
4. LCU/block-encoding sketch for a tiny sparse stencil, only after the SciPy
   sparse replay identifies the classical operator.

## Project Position

Corpus anchor: `PRIM16`.

Relationship to current tools:

- `PRIM14` Bartiq remains the first maintained symbolic bookkeeping path.
- `PRIM15` QREF remains the exchange/schema layer.
- `PRIM16` PsiQDK becomes the next implementation-backend candidate once the
  operator and resource boxes are understood.

## Sources

- [PsiQDK GitHub](https://github.com/psiq/psiqdk)
- [PsiQDK PyPI](https://pypi.org/project/psiqdk/)
- [Workbench README](https://github.com/PsiQ/psiqdk/tree/main/workbench)
- [Algorithms README](https://github.com/PsiQ/psiqdk/tree/main/algorithms)
