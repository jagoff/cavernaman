#!/usr/bin/env python3
"""Benchmark caveman vs normal Claude output token counts."""

import argparse
import hashlib
import importlib.util
import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

# Load .env.local from repo root if it exists
_env_file = Path(__file__).parent.parent / ".env.local"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

SCRIPT_VERSION = "1.0.0"
SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
PROMPTS_PATH = SCRIPT_DIR / "prompts.json"
SKILL_PATH = REPO_DIR / "skills" / "cavernaman" / "SKILL.md"
README_PATH = REPO_DIR / "README.md"
RESULTS_DIR = SCRIPT_DIR / "results"

NORMAL_SYSTEM = "You are a helpful assistant."
BENCHMARK_START = "<!-- BENCHMARK-TABLE-START -->"
BENCHMARK_END = "<!-- BENCHMARK-TABLE-END -->"

# Levels measured by --levels. Reuse the SessionStart hook's filter so each
# arm sees exactly what a real session at that level would (single source).
DEFAULT_LEVELS = ["lite", "full", "ultra", "wenyan-full"]
LEVEL_RESULTS_PATH = RESULTS_DIR / "per_level.json"

# Reuse filter_skill_to_level from evals/llm_run.py — do not reimplement.
_llm_spec = importlib.util.spec_from_file_location(
    "llm_run", REPO_DIR / "evals" / "llm_run.py"
)
_llm = importlib.util.module_from_spec(_llm_spec)
_llm_spec.loader.exec_module(_llm)


def caveman_system_for_level(skill_md, level):
    """System prompt a real session at `level` would carry (filtered ruleset)."""
    filtered = _llm.filter_skill_to_level(skill_md, level)
    return f"{filtered}\n\nCurrent level: {level}."


def load_prompts():
    with open(PROMPTS_PATH) as f:
        data = json.load(f)
    return data["prompts"]


def load_caveman_system():
    return SKILL_PATH.read_text()


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_api(client, model, system, prompt, max_retries=3):
    delays = [5, 10, 20]
    for attempt in range(max_retries + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "text": response.content[0].text,
                "stop_reason": response.stop_reason,
            }
        except anthropic.RateLimitError:
            if attempt < max_retries:
                delay = delays[min(attempt, len(delays) - 1)]
                print(f"  Rate limited, retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                raise


def run_benchmarks(client, model, prompts, caveman_system, trials):
    results = []
    total = len(prompts)

    for i, prompt_entry in enumerate(prompts, 1):
        pid = prompt_entry["id"]
        prompt_text = prompt_entry["prompt"]
        entry = {
            "id": pid,
            "category": prompt_entry["category"],
            "prompt": prompt_text,
            "normal": [],
            "caveman": [],
        }

        for mode, system in [("normal", NORMAL_SYSTEM), ("caveman", caveman_system)]:
            for t in range(1, trials + 1):
                print(
                    f"  [{i}/{total}] {pid} | {mode} | trial {t}/{trials}",
                    file=sys.stderr,
                )
                result = call_api(client, model, system, prompt_text)
                entry[mode].append(result)
                time.sleep(0.5)

        results.append(entry)

    return results


def compute_stats(results):
    rows = []
    all_savings = []

    for entry in results:
        normal_medians = statistics.median(
            [t["output_tokens"] for t in entry["normal"]]
        )
        caveman_medians = statistics.median(
            [t["output_tokens"] for t in entry["caveman"]]
        )
        savings = 1 - (caveman_medians / normal_medians) if normal_medians > 0 else 0
        all_savings.append(savings)

        rows.append(
            {
                "id": entry["id"],
                "category": entry["category"],
                "prompt": entry["prompt"],
                "normal_median": int(normal_medians),
                "caveman_median": int(caveman_medians),
                "savings_pct": round(savings * 100),
            }
        )

    avg_savings = round(statistics.mean(all_savings) * 100)
    min_savings = round(min(all_savings) * 100)
    max_savings = round(max(all_savings) * 100)
    avg_normal = round(statistics.mean([r["normal_median"] for r in rows]))
    avg_caveman = round(statistics.mean([r["caveman_median"] for r in rows]))

    return rows, {
        "avg_savings": avg_savings,
        "min_savings": min_savings,
        "max_savings": max_savings,
        "avg_normal": avg_normal,
        "avg_caveman": avg_caveman,
    }


def run_levels(client, model, prompts, skill_md, levels, trials):
    """Per-level benchmark: normal (shared) vs caveman at each intensity level.

    Returns {level: {savings ratio, medians}} plus the raw normal arm, so the
    ratios can be dropped straight into caveman-stats.js COMPRESSION.
    """
    systems = {lvl: caveman_system_for_level(skill_md, lvl) for lvl in levels}
    per_prompt = []
    total = len(prompts)

    for i, entry in enumerate(prompts, 1):
        pid, ptext = entry["id"], entry["prompt"]
        row = {"id": pid, "normal": [], "levels": {lvl: [] for lvl in levels}}
        for t in range(1, trials + 1):
            print(f"  [{i}/{total}] {pid} | normal | trial {t}/{trials}", file=sys.stderr)
            row["normal"].append(call_api(client, model, NORMAL_SYSTEM, ptext))
            time.sleep(0.5)
            for lvl in levels:
                print(f"  [{i}/{total}] {pid} | {lvl} | trial {t}/{trials}", file=sys.stderr)
                row["levels"][lvl].append(call_api(client, model, systems[lvl], ptext))
                time.sleep(0.5)
        per_prompt.append(row)

    summary = {}
    for lvl in levels:
        savings = []
        for row in per_prompt:
            nm = statistics.median([r["output_tokens"] for r in row["normal"]])
            cm = statistics.median([r["output_tokens"] for r in row["levels"][lvl]])
            if nm > 0:
                savings.append(1 - cm / nm)
        summary[lvl] = round(statistics.mean(savings), 4) if savings else None
    return summary, per_prompt


def levels_main(args):
    prompts = load_prompts()
    levels = [s.strip() for s in args.levels.split(",") if s.strip()]
    if args.dry_run:
        print(f"Model:  {args.model}")
        print(f"Trials: {args.trials}")
        print(f"Levels: {levels}")
        print(f"Prompts: {len(prompts)}")
        print(f"Total API calls: {len(prompts) * (1 + len(levels)) * args.trials}")
        print("Dry run complete. No API calls made.")
        return
    skill_md = load_caveman_system()
    client = anthropic.Anthropic()
    print(f"Per-level benchmark: {len(levels)} levels × {len(prompts)} prompts "
          f"× {args.trials} trials, model {args.model}", file=sys.stderr)
    summary, raw = run_levels(client, args.model, prompts, skill_md, levels, args.trials)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LEVEL_RESULTS_PATH.write_text(json.dumps({
        "metadata": {
            "script_version": SCRIPT_VERSION,
            "model": args.model,
            "date": datetime.now(timezone.utc).isoformat(),
            "trials": args.trials,
            "skill_md_sha256": sha256_file(SKILL_PATH),
        },
        "compression_by_level": summary,
        "raw": raw,
    }, indent=2))

    print(f"\nWrote {LEVEL_RESULTS_PATH}", file=sys.stderr)
    print("\nMeasured COMPRESSION ratios (paste into src/hooks/caveman-stats.js):")
    print("const COMPRESSION = {")
    for lvl, ratio in summary.items():
        if ratio is not None:
            print(f"  {json.dumps(lvl)}: {ratio},")
    print("};")


def format_prompt_label(prompt_id):
    labels = {
        "react-rerender": "Explain React re-render bug",
        "auth-middleware-fix": "Fix auth middleware token expiry",
        "postgres-pool": "Set up PostgreSQL connection pool",
        "git-rebase-merge": "Explain git rebase vs merge",
        "async-refactor": "Refactor callback to async/await",
        "microservices-monolith": "Architecture: microservices vs monolith",
        "pr-security-review": "Review PR for security issues",
        "docker-multi-stage": "Docker multi-stage build",
        "race-condition-debug": "Debug PostgreSQL race condition",
        "error-boundary": "Implement React error boundary",
    }
    return labels.get(prompt_id, prompt_id)


def format_table(rows, summary):
    lines = [
        "| Task | Normal (tokens) | Caveman (tokens) | Saved |",
        "|------|---------------:|----------------:|------:|",
    ]
    for r in rows:
        label = format_prompt_label(r["id"])
        lines.append(
            f"| {label} | {r['normal_median']} | {r['caveman_median']} | {r['savings_pct']}% |"
        )
    lines.append(
        f"| **Average** | **{summary['avg_normal']}** | **{summary['avg_caveman']}** | **{summary['avg_savings']}%** |"
    )
    lines.append("")
    lines.append(
        f"*Range: {summary['min_savings']}%–{summary['max_savings']}% savings across prompts.*"
    )
    return "\n".join(lines)


def save_results(results, rows, summary, model, trials, skill_hash):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = {
        "metadata": {
            "script_version": SCRIPT_VERSION,
            "model": model,
            "date": datetime.now(timezone.utc).isoformat(),
            "trials": trials,
            "skill_md_sha256": skill_hash,
        },
        "summary": summary,
        "rows": rows,
        "raw": results,
    }
    path = RESULTS_DIR / f"benchmark_{ts}.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    return path


def update_readme(table_md):
    content = README_PATH.read_text()
    start_idx = content.find(BENCHMARK_START)
    end_idx = content.find(BENCHMARK_END)
    if start_idx == -1 or end_idx == -1:
        print(
            "ERROR: Benchmark markers not found in README.md",
            file=sys.stderr,
        )
        sys.exit(1)

    before = content[: start_idx + len(BENCHMARK_START)]
    after = content[end_idx:]
    new_content = before + "\n" + table_md + "\n" + after
    README_PATH.write_text(new_content)
    print("README.md updated.", file=sys.stderr)


def dry_run(prompts, model, trials):
    print(f"Model:  {model}")
    print(f"Trials: {trials}")
    print(f"Prompts: {len(prompts)}")
    print(f"Total API calls: {len(prompts) * 2 * trials}")
    print()
    for p in prompts:
        print(f"  [{p['id']}] ({p['category']})")
        preview = p["prompt"][:80]
        if len(p["prompt"]) > 80:
            preview += "..."
        print(f"    {preview}")
    print()
    print("Dry run complete. No API calls made.")


def main():
    parser = argparse.ArgumentParser(description="Benchmark caveman vs normal Claude")
    parser.add_argument("--trials", type=int, default=3, help="Trials per prompt per mode (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Print config, no API calls")
    parser.add_argument("--update-readme", action="store_true", help="Update README.md benchmark table")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Model to use")
    parser.add_argument(
        "--levels",
        nargs="?",
        const=",".join(DEFAULT_LEVELS),
        default=None,
        help="Per-level benchmark (caveman-vs-normal ratio per intensity). "
        f"Bare flag = {','.join(DEFAULT_LEVELS)}; or pass a CSV like lite,ultra. "
        "Prints COMPRESSION ratios for caveman-stats.js.",
    )
    args = parser.parse_args()

    if args.levels:
        levels_main(args)
        return

    prompts = load_prompts()

    if args.dry_run:
        dry_run(prompts, args.model, args.trials)
        return

    caveman_system = load_caveman_system()
    skill_hash = sha256_file(SKILL_PATH)

    client = anthropic.Anthropic()

    print(f"Running benchmarks: {len(prompts)} prompts x 2 modes x {args.trials} trials", file=sys.stderr)
    print(f"Model: {args.model}", file=sys.stderr)
    print(file=sys.stderr)

    results = run_benchmarks(client, args.model, prompts, caveman_system, args.trials)
    rows, summary = compute_stats(results)
    table_md = format_table(rows, summary)

    json_path = save_results(results, rows, summary, args.model, args.trials, skill_hash)
    print(f"\nResults saved to {json_path}", file=sys.stderr)

    if args.update_readme:
        update_readme(table_md)

    print(table_md)


if __name__ == "__main__":
    main()
