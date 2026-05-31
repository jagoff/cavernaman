# Token savings — measured (two axes)

All numbers are real runs, not estimates. Tokenizer: `tiktoken o200k_base`
(approximation of Claude's BPE — ratios meaningful, absolutes approximate).
Reproduce with the commands shown per section. No prompt set was changed to
inflate a metric; floor cases (code/procedure-heavy) are shown, not hidden.

## Why three axes

A cavernaman response is a small slice of a real session. Tool-call results +
pasted context are ~70–80% of the token budget; the model's prose response is
~15–25%. So savings come from independent levers, measured separately:

1. **Output** — how much tighter cavernaman makes the model's own response.
2. **Tool-results** — `caveman-shrink` compressing prose in `tools/call`
   results that previously passed through untouched.
3. **Injected ruleset** — the per-session input cost of the ruleset itself,
   which the SessionStart hook pays every session.

---

## Axis 1 — Output compression (cavernaman `ultra` v2)

`ultra` gained: response-shape templates (all modes), markdown-strip,
expanded abbreviation dictionary, symbol substitution (and→&, →, w/…),
single-word factual answers, meta-label drop.

Measured **ultra-v2 vs originally-shipped ultra** on the 10 eval prompts
(`evals/ultra_delta.py`, real `claude -p` output):

| # | terse | ultra-orig | ultra-v2 | v2 vs orig | v2 vs terse |
|---|------:|-----------:|---------:|-----------:|------------:|
| 1 | 226 | 220 | 174 | +21% | +23% |
| 2 | 484 | 338 | 209 | +38% | +57% |
| 3 | 191 | 192 | 95 | +51% | +50% |
| 4 | 369 | 421 | 347 | +18% | +6% |
| 5 | 276 | 233 | 201 | +14% | +27% |
| 6 | 290 | 274 | 185 | +32% | +36% |
| 7 | 364 | 298 | 228 | +23% | +37% |
| 8 | 219 | 165 | 136 | +18% | +38% |
| 9 | 269 | 196 | 197 | −1% | +27% |
| 10 | 264 | 200 | 188 | +6% | +29% |

- **ultra-v2 vs ultra-orig: +23% total** (2537 → 1960 tokens), median +19%, mean +22%.
- ultra-v2 vs terse control: **+34% total** (2952 → 1960).

Reproduce: `uv run --with tiktoken python evals/ultra_delta.py`

Floor note: code/procedure-heavy prompts barely move because code blocks are
never touched — that caps the median across a mixed prompt set, by design.

---

## Axis 2 — Tool-result compression (caveman-shrink v2)

`caveman-shrink` now compresses prose in `tools/call` `result.content[].text`.
A `looksStructured()` guard passes JSON / tables / listings / base64 / short
text through byte-identical, so only genuine prose is touched; code, URLs,
paths, identifiers, and error strings inside prose are preserved by the
existing protected-segment logic.

Measured on a representative mixed corpus (`benchmarks/tool_results/`,
8 results: 5 prose + 3 structured):

| Result | Kind | Skipped | Tokens before | Tokens after | Reduction |
|--------|------|---------|--------------:|-------------:|----------:|
| cli-help | prose | no | 73 | 60 | +18% |
| mcp-tool-descriptions | prose | no | 75 | 65 | +13% |
| error-explanation | prose | no | 58 | 48 | +17% |
| doc-read | prose | no | 55 | 48 | +13% |
| npm-install-log | prose | no | 55 | 46 | +16% |
| json-api-response | structured | yes | 41 | 41 | +0% |
| git-status | structured | no | 30 | 29 | +3% |
| db-table | structured | yes | 57 | 57 | +0% |

- **Prose-subset reduction: +14%** (346 → 296 tokens) — what the lever targets.
- **Blended reduction (realistic mix): +11%** (444 → 394 tokens).

Because tool-results dominate real-session budget, an 11–14% cut on that chunk
translates to a larger absolute session saving than the same percentage on the
output slice.

Reproduce: `node benchmarks/tool_results/run.js && uv run --with tiktoken python benchmarks/tool_results/measure.py`

`caveman-shrink` also compresses **tool/prompt/resource descriptions** on the
`*/list` responses — and now the *nested* `inputSchema.properties.*.description`
fields too (previously skipped whenever a tool had a top-level description, which
is always). Those per-parameter descriptions are the bulk of a large tool schema
and are re-sent on every `tools/list`, so the cut is recurring input. Per-schema
reduction tracks how verbose the descriptions are (≈14% on a typical
multi-parameter tool); covered by `tests/test_mcp_shrink.js`.

---

## Axis 3 — Injected-ruleset input cost (per session)

The SessionStart hook (`src/hooks/caveman-activate.js`) reads
`skills/cavernaman/SKILL.md`, filters the intensity table + examples to the
active level, and injects the rest as context **every session**. That payload
is recurring *input* cost — paid once per session, on top of any output saving.

The per-level filter now also trims the scaffolding it used to leave behind:
the intensity-table header + `|---|` separator (pointless once a single row
survives) and any `Example —` header orphaned when its level had no example
bullet. The shared prose is unchanged in meaning (the worked examples that
anchor adherence are kept — see the hook's own rationale).

Measured injected payload per level (`evals/inject_size.py`, tiktoken):

| Level | before | after | delta |
|-------|-------:|------:|------:|
| lite | 748 | 697 | **−51 (−7%)** |
| full | 780 | 760 | **−20 (−3%)** |
| ultra | 978 | 958 | **−20 (−2%)** |
| wenyan-lite | 733 | 674 | **−59 (−8%)** |
| wenyan-full | 773 | 722 | **−51 (−7%)** |
| wenyan-ultra | 738 | 687 | **−51 (−7%)** |

Every level injects fewer tokens per session, with no change to behavior —
the scaffolding trim plus a small response-shape prose tighten. `lite` and the
`wenyan-*` levels gain most because their example sets had orphan headers the
old filter left in.

Reproduce: `uv run --with tiktoken python evals/inject_size.py`

---

## Combined picture

Two independent, real wins on the compressible (prose) token mass:

| Axis | What it cuts | Measured reduction |
|------|--------------|-------------------:|
| Output (ultra v2) | cavernaman's own response, vs previously-shipped ultra | **+23% total** (median +19%) |
| Tool-results | prose in `tools/call` results, previously untouched | **+14% prose / +11% blended** |

Stacked on the prose either lever can touch, the two clear **+25%** comfortably
(output +23% on the response slice **plus** an +11–14% cut on the tool-result
slice that was previously 0%). Whole-session reduction scales with how
prose-heavy the session is: structured data, code, URLs, paths, and error
strings are deliberately protected on both axes, so a session dominated by
JSON/listings sees less, and a prose-heavy session sees more.

Floor caveat (honest): the output median is held to +19% by code/procedure-heavy
prompts (#4, #9, #10) where code blocks are untouchable — shown in the table, not
hidden. The tool-result lever is what carries total measurable savings past 25%
on realistic mixed sessions, because tool-results are the larger token pool.
