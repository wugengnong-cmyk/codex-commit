"""CLI entry point for codex-commit using click + rich."""

from __future__ import annotations

from pathlib import Path

import subprocess
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from codex_commit import __version__
from codex_commit.config import Config
from codex_commit.generator import (
    detect_primary_language,
    generate_message,
    get_staged_diff,
    parse_commit_message,
)

console = Console()


@click.command()
@click.option("--dry-run", is_flag=True, help="Show message only, don't commit")
@click.option("--debug", is_flag=True, help="Show raw diff and prompt")
@click.option("--model", help="OpenAI model name")
@click.option("--base-url", help="OpenAI-compatible API base URL")
@click.option("--lang", help="Language for the commit message")
@click.option("--style", type=click.Choice(["conventional", "short", "detailed"]), help="Commit message style")
@click.option("--template", help="Custom Jinja2 prompt template file")
@click.option("--temperature", type=float, help="Model temperature")
@click.version_option(version=__version__, prog_name="codex-commit")
def main(
    dry_run: bool,
    debug: bool,
    model: str | None,
    base_url: str | None,
    lang: str | None,
    style: str | None,
    template: str | None,
    temperature: float | None,
) -> None:
    """Generate a conventional commit message from staged changes using OpenAI Codex."""

    # ── Load config ──
    cfg = Config.load()

    # CLI flags override config
    if dry_run:
        cfg.dry_run = True
    if debug:
        cfg.debug = True
    if model:
        cfg.model = model
    if base_url:
        cfg.base_url = base_url
    if lang:
        cfg.lang = lang
    if style:
        cfg.style = style
    if template:
        cfg.template_path = template
    if temperature is not None:
        cfg.temperature = temperature

    # ── Step 1: Get staged diff ──
    click.echo("🔍 Reading staged changes...", nl=False)
    diff = get_staged_diff()
    click.echo(" done")

    lang_detected = detect_primary_language(diff)

    if cfg.debug:
        console.print("[dim]Diff preview:[/dim]")
        console.print(Panel(diff[:2000] + ("..." if len(diff) > 2000 else ""), title="git diff --cached"))
        console.print(f"[dim]Detected language: {lang_detected}[/dim]")

    # ── Step 2: Generate message ──
    if not cfg.dry_run:
        click.echo(f"🤖 Generating commit message ({cfg.model})...", nl=False)

    raw_message = generate_message(
        diff=diff,
        model=cfg.model,
        api_key=cfg.api_key,
        lang=cfg.lang or lang_detected,
        style=cfg.style,
        max_length=cfg.max_length,
        base_url=cfg.base_url,
        temperature=cfg.temperature,
    )

    if not cfg.dry_run:
        click.echo(" done")

    subject, body = parse_commit_message(raw_message)

    # ── Step 3: Display ──
    if cfg.dry_run:
        console.print("\n[bold]Generated commit message:[/bold]")
        console.print(Panel(raw_message, title="📝 Dry Run"))
        return

    console.print("\n[bold]Proposed commit message:[/bold]")
    display_text = subject
    if body:
        display_text += "\n\n" + body
    console.print(Panel(display_text, title="💬 Commit Message"))

    # ── Step 4: Interactive prompt ──
    while True:
        choice = Prompt.ask(
            "[a]ccept  [e]dit  [r]egenerate  [d]ry-run  [q]uit",
            default="a",
        )

        if choice.lower() in ("a", "accept", ""):
            _do_commit(subject, body or "")
            break

        elif choice.lower() in ("e", "edit"):
            click.echo("\n[Edit the message below. Save and exit to commit.]")
            edited = _edit_message(raw_message)
            if edited:
                sub, bd = parse_commit_message(edited)
                _do_commit(sub, bd or "")
            break

        elif choice.lower() in ("r", "regenerate"):
            console.print("🔄 Regenerating...")
            raw_message = generate_message(
                diff=diff,
                model=cfg.model,
                api_key=cfg.api_key,
                lang=cfg.lang or lang_detected,
                style=cfg.style,
                max_length=cfg.max_length,
                base_url=cfg.base_url,
                temperature=(cfg.temperature or 0.3) + 0.2,
            )
            subject, body = parse_commit_message(raw_message)
            console.print("\n[bold]New commit message:[/bold]")
            display_text = subject
            if body:
                display_text += "\n\n" + body
            console.print(Panel(display_text, title="💬 Commit Message"))
            continue

        elif choice.lower() in ("d", "dry-run"):
            console.print("\n[bold]Final message (not committed):[/bold]")
            display_text = subject
            if body:
                display_text += "\n\n" + body
            console.print(Panel(display_text, title="📝 Dry Run"))
            break

        elif choice.lower() in ("q", "quit"):
            console.print("👋 Aborted.")
            sys.exit(0)


def _do_commit(subject: str, body: str | None) -> None:
    """Run git commit with the generated message."""
    message = subject
    if body:
        message += "\n\n" + body

    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
        )
        console.print("✅ Committed successfully.")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Commit failed:[/red] {e}")
        sys.exit(1)


def _edit_message(raw: str) -> str | None:
    """Open the message in the user's default editor."""
    import tempfile

    editor = _detect_editor()
    if not editor:
        console.print("[yellow]⚠️  No editor found. Using fallback text input.[/yellow]")
        return click.edit(raw)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(raw)
        f.flush()
        tmp_path = f.name

    try:
        subprocess.run([editor, tmp_path], check=True)
    except subprocess.CalledProcessError:
        console.print("[red]❌ Editor exited with error.[/red]")
        return None

    edited = Path(tmp_path).read_text().strip()
    Path(tmp_path).unlink(missing_ok=True)
    return edited


def _detect_editor() -> str | None:
    """Detect the user's preferred terminal editor."""
    import os
    from shutil import which

    for var in ("EDITOR", "VISUAL"):
        editor = os.environ.get(var)
        if editor:
            return editor
    for candidate in ("vim", "nano", "nvim", "code", "emacs"):
        if which(candidate):
            return candidate
    return None


if __name__ == "__main__":
    main()
