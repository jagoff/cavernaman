"""Measure the per-level INPUT cost of the cavernaman ruleset that the
SessionStart hook injects into context every session.

`src/hooks/caveman-activate.js` reads skills/cavernaman/SKILL.md, strips the
YAML frontmatter, filters the intensity table + example bullets to the active
level, and injects the rest verbatim. That injected payload is paid as input
tokens on every session (and the shared prose on every level). This script
reproduces the hook's filter and tokenizes the result per level so we can see
where the recurring input cost lives and prove any slimming work.

No LLM calls — pure tiktoken. Reuses filter_skill_to_level from llm_run.py so
it stays byte-identical to the eval harness's notion of the filter.

Run: uv run --with tiktoken python evals/inject_size.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import tiktoken

EVALS = Path(__file__).parent
SKILL = EVALS.parent / "skills" / "cavernaman" / "SKILL.md"

# Reuse filter_skill_to_level from llm_run.py (mirrors the SessionStart hook).
_spec = importlib.util.spec_from_file_location("llm_run", EVALS / "llm_run.py")
_llm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_llm)

ENCODING = tiktoken.get_encoding("o200k_base")

# The non-independent levels the hook actually injects a full ruleset for.
LEVELS = ["lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"]


def count(text: str) -> int:
    return len(ENCODING.encode(text))


def main() -> None:
    skill_md = SKILL.read_text()
    raw_tokens = count(skill_md)

    print(f"=== cavernaman injected-payload size per level ===")
    print(f"_Tokenizer: tiktoken o200k_base (approximation of Claude's BPE)_")
    print(f"_Source: {SKILL.relative_to(EVALS.parent)} — {raw_tokens} tokens raw_")
    print()
    print("| Level | Injected tokens | vs raw |")
    print("|-------|----------------:|-------:|")

    for level in LEVELS:
        # The hook prepends a one-line banner; include it for realism.
        banner = f"CAVERNAMAN MODE ACTIVE — level: {level}\n\n"
        injected = banner + _llm.filter_skill_to_level(skill_md, level)
        n = count(injected)
        pct = 1 - n / raw_tokens if raw_tokens else 0.0
        print(f"| {level} | {n} | −{pct * 100:.0f}% |")

    print()
    print("_Injected every SessionStart. Shared prose (Rules, Response shape,")
    print("Auto-Clarity, Boundaries) is identical across levels; only the")
    print("intensity row + matching example bullets differ._")


if __name__ == "__main__":
    main()
