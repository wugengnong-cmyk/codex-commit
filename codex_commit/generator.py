"""Commit message generation via OpenAI Codex API."""

from __future__ import annotations

import subprocess
from pathlib import Path

from openai import OpenAI


TEMPLATES_DIR = Path(__file__).parent / "templates"


# ── git helpers ──


def get_staged_diff() -> str:
    """Run `git diff --cached` and return the output."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get git diff:\n{e.stderr}")
        raise SystemExit(1) from e

    diff = result.stdout.strip()
    if not diff:
        print("⚠️  No staged changes found.\n   Stage your changes with `git add` first.")
        raise SystemExit(1)
    return diff


def detect_primary_language(diff: str) -> str:
    """Try to infer the primary language from file extensions in the diff."""
    import re

    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JSX",
        ".tsx": "TSX",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
        ".c": "C",
        ".cpp": "C++",
        ".cs": "C#",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".vue": "Vue",
        ".svelte": "Svelte",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sql": "SQL",
        ".sh": "Shell",
        ".yaml": "YAML",
        ".json": "JSON",
        ".md": "Markdown",
    }

    extensions = re.findall(r"diff --git a/(?:.*?)(\.[a-zA-Z0-9]+)", diff)
    if not extensions:
        return "Unknown"

    counts: dict[str, int] = {}
    for ext in extensions:
        lang = ext_map.get(ext, ext.lstrip("."))
        counts[lang] = counts.get(lang, 0) + 1

    return max(counts, key=counts.get)


# ── prompt construction ──


def build_prompt(diff: str, lang: str, style: str, max_length: int) -> str:
    """Build the prompt sent to Codex."""
    style_guide = {
        "conventional": (
            "The commit message MUST follow the Conventional Commits specification:\n"
            "  <type>[optional scope]: <description>\n\n"
            "  [optional body]\n\n"
            "  [optional footer(s)]\n"
            "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.\n"
            f"First line MUST be at most {max_length} characters.\n"
            "Use imperative mood: \"add\", \"fix\", \"change\" not \"added\", \"fixed\", \"changed\".\n"
            "Detect the scope automatically from the file paths."
        ),
        "short": (
            f"Write a one-line commit summary at most {max_length} characters.\n"
            "Prefix with the Conventional Commits type (feat:, fix:, etc.).\n"
            "Use imperative mood."
        ),
        "detailed": (
            "Write a detailed commit message with:\n"
            "1. A subject line (< {max_length} chars) with Conventional Commits format\n"
            "2. A blank line\n"
            "3. A body explaining WHAT changed and WHY\n"
            "4. If applicable, list breaking changes or related issues\n"
            "Use imperative mood."
        ),
    }

    prompt = (
        "You are a senior developer writing a git commit message.\n"
        f"Primary language detected: {lang}\n"
        f"{style_guide.get(style, style_guide['conventional'])}\n"
        "\n"
        "Here is the git diff:\n"
        "```\n"
        f"{diff}\n"
        "```\n"
        "\n"
        "Write the commit message only, no extra commentary."
    )
    return prompt


# ── API interaction ──


def generate_message(
    diff: str,
    model: str,
    api_key: str,
    lang: str,
    style: str,
    max_length: int,
    base_url: str | None = None,
    temperature: float | None = None,
) -> str:
    """Send the diff to Codex and return the generated commit message."""
    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = build_prompt(diff, lang, style, max_length)

    kwargs = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature

    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content

    if not content:
        print("❌ Codex returned an empty response.")
        raise SystemExit(1)

    return content.strip()


def parse_commit_message(raw: str) -> tuple[str, str | None]:
    """Split a commit message into subject and optional body."""
    lines = raw.split("\n")
    subject = lines[0].strip()
    body_lines = [l.strip() for l in lines[1:] if l.strip()]
    body = "\n".join(body_lines) if body_lines else None
    return subject, body
