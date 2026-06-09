# Environment Decision Note

Date: 2026-06-04

## Recommendation

Use local WSL as the primary research environment. Keep GitHub Codespaces as a
portable fallback for review, demos, or days when this laptop setup is awkward.

Local WSL is currently better for this project because:

- It runs Pixi, Jupyter notebooks, and PsiQDK locally with no cloud meter running.
- It can use the laptop's existing files, notebooks, PDFs, and generated caches.
- PsiQDK's heavy sandbox environment can stay local and ignored.
- It avoids pushing half-finished research notes just to use a cloud machine.

Codespaces is still worth preparing because:

- GitHub Pro currently includes monthly Codespaces quota for personal accounts:
  20 GB-month storage and 180 core-hours.
- It gives a clean Linux environment from any browser.
- It can be useful for sharing or reviewing the repo without fixing local setup.

## Current Setup

Primary local environment:

```bash
cd ~/PQ_CFD
pixi run test
pixi run notebook-smoke
pixi run notebook-execute
PYTHONPATH=src .cache/psiqdk-uv-venv/bin/python -m pytest -q
```

Cloud fallback:

```text
GitHub repository: https://github.com/Puspaaa/PQ_CFD
Codespaces config: .devcontainer/
Default setup: pixi install
Default check: pixi run imports
```

The Codespaces/devcontainer setup intentionally installs the normal Pixi
project environment only. It does not install PsiQDK by default, because that
environment is large and should be created only when a cloud PsiQDK trial is
actually needed.

## Codespaces Notes

Use Codespaces when:

- You want to review or present notebooks from a browser.
- Local WSL breaks due VPN, firewall, or laptop state.
- You want a clean Linux check independent of the local machine.

Avoid Codespaces as the default when:

- You are doing long-running exploration.
- You are installing large experimental SDKs.
- You are working with uncommitted local files not yet pushed to GitHub.

## Sources

- [GitHub Codespaces billing](https://docs.github.com/codespaces/codespaces-reference/about-billing-for-codespaces)
- [Codespaces included usage tips](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage)
- [GitHub dev container configuration](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)
- [Pixi devcontainer guide](https://pixi.prefix.dev/v0.43.2/integration/editor/devcontainer/)
