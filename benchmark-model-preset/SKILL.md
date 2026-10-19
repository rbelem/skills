---
name: benchmark-model-preset
description: Research model benchmarks (DeepSWE, Artificial Analysis, Design Arena) and provider pricing (OpenCode Go/Zen, OpenRouter, z.ai, MiniMax, OmniRoute) to build optimal-value oh-my-opencode-slim presets. Use when user wants to optimize presets, compare models, audit agent routing, or evaluate subscription-vs-PAYG cost.
---

# Benchmark Model Preset

Build optimal-value oh-my-opencode-slim presets by cross-referencing **verified** benchmark scores, provider pricing, and agent role requirements.

## Agent Role → Model Requirements

| Agent | Key Requirement | Best Signal |
|---|---|---|
| **Orchestrator** | Strong general coding + delegation judgment | DeepSWE Pass@1 + Arena Agent "Net Improvement" |
| **Oracle** | Deep reasoning, correctness, architecture | DeepSWE + AA intelligence index — always `variant: max` |
| **Council** | Consensus across diverse providers/families | Mix models from different namespaces, not just tier swaps |
| **Librarian** | Fast lookup, instruction following | Speed (latency/throughput), cheap |
| **Explorer** | Fast codebase search, pattern matching | Speed, cheap — benchmark scores less relevant |
| **Designer** | UI/UX quality, visual output | Design Arena ELO (UI component/website categories) |
| **Fixer** | Reliable bounded implementation | DeepSWE + consistency (low variance) — prefer **verified** Go models over self-reported scores |
| **Observer** | Vision, PDF/document reading | Vision capability, multimodal quality |

## Hy3 — Verified-Score Caveat

Tencent Hy3 (Apache 2.0, 295B MoE/21B active). **Self-reported** scores: SWE-bench Verified 78%, DeepSWE 28. AA Intelligence Index 34→**42.2** (updated Aug 2026, still below every frontier model). **Now on Go** ($0.14/$0.58, usage $60 → ~21.5K/mo) + OpenRouter $0.13/$0.53. Arena Agent **−2.38%**. Text-only. Reasoning modes: `no_think` (default), `low`, `high`. Structured output errors 7–11%, tool call errors 3–4%.

**Council maybe, fixer no** — kimi-k2.7-code (DeepSWE 31%, verified) and the 0731-refreshed deepseek-v4-flash (AA 51.8) beat Hy3 on every independent metric. Reach for Hy3 only when you need Tencent-provider diversity in council.

## GLM-5.3 Variant Notes

Released **Aug 14, 2026** — post-training upgrade on the GLM-5.2 base (744B total/40B active MoE, 1M ctx). Two reasoning levels map to `"variant"`: `max` (default) and `high` (faster/cheaper); `low` also exists. **Thinking is required — there is no think-off** (unlike 5.2).

**Independent signal (Aug 24):** AA Intel **59.5**, Coding **74.8**, Agentic **59.1** — the latter is the **highest agentic index of ANY model** (beats GPT-5.6 Sol 57.8, Fable 5 56.6). Design Arena overall **1347 (#5)**, GLM-5.2 was 1331. **Vendor-reported** DeepSWE 66.9 / Terminal-Bench 3.0 28.3 / Toolathlon 73.0 / AutomationBench 48.2 — not yet on the official DeepSWE leaderboard or Arena Agent (as of Aug 24).

Pricing: $1.40/$4.40 on Go (usage $15 → ~1,080/mo) and OpenRouter; z.ai Coding Plan quota multiplier (2–3×/prompt) unchanged. Open weights expected ≈Aug 28 (safety eval pending). **Always `max` for Oracle and Council; workhorse fixer if quota allows.**

## GLM-5.3-Flash Notes

Released **Aug 26, 2026** — revealed as the stealth **Ox Alpha** (OR swapped `stealth/ox-alpha` → `z-ai/glm-5.3-flash` same day). **MIT open weights** on HF (`zai-org/GLM-5.3-Flash`), 320B total/18B active MoE, first GLM-5 **native multimodal** (text+image+video→text), 1M ctx, hybrid sparse+linear attention + IndexPool (3.01× less attention compute, 4.44× less KV than GLM-5.3).

**Independent signal (AA, published day-of-release):** Intel **57** ($0.09/task, 150M verbosity). Vendor-reported: DeepSWE **63.4** (vs GLM-5.2 46.2, DS V4 Flash 54.4), Terminal-Bench 2.1 **84.3**, AutomationBench **48.8**, OfficeQA Pro (vision) 62.4.

Pricing: **$0.15/$0.50** z.ai + Go (usage $15 → ~7,900/mo) · **OR $0.075/$0.25** (launch promo 50% off) · **z.ai Coding Plan: 3× quota vs GLM-5.3, off-peak (incl. weekends) = 50% points**. Reasoning mandatory, efforts max/high/low.

**Preset status (Aug 26):** swapped in as orchestrator+fixer for both presets — quality → `opencode-go/glm-5.3-flash`, value → `zai/glm-5.3-flash` (bifrost chain: zai → deepseek-v4-flash → opencode-go). Beats DS V4 Flash 0731 on AA (+5.2) at lower price; multimodal bonus for visual-coding/frontend work. **Observer: PASSED the controlled vision QA (Aug 26, round 3)** — 4/4 exact transcript (A1 code `DEEPSWE-VISION-QA-42` read exactly, no Q→O like flash-vision-exp), shapes detailed (circle/square/line, colors, unfilled), 2/2 clean reliability probes (1.6s/6.8s), matched MiniMax-M3 on every criterion at half the price → **observer swapped to flash (max) in both presets**. M3 kept as documented fallback (bifrost minimax-m3 chain intact). Open-source domestic-chip serving (ReplaySSM, W8A8, EPD) — performance varies by provider; speed not yet on AA.

## DeepSeek V4.1-Flash-1017 Notes

Released **Oct 17, 2026** — in-place weight upgrade, **same API ID**
(`deepseek-flash`; Go: `opencode-go/deepseek-v4.1-flash`) and **same pricing**.
No config edit needed — the upgrade flows through the existing ID (probe-verified
live same-day, `#high` + `#low`). **Vendor-reported** (unverified, DeepSeek
Harness/Mini-SWE-V2): DeepSWE v1.1 **77.0** (was 74.2), Terminal-Bench 4.0 42.3,
AutomationBench v1.0.6 60.5, NL2Repo 68.2, plus native multimodal (BabyVision 92.5,
Chartography 83.0). 1M ctx, MIT weights. Go terms are the most generous of any
seat: **$80/mo cap, ~173K req/mo**, off-peak = half price (weekdays 01–04/06–10 UTC
peak). Already in budget orchestrator tail + librarian.

**Do NOT promote to fixer/observer on vendor numbers alone** — no independent
AA/DeepSWE-leaderboard score yet for 1017 (released today). Revisit when verified
scores land; the $80 bucket makes it the natural promotion candidate for a
high-volume seat if quality confirms. Tie-break via `spawn-ori-eval` if close.

**Testing (Oct 17, user call):** Bug Hunt Bench indie signal (1017 max 38.7 vs
Opus 5.5 high 31.7, n=2–3, effort-mismatched) judged credible-enough to trial.
`opencode-go/deepseek-v4.1-flash#high` is now head of budget **orchestrator** and
**fixer** (Muse 1.3/1.2 demoted to fallbacks, chains otherwise intact).
Revert = move the deepseek entry back to tail (orchestrator) / drop it (fixer).

## MiniMax M3.1 Flash Notes

Released **Oct 19, 2026** — free-only on Go (`opencode-go/minimax-m3.1-flash-free`,
**Free, Unlimited reqs**, "limited time") and on Console
(`opencode/minimax-m3.1-flash-free`, probe UP). 428B total / ~23B active MoE,
sparse attention, native visual encoder, 1M ctx (512K out), multimodal
(text+image+video in). Reasoning always-on, 5 efforts (low…max);
`thinking.type=disabled` → 400. **Independent (AA):** Intelligence Index **42**
(M3 = 29.2, M2.7 = 22.8). **Vendor-only:** DeepSWE v1.1 73.7, Terminal-Bench
4.0 38.1 — no AA Coding/Agentic sub-index yet, no Arena appearance. Weights
~Oct 23, license undisclosed. Go privacy row: training **Not used**, retention
**0 days**; free previews are region-excluded in ~20 countries.

**Smoke (Oct 19, `opencode-go/minimax-m3.1-flash-free#low`):** tool call PASS
(1 bash call completed, exact output; 2-step shell OK) · vision PARTIAL
(3/3 shapes exact with color + fill state, but the text token `VQA-7319-M3F`
read as `V0A-7319-M3F` — Q→0, so **not observer-grade**; the GLM-5.3-Flash bar
is 4/4 exact).

**Preset status (Oct 19):** free head of **librarian** and **fast-generic**
(verified live, cost 0; a live @fast-generic delegation ran on it), first
fallback of **explorer**, free tail of **investigator**, head of the
**orchestrator** chain and the **council.epsilon** seat (both user calls),
and the `opencode.jsonc` title/compaction/summary model (replacing the retired
`opencode/space-bunny-free`). Its only coding signal is vendor-reported
(DeepSWE 73.7) and AA has no Coding/Agentic sub-index yet, so it is a
reader/lookup seat first; the orchestrator and council seats are deliberate
overrides of the "writers stay on paid heads" rule. Flip the root session
model to it only if the AA-42 quality is acceptable for the main session.

## Qwen3.8-Flash-Next Notes

Released **Aug 26, 2026** — Qwen4 architecture preview. 125B/6B active MoE + 51B n-gram embeddings + 4B MTP, GDN + Qwen Sparse Attention, 262K native ctx (1M ext), multimodal (HF `image-text-to-text`, qwen4_exp tag), Qwen Community License (open weights). Vendor: DeepSWE 58.7, SWE-bench Pro 62.5, GPQA 91.7, LCBv6 91.9, CoWorkBench 73.9, JobBench 55.7, Toolathlon 73.5.

**Not on any API yet** (no OR/Go/Zen listing, Qwen Cloud pricing TBD) — no config action; watch for API availability + verified benchmarks. Closest API-available qwen3.8 tier is `qwen3.8-27b` (OR only, $0.425/$2.55, AA 52/68.1/50.9).

## Kimi K3 Notes

Released Jul 16; **Arena Agent +10.41% (#4 overall — best open model by far, Aug 19 snapshot)**, AA 59.7/76.2/54.3, **Design Arena #1 overall (1407) and #1 fullstack (1361)**. DeepSWE 67.5 is vendor-reported (not on official leaderboard). $3/$15 on Go (usage $15 → ~490/mo), Zen, OR. **Capacity risk: frequent 429s** — pair with `opencode-go/kimi-k3` fallback (bifrost circuit breaker already does this). Only `reasoning_effort=max` supported. `kimi-for-coding/k3-256k` = 256K-ctx variant via the Kimi for Coding plan (kimi.com/code) — ideal for designer/council slots where 1M ctx is unnecessary.

## Provider Gotchas (2026)

| Provider | Gotcha | Effect on preset design |
|---|---|---|
| **z.ai GLM-5.3/5.2** | 2–3× quota multiplier per prompt (peak/off-peak); 1× off-peak promo through Sept 2026 | Each z.ai Coding Pro prompt on GLM-5.x costs 2–3× quota. Use `glm-4.7` (1×) or Go/OR routing for routine fixer, reserve GLM-5.3 for reasoning-heavy roles (oracle/council). |
| **z.ai GLM-5.3-Flash** | **3× quota vs GLM-5.3; off-peak (incl. weekends) = 50% points** (Aug 26 plan update) | Best z.ai-plan value — use for high-volume fixer/orchestrator instead of GLM-5.3/5.2 when quota matters. |
| **z.ai Coding Pro** | 5-hr (~400 prompts Pro) + weekly (~2,000) caps; no PAYG fallback within plan | Hit cap = calls fail until window resets. No queue, no downgrade. |
| **Kimi K3** | Frequent 429 capacity errors; only `reasoning_effort=max` | Keep an `opencode-go/kimi-k3` fallback (bifrost circuit breaker: k3 → go/kimi-k3). 490/mo on Go — reserve for low-volume high-value slots. |
| **DeepSeek V4 Flash (0731)** | Jul 31 refresh replaced the old weights for **new** pricing; OpenRouter `deepseek/deepseek-v4-flash` (plain) still serves OLD weights (AA 42.1), refresh = `deepseek/deepseek-v4-flash-0731` (AA 51.8, Arena +3.99%) | Pin the `-0731` ID explicitly (or use Go/Zen "DeepSeek V4 Flash", which is the refresh). Plain OR ID silently downgrades quality. Peak/off-peak pricing: off-peak $0.22/$0.66, peak $0.44/$1.32. |
| **MiniMax Max** | 5-hr + weekly windows, but **passive timer drain bug** (GitHub #47) | Quota can exhaust without active API calls. Heavy fixer work can burn the 5-hr window in 50min–5hr. Use `opencode-go/*` for non-critical work to avoid drain. |
| **MiniMax Max** | All modalities (text/video/speech/music/image) share one quota pool | Video/speech usage eats LLM budget. |
| **OpenCode Go** | **Per-model dollar caps (Oct 2026)**: each model has a monthly limit ($15 / $30 / $60 / $80); its 5-h cap = 20% of that, weekly = 50%. Go $10/mo, Go Plus $40/mo doubles the caps. Free previews are unlimited (LongCat 2.5 Preview, Step 5 Preview, Cat Jam — limited time). | Budget preset design = spread seats across models so no single bucket is the bottleneck. High-volume read-only seats go on free previews; writers stay on the verified cheap workhorse (glm-5.3-flash, $60 cap, 6,320 req/5h). |
| **OpenCode Zen** | PAYG — Claude, GPT-5.x, DeepSeek | Use as overflow, not default. GLM-5.2 dropped to $1.40/$4.40; **GLM-5.3 & Qwen3.8 Max NOT on Zen**. |
| **OpenRouter** | PAYG — many models, but credits can exhaust | Check `testStatus` in OmniRoute before recommending. |
| **OmniRoute** | Unified gateway; provider `x-omniroute-provider` header in responses reveals actual routing | First `/`-segment in model ID is the **namespace** (e.g., `opencode-go/`, `zai/`, `minimax/`). Use this to verify the model actually hits the intended provider. |

## Go-Only Budget Preset (shipped Oct 15, 2026)

Live in `oh-my-opencode-slim.jsonc` as `presets.budget` (active) with
`council.presets.budget`; `opencode.jsonc` main model, title agent, and the
OptChat compactor all point at `opencode-go`. Full inventory + probe results:
[findings/2026-10-15-benchmark-snapshot.md](findings/2026-10-15-benchmark-snapshot.md);
Oct-16 refresh (beam-free, muse-1.2, luna, haiku, `opencode/*-free` wiring):
[findings/2026-10-16-go-refresh.md](findings/2026-10-16-go-refresh.md).

Live chains live in `oh-my-opencode-slim.jsonc` `presets.default` (the
Oct-15 `presets.budget` was folded back into `default` on Oct 18) — read them
there, never from a copy in this file. Seat rationale (the part the config
cannot confess):

| Seat | Why this head |
|---|---|
| orchestrator | cheapest strong writer per request (Muse $60 cap ≈226.6K req/mo, ~7× GLM-Flash; cache-read 15× cheaper); 1.2 second (separate $60 bucket = quota-spread) |
| oracle | verified DeepSWE 69 (GLM-5.3); K3 as quality escalation despite 429 history |
| librarian | free first (`opencode/` GLM-Flash = proven quality at $0; beam-free = Go-gated backup); paid Luna/deepseek behind |
| explorer | Muse for retrieval quality (verified live); free GLM-Flash/beam behind |
| designer | qwen3.8-max WebDev ELO 1685 (best open-tier design) |
| fixer | Muse 1.3 → 1.2 (quota-spread) → GLM-Flash; writers stay off free tiers (stop-not-overflow policy) |
| observer | GLM-5.3-Flash vision QA-passed |
| council (synth) | GLM-5.3 reasoning |
| fast-generic | free first (GLM-Flash, then beam); haiku (verified tool use) before paid GLM-Flash |
| councillors | 4 families (K3 / GLM-5.3 / qwen3.8-max / mimo-pro); alpha carries a GLM-5.3 fallback for K3's 429s |

**Late-Oct-15 tunings:** observer enabled; compaction + summary pinned to Muse
in `opencode.jsonc`; fast-generic → cat-jam-free; explorer → Muse; council
alpha fallback. **Free-tier finding:** `opencode/*-free` models (e.g.
`opencode/deepseek-v4.1-flash-free`, `opencode/muse-spark-1.3-contributor-free`)
are client-attested — raw curl gets `FreeTierError`, and they need a signed-in
**OpenCode Console** (`OpencodeConsole.SignedOut` observed 2026-10-15; free
attempts silently fail over via the retry hook). Reconnect the Console from the
TUI, then free models become wireable. **Audit result (tool/MCP surface):** the
~33K-token/turn main-session baseline is host-owned — preset `skills`/`mcps`
edits and disabling MCP servers changed it by 0 tokens (32,932 → 32,979 → 32,979).
No MCP trim needed; tools ride a deferred catalog. **Side finding:** local
plugins `jev-measure.ts`, `dcg-guard.ts`, `jev-screen.ts`, `rtk.ts`,
`model-announcer.ts` fail to load on the V2 host (`Schema.isStartsWith is not a
function`) — fix pending.

**Policy (2026-10-15, later same day):** the open-weight-only restriction and
the no-data-training restriction were **removed** by user call. Proprietary and
"used to improve our products" tiers are now allowed — Muse Spark 1.3
Contributor became the orchestrator + fixer primary, and the bifrost OpenRouter
allowlist was restored (24 → 39 models: Claude / GPT-6 / Gemini / Grok / Muse /
Mercury added). Decision-quality signals for Muse: 368M completed sessions on
OpenCode, #2 by tokens, 67% weekly retention, 95% cache ratio, $0.0010 avg
cost/session. Quota: same $60/mo cap as GLM-5.3-Flash but ~226.6K est
requests/mo vs ~31.6K (~7×), cache-read 15× cheaper ($0.002 vs $0.03). Go docs
state the trade explicitly ("permission to use your prompts and completions to
train future Meta models"; terms table: training Yes / Not ZDR).

**V2 host mechanic (learned 2026-10-15):** the MAIN session model comes from the
`opencode.jsonc` root `model`, **not** the preset's orchestrator entry. The
preset orchestrator entry feeds the agent registry + the fallback chain
(retry-hook steering on V2) and controls subagents. Switch the orchestrator by
setting **both**: root `model` (session) and the preset chain (fallback). Root
model retains no variant — the session runs Muse at its default effort.
Verified live: fresh session resolved to `opencode-go/muse-spark-1.3-contributor`.

**OpenRouter removed (later Oct 15, user call):** "if Go quota empties we stop"
— no PAYG overflow. OR deleted from all routing: every preset chain
(`default`, `privacy`, councillors, council agents) had its `openrouter/*`
entries stripped, and `bifrost/config.json` lost the whole `openrouter`
provider block plus OR entries in 8 governance failover chains (allowlist
restored earlier the same day went with it). Backups:
`oh-my-opencode-slim.jsonc.bak-20261015-drop-openrouter`,
`config.json.bak-20261015-drop-openrouter`. Left in place, flagged: the
`OPENROUTER_API_KEY` env in the `jev-mcp`/`jev-review` MCP servers (Jev judge
calls) and the `openrouter` credential in `auth.json` (last manual path —
remove on request). Go caps exhausted now = the session stops/errors.

**Preset-design rules for Go-only mode**

1. Free tiers go on **high-volume read-only/mechanical seats only**
   (explorer, librarian, fast-generic) — never on writers. A retirement then
   degrades to the chain instead of breaking a writer seat. Two namespaces
   exist: `opencode-go/*-free` (Go quota) and `opencode/*-free`
   (Console-attested, needs signed-in Console; lapses fail over silently).
   Probe a free name under **both** namespaces before declaring it dead, and
   mix namespaces inside a chain so either gate dropping still leaves a path.
   Check liveness every refresh with `./scripts/probe-heads.sh` — `doctor`
   passes with dead models still in chains (Oct-16 lesson: two lanes
   dispatched onto retired previews).
2. Variant strings must exist in the model's models.dev `reasoning_options`
   values (glm-5.3-flash: low/high/max; kimi-k3: max; qwen3.8-*: low/medium/
   xhigh; space-bunny: low…max; mimo-v2.6-*: none). Unknown variant =
   model-resolution error. **A bare-string model entry inherits the seat-level
   variant** (Oct 19: `mimo-v2.6-flash` as a bare string inherited `high` and
   died; models with `reasoning_options: []` need an explicit
   `{id, variant: "default"}` — `"none"` is rejected too). The seat-level
   `variant` is also what the head actually runs at (Oct 19: seat `low` beat
   the head's per-entry `high` on a live delegation), so keep the seat
   variant and the chain[0] per-entry variant equal.
3. Chains: per-entry `{id, variant}` objects; the agent-level `variant` is only
   the chain[0] default. **Councillor seats** take the seat-level `variant`
   (per-entry object variants are ignored there).
4. `council.default_preset` is global — flip it with `preset` when switching
   between normal and budget modes.
5. Presets may override custom agents (e.g. `fast-generic`); effective map is
   `deepMerge(config.agents, resolvedPreset.agents)`.
6. Validate with `bunx oh-my-opencode-slim doctor --json` (config + preset
   resolution) **plus `./scripts/probe-heads.sh <preset>`** (every chain head
   serving live — doctor cannot see server-side retirements) plus a live
   delegation run; `opencode api get
   /api/session/<id>/message` shows each agent's *applied* provider/model/variant.
   For one-off checks: `./scripts/probe-model.sh <provider/model[#variant]>`.
7. **Probe every chain entry, not just the heads** (Oct 19). Head-only probing
   hid eight broken entries: a retired model sitting mid-chain
   (`space-bunny` on Go), two invalid variants (`kimi-k3#high`, `qwen3.8-max#high`
   — the latter broke the whole designer seat), and four bare-string entries
   inheriting an unusable seat variant. A head-only probe also reports "UP"
   for a chain whose tail is dead. Probe each entry with
   `probe-model.sh <id[#variant]>`; the seat name + entry list comes from
   `probe-heads.py` with a per-entry loop.
8. models.dev **lags the server**: on Oct 19 it still listed
   `opencode-go/space-bunny` after Go retired it ("Model unavailable"), and
   `cat-jam-free` / `step-5-preview-free` lingered weeks after their
   retirements. A models.dev entry is a candidate, not a liveness proof.
9. `opencode/*-free` (Console-attested) ids are **intermittent**, not dead:
   on Oct 19 the same id served one probe and failed over on the next, and the
   failover steered a *paid* model into a free-tier seat. `opencode-go/*-free`
   (Go-gated) ids did not fail once all session. Prefer a Go-gated free head
   on read-only seats and keep the Console-gated one behind it.

## Workflow

### Step 1: Gather Current State
```bash
cat ~/.config/opencode/oh-my-opencode-slim.jsonc
cat ~/.config/opencode/opencode.jsonc
chezmoi diff ~/.config/opencode/oh-my-opencode-slim.jsonc ~/.config/opencode/opencode.jsonc
```
The `chezmoi diff` line is not optional. The destination file is what the host
reads; the source is what survives a `chezmoi apply`. Drift between them — a
hand-edited MCP `enabled` vs `disabled` flag — is invisible in the files
themselves and only shows up in the diff.

### Step 2: Fetch Latest Pricing + Benchmarks

**Automated (agent-browser):** `./scripts/fetch-pricing.sh [--deepswe | --go | --zen | --swe | --arena | --openrouter | --all]`
Prerequisite: `npm i -g agent-browser && agent-browser install`. See REFERENCE.md for manual scraping steps.

**Go catalog (no browser):** `./scripts/go-catalog.py [--json | --table | --ids]`
parses `https://opencode.ai/docs/go/` into the live model list, prices, monthly
caps, request counts, privacy rows and free-model notes. The tables are in the
raw HTML — no JS, no browser. Use it instead of hand-parsing the page; use
`--ids` to diff the live catalog against models.dev.

**Live via OpenRouter MCP** (no browser):
- `openrouter_models-list` — catalog with pricing, context, AA benchmarks
- `openrouter_model-endpoints author="z-ai" slug="glm-5.2"` — per-provider pricing/latency
- `openrouter_benchmarks source="artificial-analysis"` — AA indices
- `openrouter_benchmarks source="design-arena"` — UI/UX ELO scores
- `openrouter_rankings-daily` — model popularity

**Task-specific live eval (spawn-ori-eval):** when static benchmarks disagree, or the deciding metric is the user's own workload, run the `spawn-ori-eval` skill instead of guessing. It spawns Ori as a subprocess to write and grade a throwaway eval on a pinned harness and judge model (`openai/gpt-5.6-terra`), so the bench is identical for every candidate and the score change comes only from the user's agent. Costs real OpenRouter credits (~$4–15/run, its appendix F) — use it to settle close calls between runner-up candidates, not for routine tier audits.

**Live via curl (no browser, no MCP — fallback when agents/MCP are down):**
- OpenRouter catalog (prices + AA indices + ctx): `curl https://openrouter.ai/api/v1/models` (public, no key)
- DeepSWE raw trials (pass/fail per task×model run): `https://deepswe.datacurve.ai/artifacts/v1/trials.json` — aggregate pass@1 per model yourself; v1.1-era set only (no k3/glm-5.3/qwen3.8-max yet) — see findings/2026-08-24-benchmark-snapshot.md for an example aggregation
- Arena Agent: `curl -sL https://arena.ai/leaderboard/agent/` → parse the escaped `\"rows\":[...]` JSON in the RSC payload (snapshot date in `lastUpdated`)
- OpenCode Go/Zen: `./scripts/go-catalog.py` (parses the live Go page — model
  list, prices, monthly/5-h/weekly caps, privacy, free-model notes). Raw
  `curl https://opencode.ai/docs/go/` also works: the tables are in the HTML
  (the old `go.md`/`zen.md` markdown routes were removed — 404 since Oct 15,
  2026).
- Design Arena: client-rendered; use `agent-browser eval` after load
- DeepSWE/Arena pages are JS shells — curl alone gets nothing; agent-browser or the artifacts endpoint is required

**Provider-specific scraping (librarian + firecrawl):** for subscription plan limits (5-hr caps, weekly caps, multipliers), dispatch a librarian to scrape the provider's docs and pricing pages. Provider docs often hide the real limits behind JavaScript.

### Step 3: Test Endpoint Health
Before recommending models, verify they are actually serving inference.
Climb the ladder, cheapest first — only step 3 costs quota.

**1. Lint the config (FREE):** `./scripts/lint-preset.py [--preset default]`
Cross-checks every chain entry against models.dev: variant validity, model
existence, bare-string entries that inherit a seat variant, seat-vs-chain[0]
variant mismatch. Catches the classes `doctor` cannot see (Oct 19: `doctor`
said `ok: true` while the designer seat was dead on an invalid variant).

**2. Diff against the live catalog (FREE):** `./scripts/go-catalog.py --ids`
An id missing from the live Go catalog is retired server-side even when
models.dev still lists it (models.dev lagged on `space-bunny` for weeks).
`./scripts/go-catalog.py --diff-models-dev` prints the two-way diff —
on Oct 19 it named `cat-jam-free`, `minimax-m2.7`, `space-bunny` and
`step-5-preview-free` as models.dev-only. `probe-all-entries.sh` skips
entries the live catalog dropped (reported RETIRED, no quota spent) unless
you pass `--probe-retired`.

**3. Probe what survives (PAID):** in-stack probes resolve variants and
report the *applied* model + cost via the message API — raw curl cannot see
failover.

```bash
# Every chain entry, live (not just the heads — a dead mid-chain fallback
# is invisible to a head-only probe)
./scripts/probe-all-entries.sh default

# Only the seats a refresh touched (a full run burns ~$0.40 of paid quota;
# filtered runs are the daily habit, full runs are for structural edits)
./scripts/probe-all-entries.sh default librarian fast-generic

# One model, e.g. a free name under both namespaces before declaring it dead
./scripts/probe-model.sh opencode/glm-5.3-flash-free#low
./scripts/probe-model.sh opencode-go/glm-5.3-flash-free#low
```

Raw-HTTP fallback (`test-endpoints.sh`) when the stack itself is down:

```bash
# Quick ping (checks endpoint exists)
./scripts/test-endpoints.sh --ping-only

# Full live inference test (needs API key)
./scripts/test-endpoints.sh $OPENCODE_GO_API_KEY
```

**Auth differences:**
- OpenAI-compatible models (`/chat/completions`): `Authorization: Bearer <key>`
- Anthropic-compatible models (`/messages`): `x-api-key: <key>`

**Expected results (Oct 15, 2026):** 24/24 up on the raw-HTTP subset (22
OpenAI-protocol + 2 Anthropic-protocol), 7 closed-protocol models skipped
(grok/gpt/gemini/muse — raw curl gets `ModelProtocolUnsupported`; they DO work
through opencode, verified with `opencode run`). Raw curl requires a non-SDK
`User-Agent` (Cloudflare 403/1010 otherwise) and `x-opencode-session`.

**Via OmniRoute:** inspect `x-omniroute-provider` and `x-omniroute-response-cost` headers to confirm routing + cost.

### Step 4: Cross-Reference Per Agent
1. **List candidates** on each provider namespace (opencode-go, opencode-zen, openrouter, zai, minimax)
2. **Filter by capability**: vision, speed, reasoning
3. **Check benchmarks**: DeepSWE for coding, AA indices for reasoning
4. **Compare pricing**: Go (free within limits) vs Zen PAYG vs OpenRouter PAYG vs subscription flat-fee — see REFERENCE.md for rules
5. **Check context window**: ≥128K for Orchestrator, Fixer
6. **Check provider health** via OmniRoute dashboard before recommending
7. **Tie-break with a live eval**: when two candidates are close on DeepSWE/AA and the seat is high-stakes (Oracle, Council, Fixer), run the `spawn-ori-eval` skill on the user's real workload instead of resolving by price alone

### Step 5: Build the Preset
```jsonc
"my-best-value": {
  "orchestrator": { "model": "opencode-go/<model>", "skills": ["*"], "mcps": ["*"] },
  "oracle": { "model": "opencode-go/<model>", "variant": "max", "skills": ["..."], "mcps": [] },
  "librarian": { "model": "opencode-go/<model>", "variant": "low", "skills": ["..."], "mcps": ["..."] },
  "explorer": { "model": "opencode-go/<model>", "variant": "low", "skills": [], "mcps": [] },
  "designer": { "model": "opencode-go/<model>", "variant": "medium", "skills": ["..."], "mcps": [] },
  "fixer": { "model": "opencode-go/<model>", "variant": "high|low", "skills": ["..."], "mcps": [] },
  "observer": { "model": "opencode-go/<model>", "skills": ["docling"] },
  "council": { "model": "opencode-go/<model>", "variant": "max" }
}
```

### Step 6: Validate
Switch the active preset and run a real coding task end-to-end. Confirm:
- All agents respond (no 404 from OmniRoute)
- `x-omniroute-provider` header matches the intended provider
- No cap errors in 30+ minutes of active use
- Cost per task matches the projected budget

**Session record shape** (the ground truth every probe reads; the parts live in
`content`, NOT `parts`):

```
opencode api get /api/session/<id>/message
  -> { data: [ { type:"assistant",
                  model: { id, providerID, variant },   # the APPLIED model
                  cost, tokens,
                  content: [ {type:"text", text},
                             {type:"tool", tool, input, state:{status,output}},
                             {type:"reasoning", text} ] } ] }
```
`./scripts/session-report.py` prints that record as served-model + tool calls +
text; feed it the endpoint output on stdin. A tool call is
`content[] where type=="tool"`, and its result is `state.output`.

## See Also

Scripts — one line each, with the branch that reaches for it:

- [scripts/lint-preset.py](scripts/lint-preset.py) — FREE config lint: variant validity, model existence, bare-string entries, seat/chain variant mismatch. Use after every preset edit, before any probe.
- [scripts/go-catalog.py](scripts/go-catalog.py) — live Go catalog (models, prices, caps, request counts, privacy, free-model notes) parsed from the docs HTML. Use to price a model or to diff the live catalog against models.dev.
- [scripts/probe-all-entries.sh](scripts/probe-all-entries.sh) — PAID: probes every chain entry in a preset, not only the heads. Use when a seat misbehaves or after a structural edit.
- [scripts/probe-model.sh](scripts/probe-model.sh) — PAID: one model id, live, with the applied model + cost. Use to settle one candidate.
- [scripts/probe-heads.sh](scripts/probe-heads.sh) — PAID: chain heads only. Use for a cheap smoke check; it cannot see a dead mid-chain fallback.
- [scripts/smoke-model.sh](scripts/smoke-model.sh) — PAID: tool-call + vision QA for one model. Use before putting a model on the observer seat, or on a seat that runs shell commands.
- [scripts/session-report.py](scripts/session-report.py) — prints a session record (applied model, tool calls, text) from the message API. Use to read what a probe or a delegation actually served.
- [scripts/fetch-pricing.sh](scripts/fetch-pricing.sh) — automated data fetcher (agent-browser + OpenRouter API) for the benchmark leaderboards.
- [scripts/test-endpoints.sh](scripts/test-endpoints.sh) — raw-HTTP endpoint health checker, used when the opencode stack itself is down.
- [REFERENCE.md](REFERENCE.md) — benchmark archives, methodology, data-quality notes, manual scraping guide. Prices live in the live catalog, not in here.
- [spawn-ori-eval](https://openrouter.ai/skills/spawn-ori-eval) — throwaway model eval on a pinned harness (Ori subprocess); live task-specific tie-break for preset choices. Install: `skills add https://openrouter.ai/skills/spawn-ori-eval -s spawn-ori-eval --agent opencode -g`
- [scripts/fetch-pricing.sh](scripts/fetch-pricing.sh) — automated data fetcher (agent-browser + OpenRouter API) for the benchmark leaderboards.
- [scripts/test-endpoints.sh](scripts/test-endpoints.sh) — raw-HTTP endpoint health checker, used when the opencode stack itself is down.
- **OpenRouter MCP:** `openrouter_models-list`, `openrouter_benchmarks`, `openrouter_rankings-daily`, `openrouter_model-endpoints`
- **OmniRoute MCP:** `omniroute_list_models_catalog`, `omnirroute_simulate_route`, `omnirroute_explain_route`, `omnirroute_check_quota`, `omnirroute_cost_report` — for subscription plan limits and routing verification
