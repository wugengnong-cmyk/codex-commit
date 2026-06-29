"""Tests for the generator module."""

from codex_commit.generator import (
    build_prompt,
    detect_primary_language,
    parse_commit_message,
)


class TestDetectPrimaryLanguage:
    """Tests for language detection from git diff."""

    def test_python_diff(self) -> None:
        diff = """diff --git a/app.py b/app.py
index abc..def 100644
--- a/app.py
+++ b/app.py
@@ -1,3 +1,5 @@
+def hello():\n+    print("world")"""
        assert detect_primary_language(diff) == "Python"

    def test_javascript_diff(self) -> None:
        diff = """diff --git a/src/index.js b/src/index.js
--- a/src/index.js
+++ b/src/index.js"""
        assert detect_primary_language(diff) == "JavaScript"

    def test_go_diff(self) -> None:
        diff = """diff --git a/main.go b/main.go
--- a/main.go
+++ b/main.go"""
        assert detect_primary_language(diff) == "Go"

    def test_rust_diff(self) -> None:
        diff = """diff --git a/src/lib.rs b/src/lib.rs
--- a/src/lib.rs
+++ b/src/lib.rs"""
        assert detect_primary_language(diff) == "Rust"

    def test_mixed_diff(self) -> None:
        diff = """
diff --git a/app.py b/app.py
diff --git a/main.py b/main.py
diff --git a/src/lib.rs b/src/lib.rs
"""
        assert detect_primary_language(diff) == "Python"

    def test_empty_diff(self) -> None:
        assert detect_primary_language("") == "Unknown"

    def test_no_extension(self) -> None:
        diff = """diff --git a/Makefile b/Makefile"""
        assert detect_primary_language(diff) == "Unknown"


class TestBuildPrompt:
    """Tests for prompt construction."""

    def test_conventional_style(self) -> None:
        diff = "diff --git a/app.py b/app.py"
        prompt = build_prompt(diff, "Python", "conventional", 72)
        assert "Conventional Commits" in prompt
        assert "Python" in prompt
        assert "72" in prompt

    def test_short_style(self) -> None:
        diff = "diff --git a/app.py b/app.py"
        prompt = build_prompt(diff, "Python", "short", 50)
        assert "oneline" in prompt.lower() or "one-line" in prompt.lower()
        assert "50" in prompt

    def test_detailed_style(self) -> None:
        diff = "diff --git a/app.py b/app.py"
        prompt = build_prompt(diff, "Python", "detailed", 72)
        assert "detailed" in prompt.lower()
        assert "breaking" in prompt.lower()

    def test_diff_included(self) -> None:
        diff = "diff --git a/test.py b/test.py"
        prompt = build_prompt(diff, "Python", "conventional", 72)
        assert diff in prompt

    def test_unknown_language(self) -> None:
        diff = "diff --git a/Makefile b/Makefile"
        prompt = build_prompt(diff, "Unknown", "conventional", 72)
        assert "Unknown" in prompt


class TestParseCommitMessage:
    """Tests for commit message parsing."""

    def test_subject_only(self) -> None:
        subject, body = parse_commit_message("feat: add new feature")
        assert subject == "feat: add new feature"
        assert body is None

    def test_subject_and_body(self) -> None:
        msg = "feat: add new feature\n\nThis is the body of the commit."
        subject, body = parse_commit_message(msg)
        assert subject == "feat: add new feature"
        assert body == "This is the body of the commit."

    def test_multiline_body(self) -> None:
        msg = "fix: resolve timeout\n\nLine one\nLine two\nLine three"
        subject, body = parse_commit_message(msg)
        assert subject == "fix: resolve timeout"
        assert body == "Line one\nLine two\nLine three"

    def test_whitespace_handling(self) -> None:
        msg = "   chore: cleanup   \n\n   trailing spaces   "
        subject, body = parse_commit_message(msg)
        assert subject == "chore: cleanup"
        assert body == "trailing spaces"

    def test_empty_body(self) -> None:
        msg = "refactor: extract logic\n\n"
        subject, body = parse_commit_message(msg)
        assert subject == "refactor: extract logic"
        assert body is None
