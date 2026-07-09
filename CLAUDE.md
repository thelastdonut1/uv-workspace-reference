## Toolchain

This project uses the Astral stack: uv, ruff, and ty. Use the `astral:uv`,
`astral:ruff`, and `astral:ty` skills for commands. Do not use pip, poetry,
conda, black, flake8, isort, mypy, or pyright.

- Commit `uv.lock` to version control.
- Do not edit dependencies in pyproject.toml by hand; use `uv add` / `uv remove`.
  If you must edit directly, dev dependencies go under `[dependency-groups]`
  (PEP 735), not the legacy `dev-dependencies` key in `[tool.uv]`.
- Tool configuration lives in `pyproject.toml` (`[tool.ruff]`, `[tool.ty]`).

## Testing

- Framework: pytest — run with `uv run pytest`
- Unit tests live in each package's own `tests/` directory, colocated with its
  source (e.g. `packages/core/tests/`); no `__init__.py` needed
- Cross-package integration tests go in `tests/` at the workspace root
- Files named `test_*.py`, functions named `test_*`

## Type checking

- Fix type errors rather than suppressing them. If a suppression is
  unavoidable, use `ty: ignore[rule-name]` — never bare or `type: ignore`.
