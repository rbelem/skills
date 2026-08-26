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
| **OpenCode Go** | **Dollar-based usage now**: $12/5h, $30/wk, $60/mo with per-model usage caps ($15 new frontier / $60 legacy) | Request counts vary by model. Cap-conscious model: LongCat-2.0 ($0.30/$1.20, ~57K/mo) and Muse Spark 1.2 Contributor ($0.10/$0.20, ~226K/mo) for high-volume lanes. |
| **OpenCode Zen** | PAYG — Claude, GPT-5.x, DeepSeek | Use as overflow, not default. GLM-5.2 dropped to $1.40/$4.40; **GLM-5.3 & Qwen3.8 Max NOT on Zen**. |
| **OpenRouter** | PAYG — many models, but credits can exhaust | Check `testStatus` in OmniRoute before recommending. |
| **OmniRoute** | Unified gateway; provider `x-omniroute-provider` header in responses reveals actual routing | First `/`-segment in model ID is the **namespace** (e.g., `opencode-go/`, `zai/`, `minimax/`). Use this to verify the model actually hits the intended provider. |

## Workflow

### Step 1: Gather Current State
```bash
cat ~/.config/opencode/oh-my-opencode-slim.json
cat ~/.config/opencode/opencode.json
```

### Step 2: Fetch Latest Pricing + Benchmarks

**Automated (agent-browser):** `./scripts/fetch-pricing.sh [--deepswe | --go | --zen | --swe | --arena | --openrouter | --all]`
Prerequisite: `npm i -g agent-browser && agent-browser install`. See REFERENCE.md for manual scraping steps.

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
- OpenCode Go/Zen: `curl https://opencode.ai/docs/go.md` (and `zen.md`) — plain markdown
- Design Arena: client-rendered; use `agent-browser eval` after load
- DeepSWE/Arena pages are JS shells — curl alone gets nothing; agent-browser or the artifacts endpoint is required

**Provider-specific scraping (librarian + firecrawl):** for subscription plan limits (5-hr caps, weekly caps, multipliers), dispatch a librarian to scrape the provider's docs and pricing pages. Provider docs often hide the real limits behind JavaScript.

### Step 3: Test Endpoint Health
Before recommending models, verify they are actually serving inference:

```bash
# Quick ping (checks endpoint exists)
./scripts/test-endpoints.sh --ping-only

# Full live inference test (needs API key)
./scripts/test-endpoints.sh $OPENCODE_GO_API_KEY
```

**Auth differences:**
- OpenAI-compatible models (`/chat/completions`): `Authorization: Bearer <key>`
- Anthropic-compatible models (`/messages`): `x-api-key: <key>`

**Expected results:** 13/14 models up. `qwen3.7-max` observed "temporarily unavailable" intermittently.

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

## See Also

- [REFERENCE.md](REFERENCE.md) — data sources, pricing tables, pool strategy, cost heuristics, data quality notes, manual scraping guide
- [spawn-ori-eval](https://openrouter.ai/skills/spawn-ori-eval) — throwaway model eval on a pinned harness (Ori subprocess); live task-specific tie-break for preset choices. Install: `skills add https://openrouter.ai/skills/spawn-ori-eval -s spawn-ori-eval --agent opencode -g`
- [scripts/fetch-pricing.sh](scripts/fetch-pricing.sh) — automated data fetcher (agent-browser + OpenRouter API)
- [scripts/test-endpoints.sh](scripts/test-endpoints.sh) — live endpoint health checker for all OpenCode Go models
- **OpenRouter MCP:** `openrouter_models-list`, `openrouter_benchmarks`, `openrouter_rankings-daily`, `openrouter_model-endpoints`
- **OmniRoute MCP:** `omniroute_list_models_catalog`, `omnirroute_simulate_route`, `omnirroute_explain_route`, `omnirroute_check_quota`, `omnirroute_cost_report` — for subscription plan limits and routing verification
