# Token Savings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce recurring token cost in cavernaman without changing core behavior, and prove the reduction with before/after measurements.

**Architecture:** Keep the session-start activation path intact, remove the per-turn reinforcement payload, and shrink the maintainer docs that are read every session. Preserve behavior that users rely on, but stop paying for repeated context that does not change outcomes.

**Tech Stack:** Node.js hooks, Markdown docs, Python measurement scripts with `tiktoken`, existing repository test harness.

## Global Constraints

- Preserve caveman behavior for activation, mode switching, and statusline output.
- Do not increase recurring input cost to fix unrelated correctness bugs.
- Verify savings against the previous architecture with a reproducible token-count measurement.

---

### Task 1: Add regression coverage for per-turn reminder removal

**Files:**
- Modify: `tests/verify_repo.py`

**Interfaces:**
- Consumes: `src/hooks/caveman-mode-tracker.js` CLI behavior on ordinary prompts
- Produces: a failing assertion if the hook emits a reinforcement payload on every user prompt

- [ ] **Step 1: Write the failing test**

```python
        ordinary = run(
            ["node", "src/hooks/caveman-mode-tracker.js"],
            env={**hook_env, "CAVEMAN_DEFAULT_MODE": "full"},
            check=True,
        )
        ensure(ordinary.stdout.strip() == "", "ordinary prompts should not emit reinforcement")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/verify_repo.py`
Expected: fail while the tracker still emits `hookSpecificOutput`

- [ ] **Step 3: Write minimal implementation**

Remove the unconditional per-turn `hookSpecificOutput` block from `src/hooks/caveman-mode-tracker.js`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/verify_repo.py`
Expected: pass for the hook section and still pass the rest of the repository checks

- [ ] **Step 5: Commit**

```bash
git add tests/verify_repo.py src/hooks/caveman-mode-tracker.js
git commit -m "refactor: drop per-turn caveman reminder"
```

### Task 2: Trim session-read maintainer docs

**Files:**
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`
- Modify: `GEMINI.md`

**Interfaces:**
- Consumes: current maintainer instructions and repo layout
- Produces: shorter session-loaded guidance with the same operational constraints

- [ ] **Step 1: Write the failing test**

```bash
uv run --with tiktoken python - <<'PY'
from pathlib import Path
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
for path, limit in [("CLAUDE.md", 1500), ("AGENTS.md", 80), ("GEMINI.md", 80)]:
    n = len(enc.encode(Path(path).read_text()))
    print(path, n, "limit", limit)
PY
```

- [ ] **Step 2: Run test to verify it fails**

Expected: `CLAUDE.md` above budget, `AGENTS.md`/`GEMINI.md` still carrying unnecessary imports

- [ ] **Step 3: Write minimal implementation**

Rewrite the docs as compact maintainer instructions and remove redundant skill imports from `AGENTS.md` and `GEMINI.md`.

- [ ] **Step 4: Run test to verify it passes**

Run the same token-count command.
Expected: `CLAUDE.md` under 1500 tokens, `AGENTS.md` and `GEMINI.md` under 80 tokens each

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md AGENTS.md GEMINI.md
git commit -m "docs: compress maintainer instructions"
```

### Task 3: Measure before/after savings

**Files:**
- Create: `evals/context_budget.py`

**Interfaces:**
- Consumes: current repo docs and `git show HEAD:` baseline copies
- Produces: a markdown table with token counts and percentage savings

- [ ] **Step 1: Write the failing script**

Create a script that prints current vs `HEAD` token counts for `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and the mode-tracker reminder payload.

- [ ] **Step 2: Run the script**

Run: `uv run --with tiktoken python evals/context_budget.py`
Expected: report at least 5% total savings vs `HEAD`

- [ ] **Step 3: Commit**

```bash
git add evals/context_budget.py
git commit -m "chore: add token budget comparison"
```
