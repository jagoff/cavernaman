# CLAUDE.md - cavernaman

## README

README is product copy. Treat it like UI text.

- Keep before/after examples first.
- Keep install commands accurate.
- Sync "What You Get" with real code.
- Preserve cavernaman voice. Do not normalize it away.
- Use real benchmark data from `benchmarks/` and `evals/`. Do not invent numbers.
- If README changes, make it understandable to a non-technical reader in under a minute.

## Project

Cavernaman makes coding agents speak in compressed caveman-style prose while keeping the technical substance intact. It ships as a Claude Code plugin, Codex plugin, Gemini CLI extension, repo rule files, and `npx skills` installable skills.

## Source of Truth

Edit the canonical file for each concern. Mirrors and build outputs follow from these.

| File | Owns |
|------|------|
| `skills/caveman/SKILL.md` | Caveman behavior and intensity levels |
| `src/rules/caveman-activate.md` | Auto-activation rule body for repo-level IDE rules |
| `src/rules/caveman-openclaw-bootstrap.md` | OpenClaw bootstrap snippet |
| `bin/lib/openclaw.js` | OpenClaw install / uninstall helper |
| `skills/caveman-commit/SKILL.md` | Commit-message mode |
| `skills/caveman-review/SKILL.md` | Review mode |
| `skills/caveman-help/SKILL.md` | One-shot help card |
| `skills/caveman-compress/SKILL.md` | Compression mode |
| `skills/cavecrew/SKILL.md` | Cavecrew delegation rules |
| `agents/cavecrew-*.md` | Cavecrew subagents |
| `src/plugins/opencode/plugin.js` | opencode plugin wiring |
| `src/plugins/opencode/commands/*.md` | opencode command prompts |

## Mirrors and build outputs

- `plugins/caveman/` mirrors the Claude plugin distribution.
- `dist/caveman.skill` is a release ZIP of `skills/caveman/`.
- Do not edit generated copies unless a sync step explicitly requires it.

## CI sync

`.github/workflows/sync-skill.yml` mirrors source skills and agents into the plugin bundle and rebuilds `dist/caveman.skill` on main pushes. If a source skill changes, expect the mirrored copy to be refreshed by CI.

## Hooks

Three hooks live in `src/hooks/` and share `src/hooks/caveman-config.js`. They communicate through `$CLAUDE_CONFIG_DIR/.caveman-active` with a fallback to `~/.claude/.caveman-active`.

- `caveman-activate.js` runs on `SessionStart`, writes the active mode, and emits the caveman ruleset as hidden context.
- `caveman-mode-tracker.js` runs on `UserPromptSubmit`, handles `/caveman` commands and activation/deactivation phrases, and handles `/caveman-stats`.
- `caveman-statusline.sh` / `.ps1` render the active badge and optional savings suffix.

Keep the hook payload small. Do not add recurring per-turn reminder text unless absolutely necessary.

## Hook install

- Plugin install wires hooks automatically.
- Standalone install uses `bin/install.js` and the `src/hooks/install.*` shims.
- Uninstall removes the hook entries and hook files; it must preserve unrelated user settings.

## Skill system

- Caveman modes: `lite`, `full`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`.
- Independent skills: `commit`, `review`, `compress`.
- `stop cavernaman` and `normal mode` must deactivate.
- Keep code/commits/PRs normal; only chat style is compressed.

## Benchmarking

- Measure token changes with real scripts in `evals/` and `benchmarks/`.
- If a number is uncertain, rerun the measurement.
- When changing token economics, compare before/after and report the delta plainly.

## Repo hygiene

- Keep files focused. Split responsibilities when a file starts doing too much.
- Preserve existing test coverage and add a regression before changing behavior.
- Do not rewrite unrelated files just to make a diff look tidy.
