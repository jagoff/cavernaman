"""Token-count the tool-result corpus before/after caveman-shrink compression.

Reads results-raw.json (produced by run.js using the real proxy code) and
reports the token reduction with tiktoken. Mirrors evals/measure.py: Node
produces, Python measures. tiktoken o200k_base approximates Claude's BPE —
ratios are meaningful, absolute numbers approximate.

Run: uv run --with tiktoken python benchmarks/tool_results/measure.py
"""

from __future__ import annotations

import json
from pathlib import Path

import tiktoken

ENCODING = tiktoken.get_encoding("o200k_base")
RAW = Path(__file__).parent / "results-raw.json"


def count(text: str) -> int:
    return len(ENCODING.encode(text))


def fmt_pct(x: float) -> str:
    sign = "−" if x < 0 else "+"
    return f"{sign}{abs(x) * 100:.0f}%"


def main() -> None:
    if not RAW.exists():
        print(f"No {RAW.name}. Run `node benchmarks/tool_results/run.js` first.")
        return

    data = json.loads(RAW.read_text())
    rows = data["results"]

    print("_Tokenizer: tiktoken o200k_base (approximation of Claude's BPE)_")
    print(f"_n = {len(rows)} representative tool-call results (prose + structured)_")
    print()
    print("| Result | Kind | Skipped | Tokens before | Tokens after | Reduction |")
    print("|--------|------|---------|--------------:|-------------:|----------:|")

    tot_b = tot_a = 0
    prose_b = prose_a = 0
    for r in rows:
        b, a = count(r["before"]), count(r["after"])
        tot_b += b
        tot_a += a
        if not r["skipped"]:
            prose_b += b
            prose_a += a
        red = fmt_pct(1 - a / b) if b else "+0%"
        print(
            f"| {r['id']} | {r['kind']} | {'yes' if r['skipped'] else 'no'} "
            f"| {b} | {a} | {red} |"
        )

    blended = 1 - tot_a / tot_b if tot_b else 0.0
    prose_only = 1 - prose_a / prose_b if prose_b else 0.0
    print()
    print(f"**Blended reduction (all results): {fmt_pct(blended)}** "
          f"({tot_b} → {tot_a} tokens)")
    print(f"**Prose-subset reduction (compressible results only): {fmt_pct(prose_only)}** "
          f"({prose_b} → {prose_a} tokens)")
    print()
    print("_Structured results (JSON/tables/listings) pass through unchanged by "
          "design — looksStructured() guards them. The blended number is the "
          "honest expected savings on a realistic mix._")


if __name__ == "__main__":
    main()
