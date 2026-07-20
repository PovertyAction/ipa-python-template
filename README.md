# Python project template

Template repository for a python project.

## Project layout

```text
├── src/project_name/   # Python package code (rename to your project)
├── tests/              # pytest test suite
├── docs/               # Quarto documentation site
├── Justfile            # common command line tasks (run `just` to list them)
├── pyproject.toml      # project metadata, dependencies, and tool config
├── panache.toml        # markdown/Quarto formatter and linter config
└── uv.lock             # locked dependency versions for reproducible builds
```

After creating a project from this template, rename the package: change
`name = "project-name"` in `pyproject.toml`, rename the `src/project_name/`
directory to match (dashes become underscores), then run `uv lock` and
`uv sync`.

## Development set up

Development relies on the following software

- `winget` (Windows) or `homebrew` (MacOS/Linux) or `snap` (Linux) for package
  management and installation
- `git` for source control management
- `just` for running common command line patterns
- `uv` for installing Python and managing virtual environments

This repository uses a `Justfile` for collecting common command line actions that we run
to set up the computing environment and build the assets of the project. Note that you
should also have Git installed

To get started, make sure you have `Just` installed on your computer by running the
following from the command line:

| Platform  | Commands                                                            |
| --------- | ------------------------------------------------------------------- |
| Windows   | `winget install Git.Git Casey.Just astral-sh.uv GitHub.cli Posit.Quarto` |
| Mac/Linux | `brew install just uv gh`                                          |

This will make sure that you have the latest version of `Just`, as well as
[uv](https://docs.astral.sh/uv/) (installer for Python) and
[Quarto](https://quarto.org/docs/guide/) (for writing and compiling scientific and
technical documents).

- We use `Just` in order to make it easier for all IPA users to be productive with data
  and technology systems. The goal of using a `Justfile` is to help make the end goal of
  the user easier to achieve without needing to know or remember all of the technical
  details of how we get to that goal.
- We use `uv` to help ease use of Python. `uv` provides a global system for creating and
  building computing environments for Python.
- We use Quarto to allow users to focus on writing and data analytics. Writing in
  markdown, jupyter notebooks, python scripts, R scripts, etc. makes it easier to
  review, update, and deploy technical documentation.
- We also recommend using in Integrated Development Environment (IDE).
  Preferred options are `VS Code` or `Positron`.

| Platform  | Commands                                                            |
| --------- | ------------------------------------------------------------------- |
| Windows   | `winget install Microsoft.VisualStudioCode`                         |
| Mac       | `brew install --cask visual-studio-code`                            |
| Linux     | `sudo snap install code --classic`                                  |

| Platform  | Commands                                                            |
| --------- | ------------------------------------------------------------------- |
| Windows   | `winget install Posit.Positron`                                     |
| Mac       | `brew install --cask positron`                                      |

As a shortcut, if you already have `Just` installed, you can run the following to
install required software and build a python virtual environment:

```bash
just get-started
```

Note: you may need to restart your terminal after running the command above to activate
the installed software.

After the required software is installed, you can activate the Python virtual
environment:

| Shell      | Commands                                |
| ---------- | --------------------------------------- |
| Bash       | `.venv/Scripts/activate`                |
| Powershell | `.venv/Scripts/activate.ps1`            |
| Nushell    | `overlay use .venv/Scripts/activate.nu` |

## Common tasks

Run `just` with no arguments to list all available recipes. The most common ones:

| Command             | What it does                                            |
| ------------------- | ------------------------------------------------------- |
| `just venv`         | Create/update the virtual environment and install hooks |
| `just test`         | Run the test suite with pytest                          |
| `just test-cov`     | Run tests with a coverage report                        |
| `just fmt-all`      | Format python (ruff) and markdown/Quarto (panache)      |
| `just lint-py`      | Lint python code with ruff                              |
| `just lint-md`      | Lint markdown/Quarto files with panache                 |
| `just check-all`    | Run every check: lint, format check, tests, hooks       |
| `just preview-docs` | Preview the Quarto docs site locally                    |
| `just update-reqs`  | Upgrade locked dependencies and pre-commit hooks        |

## Code quality tooling

- **[ruff](https://docs.astral.sh/ruff/)** lints and formats python code.
- **[panache](https://panache.bz/)** lints and formats markdown and Quarto files
  (configured in `panache.toml`).
- **[pre-commit](https://pre-commit.com/)** runs these checks automatically on every
  commit (installed by `just venv`).
- **[pytest](https://docs.pytest.org/)** runs the test suite in `tests/`.

All checks also run in CI on pull requests to `main`.
