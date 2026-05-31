"""Measure the output-token improvement of caveman `ultra` after the
compression-rule work (markdown-strip + response-shape templates + ultra v2
symbols/abbrev), vs the originally-shipped `ultra`, on the eval prompts.

Three arms, real `claude -p` output, tiktoken counts:
  1. terse        — "Answer concisely." (control)
  2. ultra-orig   — terse + git HEAD SKILL.md, filtered to ultra
  3. ultra-v2     — terse + working-tree SKILL.md, filtered to ultra

Headline = ultra-v2 vs ultra-orig (how much tighter ultra got). Also reports
each vs terse. Floor prompts (code/procedure-heavy) won't move — that's
expected and shown per-prompt, no metric gaming.

Run: uv run --with tiktoken python evals/ultra_delta.py
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import tiktoken

EVALS = Path(__file__).parent
PROMPTS = EVALS / "prompts" / "en.txt"
SNAPSHOT = EVALS / "snapshots" / "ultra_delta.json"
TERSE_PREFIX = "Answer concisely."

# Reuse run_claude + filter_skill_to_level from llm_run.py.
_spec = importlib.util.spec_from_file_location("llm_run", EVALS / "llm_run.py")
_llm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_llm)

ENCODING = tiktoken.get_encoding("o200k_base")


def count(text: str) -> int:
    return len(ENCODING.encode(text))


def head_skill() -> str:
    out = subprocess.run(
        ["git", "show", "HEAD:skills/cavernaman/SKILL.md"],
        capture_output=True, text=True, check=True, cwd=EVALS.parent,
    )
    return out.stdout


def fmt_pct(x: float) -> str:
    sign = "−" if x < 0 else "+"
    return f"{sign}{abs(x) * 100:.0f}%"


def main() -> None:
    prompts = [p.strip() for p in PROMPTS.read_text().splitlines() if p.strip()]
    orig_md = head_skill()
    work_md = (EVALS.parent / "skills" / "cavernaman" / "SKILL.md").read_text()

    ultra_orig_sys = f"{TERSE_PREFIX}\n\n{_llm.filter_skill_to_level(orig_md, 'ultra')}\n\nCurrent level: ultra."
    ultra_v2_sys = f"{TERSE_PREFIX}\n\n{_llm.filter_skill_to_level(work_md, 'ultra')}\n\nCurrent level: ultra."

    arms = {}
    print(f"=== {len(prompts)} prompts × 3 arms (terse, ultra-orig, ultra-v2) ===", flush=True)
    print("terse", flush=True)
    arms["terse"] = [_llm.run_claude(p, system=TERSE_PREFIX) for p in prompts]
    print("ultra-orig", flush=True)
    arms["ultra_orig"] = [_llm.run_claude(p, system=ultra_orig_sys) for p in prompts]
    print("ultra-v2", flush=True)
    arms["ultra_v2"] = [_llm.run_claude(p, system=ultra_v2_sys) for p in prompts]

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps({"prompts": prompts, "arms": arms}, ensure_ascii=False, indent=2))

    t = [count(o) for o in arms["terse"]]
    o = [count(o) for o in arms["ultra_orig"]]
    v = [count(o) for o in arms["ultra_v2"]]

    print()
    print("| # | terse | ultra-orig | ultra-v2 | v2 vs orig | v2 vs terse |")
    print("|---|------:|-----------:|---------:|-----------:|------------:|")
    deltas = []
    for i in range(len(prompts)):
        d = 1 - v[i] / o[i] if o[i] else 0.0
        deltas.append(d)
        vt = 1 - v[i] / t[i] if t[i] else 0.0
        print(f"| {i+1} | {t[i]} | {o[i]} | {v[i]} | {fmt_pct(d)} | {fmt_pct(vt)} |")

    import statistics
    print()
    print(f"**ultra-v2 vs ultra-orig — median {fmt_pct(statistics.median(deltas))}, "
          f"mean {fmt_pct(statistics.mean(deltas))}** "
          f"(totals {sum(o)} → {sum(v)} tokens, {fmt_pct(1 - sum(v)/sum(o))})")
    print(f"_ultra-v2 vs terse: {fmt_pct(1 - sum(v)/sum(t))} total ({sum(t)} → {sum(v)})_")
    print(f"_Saved {SNAPSHOT.name}_")


if __name__ == "__main__":
    main()
