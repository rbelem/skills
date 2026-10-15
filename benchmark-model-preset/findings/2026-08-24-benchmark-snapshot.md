# Benchmark & Pricing Snapshot — Aug 24, 2026

Sources: OpenRouter catalog API (live), DeepSWE raw trials artifact (v1.1), arena.ai Agent leaderboard RSC payload (Aug 19 snapshot), opencode.ai/docs/go + /docs/zen (current), designarena.ai scrape (live), z.ai GLM-5.3 launch data via atoms.dev guide, bifrost gateway config.

## New / changed frontier open models

| Model | Released | Independently verified (AA / Arena / Design) | Vendor claims | Price (I/O) | Access |
|---|---|---|---|---|---|
| **GLM-5.3** | Aug 14 | AA 59.5/74.8/**59.1***; Design 1347 (#5); Arena N/A (not yet run) | DeepSWE 66.9, TB3 28.3, Toolathlon 73.0, AutoBench 48.2 | $1.40/$4.40 | Go (usage $15), z.ai plan, OR |
| **Kimi K3** | Jul 16 | AA 59.7/76.2/54.3; Arena **+10.41% (#4)**; Design **1407 (#1)**, fullstack **1361 (#1)** | DeepSWE 67.5† | $3/$15 | Go (usage $15, 490/mo), Zen, kimi-for-coding (k3, k3-256k), OR |
| **Qwen3.8 Max** | ~Jul 19→prod | AA 58.1/71.8/58.4; Arena **+6.20% (#15)**; Design 1321 (#11), fullstack 1331 (#3), backend 7.0 (#3=t) | — | $2/$6 | Go (usage $15, 810/mo), alibaba-token-plan, OR, NOT Zen |
| **DeepSeek V4 Flash (0731)** | Jul 31 | AA 51.8/69.1/48.4; Arena **+3.99% (#20)** (recovered from −4.64%) | — | $0.07/$0.13 OR (DeepInfra); $0.22/$0.66 off-peak, $0.44/$1.32 peak (Go/Zen) | OR (pinned ID), Go (unnamed), Zen, deepseek API |
| **DeepSeek V4 Pro (0813)** | Aug 13 | AA 53.2/68.8/49.6; Arena **+6.26% (#14)** (was +0.05%) | DeepSWE 62.7† | $1.12/$3.37 | OR, Go usage $15, Zen (off-peak $0.66/$1.98) |
| **Ox Alpha** (stealth) | ~Aug | none yet | — | Free | Go (limited time), OR `stealth/ox-alpha`, 1M ctx, text+img+video in |
| **Hy3** | Jul 6 | AA 42.2/58.8/31.4 (hy3-preview); Arena −2.38% | (unchanged, unverified) | $0.14/$0.58 | **Now on Go too** (usage $60 → ~21.5K/mo), OR $0.13/$0.53 |

\* AA Agentic 59.1 = highest of ANY model incl. GPT-5.6 Sol (57.8). † vendor-reported, not on official DeepSWE leaderboard (trials artifact has no glm-5.3/k3/qwen3.8-max runs).

## DeepSWE v1.1 — exact figures from raw trials artifact (n=13,918 deep-swe trials, all efforts)

gpt-5.5 60.9% ($4.63) · gpt-5.4 54.6% · claude-opus-4.8 53.5% · opus-4.7 43.0% · **glm-5.2 [max] 42% ($3.95)** · sonnet-4.6 29.8% · gemini-3.5-flash 28.3% · kimi-k2.6 23.9% · gpt-5.4-mini 23.1% · minimax-m3 20.4% · mimo-v2.5-pro 19.5% · qwen3.7-max 17.7% · glm-5.1 17.5% · deepseek-v4-pro 7.5%.

No new models (k3, glm-5.3, qwen3.8-max, flash-0731) on DeepSWE as of Aug 24.

## Arena Agent (Aug 19, 2026 — 1.91M sessions, 51 models)

Open/Go-relevant: **Kimi K3 +10.41 (#4)** · DS V4 Pro 0813 +6.26 (#14) · **Qwen3.8 Max +6.20 (#15)** · Grok 4.5 +6.17 (#16) · GLM 5.2 +5.82 (#17) · **DS V4 Flash 0731 +3.99 (#20)** · Gemini 3.7 Flash +3.32 (#21) · Muse 1.2 +2.06 (#25) · K2.7 Code +0.43 · GLM 5.1 −0.00 · Qwen3.7 Max −0.75 · Mimo V2.5 Pro −2.25 · Hy3 −2.38 · Minimax M3 −3.15 · Gemini 3.5 Flash −0.68 · K2.6 −1.10 · Minimax M2.7 −11.86. Top: Opus 5 (High) +12.47, Opus 5 (Max) +12.00, Fable 5 (High) +11.57, GPT-5.6 Sol xHigh +9.74.

## Design Arena (live)

Overall: **Kimi K3 1407 #1** · GPT-5.6 Sol xHigh 1367 · Sol medium 1351 · Opus 5 1349 · **GLM-5.3 1347** · Muse 1.2 1343 · Fable 5 1339 · Gemini 3.7 Flash 1332 · GLM 5.2 1331 · Grok 4.6 1326 · **Qwen3.8 Max 1321**.
Fullstack: **K3 1361 #1** · Opus 5 1347 · **Qwen3.8 Max 1331** · Fable 5 1287 · Sol xHigh 1284 · Grok 4.6 1283 · Sonnet 5 1271 · GLM 5.2 1261.
Backend rubric avg: Grok 4.6 7.6 · Qwen3.8 Max 7.0 · **K3 6.3** · GLM 5.2 4.7 (weak backend).

## OpenCode Go (current — DOLLAR-based limits)

$10/mo; 5h $12 · week $30 · month $60 usage (≈6× multiplier). Per-model usage: GLM-5.3 $15 (~1,080/mo) · Kimi K3 $15 (~490/mo) · Qwen3.8 Max $15 (~810/mo) · GPT 5.6 Luna $15 (~10,250/mo) · DS V4 Pro $15 · DS V4 Flash $30 (~37,800/mo) · DS V4 Flash Vision Exp $15 · GLM-5.2 $60 (4,300/mo) · GLM-5.1 $60 · Hy3 $60 (~21,500/mo) · MiMo-V2.5 $60 · MiMo-V2.5-Pro $15 · MiniMax M3 $60 · MiniMax M2.7 $60 · K2.7-code $60 · K2.6 $60 · LongCat-2.0 $60 (~57,200/mo) · Muse Spark 1.2 Contributor $60 (~226,600/mo) · Qwen3.7 Max $60 · Qwen3.7 Plus $60 · Qwen3.6 Plus $60 · Ox Alpha Free.
Pricing highlights: GLM-5.x $1.40/$4.40 (GLM-5.2 HALVED) · Qwen3.8 Max $2/$6 · K3 $3/$15 · flash off-peak $0.22/$0.66, peak $0.44/$1.32 · Luna $0.20/$1.20.

## OpenCode Zen (current highlights)

New: Claude Opus 5 $5/$25 · Gemini 3.7 Flash $1.50/$7.50 · Grok 4.6 $2/$6 · Kimi K3 $3/$15. Changed: GLM 5.2 $1.40/$4.40 (was $2.80/$8.80) · GPT-5.6 Sol $2/$10 · Luna $0.20/$1.20 · DS V4 Flash off-peak $0.22/$0.66. NOT on Zen: GLM-5.3, Qwen3.8 Max, Hy3. Still: Fable 5 $10/$50, Opus 4.8 $5/$25, Sonnet 5 $2/$10, MiniMax M3 $0.30/$1.20, Gemini 3.5 Flash $1.50/$9.

## OpenRouter prices (live, DeepInfra-cheapest where noted)

GLM-5.3 $1.40/$4.40 · GLM-5.2 $0.97/$3.04 (dropped) · Kimi K3 $3/$15 · Qwen3.8 Max $2/$6 · qwen3.8-27b $0.40/$3 (AA 52/68.1/50.9) · flash-0731 $0.07/$0.13 · flash (plain) $0.06/$0.11 **OLD weights (AA 42.1)** · flash-vision-exp $0.22/$0.66 · pro-0813 $1.12/$3.37 · pro (plain) $0.52/$1.04 · mimo-v2.5 $0.14/$0.28 · mimo-v2.5-pro $0.43/$0.87 · minimax-m3 $0.30/$1.20 · K2.7-code $0.67/$3.40 · Luna $0.20/$1.20 (AA 52.3/71.4/46.9, ctx 1.05M) · Sol $2/$10 (AA 60.9/77.4/57.8) · Terra $2/$12 · Fable 5 $10/$50 (62.1/76.5/56.6) · Sonnet 5 $2/$10 (55.3/71.5/49.7) · Grok 4.5 $2/$6 (55.8/72.4/48.9) · kat-coder-air-v2.5 $0.15/$0.60 · kat-coder-pro-v2.5 $0.74/$2.96 · laguna-s-2.1 $0.09/$0.18 · laguna-xs-2.1 $0.06/$0.12 · inkling $1/$4.05 (AA 42.3/52.1/34.1, Arena −7.19 — skip) · Hy3 $0.13/$0.53 · hy3-preview AA 42.2/58.8/31.4.

## GLM-5.3 details (launch Aug 14, z.ai)

- Same 744B/40B MoE base as 5.2; post-training: longer agent trajectories, richer envs, verification.
- **Thinking required** — no think-off; reasoning_effort: low | high | max (default max).
- Vendor table: DeepSWE 66.9 (5.2→46.2), TB3 28.3 (4.6), Toolathlon Verified 73.0, AutomationBench 48.2, CyberGym 84.5, NL2Repo 58.0, HLE w/ tools 62.5, Agents' Last Exam 28.5.
- Open weights announced ~2 weeks post-launch (≈Aug 28) — pending safety eval.
- z.ai Coding Plan quota multiplier unchanged (2–3×/prompt; off-peak promo ended? not re-verified).

## Local routing (bifrost config, Aug 14 version)

zai: glm-5.3/5.2/4.7 · moonshotai: kimi-k3, k2.7-code(+highspeed) · kimi-for-coding: k3, k3-256k, kimi-for-coding(-highspeed) · minimax: MiniMax-M3 · openrouter: flash/flash-0731/flash-vision/pro-0813, kimi-k3, glm-5.2, mimo-v2.5(-pro), minimax-m3, ox-alpha · opencode-go: `*` · alibaba-token-plan: qwen3.8-max + others · deepseek: flash(±vision), pro.
Circuit breakers: glm-5.3→alibaba glm-5.2, k3→go kimi-k3, M3→go minimax-m3, flash→deepseek flash.

## Open items / flags

- MiniMax #47 (passive timer drain) status unverified — assume still open (was open Jul 18).
- k3 429 capacity risk still active per prior notes; bifrost fallback covers it.
- GLM-5.3 / k3 / qwen3.8-max DeepSWE runs are vendor-reported only (glm-5.3: 66.9 self; k3: 67.5 self; qwen3.8-max: not published).
- DeepSeek plain-vs-refresh weight ambiguity: OR `deepseek/deepseek-v4-flash` = OLD (AA 42.1); `-0731` = new (51.8). Go/Zen flash pricing implies 0731 weights. DeepSeek direct API: verify once.
## Vision QA addendum (Aug 25 — live test: flash-vision-exp vs MiniMax M3)

Controlled PNG: 4 text lines (incl. unique code `DEEPSWE-VISION-QA-42`), red circle + blue square + green line. Same prompt both models, via direct APIs (api.deepseek.com / api.minimax.io/v1).

| Criterion | flash-vision-exp | MiniMax M3 |
|---|---|---|
| Exact code read (A1) | **FAIL** — "DEEPSWE-VISION-OA-42" (Q→O) | PASS |
| Value read (A2) | PASS (67.5) | PASS |
| Shape count/colors (A3) | PASS (3; red/blue/green — no types) | PASS (circle/square/line, detailed) |
| glm-5.3 mention (A4) | PASS (66.9) | PASS (even flagged l→I glyph) |
| Transcript | 3/4 exact (line-1 error) | 3/4 exact (l→I, missing space) |
| Reliability | **1st call returned EMPTY content** (retry ok); 816 reasoning tokens on trivial image | clean single call |

**Verdict: keep MiniMax-M3 as observer** (both presets). flash-vision-exp fails the exact-identifier read — the core observer job — and had an empty-response flake. It remains a cheap casual-vision fallback (summaries, non-exact reads) at $0.22/$0.66 and higher Go quota, but no preset swap. Addendum supersedes the earlier "value-observer candidate" suggestion.

## Vision QA round 2 (Aug 25 — Kimi K3 added)

Same controlled PNG + prompt. Route notes: moonshot.ai key = **suspended (insufficient balance)**; OpenRouter balance ≈ **0 credits (402)**; opencode-go kimi-k3 = **Cloudflare 1010 (blocked for direct client, needs Go auth cookie/workspace)** — K3 tested via **kimi-for-coding `k3-256k`** (api.kimi.com/coding/v1), which is also the preset designer route.

| Criterion | flash-vision-exp | MiniMax M3 | **kimi-k3 (k3-256k)** |
|---|---|---|---|
| Exact code read (A1) | ❌ OA-42 | ✅ | ✅ |
| A2 / A4 | ✅ | ✅ | ✅ |
| Shapes (A3) | ✅ basic | ✅ detailed (circle/square/line) | ✅ **most detailed** (filled circle, outlined square, diagonal line) |
| Transcript | 3/4 (line-1 error) | 3/4 (gIm-5.3, AAagentic) | 3/4 (AAgentic) |
| Reliability | ❌ 1 empty-content flake | ✅ clean | ✅ clean (751 reasoning tokens) |

**Verdict:** MiniMax M3 and Kimi K3 tie on the critical reads (A1 exact both); K3 edges shape detail, M3 edges transcript. flash-vision-exp loses on A1 + flakiness — **not an observer candidate**. Observer stays M3 (both presets); k3-256k is a valid quality-observer *alternative* if M3 quota drains — kimi-for-coding console showed **only 5% used (Aug 25)**, so shared-quota pressure is a non-issue at current volumes; K3 upgrades to top fixer candidate too (AA coding 76.2 > glm-5.3 74.8, no zai 2-3x multiplier). Other key findings: OpenRouter credits empty, moonshot.ai suspended — check before any OR/moonshot routing.
