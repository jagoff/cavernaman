#!/usr/bin/env python3
"""20-turn A/B session token budget benchmark.

This is a reproducible proxy for the recurring input cost of cavernaman.
It compares the current worktree against HEAD and asks one question:
over the same prompt sequence, does the new architecture use fewer input
tokens than the previous one?

What it measures:
- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `src/hooks/caveman-activate.js` SessionStart payload
- per-turn reinforcement from `src/hooks/caveman-mode-tracker.js`
- the 20-turn prompt set in `evals/prompts/en.txt`

The model output is not involved. This is a token-budget benchmark, not an
LLM quality benchmark.

Set `CAVEMAN_BENCH_TURNS=100` to run a longer A/B pass.
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import tempfile
from pathlib import Path

import tiktoken


ROOT = Path(__file__).resolve().parents[1]
ENCODING = tiktoken.get_encoding("o200k_base")
PROMPTS = [p.strip() for p in (ROOT / "evals" / "prompts" / "en.txt").read_text(encoding="utf-8").splitlines() if p.strip()]
TURN_COUNT = int(os.environ.get("CAVEMAN_BENCH_TURNS", "20"))
DOCS = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]
BASELINE_REF = os.environ.get("CAVEMAN_BENCH_BASELINE", "HEAD^")


def count(text: str) -> int:
    return len(ENCODING.encode(text))


def read_current(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def read_head(rel_path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASELINE_REF}:{rel_path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def tracker_output(script_path: Path, claude_dir: Path, prompt: str) -> str:
    return subprocess.check_output(
        ["node", str(script_path)],
        cwd=ROOT,
        env={**os.environ, "HOME": str(claude_dir.parent), "CLAUDE_CONFIG_DIR": str(claude_dir)},
        input=json.dumps({"prompt": prompt}).encode("utf-8"),
    ).decode("utf-8")


def activate_output(script_path: Path, claude_dir: Path) -> str:
    return subprocess.check_output(
        ["node", str(script_path)],
        cwd=ROOT,
        env={**os.environ, "HOME": str(claude_dir.parent), "CLAUDE_CONFIG_DIR": str(claude_dir)},
    ).decode("utf-8")


def head_tracker_output(prompt: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / ".cavernaman-active").write_text("full", encoding="utf-8")

        old_dir = tmp_root / "old"
        old_dir.mkdir()
        (old_dir / "caveman-config.js").write_text(read_current("src/hooks/caveman-config.js"), encoding="utf-8")
        old_tracker = old_dir / "caveman-mode-tracker.js"
        old_tracker.write_text(read_head("src/hooks/caveman-mode-tracker.js"), encoding="utf-8")
        return tracker_output(old_tracker, claude_dir, prompt)


def current_activate_output() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        return activate_output(ROOT / "src/hooks/caveman-activate.js", claude_dir)


def head_activate_output() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        claude_dir = tmp_root / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        (claude_dir / ".cavernaman-active").write_text("full", encoding="utf-8")

        old_dir = tmp_root / "old"
        old_dir.mkdir()
        for rel in ["caveman-config.js", "caveman-session-prompt.js"]:
            (old_dir / rel).write_text(read_current(f"src/hooks/{rel}"), encoding="utf-8")
        old_activate = old_dir / "caveman-activate.js"
        old_activate.write_text(read_head("src/hooks/caveman-activate.js"), encoding="utf-8")
        return activate_output(old_activate, claude_dir)


def main() -> int:
    turns = list(itertools.islice(itertools.cycle(PROMPTS), TURN_COUNT))

    current_docs_tokens = sum(count(read_current(doc)) for doc in DOCS)
    head_docs_tokens = sum(count(read_head(doc)) for doc in DOCS)

    current_activate_tokens = count(current_activate_output())
    head_activate_tokens = count(head_activate_output())

    current_tracker_tokens = 0
    head_tracker_tokens = count(head_tracker_output("what is the status"))

    current_overhead = current_docs_tokens + current_activate_tokens + current_tracker_tokens
    head_overhead = head_docs_tokens + head_activate_tokens + head_tracker_tokens

    print(f"{TURN_COUNT}-turn A/B session budget")
    print("turn,current_input,baseline_input,saved,saved_pct")

    total_current = 0
    total_head = 0
    for idx, prompt in enumerate(turns, start=1):
        prompt_tokens = count(prompt)
        cur = current_overhead + prompt_tokens
        head = head_overhead + prompt_tokens
        saved = head - cur
        pct = (saved / head * 100) if head else 0.0
        total_current += cur
        total_head += head
        print(f"{idx},{cur},{head},{saved},{pct:.1f}%")

    total_saved = total_head - total_current
    total_pct = (total_saved / total_head * 100) if total_head else 0.0
    print(f"total,{total_current},{total_head},{total_saved},{total_pct:.1f}%")
    print("result,PASS" if total_pct >= 5.0 else "result,FAIL")
    return 0 if total_pct >= 5.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
