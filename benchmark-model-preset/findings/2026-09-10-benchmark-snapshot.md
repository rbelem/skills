# Benchmark & Pricing Snapshot — Sep 10, 2026

Sources: artificialanalysis.ai (live, AA Intelligence Index v4.3), arena.ai Code/Website leaderboard (live, Sep 8), datacurve.ai DeepSWE leaderboard, OpenCode Go/Zen docs (live), bifrost provider probes (Sep 10), OpenRouter account telemetry, librarian research (Aug 26 → Sep 10 releases).

## New releases Aug 26 → Sep 10, 2026

| Model | Released | Verified | Vendor claims | Access |
|---|---|---|---|---|
| **Claude Fable 5.1** | **Sep 1** | **#1 AA (53.4)**, **#1 Arena Agent +14.51%** | — | Zen (closed, unrouted) |
| Gemini 3.8 Flash | Sep 2 | — | — | Zen (closed, unrouted) |
| Muse Spark 1.3 | Sep 2 | Leads DeepSWE in some sources | — | Go (Contributor $60), Zen — Meta-proprietary (not open-weight) |
| **GPT-6 Astra / Pro** | **Sep 3** | **AA 52.8** | — | Zen (closed, unrouted) |
| **Qwen3.8 Max 0902** | **Sep 3** | WebDev ELO **1685** | Post-trained API snapshot | alibaba-token-plan, Go, OR |
| **K2 Horizon 375B-A23B** | **Sep 3** | **AA 47 — highest open-weight** | — | MBZUAI, Apache 2.0 — **NOT on Go/Zen/OR** |
| Hy4 preview | Aug 28 | Not on AA | DeepSWE 64.3 (self) | Apache 2.0; Go ($30), Zen |
| **DeepSeek V4.1 Flash** | **Sep 10** | n/a | DeepSWE 74.2 (self, provisional) | MIT; API id `deepseek-flash`; Go ($15), direct |

DeepSeek V4.1 Flash retirements **same day (Sep 10)**: V4 Flash and V4 Flash Vision Exp retired; legacy IDs reroute. **V4 Pro retired Sep 14.**

Not in this window (avoid assuming): **no GLM-5.4/5.5** (projected Oct–Nov), **no Kimi K4**, **no MiniMax M3 Pro**.

## Open-weight master table (Sep 10, 2026)

Key discriminators this cycle. WebDev ELO = arena.ai Code/Website (text-to-HTML, Sep 8); Arena Agent net% = arena.ai agent leaderboard.

| Model | License | AA Intel | DeepSWE | WebDev ELO | Arena Agent net% | Ctx | Inputs | Price (I/O per M) |
|---|---|---|---|---|---|---|---|---|
| **GLM-5.3** | MIT (weights "forthcoming") | **45** | **69%** | 1613 | 2.56% | 1.31M | text | $1.40/$4.40 |
| **GLM-5.3-Flash** | MIT | 42 | 63% | 1605 | 2.00% | 1.31M | text+img+video | $0.15/$0.50 |
| Qwen3.8-Max-0902 | Proprietary API | 40 | 57% | **1685** | 3.90% | 1M | text+img+video | $2.00/$6.00 |
| Qwen3.8-Flash | Hosted | 40 | — | 1631 | 0.81% | 1M/256k | text+img+video | $0.15/$0.47 |
| **Kimi K3** | Non-OSI Kimi license | 44 | 69% | 1674 | **6.59%** | 1M | text+img+video | $3.00/$15.00 |
| **DeepSeek V4.1-Flash** | MIT | n/a | *74.2 self* | n/a | n/a | 1M | text+img | $0.15/$0.60 off-peak |
| DeepSeek V4-Flash-0731 | MIT | 35 | 53% | 1582 | 2.22% | 1.31M | text | $0.065/$0.18 OR |
| DeepSeek V4-Pro-0813 | MIT | 36 | 63% | 1580 | 4.43% | 1M | text | $0.58/$1.74 |
| Hy4 preview | Apache 2.0 | Not on AA | 64.3 (self) | 1623 | 5.37% | 1M | text | $0.83/$2.50 |
| MiniMax M3 | MiniMax Community | 30 | — | 1486 | 5.26% | 1M | text+img+video | $0.30/$1.20 |
| MiMo-V2.5 | MIT | 22 | — | 1437 | — | 1.05M | text+img+audio+video | $0.14/$0.28 |
| MiMo-V2.5-Pro | MIT | 26 | — | 1475 | 5.08% | 1.05M | text | $0.435/$0.87 |
| LongCat-2.0 | — | 20 | — | — | — | — | — | — |

**Unrouted (open-weight, no provider):** **K2 Horizon 375B-A23B** — MBZUAI, Apache 2.0, AA 47 (highest open-weight AA measured), but not on Go/Zen/OpenRouter.

## Flags / caveats

1. **WebDev ELO column is arena.ai Code/Website (text-to-HTML, Sep 8) — NOT Design Arena.** designarena.ai is JS/Firebase-rendered and not statically extractable; no Design Arena numbers are used in this snapshot.
2. **DeepSeek V4.1-Flash 74.2 DeepSWE is provider-run / self-reported** — not yet on datacurve or AA. Treat as **provisional**.
3. **AA v4.3 no longer exposes standalone Coding/Agentic indices** — use DeepSWE + Arena (and WebDev ELO) as the discriminators.
4. **Kimi K3 license is non-OSI**; **GLM-5.3 weights still "forthcoming"** as of Sep 10 (MIT promised, not dropped).
5. **Qwen3.8-Max hosted API is proprietary.** Open sibling Qwen3.8-2.4T-A95B is text-only and impractical; the usable open one is **Qwen3.8-27B (Apache 2.0)**.
6. **Muse Spark 1.3 is Meta-proprietary** (not open-weight) despite leading DeepSWE in some sources.

## Provider availability (Sep 10)

### OpenCode Go (new/changed models)

| Model | Usage cap | Price I/O |
|---|---|---|
| Qwen3.8 Max | $15 | $2.00/$6.00 |
| Qwen3.8 Flash | $30 | $0.15/$0.47 |
| GLM-5.3-Flash | $60 | $0.15/$0.50 |
| GLM-5.3 | $15 | $1.40/$4.40 |
| Kimi K3 | $15 | $3.00/$15.00 |
| DeepSeek V4.1 Flash | $15 | $0.15/$0.60 off-peak, id `deepseek-flash` |
| Grok 4.6 | $15 | — |
| GPT 5.6 Luna | $15 | — |
| Hy4 preview | $30 | — |
| Muse Spark 1.3 Contributor | $60 | — |

**Not on Go:** GPT-6 Astra, Fable 5.1, Gemini.

### OpenCode Zen

- **Present:** GLM-5.3 + GLM-5.3-Flash; GPT-6 Astra, Fable 5.1, Gemini 3.8 Flash, Grok 4.6, Muse Spark 1.3 listed.
- **Absent:** Qwen3.8 Max (tops at Qwen3.7 Max).
- **Promo:** GPT 5.6 Sol 50% off through Sep 18.

## Operational state (probed Sep 10)

| Provider / route | Status |
|---|---|
| OpenRouter (all `openrouter/*`) | **Exhausted** — total_credits $40 / total_usage $40.20 → every call returns 502 `upstream_credentials_exhausted` |
| `zai/glm-5.3` | **429, no failover** — plan weekly/monthly cap, resets 2026-09-13; **8/8 429** on unique-prompt retest (bifrost does not reroute this model) |
| `zai/glm-5.3-flash` | 429 direct; bifrost routes to fallback (served by deepseek) — chain works |
| `zai/glm-5.2` (via Alibaba plan) | **200 OK** — working GLM substitute while z.ai is capped |
| `kimi-for-coding/k3` | Live-OK |
| `deepseek/deepseek-v4-flash` | Live-OK |
| `minimax/MiniMax-M3` | Live-OK |
| `alibaba-token-plan/qwen3.8-max` | Live-OK |

**Note:** OpenCode Go models require an `x-opencode-session` header — present in opencode, absent in raw curl (raw curl to Go fails auth).

## Config changes applied (Sep 10)

1. **`opencode.jsonc`** — added `opencode-go/deepseek-flash` (DeepSeek V4.1 Flash, multimodal, 1M ctx) and `alibaba-token-plan/glm-5.2` (working GLM substitute while z.ai is capped).
2. **Pruned non-open-weight registrations** — removed Grok 4.5/4.6, GPT-5.6 Luna, GPT-6 Astra/Astra Pro, Claude Fable 5.1, Gemini 3.8 Flash, Muse Spark 1.3 Contributor, Mercury 2.5 Preview (9 entries) from `opencode.jsonc` and the bifrost OpenRouter allowlist. Registry now 37 models, all open-weight / Chinese-ecosystem.
3. **`oh-my-opencode-slim.jsonc`** — oracle kept on `alibaba-token-plan/qwen3.8-max`; a trial move to `zai/glm-5.3` was **reverted** (z.ai capped + no bifrost failover for glm-5.3 → 8/8 429). Council alpha moved `zai/glm-5.3` → `alibaba-token-plan/glm-5.2` (working GLM family). GLM-5.3 remains the post-Sep-13 upgrade target.
4. **`bifrost/config.json`**:
   - Refreshed `glm-5.3-failover-chain` (zai → alibaba glm-5.2 → opencode-go/glm-5.3 → OR).
   - Extended `kimi-k3-failover-chain` (added opencode-go/kimi-k3).
   - Added `qwen3.8-max-failover-chain` (alibaba → go → OR, p10).
   - Added `qwen3.8-flash-failover-chain` (go → alibaba → OR, p11).
   - Added `deepseek-v4.1-flash-failover-chain` (go/deepseek-flash → deepseek → OR, p12).

**Open-weight only:** OpenAI/Gemini/Claude/xAI/Meta/Inception registrations pruned (9 entries). OR allowlist is now open-weight only, but OR itself is drained, so those routes stay unusable until funding.

## Preset seat rationale (Sep 10)

| Seat | Model | Rationale |
|---|---|---|
| orchestrator | **GLM-5.3-Flash** | 95% of GLM-5.3 at ~1/10 cost; 6,320 req/5h vs 220 |
| oracle | **Qwen3.8-Max** | GLM-5.3 blocked by z.ai cap + no bifrost failover until Sep 13 |
| designer | **Qwen3.8-Max** | WebDev ELO 1685 — best open-tier design |
| fixer | **GLM-5.3-Flash** | Cost/quality sweet spot |
| explorer | **DeepSeek V4.1-Flash** | Legacy id reroutes; cheapest long-ctx |
| observer | **GLM-5.3-Flash** | Validated multimodal (vision QA round 3) |
| council | **GLM-5.2 (Alibaba) + Qwen3.8-Max + Kimi K3** | 3 families; GLM via Alibaba plan while z.ai capped |
