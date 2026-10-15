# Benchmark & Pricing Snapshot — Oct 15, 2026 (budget / Go-only session)

Context: user left their job (Oct 9, 2026) → OpenCode Go ($10/mo) is the only
paid route. Deliverable: a Go-only "budget" preset for `oh-my-opencode-slim.jsonc`
+ `opencode.jsonc`. Everything below is from live sources this session.

Sources: `https://opencode.ai/docs/go/` (HTML, live Oct 15), models.dev
`/api.json` provider `opencode-go` (38 models), live inference probes against
`https://opencode.ai/inference/go/v1` with the stored key, and end-to-end
`opencode run` sessions in a scratch dir (`/tmp/opencode/probe-dir`) with
per-session message inspection via `opencode api get /api/session/<id>/message`.

## Go model inventory (live, Oct 15 2026)

`ow` = open weights; `vis` = image input; caps are monthly USD usage; req
counts are the docs' estimated requests/month (Go plan).

| Model (`opencode-go/…`) | ow | ctx | vis | Price I/O | Cap | Req/mo | Reasoning opts |
|---|---|---|---|---|---|---|---|
| glm-5.3-flash | Y | 1M | v/p | $0.15/$0.50 | $60 | 31,580 | low, high, max |
| glm-5.3 | Y | 1M | – | $1.40/$4.40 | $15 | 1,080 | low, high, max |
| glm-5.2 | Y | 1M | – | $1.40/$4.40 | $60 | 4,300 | high, max |
| kimi-k3 | Y* | 1M | v | $3.00/$15.00 | $15 | 490 | max |
| kimi-k2.7-code | Y | 262K | v | $0.95/$4.00 | $60 | 6,750 | – |
| deepseek-v4.1-flash | Y | 1M | img | $0.15/$0.60 | **$80** | 173,330 | low, high, max |
| deepseek-v4-pro | Y | 1M | – | $0.66/$1.98 | $15 | 5,200 | high, max |
| mimo-v2.6-flash | Y | 1M | a/v | $0.14/$0.28 | $60 | 150,400 | – |
| mimo-v2.6-pro | Y | 1M | a/v | $0.435/$0.87 | $15 | 16,300 | – |
| qwen3.8-max | n | 1M | v | $2.00/$6.00 | $15 | 810 | low, medium, xhigh |
| qwen3.8-flash | n | 1M | v | $0.15/$0.47 | $30 | 27,000 | low, medium, xhigh |
| qwen3.7-plus | n | 1M | v | $0.40/$1.60 | $60 | 21,600 | – |
| minimax-m3 | Y | 1M | v | $0.30/$1.20 | $60 | 16,000 | toggle |
| hy4-preview | Y | 1M | – | $0.834/$2.501 | $30 | 6,770 | none, high |
| hy3 | Y | 256K | – | $0.14/$0.58 | $60 | 21,500 | none, low, high |
| space-bunny | n (anon preview) | 1M | v | $0.15/$0.60 | $30 | 15,630 | low…max (5) |
| longcat-2.0 | n | 1M | – | $0.30/$1.20 | $60 | 57,200 | toggle |
| **longcat-2.5-preview-free** | n | 1M | img | **free** | ∞ | ∞ | toggle |
| **step-5-preview-free** | n | 1M | v | **free** | ∞ | ∞ | low, medium, high |
| **cat-jam-free** | n (stealth) | 256K | – | **free** | ∞ | ∞ | low…max (5) |
| muse-spark-1.3-contributor | n | 1M | a/v | $0.10/$0.20 | $60 | 226,600 | minimal…xhigh |
| claude-haiku-5.5 | n | 1M | p | $0.10/$0.50 | $15 | 19,230 | toggle + 5 |
| gpt-6-luna | n | 1.05M | p | $0.10/$0.50 | $15 | 21,130 | none…max |
| gpt-5.6-luna | n | 1.05M | p | $0.20/$1.20 | $15 | 10,250 | none…max |
| grok-4.7 / 4.6 | n | 500K | p | $2.00/$6.00 | $15 | 845 | low…xhigh |
| gemini-4-argon-contributor | n | 1M | a/v | $4.00/$20.00 | $30 | 1,060 | low, medium, high |

\* K3 license is non-OSI. Space-bunny is an anonymous preview (`open_weights: false`
in the catalog but provider-unknown). Free-preview data policy (console docs):
LongCat 2.5 / Step 5 / Space Bunny Free = zero retention, no training; Cat Jam =
no training, 30-day safety retention, region-restricted list (BR not excluded).

**Removed/liveness notes:** `space-bunny-free` is **gone** — `opencode run
--model opencode-go/space-bunny-free#max` → "Model unavailable". The paid
`space-bunny` replaced it. DeepSeek V4 Flash + V4 Flash Vision Exp retired
Sep 10 (legacy ids reroute); V4 Pro retired Sep 14.

## New since the Sep 10 snapshot

| Model | Released | Signal |
|---|---|---|
| **MiMo-V2.6 Pro / Flash** | Sep 21–22 | Xiaomi, MIT, omnimodal. Vendor: Pro DeepSWE v1.1 **72.57** (own RL-run dashboard), Flash 67.9; Flash 87.6 / Pro 89.9 Terminal-Bench 2.1; "top open weights model in the world" (VentureBeat). Not yet independently verified. |
| **Space Bunny** | Sep 23 | Anonymous stealth preview; "tops OpenCode usage six days after launch"; 1M ctx, up to 524K output; $0.15/$0.60. Identity unknown. |
| **LongCat 2.5 Preview** | ~Sep 26 | Meituan 1.6T, 1M ctx, free on Go; **no benchmarks published**; slowest in probe (21.9s for a 1-tool-call prompt). |
| **Step 5 Preview** | Oct 8 | StepFun MoE. Kingbench **83.75%** (above GLM-5.3-Flash, behind GLM-5.3 91.25%); weights planned Oct 15; free on Go. |
| **Cat Jam** | Oct 13 | Stealth, "very fast — built for agentic coding", free on Go, 256K ctx, text-only. |

## Live probes (Oct 15, this session)

All 10 candidates returned a correct `get_weather` tool call with
`reasoning_effort` set (no 400s), via direct API (`User-Agent` header required —
bare urllib got Cloudflare 403 code 1010):

| Model | eff | latency | note |
|---|---|---|---|
| glm-5.3-flash | high | 1.1s | fastest + proven |
| cat-jam-free | high | 1.1s | matches its speed claim |
| step-5-preview-free | high | 2.0s | |
| space-bunny | max | 2.0s | |
| qwen3.8-max | xhigh | 3.8s | |
| mimo-v2.6-flash / pro | – | 4.0 / 4.8s | |
| glm-5.3 | max | 1.5s | |
| deepseek-v4.1-flash | low | 16.0s | slow even at low effort |
| longcat-2.5-preview-free | – | 21.9s | slowest |

End-to-end (`opencode run` + session message inspection): every chosen
`model#variant` resolved, and a delegated run proved preset application:

- orchestrator → `opencode-go/glm-5.3-flash`
- explorer → `opencode-go/cat-jam-free#high` (per-entry chain variant applied)
- fast-generic (custom agent) → `opencode-go/glm-5.3-flash` (preset override applies to custom agents)
- council → `glm-5.3#max`; councillors → `glm-5.3#max`, `qwen3.8-max#xhigh`, `mimo-v2.6-pro`, `space-bunny#max`

## Config mechanics learned (oh-my-opencode-slim 3.0.4 + OpenCode V2)

1. **Variant names must exist in the model's catalog metadata** ("unknown
   variant produces a model-resolution error" — V2 models doc). Values come from
   models.dev `reasoning_options` effort values (e.g. glm-5.3-flash:
   low/high/max; kimi-k3: max only; mimo-v2.6-*: none; qwen3.8-*: low/medium/
   xhigh; space-bunny: low/medium/high/xhigh/max).
2. **Fallback chains**: per-entry `{ "id": …, "variant": … }` objects; the
   agent-level `variant` string is only the default for chain[0] when that entry
   has no variant (`variantFor()` in dist). Mixed strings/objects are legal.
3. **Councillors** (`council.presets.<name>` seats) take the **seat-level**
   `variant`; per-entry object variants on seats showed up as `default` in a live
   run — use the seat-level style (`"variant": "max"` beside `"model": [...]`).
4. **Presets can override custom agents** (`agents.fast-generic` etc.) — the
   effective map is `deepMerge(config.agents, resolvedPreset.agents)`.
5. **Council preset selection is global** (`council.default_preset`), *not*
   per model preset — flip it together with `preset`.
6. **`preset` activation** binds at plugin load per directory; a running shared
   service keeps old agents until restart/next run. `bunx oh-my-opencode-slim
   doctor --json` validates config + preset resolution without a restart.
7. Go inference needs a session header (`x-opencode-session`) + non-SDK
   User-Agent for raw curl; opencode sends both.
8. **Three access modes on Go** (healthcheck, Oct 15): open-weight models →
   OpenAI `/chat/completions`; `claude-haiku-5-5` + `minimax-m2.7` → Anthropic
   `/messages`; grok/gpt/gemini/muse → a client-only protocol (raw curl 400
   `ModelProtocolUnsupported`, but `opencode run --model opencode-go/gpt-6-luna`
   works). `scripts/test-endpoints.sh` now probes the first two and skips the
   third with instructions.

## Budget preset (shipped this session)

`presets.budget` (extends default; skills/mcps inherited), all `opencode-go`:

| Seat | Chain |
|---|---|
| orchestrator | glm-5.3-flash#high → muse-spark-1.3-contributor → mimo-v2.6-flash → deepseek-v4.1-flash#high |
| oracle | glm-5.3#max → space-bunny#max → kimi-k3#max |
| librarian | step-5-preview-free#low → deepseek-v4.1-flash#low → qwen3.8-flash#low |
| explorer | cat-jam-free#high → mimo-v2.6-flash → glm-5.3-flash#low |
| designer | qwen3.8-max#xhigh → glm-5.3-flash#high |
| fixer | muse-spark-1.3-contributor#high → glm-5.3-flash#high → space-bunny#high → mimo-v2.6-flash |
| observer (disabled) | glm-5.3-flash#high |
| council (synth) | glm-5.3#max → mimo-v2.6-pro |
| fast-generic | glm-5.3-flash#low → deepseek-v4.1-flash#low |
| councillors | alpha kimi-k3#max · beta glm-5.3#max · gamma qwen3.8-max#xhigh · delta mimo-v2.6-pro |

Design rules: free previews sit on high-volume read-only seats (explorer,
librarian) so a retirement degrades to the chain, never breaks a writer seat;
the fixer runs the cheapest strong writer (Muse Spark 1.3 Contributor since
the training-tier restriction was lifted; glm-5.3-flash is its fallback);
stealth models stay clear of primary write seats (space-bunny is only an
oracle/fixer fallback now; dropped from the council roster on Oct 15).

### Policy change — restrictions lifted (later Oct 15)

Per explicit user call: **the open-weight-only restriction and the
no-data-training restriction are both removed.**

- **Training-tier models now allowed** (Muse Spark Contributor / any
  "used to improve our products" tier; free-preview terms no longer gating).
- **Bifrost OR allowlist restored**: 24 → 39 models; closed frontier set added
  back — `anthropic/claude-{fable-5.1,opus-5.5,sonnet-5.5,haiku-5.5}`,
  `openai/gpt-6-{astra-pro,astra,sol,luna}`, `google/gemini-{4-argon,3.8-flash}`,
  `x-ai/grok-{4.7,4.6}`, `meta/muse-spark-{1.3-contributor,1.3}`,
  `inception/mercury-2.5`. Backup: `config.json.bak-20261015-restrictions-lifted`.
- **Muse Spark 1.3 Contributor moved into the fixer seat** (primary). Live
  evidence pulled the same day: 368,487,309 completed sessions, 1.4M users,
  #2 by tokens (22% of 2-month volume), 67% weekly retention, 95% input-cache
  ratio, $0.0010 avg cost/session; Meta-claimed DeepSWE 1.1 75.4 / TB2.1 88.8
  (still not in the official DeepSWE artifact set). Verified live in-stack:
  fixer delegated task completed on `muse-spark-1.3-contributor#high`
  (cost $0.00013 vs the supervising orchestrator turn at $0.00125).
- Orchestrator: **Muse primary, glm-5.3-flash first fallback** (user call).
  Required a second change: on V2 the main session model comes from the
  `opencode.jsonc` root `model` — the preset orchestrator entry alone does not
  move it (that entry feeds the agent registry + retry-hook fallback chain).
  Root `model` set to `opencode-go/muse-spark-1.3-contributor`; chain is
  muse → glm-5.3-flash → mimo-v2.6-flash → deepseek-v4.1-flash. Verified live:
  fresh session ran `muse-spark-1.3-contributor` (v=None — root model keeps no
  variant).
- Quota check (Go docs, Oct 15): same $60 cap for both, but Muse ≈226.6K est
  req/mo vs GLM-Flash ≈31.6K (~7×) — cheaper tokens ($0.10/$0.20, cache-read
  $0.002 vs $0.15/$0.50/$0.03). Docs disclose the trade: "permission to use
  your prompts and completions to train future Meta models" (training: Yes,
  Not ZDR); GLM-5.3-Flash: training Not used, 0-day retention.

### Tunings + audit (later Oct 15, session 2)

| Tuning | State | Verification |
|---|---|---|
| Observer | enabled (`disabled_agents: []`) | live: analyzed a generated red-PNG via @observer on `glm-5.3-flash#high` |
| Compaction + summary | pinned to `opencode-go/muse-spark-1.3-contributor` | config (`agents.compaction/summary` in opencode.jsonc) |
| Explorer | `muse#high → cat-jam-free#high → mimo-v2.6-flash` | live: explorer session ran muse v=high |
| fast-generic | `cat-jam-free#high → glm-5.3-flash#low` | config (pattern proven twice) |
| Council alpha | `[kimi-k3, glm-5.3]` variant max (both council presets) | config; covers K3's 429 history |

**Audit — main-session token surface (measured):** trivial-turn input tokens:
- baseline (all tools): **32,932**
- + preset orchestrator `mcps` exclusions ×5 groups (browser-harness,
  firefox-devtools, jev-mcp, jev-review, agentmemory): **32,979**
- + preset orchestrator `skills: []`: **32,979**
- + firefox-devtools & browser-harness MCP servers disabled host-side: **32,979**

Conclusion: the ~33K/turn is host-owned (system prompt + instructions + env);
preset `skills`/`mcps` lists do **not** reach the main session's surface, MCP
tool schemas ride a deferred catalog and cost ~nothing. **No trim list** — the
earlier "MCP audit" plan is a dead end on this host. All temporary experiment
edits were reverted.

**Free-tier finding:** `opencode/*-free` models are client-attested
(`FreeTierError` on raw curl) and additionally require a signed-in OpenCode
Console — host logs show `OpencodeConsole.SignedOut: Reconnect OpenCode Console
to continue`, and free-model attempts fail over to Muse via the retry hook
(observed twice). Reconnect the Console, then wire `opencode/deepseek-v4.1-flash-free`
+ `opencode/muse-spark-1.3-contributor-free` (both enabled in the catalog).

**Side finding (pre-existing):** local plugins fail to load on the V2 host —
`jev-measure.ts`, `dcg-guard.ts`, `jev-screen.ts`, `rtk.ts`,
`model-announcer.ts` all die with `Schema.isStartsWith is not a function`. Fix
pending; unrelated to the model work.

### OpenRouter removed from all routing (later Oct 15)

User call: "if Go quota empties we stop" — no PAYG overflow. Changes:
- `oh-my-opencode-slim.jsonc`: 17 `openrouter/*` lines stripped (default +
  privacy preset chains, all councillor seats, council agents); trailing commas
  fixed; `"!openrouter"` mcps exclusion dropped. Backup:
  `oh-my-opencode-slim.jsonc.bak-20261015-drop-openrouter`.
- `bifrost/config.json`: `providers.openrouter` block deleted (the 39-model
  allowlist went with it) + OR fallbacks removed from 8 governance chains;
  rule descriptions cleaned. Backup:
  `config.json.bak-20261015-drop-openrouter`.
- Left in place (flagged to user): `OPENROUTER_API_KEY` env for the
  `jev-mcp`/`jev-review` MCP servers; the `openrouter` entry in `auth.json`.
- Verified: doctor ok, 0 remaining OR routing references, chains spot-checked.

**Council roster (final, 2026-10-15):** alpha `kimi-k3#max`, beta `glm-5.3#max`,
gamma `qwen3.8-max#xhigh`, delta `mimo-v2.6-pro` — 4 families, all Go, all
verified live in a real council run. The `default` council preset was flipped to
the same Go-only roster (legacy kimi-plan/zai/OpenRouter member chains removed).
`opencode.jsonc` main model, title agent (mimo-v2.6-flash), and the OptChat
compactor all moved to opencode-go.

Side fix: the pre-existing council delta held `opencode-go/space-bunny-free`,
now dead — swapped to paid `opencode-go/space-bunny` in the default council
preset too.
