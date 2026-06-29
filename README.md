# codex-commit ✨

**AI-powered conventional commit messages, generated from your actual code changes.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI version](https://img.shields.io/pypi/v/codex-commit)](https://pypi.org/project/codex-commit/)

`codex-commit` analyzes your staged git changes and generates a meaningful,
well-formatted commit message following the [Conventional Commits](https://www.conventionalcommits.org/)
specification — powered by OpenAI Codex.

Stop agonizing over commit messages. Let Codex read your diff and write one
that actually describes what changed and why.

---

## Features

- 🔍 **Reads `git diff --cached`** — works with your actual staged changes
- 🧠 **Powered by OpenAI Codex** — understands code semantics, not just keywords
- 📐 **Conventional Commits output** — `feat:`, `fix:`, `refactor:`, etc.
- ✏️ **Interactive preview** — see the message, edit it, approve or regenerate
- 🔧 **Custom prompt templates** — control the style and detail level
- 🧩 **Multi-language aware** — works with Python, JavaScript, Go, Rust, and more
- 🎯 **Scope detection** — automatically infers module/component scope from paths
- 🚫 **Zero config** — works out of the box with `OPENAI_API_KEY`
- 🔐 **Works with any OpenAI-compatible API** — Codex, GPT-4, or local LLMs

## Installation

```bash
# Via pip
pip install codex-commit

# Via pipx (recommended for CLI tools)
pipx install codex-commit

# Or clone and run
git clone https://github.com/<your-username>/codex-commit.git
cd codex-commit
pip install -e .
```

## Quick Start

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY='sk-...'

# 2. Stage your changes
git add .

# 3. Generate a commit message
codex-commit

# 4. Preview, edit, approve
#    You'll see something like:
#    ┌────────────────────────────────────────────┐
#    │ feat(parser): add markdown table support   │
#    │                                            │
#    │ Implements parsing for GitHub-flavored     │
#    │ markdown tables, including alignment       │
#    │ specifiers and multi-line cell content.    │
#    └────────────────────────────────────────────┘
#    [a]ccept  [e]dit  [r]egenerate  [q]uit

# 5. Accept and it auto-commits:
#    git commit -m "..."
```

## Usage

```bash
# Generate commit message from staged changes
codex-commit

# Dry run — just show the message, don't commit
codex-commit --dry-run

# Custom model / endpoint (OpenAI-compatible)
codex-commit --model gpt-4o --base-url https://api.openai.com/v1

# Custom language / style
codex-commit --lang zh           # Chinese commit message
codex-commit --style short       # One-line summary only
codex-commit --style detailed    # Full changelog format

# Custom prompt template file
codex-commit --template my-template.j2

# Debug mode — show the raw diff and prompt
codex-commit --debug
```

## Configuration

`codex-commit` respects a `pyproject.toml` or `.codex-commit.toml` in your project root:

```toml
[tool.codex-commit]
model = \"gpt-4o\"
lang = \"en\"
style = \"conventional\"
max-length = 72
scope-detection = true
temperature = 0.3
```

Or via environment variables:

```bash
export CODEX_COMMIT_MODEL=gpt-4o
export CODEX_COMMIT_LANG=zh
export CODEX_COMMIT_STYLE=short
```

## Examples

### Before
```bash
# Typical vague commit
git commit -m \"update things\"
```

### After
```bash
codex-commit
# → feat(auth): implement OAuth2 PKCE flow for mobile clients
#
# Adds Proof Key for Code Exchange (PKCE) extension to the
# OAuth2 authorization flow, enabling secure token exchange
# for public clients (mobile apps, SPAs).
```

| Diff Type | Generated Message |
|-----------|-------------------|
| New feature | `feat(api): add rate limiting with Redis backend` |
| Bug fix | `fix(parser): handle empty input in JSON decoder` |
| Refactor | `refactor(core): extract validation logic into mixin` |
| Docs | `docs(readme): update installation instructions` |
| Test | `test(cli): add integration tests for dry-run mode` |

## Template Customization

Create a Jinja2 template file to control the prompt:

```jinja2
You are a code reviewer. Analyze the following git diff and write a
commit message in {{ lang }} language.

The message must follow this structure:
- First line: {{ style }} type(scope): short description
- Body: explain the change, the motivation, and any side effects

Diff:
```
{{ diff }}
```
```

## How It Works

1. **`codex-commit`** runs `git diff --cached` to capture staged changes
2. Constructs a prompt with the diff, project context, and style preferences
3. Sends the prompt to Codex (or any OpenAI-compatible API)
4. Parses the response into a structured commit message
5. Shows it in an interactive preview — accept, edit, or regenerate
6. On accept, runs `git commit` with the generated message

## Why codex-commit?

- **Saves time** — no more staring at \"what should I write?\"
- **Better messages** — Codex sees the full diff, not just file names
- **Consistent format** — every commit follows Conventional Commits
- **Team friendly** — consistent messages make changelogs and `git blame` easier

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

- Report bugs via [GitHub Issues](https://github.com/<your-username>/codex-commit/issues)
- Submit PRs for features, fixes, or documentation
- Star the repo if you find it useful ⭐

## License

[MIT](LICENSE) — free for personal and commercial use.
"
}