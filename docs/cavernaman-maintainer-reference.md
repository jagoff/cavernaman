# Cavernaman maintainer reference

This doc holds the detail removed from `CLAUDE.md` so the hot-path file stays small.

## Project

Cavernaman makes coding agents speak in compressed caveman-style prose while keeping the technical substance intact. It ships as a Claude Code plugin, Codex plugin, Gemini CLI extension, repo rule files, and `npx skills` installable skills.

## Source of truth map

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

Three hooks live in `src/hooks/` and share `src/hooks/caveman-config.js`. They communicate through `$CLAUDE_CONFIG_DIR/.cavernaman-active` with a fallback to `~/.claude/.cavernaman-active`.

- `caveman-activate.js` runs on `SessionStart`, writes the active mode, and emits the compiled caveman prompt as hidden context.
- `caveman-mode-tracker.js` runs on `UserPromptSubmit`, handles `/caveman` commands and activation/deactivation phrases, and handles `/caveman-stats`.
- `caveman-statusline.sh` / `.ps1` render the active badge and optional savings suffix.

## Skill system

- Caveman modes: `lite`, `full`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`.
- Independent skills: `commit`, `review`, `compress`.
- `stop cavernaman` and `normal mode` must deactivate.
- Keep code/commits/PRs normal; only chat style is compressed.
