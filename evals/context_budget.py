#!/usr/bin/env python3
"""Measure recurring token budget before and after local changes.

This script compares the current worktree against `HEAD` for the files that
get loaded or reinforced on every session:

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `src/hooks/caveman-activate.js` SessionStart output
- `src/hooks/caveman-mode-tracker.js` ordinary-prompt output

The goal is not exact Claude billing. The goal is a stable, reproducible
approximation that answers one question: did this change reduce recurring
context by at least 5%?
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import tiktoken


ROOT = Path(__file__).resolve().parents[1]
ENCODING = tiktoken.get_encoding("o200k_base")
DOCS = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]
BASELINE_REF = os.environ.get("CAVEMAN_BENCH_BASELINE", "HEAD^")


def token_count(text: str) -> int:
    return len(ENCODING.encode(text))


def current_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def head_text(rel_path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASELINE_REF}:{rel_path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def run_tracker(script_path: Path, claude_dir: Path) -> str:
    return subprocess.check_output(
        ["node", str(script_path)],
        cwd=ROOT,
        env={**os.environ, "HOME": str(claude_dir.parent), "CLAUDE_CONFIG_DIR": str(claude_dir)},
        input=b'{"prompt":"what is the status"}',
    ).decode("utf-8")


def run_activate(script_path: Path, claude_dir: Path) -> str:
    return subprocess.check_output(
        ["node", str(script_path)],
        cwd=ROOT,
        env={**os.environ, "HOME": str(claude_dir.parent), "CLAUDE_CONFIG_DIR": str(claude_dir)},
    ).decode("utf-8")


def tracker_head_output() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / ".cavernaman-active").write_text("full", encoding="utf-8")

        old_dir = tmp_root / "old"
        old_dir.mkdir()
        (old_dir / "caveman-config.js").write_text(current_text("src/hooks/caveman-config.js"), encoding="utf-8")
        old_tracker = old_dir / "caveman-mode-tracker.js"
        old_tracker.write_text(head_text("src/hooks/caveman-mode-tracker.js"), encoding="utf-8")
        return run_tracker(old_tracker, claude_dir)


def current_activate_output() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        return run_activate(ROOT / "src/hooks/caveman-activate.js", claude_dir)


def activate_head_output() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        (claude_dir / ".cavernaman-active").write_text("full", encoding="utf-8")

        old_dir = tmp_root / "old"
        old_dir.mkdir()
        for rel in ["caveman-config.js", "caveman-session-prompt.js"]:
            (old_dir / rel).write_text(current_text(f"src/hooks/{rel}"), encoding="utf-8")
        old_activate = old_dir / "caveman-activate.js"
        old_activate.write_text(head_text("src/hooks/caveman-activate.js"), encoding="utf-8")
        return run_activate(old_activate, claude_dir)


def main() -> int:
    print("file,current,head,saved,saved_pct")
    current_total = 0
    head_total = 0

    for rel_path in DOCS:
        cur = token_count(current_text(rel_path))
        head = token_count(head_text(rel_path))
        saved = head - cur
        pct = (saved / head * 100) if head else 0.0
        current_total += cur
        head_total += head
        print(f"{rel_path},{cur},{head},{saved},{pct:.1f}%")

    cur_tracker = token_count("")
    head_tracker = token_count(tracker_head_output())
    tracker_saved = head_tracker - cur_tracker
    tracker_pct = (tracker_saved / head_tracker * 100) if head_tracker else 0.0
    current_total += cur_tracker
    head_total += head_tracker
    print(f"src/hooks/caveman-mode-tracker.js,{cur_tracker},{head_tracker},{tracker_saved},{tracker_pct:.1f}%")

    cur_activate = token_count(current_activate_output())
    head_activate = token_count(activate_head_output())
    activate_saved = head_activate - cur_activate
    activate_pct = (activate_saved / head_activate * 100) if head_activate else 0.0
    current_total += cur_activate
    head_total += head_activate
    print(f"src/hooks/caveman-activate.js,{cur_activate},{head_activate},{activate_saved},{activate_pct:.1f}%")

    total_saved = head_total - current_total
    total_pct = (total_saved / head_total * 100) if head_total else 0.0
    print(f"total_docs_plus_tracker,{current_total},{head_total},{total_saved},{total_pct:.1f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
