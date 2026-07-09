## Toolchain

This project uses the Astral stack: uv, ruff, and ty. Use the `astral:uv`,
`astral:ruff`, and `astral:ty` skills for commands. Do not use pip, poetry,
conda, black, flake8, isort, mypy, or pyright.

- This is a uv workspace: install with `uv sync --all-packages`. Plain
  `uv sync` only syncs the (empty) virtual root and UNINSTALLS the workspace
  members from the venv.
- Commit `uv.lock` to version control.
- Do not edit dependencies in pyproject.toml by hand; use `uv add` / `uv remove`.
  If you must edit directly, dev dependencies go under `[dependency-groups]`
  (PEP 735), not the legacy `dev-dependencies` key in `[tool.uv]`.
- Tool configuration lives in `pyproject.toml` (`[tool.ruff]`, `[tool.ty]`).
- Common tasks have `justfile` recipes (`just --list`); prefer them where they
  fit. Each recipe is a thin wrapper over a uv command.

## Testing

- Framework: pytest — run with `uv run pytest`
- Unit tests live in each package's own `tests/` directory, colocated with its
  source (e.g. `packages/core/tests/`); no `__init__.py` needed
- Cross-package integration tests go in `tests/` at the workspace root
- Files named `test_*.py`, functions named `test_*`
- Shared fixtures and sample data live in that directory's `conftest.py`;
  expose constants to tests through fixtures — never `from conftest import ...`

## Pre-commit Hooks

- `.pre-commit-config.yaml` (repo root) is run by prek. Hooks for ruff, ty,
  and pytest are `repo: local` entries running `uv run ...`, so `uv.lock` is
  the only place tool versions are pinned. Do not switch them to remote hook
  repos (e.g. `ruff-pre-commit`) — that would pin versions a second time.
- prek and just are deliberately NOT dev dependencies. The dev group is only
  for tools that run inside the project env (ruff, ty, pytest); orchestrators
  are installed as uv tools or invoked via `uvx`.

## Git Hygiene

Never run `git commit --no-verify`, `git commit -n`, or any equivalent
that skips pre-commit hooks. If a hook fails, fix the underlying issue.
If a hook is genuinely broken, fix the hook in a separate commit. Do
not use `git stash` to manipulate staged state in order to dodge a hook.

## Type Checking

- Fix type errors rather than suppressing them. If a suppression is
  unavoidable, use `ty: ignore[rule-name]` — never bare or `type: ignore`.
