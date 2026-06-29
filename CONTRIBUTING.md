# Contributing to codex-commit

Thanks for considering a contribution! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/<your-username>/codex-commit.git
cd codex-commit
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
ruff check .
ruff format .
```

## Pre-commit

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Making Changes

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes
3. Write/update tests
4. Run `pytest` to verify everything passes
5. Run `ruff check .` to check code style
6. Commit with `codex-commit` to generate a proper commit message 😄
7. Push and open a pull request

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation if needed
- Ensure CI passes (tests + linting)

## Code of Conduct

Be respectful, constructive, and welcoming to all contributors.
