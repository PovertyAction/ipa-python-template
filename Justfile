# Set shell for Windows
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available recipes
[private]
default:
    @just --list

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

# Install required system tools, then build the environment
[group("setup")]
get-started: pre-install venv

# Install required system tools
[group("setup")]
[windows]
pre-install:
    winget install Casey.Just astral-sh.uv GitHub.cli Posit.Quarto

[group("setup")]
[linux]
pre-install:
    brew install just uv gh

[group("setup")]
[macos]
pre-install:
    brew install just uv gh
    brew install --cask quarto

# Create/update the virtual environment and install git hooks
[group("setup")]
venv:
    uv sync
    uv run pre-commit install

# Print how to activate the virtual environment
[group("setup")]
activate-venv:
    @echo "Windows (PowerShell): .venv\Scripts\Activate.ps1"
    @echo "Windows (Git Bash):   source .venv/Scripts/activate"
    @echo "macOS/Linux:          source .venv/bin/activate"
    @echo "Or prefix commands with 'uv run' instead."

# Upgrade locked dependencies and pre-commit hooks
[group("setup")]
update-reqs:
    uv lock --upgrade
    uv sync
    uv run pre-commit autoupdate

# Remove the virtual environment
[group("setup")]
[unix]
clean:
    rm -rf .venv

# Remove the virtual environment
[group("setup")]
[windows]
clean:
    if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }

# Display system information
[group("setup")]
system-info:
    @echo "CPU architecture: {{ arch() }}"
    @echo "Operating system type: {{ os_family() }}"
    @echo "Operating system: {{ os() }}"

# ---------------------------------------------------------------------------
# Develop
# ---------------------------------------------------------------------------

# Launch Jupyter Lab
[group("develop")]
lab:
    uv run jupyter lab

# Preview the Quarto docs site
[group("develop")]
preview-docs:
    quarto preview docs

# Render the Quarto docs site
[group("develop")]
build-docs:
    quarto render docs

# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

# Lint python code
[group("check")]
lint-py:
    uv run ruff check .

# Format python code
[group("check")]
fmt-py *paths=".":
    uv run ruff format {{ paths }}

# Lint sql scripts (auto-fix)
[group("check")]
lint-sql:
    uv run sqlfluff fix --dialect duckdb .

# Format markdown and Quarto files
[group("check")]
fmt-md *paths=".":
    uv run panache format {{ paths }}

# Check markdown/Quarto formatting without changing files
[group("check")]
fmt-check-md:
    uv run panache format --check .

# Lint markdown and Quarto files
[group("check")]
lint-md:
    uv run panache lint .

# Run the test suite
[group("check")]
test *args:
    uv run pytest {{ args }}

# Run the test suite with coverage
[group("check")]
test-cov:
    uv run pytest --cov=project_name --cov-report=term-missing

# Format everything
[group("check")]
fmt-all: fmt-py fmt-md

# Run all pre-commit hooks against all files
[group("check")]
pre-commit-run:
    uv run pre-commit run --all-files

# Run every check (lint, format check, tests, hooks)
[group("check")]
check-all: lint-py lint-md fmt-check-md test pre-commit-run

# Backwards-compatible aliases
alias fmt-python := fmt-py
alias fmt-markdown := fmt-md
alias fmt-check-markdown := fmt-check-md
