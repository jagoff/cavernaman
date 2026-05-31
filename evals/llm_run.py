"""
Run each prompt through Claude Code in three conditions and snapshot the
real LLM outputs:

  1. baseline      — no extra system prompt at all
  2. terse         — system prompt: "Answer concisely."
  3. terse+skill   — system prompt: "Answer concisely.\n\n{SKILL.md}"

The honest delta is (3) vs (2): how much does the SKILL itself add on top
of a plain "be terse" instruction? Comparing (3) vs (1) conflates the
skill with the generic terseness ask, which is what the previous version
of this harness did.

This is the source-of-truth generator. It calls a real LLM and produces
evals/snapshots/results.json. Run it locally when SKILL.md files change.
The CI-side `measure.py` only reads the snapshot and counts tokens.

Requires:
  - `claude` CLI on PATH (Claude Code), authenticated

Run: uv run python evals/llm_run.py

Environment:
  CAVEMAN_EVAL_MODEL  optional --model flag value passed through to claude
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path

EVALS = Path(__file__).parent
SKILLS = EVALS.parent / "skills"
PROMPTS = EVALS / "prompts" / "en.txt"
SNAPSHOT = EVALS / "snapshots" / "results.json"

TERSE_PREFIX = "Answer concisely."

# Intensity levels measured as isolated arms so we can prove the savings gap
# between them (e.g. ultra vs full). Without this, the harness only ever sees
# caveman at its default level and can't show that ultra compresses harder.
CAVEMAN_LEVELS = ["lite", "full", "ultra"]


def filter_skill_to_level(skill_md: str, level: str) -> str:
    """Reduce caveman SKILL.md to a single intensity level.

    Mirrors the SessionStart hook filter (src/hooks/caveman-activate.js):
    strip YAML frontmatter, keep the intensity-table header/separator but only
    the active level's `| **level** |` row, and keep only the `- level:`
    example lines for that level. Everything else passes through.
    """
    body = re.sub(r"^---.*?---\s*", "", skill_md, count=1, flags=re.DOTALL)
    out: list[str] = []
    for line in body.splitlines():
        table_row = re.match(r"^\|\s*\*\*(\S+?)\*\*\s*\|", line)
        if table_row:
            if table_row.group(1) == level:
                out.append(line)
            continue
        example = re.match(r"^- (\S+?):\s", line)
        if example:
            if example.group(1) == level:
                out.append(line)
            continue
        out.append(line)
    return "\n".join(out)


def run_claude(prompt: str, system: str | None = None) -> str:
    cmd = ["claude", "-p"]
    if system:
        cmd += ["--system-prompt", system]
    if model := os.environ.get("CAVEMAN_EVAL_MODEL"):
        cmd += ["--model", model]
    cmd.append(prompt)
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def claude_version() -> str:
    try:
        out = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def main() -> None:
    prompts = [p.strip() for p in PROMPTS.read_text().splitlines() if p.strip()]
    skills = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists())

    print(
        f"=== {len(prompts)} prompts × ({len(skills)} skills + "
        f"{len(CAVEMAN_LEVELS)} caveman levels + 2 control arms) ===",
        flush=True,
    )

    snapshot: dict = {
        "metadata": {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "claude_cli_version": claude_version(),
            "model": os.environ.get("CAVEMAN_EVAL_MODEL", "default"),
            "n_prompts": len(prompts),
            "terse_prefix": TERSE_PREFIX,
        },
        "prompts": prompts,
        "arms": {},
    }

    print("baseline (no system prompt)", flush=True)
    snapshot["arms"]["__baseline__"] = [run_claude(p) for p in prompts]

    print("terse (control: terse instruction only, no skill)", flush=True)
    snapshot["arms"]["__terse__"] = [
        run_claude(p, system=TERSE_PREFIX) for p in prompts
    ]

    for skill in skills:
        skill_md = (SKILLS / skill / "SKILL.md").read_text()
        system = f"{TERSE_PREFIX}\n\n{skill_md}"
        print(f"  {skill}", flush=True)
        snapshot["arms"][skill] = [run_claude(p, system=system) for p in prompts]

    # Per-level caveman arms — isolate each intensity to prove the savings gap.
    caveman_md = (SKILLS / "caveman" / "SKILL.md").read_text()
    for level in CAVEMAN_LEVELS:
        filtered = filter_skill_to_level(caveman_md, level)
        system = f"{TERSE_PREFIX}\n\n{filtered}\n\nCurrent level: {level}."
        arm = f"caveman:{level}"
        print(f"  {arm}", flush=True)
        snapshot["arms"][arm] = [run_claude(p, system=system) for p in prompts]

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print(f"\nWrote {SNAPSHOT}")


if __name__ == "__main__":
    main()
