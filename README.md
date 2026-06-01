<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">cavernaman</h1>

<p align="center">
  <strong>why use many token when few do trick</strong>
</p>

<p align="center">
  <em>Fork of <a href="https://github.com/JuliusBrussee/caveman">caveman</a> by Julius Brussee (MIT). See <a href="NOTICE">NOTICE</a>.</em>
</p>

<p align="center">
  <a href="https://github.com/jagoff/cavernaman/stargazers"><img src="https://img.shields.io/github/stars/jagoff/cavernaman?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/jagoff/cavernaman/commits/main"><img src="https://img.shields.io/github/last-commit/jagoff/cavernaman?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/jagoff/cavernaman?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="#before--after">Before/After</a> •
  <a href="#install">Install</a> •
  <a href="#what-you-get">What You Get</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="./INSTALL.md">Full install guide</a>
</p>

---

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill/plugin (also Codex, Gemini, Cursor, Windsurf, Cline, Copilot, 30+ more) that makes agent talk like cavernaman — cuts **~75% of output tokens**, keeps full technical accuracy. Brain still big. Mouth small.

## Before / After

<table>
<tr>
<td width="50%">

### 🗣️ Normal Claude (69 tokens)

> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."

</td>
<td width="50%">

### <img src="docs/assets/dancing-rock.svg" width="20" height="20" alt="rock"/> Cavernaman Claude (19 tokens)

> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Normal Claude

> "Sure! I'd be happy to help you with that. The issue you're experiencing is most likely caused by your authentication middleware not properly validating the token expiry. Let me take a look and suggest a fix."

</td>
<td>

### <img src="docs/assets/dancing-rock.svg" width="20" height="20" alt="rock"/> Cavernaman Claude

> "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

</td>
</tr>
</table>

**Same fix. 75% less word. Brain still big.**

```
┌─────────────────────────────────────┐
│  TOKENS SAVED          ████████ 75% │
│  TECHNICAL ACCURACY    ████████ 100%│
│  SPEED INCREASE        ████████ ~3x │
│  VIBES                 ████████ OOG │
└─────────────────────────────────────┘
```

Pick your level of grunt — `lite` (drop filler), `full` (default cavernaman), `ultra` (telegraphic), or `wenyan` (classical Chinese, even shorter). One command switch. Cost go down forever.

<table align="center">
<tr><td>

### <img src="docs/assets/dancing-rock.svg" width="22" height="22" alt="rock"/> Like this trick? Now get whole agent — **caveman-code**

This skill shrink what agent **say**. **[caveman-code](https://github.com/JuliusBrussee/caveman-code)** shrink **everything** — full terminal coding agent, caveman top to bottom. **~2× fewer tokens than Codex** on identical tasks. 20+ providers · plan mode · autopilot goal loop · MIT.

```bash
npm install -g @juliusbrussee/caveman-code
```

[**▶ Try caveman-code now →**](https://github.com/JuliusBrussee/caveman-code) — *why use many token when whole agent save*

</td></tr>
</table>

## Install

One line. Find every agent. Install for each.

```bash
# macOS / Linux / WSL / Git Bash
curl -fsSL https://raw.githubusercontent.com/jagoff/cavernaman/main/install.sh | bash

# Windows (PowerShell 5.1+)
irm https://raw.githubusercontent.com/jagoff/cavernaman/main/install.ps1 | iex
```

~30 seconds. Needs Node ≥18. Skip agent you no have. Safe to re-run.

**Trigger:** type `/cavernaman` or say "talk like cavernaman". Stop with "normal mode".

One agent only, manual command, or any of 30+ other agents → [**INSTALL.md**](./INSTALL.md).
Install break? Open agent, say *"Read CLAUDE.md and INSTALL.md, install cavernaman for me."* Agent fix own brain.

## What You Get

| Skill | What |
|---|---|
| `/cavernaman [lite\|full\|ultra\|wenyan]` | Compress every reply. Levels stick until session end. |
| `/cavernaman-commit` | Conventional Commit messages, ≤50 char subject. Why over what. |
| `/cavernaman-review` | One-line PR comments: `L42: 🔴 bug: user null. Add guard.` |
| `/cavernaman-stats` | Real session token usage + lifetime savings + USD. Tweetable line via `--share`. |
| `/cavernaman-compress <file>` | Rewrite memory file (e.g. `CLAUDE.md`) into caveman-speak. Cuts ~46% input tokens every session. Code/URLs/paths byte-preserved. |
| `caveman-shrink` | MCP middleware. Wraps any MCP server, compresses tool descriptions. [npm](https://www.npmjs.com/package/caveman-shrink). |
| `cavecrew-*` | Cavernaman subagents (investigator/builder/reviewer). ~60% fewer tokens than vanilla, main context lasts longer. |

**Statusline badge** — Claude Code shows `[CAVERNAMAN] ⛏ 12.4k` (lifetime tokens saved). Updates every `/cavernaman-stats` run. Set `CAVEMAN_STATUSLINE_SAVINGS=0` to silence.

Auto-activate every session: Claude Code, Codex, Gemini (built-in). Cursor / Windsurf / Cline / Copilot get always-on rule files via `--with-init`. Other agents trigger with `/cavernaman` per session. Full feature matrix in [INSTALL.md](./INSTALL.md#what-you-get).

## Benchmarks

Real token counts from the Claude API. Average **65% output reduction** across 10 prompts (range 22-87%).

<!-- BENCHMARK-TABLE-START -->
| Task | Normal | Cavernaman | Saved |
|------|-------:|--------:|------:|
| Explain React re-render bug | 1180 | 159 | 87% |
| Fix auth middleware token expiry | 704 | 121 | 83% |
| Set up PostgreSQL connection pool | 2347 | 380 | 84% |
| Explain git rebase vs merge | 702 | 292 | 58% |
| Refactor callback to async/await | 387 | 301 | 22% |
| Architecture: microservices vs monolith | 446 | 310 | 30% |
| Review PR for security issues | 678 | 398 | 41% |
| Docker multi-stage build | 1042 | 290 | 72% |
| Debug PostgreSQL race condition | 1200 | 232 | 81% |
| Implement React error boundary | 3454 | 456 | 87% |
| **Average** | **1214** | **294** | **65%** |
<!-- BENCHMARK-TABLE-END -->

Raw data and reproduction script: [`benchmarks/`](./benchmarks/). Three-arm eval harness (baseline / terse / skill) lives in [`evals/`](./evals/) — cavernaman compared against `Answer concisely.` not against verbose default, so the delta is honest.

**caveman-compress receipts** (real memory files):

| File | Original | Compressed | Saved |
|---|---:|---:|---:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Average** | **898** | **481** | **46%** |

> [!IMPORTANT]
> Cavernaman only affects output tokens — thinking/reasoning tokens untouched. Cavernaman no make brain smaller. Cavernaman make *mouth* smaller. Biggest win is **readability and speed**, cost savings a bonus.

A March 2026 paper ["Brevity Constraints Reverse Performance Hierarchies in Language Models"](https://arxiv.org/abs/2604.00025) found that constraining large models to brief responses **improved accuracy by 26 points** on certain benchmarks. Verbose not always better. Sometimes less word = more correct.

## How cavernaman differ from caveman

cavernaman a fork of **[caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee (MIT). caveman invent whole thing — the voice, the levels, the install matrix, the hook that make Claude talk terse from message one. Big thanks. cavernaman stand on caveman shoulder. **Go star [caveman](https://github.com/JuliusBrussee/caveman).** 🙏

cavernaman add a "token-savings v2" pass on top — every number a real run:

<p align="center">
  <img src="docs/assets/diagrams/fork-lineage.png" width="680" alt="cavernaman = caveman + token-savings v2" />
</p>

- **`ultra` v2** — response-shape templates, markdown-strip, symbol swaps, single-word answers. **+23%** tighter output vs caveman shipped ultra (median +19%).
- **`caveman-shrink` v2** — compress prose in tool-call results that used to pass through untouched. **+14%** on prose; structured data (JSON/tables/code) stay byte-identical.
- **Injected-ruleset trim** — per-session ruleset cost drop **2–8%** per level, no behavior change.
- **Three-axis measurement harness** — savings checkable, floor cases shown not hidden.

cavernaman cut tokens on three independent levers, each measured separately:

<p align="center">
  <img src="docs/assets/diagrams/three-axis-savings.png" width="760" alt="Cavernaman cuts tokens on three independent axes" />
</p>

Full breakdown, repro commands, honest caveats → **[docs/cavernaman-vs-caveman.md](docs/cavernaman-vs-caveman.md)**.

## How It Work

1. Install drop skill file in agent.
2. Skill tell agent: drop filler, keep substance, use fragments.
3. For Claude Code, hook also write tiny flag file each session — agent see flag, talk cavernaman from message one. No need say `/cavernaman`.
4. Stats command read Claude Code session log, count tokens saved, write number to statusline.
5. Cavernaman-compress sub-skill rewrite memory files (CLAUDE.md, project notes) so each session start with smaller context. Save tokens forever, not just one reply.

Maintainer detail (hook architecture, file ownership, CI sync) live in [CLAUDE.md](./CLAUDE.md).

## Lobster, Meet Rock 🦞 <img src="docs/assets/dancing-rock.svg" width="22" height="22" alt="rock"/>

[**OpenClaw**](https://openclaw.ai) the self-host gateway. One box, many agent inside (Claude Code, Codex, Pi, OpenCode), wired to your Slack / Discord / iMessage / Telegram / whatever. Tagline: *"The lobster way."* Lobster strong. Lobster smart. Lobster also talk a lot.

Cavernaman teach lobster brevity — same canonical installer, scoped to one agent:

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/jagoff/cavernaman/main/install.sh | bash -s -- --only openclaw

# Windows (PowerShell): no Node? install Node ≥18 first, then
npx -y github:jagoff/cavernaman -- --only openclaw
```

Two thing happen, no more:

1. **Skill drop** at `~/.openclaw/workspace/skills/caveman/SKILL.md` — spec-correct frontmatter (`version`, `always: true`), discoverable by `openclaw skills list`. Skill not auto-inject (OpenClaw load skill on demand) — that why we also do step 2.
2. **SOUL.md nudge.** Tiny marker-fenced block appended to `~/.openclaw/workspace/SOUL.md`. OpenClaw inject SOUL.md into *every* turn under "Project Context" (12K-per-file, 60K total — block well under). Lobster terse from message one. No `/cavernaman` per session. No nag.

```
~/.openclaw/workspace/
├── skills/caveman/SKILL.md   ← full ruleset, on-demand load
└── SOUL.md                    ← <!-- caveman-begin --> ... <!-- caveman-end -->
                                  ↑ auto-inject every turn
```

Custom workspace path? `OPENCLAW_WORKSPACE=/your/path` before the command. Uninstall: same one-liner with `--uninstall` — skill folder gone, SOUL.md block ripped out cleanly, your other workspace content stay untouched. Idempotent re-runs (frontmatter not double-prepended, marker block not duplicated).

Lobster claw still sharp. Lobster mouth now small. Brain still big.

## Cavernaman Ecosystem

Five tools. One philosophy: **agent do more with less**.

| Repo | What |
|------|------|
| [**cavernaman**](https://github.com/jagoff/cavernaman) *(you here)* | Output compression — *why use many token when few do trick* |
| [**caveman-code**](https://github.com/JuliusBrussee/caveman-code) | Whole terminal coding agent — *why use many token when whole agent can save* |
| [**cavemem**](https://github.com/JuliusBrussee/cavemem) | Cross-agent memory — *why agent forget when agent can remember* |
| [**cavekit**](https://github.com/JuliusBrussee/cavekit) | Spec-driven build loop — *why agent guess when agent can know* |
| [**cavegemma**](https://github.com/JuliusBrussee/finetune-cavernaman) | Gemma 4 31B fine-tuned on cavernaman pairs — *why prompt every turn when weight remember* |

Compose: cavekit drive build, cavernaman compress what agent *say*, cavemem compress what agent *remember*, cavegemma bake compression into weight, caveman-code ship it all as one terminal agent. One rock. Two rock. Three rock. Four rock. Five rock. That it.

## Links

- [INSTALL.md](./INSTALL.md) — full install matrix, all flags, per-agent detail
- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to send patch
- [CLAUDE.md](./CLAUDE.md) — maintainer guide (file ownership, hook architecture, CI)
- [docs/](./docs/) — extra guides (Windows install, etc.)
- [Issues](https://github.com/jagoff/cavernaman/issues) — bug, feature, weird behavior

## Star This Repo

Cavernaman save you token, save you money. Star cost zero. Fair trade. ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=jagoff/cavernaman&type=Date)](https://star-history.com/#jagoff/cavernaman&Date)

## Also by Julius Brussee

- **[Revu](https://github.com/JuliusBrussee/revu-swift)** — local-first macOS study app with FSRS spaced repetition. [revu.cards](https://revu.cards)

## License

MIT — free like mass mammoth on open plain.
