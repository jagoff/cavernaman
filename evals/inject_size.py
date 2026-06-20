"""Measure the per-level INPUT cost of the cavernaman ruleset that the
SessionStart hook injects into context every session.

`src/hooks/caveman-activate.js` now injects a compiled prompt per level.
This script measures the prompt payload by running the hook for each level and
tokenizing the stdout so we can see where the recurring input cost lives and
prove any slimming work.

No LLM calls — pure tiktoken. Reuses filter_skill_to_level from llm_run.py so
it stays byte-identical to the eval harness's notion of the filter.

Run: uv run --with tiktoken python evals/inject_size.py
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "src" / "hooks" / "caveman-activate.js"
EVALS = Path(__file__).parent

ENCODING = tiktoken.get_encoding("o200k_base")

# The non-independent levels the hook actually injects a full ruleset for.
LEVELS = ["lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"]


def count(text: str) -> int:
    return len(ENCODING.encode(text))


def run_hook(mode: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        claude_dir = Path(tmp) / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        out = subprocess.check_output(
            ["node", str(HOOK)],
            cwd=ROOT,
            env={**os.environ, "HOME": tmp, "CLAUDE_CONFIG_DIR": str(claude_dir), "CAVEMAN_DEFAULT_MODE": mode},
        )
        return out.decode("utf-8")


def main() -> None:
    print(f"=== cavernaman injected-payload size per level ===")
    print(f"_Tokenizer: tiktoken o200k_base (approximation of Claude's BPE)_")
    print(f"_Source: {HOOK.relative_to(ROOT)}_")
    print()
    print("| Level | Injected tokens |")
    print("|-------|----------------:|")

    for level in LEVELS:
        injected = run_hook(level)
        n = count(injected)
        print(f"| {level} | {n} |")

    print()
    print("_Injected every SessionStart. The compiled prompt is identical across")
    print("levels except for the level-specific lines._")


if __name__ == "__main__":
    main()
