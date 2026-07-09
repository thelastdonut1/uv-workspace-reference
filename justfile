# Use PowerShell on Windows so recipes don't depend on a POSIX sh being on PATH
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Show available recipes
default:
    @just --list

# One-time setup after cloning: install dependencies and activate git hooks
setup:
    uv sync --all-packages
    uvx prek install

# Lint all packages (with autofix)
lint:
    uv run ruff check --fix

# Format all packages
fmt:
    uv run ruff format

# Type check all packages
typecheck:
    uv run ty check

# Run the test suite
test:
    uv run pytest

# Run every pre-commit hook against all files
check:
    uvx prek run --all-files
