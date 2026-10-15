# Open-Weights LLM Scan — July 25, 2026

## Scope

Survey of open-weights LLM/multimodal releases since the REFERENCE.md last update (Jul 18, 2026), focused on models relevant to the `oh-my-opencode-slim` preset skill (coding agents, reasoning, multimodal).

## Method

- `wigolo_search` (multi-engine) × 4 queries (open weights LLM release, DeepSWE, brand-specific, etc.)
- `wigolo_fetch` × 4 (theopenweights.com, Qwen 3.8 benchmarks, Laguna + KAT-Coder HF pages)
- `wigolo_cache` (empty — no prior coverage)

Engine pool was degraded (lobsters/mojeek breakers open) — relied on Bing News + DuckDuckGo + theopenweights.com listings.

## New Open-Weights Models Discovered (13+ in 25 days)

### Frontier-tier coding

| Model | Lab | Params | DeepSWE | SWE-bench Ver | SWE-bench Pro | License | Provider |
|---|---|---|---|---|---|---|---|
| **Laguna-S-2.1** | Poolside | 118B-A8B | **40.4%** | — | 59.4% | OpenMDW-1.1 | **OpenRouter ✓** |
| **KAT-Coder V2.5 Dev** | Kwaipilot/Kuaishou | 35B-A3B | — | **69.4%** | 45.96% | Apache 2.0 | HF only |
| **Inkling** | Thinking Machines (Mira Murati) | 975B-A41B | — | 77.6% | 54.3% | Apache 2.0 | HF only |
| **Qwen 3.8-Max** | Alibaba | ~2.4T | *Elo 47–48 on Code Arena (no DeepSWE)* | — | — | Open-weight planned | Alibaba sub only |
| **Hy3** (was in Jul 18 delta) | Tencent | 295B-A21B | 28%† | 78%† | 57.9%† | Apache 2.0 | OR only (†self-reported) |

### Reasoning / multimodal

| Model | Lab | Params | Notes | License | Provider |
|---|---|---|---|---|---|
| **Ring-Zero** | inclusionAI | trillion-param MoE | Zero-RL reasoning (no human-labeled CoT) | Open | HF only |
| **Intern-S2-Preview-397B** | InternLM/Shanghai AI | 397B multimodal | Apache 2.0 | Apache 2.0 | HF only |
| **Audio-Visual Flamingo** | NVIDIA | multimodal | Audio+image+video reasoning | Open | HF only |
| **MOSS-VL-Realtime** | OpenMOSS | streaming VLM | Live video understanding | Open | HF only |
| **Gemma 4** (was missed in Jul 18) | Google DeepMind | multimodal MoE | Encoder-free, thinking mode | Open | HF |
| **Microsoft Fara1.5-27B** | Microsoft | 27B VLM | Computer-use agents target | MIT | HF only |

### Niche / smaller

| Model | Lab | Notes | License | Provider |
|---|---|---|---|---|
| **Solar Open2 250B** | Upstage (Korea) | EN/KR MoE | Open | HF only |
| **Motif 3 Beta** | Motif Technologies (Korea) | Long-context multilingual MoE | Open (beta) | HF only |
| **Soofi S** | German consortium | 30B dense, EN+DE | Open | HF only |
| **Mage-Flow** | Microsoft | 4B text→image, MIT | MIT | HF only |

## Open-Weights DeepSWE Ranking (Verified Only)

| # | Model | DeepSWE | Notes |
|---|---|---|---|
| 1 | Kimi K3 (Moonshot) | 69% | AA Intel 57 — open weights Jul 27, 2026 |
| 2 | GLM-5.2 (Z.ai) | 44% | MIT, fully open |
| 3 | **Laguna-S-2.1** (Poolside) | 40.4% | OpenRouter-routable now |
| 4 | kimi-k2.7-code (Moonshot) | 31% | On Go + Zen |
| 5 | Hy3 (Tencent) | 28%† | †self-reported, not on official DeepSWE leaderboard |
| 6 | GLM-5.1 | 18% | MIT |
| 7 | Qwen 3.7 Max | 18% | Proprietary — NOT open |

## SWE-bench Verified Leaderboard (Open Weights)

| # | Model | SWE-bench Ver | License | Provider |
|---|---|---|---|---|
| 1 | Inkling (Thinking Machines) | 77.6% | Apache 2.0 | HF only |
| 2 | KAT-Coder V2.5 Dev (Kwaipilot) | 69.4% | Apache 2.0 | HF only |
| 3 | Hy3 (Tencent) | 78%† | Apache 2.0 | OR only (†self) |
| 4 | Kimi K3 | no official SWE-V number | Open (Jul 27) | Go + OR |
| 5 | Claude Fable 5 (closed) | 69.7% | Proprietary | Zen |

## Multi-Axis Comparison (Preset Decision Aid)

| Model | Coding | Reasoning (AA) | Open-wt | Routable now | Best role |
|---|---|---|---|---|---|
| Kimi K3 | 69% | 57 | ✓ (Jul 27) | Go + OR | Oracle (low-vol, 429 risk) |
| GLM-5.2 | 44% | 51 | ✓ MIT | Go + Zen + OR | Orchestrator/Designer |
| **Laguna-S-2.1** | 40% | — | ✓ OpenMDW | **OR ✓** | **Fixer (immediate)** |
| Inkling | 78% (SWE-V) | — | ✓ Apache 2.0 | HF only | Wait for OR |
| KAT-Coder | 69% (SWE-V) | — | ✓ Apache 2.0 | HF only | Wait for OR |
| Hy3 | 28%† | 34 | ✓ Apache 2.0 | OR | Council (Tencent diversity) |
| kimi-k2.7-code | 31% | 41.9 | ✓ | Go + Zen | Fixer (cheap) |

## Key Insights

1. **Jul 2026 = open-weights explosion.** 13+ releases in 25 days. Weekly frontier cycle.
2. **Pendulum reversal:** Qwen 3.6 Apache 2.0 → Qwen 3.7 proprietary → Qwen 3.8 returning to open-weight. Poolside (Laguna) and Thinking Machines (Inkling) follow same playbook.
3. **Laguna-S-2.1 is the only new open-weights frontier model immediately routable** (OpenRouter). Others are HuggingFace-only pending OR routing.
4. **Coding gap to closed frontier narrowed.** SWE-bench Verified 77.6% (Inkling) and 69.4% (KAT-Coder) close the gap to Claude Fable 5 (69.7%) and GPT-5.6 Sol (73%).
5. **Customization over leaderboard** is the new open-weight pitch (Inkling positioning).
6. **TRL (terminal reasoning) divergence:** Different labs emphasizing different reasoning strategies — Wang (zero-RL no human labels), Moonshot (prefill_no_think), etc.

## Preset Impact (NOT applied — user declined)

Three candidate changes identified:

| # | Preset / Role | Old | New | Gain | Risk |
|---|---|---|---|---|---|
| 1 | **value.fixer** | `moonshotai/kimi-k2.7-code-highspeed/high` | `poolside/laguna-s-2.1/high` | DeepSWE +9.4pp, SWE-Pro +17pp | OR pricing TBD; not in `provider.omniroute.models` map |
| 2 | **quality.fixer** | `opencode-go/glm-5.2/max` | `poolside/laguna-s-2.1/max` OR keep GLM-5.2 | +cap headroom, comparable quality | Loses AA Intelligence + Arena data |
| 3 | **council.presets.default** | current 5 seats | add `poolside/laguna-s-2.1` to delta slot | Provider diversity (Poolside) | Same routing risk |

**Blocked (HuggingFace-only, wait for OR routing):**
- KAT-Coder V2.5 Dev as Fixer
- Inkling as Oracle or Fixer
- Qwen 3.8-Max as Orchestrator (no DeepSWE score yet)
- Intern-S2-397B as Observer replacement for M3

## Sources

- **theopenweights.com** — daily aggregator, 322 releases tracked
- **huggingface.co/poolside/Laguna-S-2.1** — full benchmark table from Poolside
- **huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev** — full benchmark table
- **wan27.org/blog/qwen3-8-benchmarks** — Qwen 3.8-Max community analysis
- **ia4pymes.tech** — comparison of GLM-5.2 / K3 / Qwen 3.8-Max
- **explainx.ai** — Inkling overview
- **Reddit/HN** — kaleb stealth discovery context

## Open Questions

- Laguna-S-2.1 OpenRouter pricing (not yet public as of Jul 25)
- KAT-Coder V2.5 Dev DeepSWE score (not posted)
- Qwen 3.8-Max official DeepSWE / AA scores (preview only)
- Inkling on OpenRouter (not yet)
- Whether poolside/laguna-s-2.1 will be added to provider.omniroute.models map
- qwen3.7-flash on alibaba-token-plan (currently DashScope-only)

## Correction (Jul 26)

**qwen3.7-flash DOES exist** — confirmed via qwencloud.com (earlier search missed it). My prior "doesn't exist" claim was wrong.

| Property | Value |
|---|---|
| Release | Jul 14, 2026 (snapshot `qwen3.7-flash-2026-07-15`) |
| Type | Native vision-language Flash model |
| Pricing (qwencloud) | $0.03/M input, $0.13/M output, $0.006 implicit cache, $0.003 explicit cache read |
| Context | 1M input, 65K output |
| Rate | 15K RPM, 5M TPM |
| Capabilities | Function calling, structured output, prefix completion, web search, fine-tuning |
| Modalities | Input: image/text/video; Output: text |
| Description | "Upgrade over 3.6-Flash in multimodal understanding and agent execution. Optimized multimodal coding for smoother vibe coding experience." |
| Provider | DashScope API direct (qwencloud.com) — NOT on alibaba-token-plan list |

**For CHEAP preset fixer comparison:**

| Candidate | $/M in-out | Provider | Bench |
|---|---|---|---|
| qwen3.7-flash | $0.03 / $0.13 | DashScope | None published |
| alibaba-token-plan/qwen3.7-plus | $0.40 / $1.60 | Alibaba sub | None published |
| alibaba-token-plan/kimi-k2.7-code | $0.95 / $4.00 | Alibaba sub | DeepSWE 31% verified |
| alibaba-token-plan/kimi-k2.6 | $0.95 / $4.00 | Alibaba sub | DeepSWE 24% verified |

qwen3.7-flash is **13× cheaper** than qwen3.7-plus and **31× cheaper** than kimi-k2.7-code. Best $/benchmark candidate IF quality holds.

## Action Items

- [ ] Re-check OpenRouter pricing for `poolside/laguna-s-2.1` weekly
- [ ] Watch for KAT-Coder DeepSWE leaderboard entry
- [ ] Watch for Qwen 3.8-Max open-weight drop + DeepSWE run
- [ ] Watch for Inkling on OpenRouter
- [ ] Re-test endpoint health when Kimi K3 open weights drop (Jul 27)
- [ ] Test qwen3.7-flash via DashScope as cheap-fix candidate (no DeepSWE published)
