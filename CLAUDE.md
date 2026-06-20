# CLAUDE.md - cavernaman

Hot-path maintainer notes. Keep this file small.

## What matters here

- README is product copy. Preserve voice, before/after examples, and accurate install commands.
- When changing token economics, measure with `evals/` or `benchmarks/` and report the real delta.
- Keep generated copies out of manual edits.

## Canonical files

- `skills/cavernaman/SKILL.md` — caveman behavior and intensity levels
- `src/hooks/caveman-activate.js` — SessionStart hook
- `src/hooks/caveman-session-prompt.js` — compiled session prompt
- `src/hooks/caveman-mode-tracker.js` — mode tracking and `/caveman-stats`
- `src/hooks/caveman-statusline.sh` / `.ps1` — badge output
- `src/rules/caveman-activate.md` — repo rule body
- `src/rules/caveman-openclaw-bootstrap.md` — OpenClaw bootstrap snippet
- `bin/lib/openclaw.js` — OpenClaw helper
- `skills/caveman-commit/SKILL.md`, `skills/caveman-review/SKILL.md`, `skills/caveman-help/SKILL.md`, `skills/caveman-compress/SKILL.md` — submodes
- `skills/cavecrew/SKILL.md` and `agents/cavecrew-*.md` — cavecrew delegation
- `src/plugins/opencode/plugin.js` and `src/plugins/opencode/commands/*.md` — opencode wiring

## Hooks

- `caveman-activate.js` writes the mode flag and injects the compiled prompt.
- `caveman-mode-tracker.js` keeps the flag in sync with commands and natural-language toggles.
- `caveman-statusline.*` renders the active badge and savings suffix.
- Keep the hook payload small. Every recurring token here compounds.

## Install / uninstall

- Plugin install wires hooks automatically.
- Standalone install uses `bin/install.js` and the `src/hooks/install.*` shims.
- Uninstall must remove only caveman-owned entries and files.

## Benchmarks

- `evals/context_budget.py` measures recurring doc + hook overhead.
- `evals/session_ab_20.py` measures a 20-turn A/B session budget.
- Re-run the measurement if the number is uncertain.

## Hygiene

- Split files when responsibility starts creeping.
- Preserve test coverage and add regressions before behavior changes.
- Do not rewrite unrelated files to make the diff look tidy.
