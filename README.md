# uv Workspace Reference

A minimal, working reference implementation of a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/): multiple Python packages in one repo, sharing a single lockfile and virtual environment, with local packages depending on each other.

The demo app fetches the top Hacker News headlines and summarizes them with OpenAI. The logic lives in two shared libraries that two front-ends consume:

```
.
├── pyproject.toml          # workspace root (virtual — not a package itself); shared ruff config
├── uv.lock                 # ONE lockfile for the whole workspace
├── .env.example            # copy to .env and fill in (OPENAI_API_KEY, PORT)
└── packages/
    ├── core/               # shared library: fetches headlines (httpx + bs4)
    │   ├── pyproject.toml
    │   └── src/core/
    ├── summarizer/         # shared library: summarizes text (openai)
    │   ├── pyproject.toml
    │   └── src/summarizer/
    ├── cli/                # CLI front-end (typer + rich), depends on core + summarizer
    │   ├── pyproject.toml
    │   └── src/cli/
    └── api/                # HTTP front-end (fastapi + uvicorn), depends on core + summarizer
        ├── pyproject.toml
        └── src/api/
```

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+ (uv will fetch Python for you if needed).

```sh
# Install everything into a single .venv at the repo root
uv sync --all-packages

# Configure your OpenAI API key (used for the summary step)
cp .env.example .env    # then edit .env and set OPENAI_API_KEY

# Run the CLI
uv run cli --limit 3

# Run the API server (defaults to port 8080, override with PORT env var)
uv run api
curl http://127.0.0.1:8080/headlines?limit=3
```

Without a valid `OPENAI_API_KEY`, the CLI still prints headlines but exits 1 at the summary step, and the API returns `503` (key missing) or `502` (OpenAI request failed).

## How the workspace is wired together

### 1. The root `pyproject.toml` declares the workspace

```toml
[tool.uv]
package = false             # the root is "virtual": it groups packages but isn't installed itself

[tool.uv.workspace]
members = ["packages/*"]    # every directory matching this glob is a workspace member
```

`package = false` makes the root a *virtual* workspace root — it exists only to define the workspace and hold shared config. If your repo instead has a primary application at the root with helper libraries alongside it, you can omit `package = false` and the root becomes a workspace member too.

### 2. Members depend on each other via `workspace = true`

In `packages/cli/pyproject.toml` (and likewise `api`), `core` and `summarizer` are declared as normal dependencies, then `[tool.uv.sources]` tells uv to resolve them from the workspace instead of PyPI:

```toml
[project]
dependencies = [
    "core",                       # ordinary dependency declarations...
    "summarizer",
    "rich>=15.0.0",
    "typer>=0.26.8",
]

[tool.uv.sources]
core = { workspace = true }       # ...but sourced from this workspace, not PyPI
summarizer = { workspace = true }
```

Workspace members are installed as *editable*, so changes to `packages/core/src/` or `packages/summarizer/src/` are picked up immediately by `cli` and `api` — no reinstall needed.

### 3. One lockfile, one environment

The entire workspace resolves together into a single `uv.lock` and installs into a single `.venv` at the root. This guarantees every package agrees on the version of every shared dependency — the main reason to use a workspace. (The flip side: members can't pin *conflicting* versions of the same package. If you need that, uv's docs suggest independent projects with `path` sources instead.)

`uv.lock` is committed. Run `uv lock --check` in CI to catch a drifted lockfile.

### 4. Each member is a real, buildable package

Every member uses the `src/` layout and the `uv_build` backend:

```toml
[build-system]
requires = ["uv_build>=0.11.7,<0.12.0"]
build-backend = "uv_build"
```

`cli` and `api` also expose console scripts via `[project.scripts]`, which is what makes `uv run cli` and `uv run api` work from the workspace root.

## Everyday commands

| Task | Command |
|---|---|
| Install / update the environment | `uv sync --all-packages` |
| Add a dependency to one member | `uv add --package core requests` |
| Run a command in a member's context | `uv run --package api -- python -c "import api"` |
| Lock without installing | `uv lock` |
| Verify lockfile is current | `uv lock --check` |
| Lint all packages | `uv run ruff check .` |
| Format all packages | `uv run ruff format .` |

Note that plain `uv sync` (without `--all-packages`) only installs the root's own dependencies; from a member directory, uv commands operate on that member but still use the shared root `.venv` and `uv.lock`.

## Notes

- Configuration comes from environment variables (`OPENAI_API_KEY`, and `PORT` for the API, defaulting to 8080), with a `.env` file as a local-dev convenience — see `.env.example`. Each front-end calls `load_dotenv()` at its entrypoint, which searches upward from the *package's source directory* (not the working directory) to the first `.env` it finds — so a single `.env` at the repo root serves both `cli` and `api`. A `.env` inside a package directory would shadow the root one for that package. Real environment variables always take precedence over `.env` values.
- Lint/format config is shared: `[tool.ruff]` lives only in the root `pyproject.toml`. Ruff's config discovery is per-file and independent of uv — each file uses the *closest* `pyproject.toml` containing a `[tool.ruff]` section, so the root config governs every package as long as members don't declare their own. `ruff` is installed via the root `[dependency-groups]` dev group (`uv sync` includes dev groups by default).
- `requires-python = ">=3.13"` is set in every member; the workspace resolves against the intersection of all members' Python requirements.
