# Benchmark & Pricing Snapshot — Aug 26, 2026

Sources: OpenRouter catalog API (live, 417 models), artificialanalysis.ai (live, published day-of), docs.bigmodel.cn (official, Chinese), go.md (live), HF API (live), librarian research (Aug 21–26 releases).

## New releases since Aug 24 snapshot

| Model | Released | Org | Params | Verified (AA) | Vendor claims | Price (I/O per M) | Access |
|---|---|---|---|---|---|---|---|
| **GLM-5.3-Flash** | **Aug 26** | Z.AI | 320B/18B MoE, hybrid sparse+linear attn + IndexPool | **Intel 57** ($0.09/task, 150M verbosity); speed N/A yet | DeepSWE 63.4, TB2.1 84.3, AutoBench 48.8, OfficeQA Pro 62.4 | $0.15/$0.50 (z.ai, Go); **OR $0.075/$0.25** (50% promo) | Go ($15 → ~7,900/mo), z.ai Coding Plan (**3× quota vs 5.3, off-peak 50%**), OR, **MIT weights on HF** |
| **Qwen3.8-Flash-Next** | **Aug 26** | Alibaba | 125B/6B MoE + 51B n-gram emb + 4B MTP; GDN + QSA | none yet | DeepSWE 58.7, SWE-bench Pro 62.5, GPQA 91.7, LCBv6 91.9, CoWorkBench 73.9, JobBench 55.7, Toolathlon 73.5 | Free (open weights, Qwen license); API TBD | **No API yet** (no OR/Go/Zen) — watch only |
| Wan 3.0 | Aug 24 | Alibaba | — | — | — | $0.0425/s (15% promo) | OR (video gen, 30s, doc input) |
| DeepSeek V4 Flash Vision Exp | Aug 21 | DeepSeek | 284B/13B + vision | — | matches V4 Flash text + multimodal | $0.22/$0.66 | already wired (deepseek + Go + OR) |
| Muse Spark 1.2 Contributor | Aug 21 | Meta | 1M ctx | — | — | $0.10/$0.20 | OR (95% off; data used for Meta training) |

Also: OpenAI **o3 retired** from ChatGPT (Aug 26); GLM-5.5 still rumor-only (no official announcement); GLM-5.3 open weights still expected ≈Aug 28.

## GLM-5.3-Flash details

- **Ox Alpha revealed**: OR swapped `stealth/ox-alpha` → `z-ai/glm-5.3-flash` (canonical `z-ai/glm-5.3-flash-20260826`); Go model list replaced Ox Alpha Free with GLM-5.3-Flash. Stealth stats: 503K users, 13.12M sessions, 44T tokens.
- Architecture: first open frontier model with sparse+linear attention; 3.01× less attention compute and 4.44× less KV cache than GLM-5.3; KV still slightly above Kimi-K3 and DS-V4-Flash. Runs on domestic Chinese chips (ReplaySSM, W8A8, INT8/FP8/BF16 mixed cache, EPD serving); 3× e2e perf vs initial baseline.
- Native multimodal: vision integrated into coding loop (frontend, games, Blender, BUA/CUA); Office/PPTX/PDF/DOCX/XLSX self-verification; financial/legal workflows.
- Reasoning: mandatory thinking (no off), `reasoning_effort` max/high/low, default max; temperature 1, top_p 0.95; supports tools, structured output, caching (83% cache discount); 131K max output.
- OpenRouter endpoint: single Z.AI provider, fp8, uptime 100% (30m), launch discount 0.5.

## Qwen3.8-Flash-Next details

- Explicit **Qwen4 architecture preview** (qwen4_exp HF tag). Native multimodal (image-text-to-text). 262K ctx native / 1M extended. Trained at ~1/9 cost of larger competitors per vendor.
- OpenRouter catalog has NO qwen3.8-flash; only qwen3.8-max ($2/$6), qwen3.8-2.4t-a95b ($2/$6), qwen3.8-27b ($0.425/$2.55). Go has qwen3.8-max only.
- Action: none until API availability + verified AA/DeepSWE.

## OpenCode Go (live, Aug 26)

New: **GLM-5.3-Flash $0.15/$0.50, usage $15 → ~7,900 req/mo** (1,580/5h). Everything else matches Aug 24 snapshot (GLM-5.3 $15/1,080 · K3 $15/490 · Qwen3.8 Max $15/810 · DS V4 Flash $30/37,800 · Hy3 $60/21,500 · LongCat $60/57,200 · Muse Contributor $60/226,600). Ox Alpha Free gone (replaced by flash).

## z.ai provider status (Aug 26)

- **GLM Coding Plan: GLM-5.3-Flash 已全面放开 — 3× quota vs GLM-5.3; off-peak (incl. weekends all day) = 50% points** (new points-based quota system, official docs).
- GLM-5.3/5.2 still 2–3×/prompt (unchanged); glm-4.7 still 1×.
- z.ai API model code `glm-5.3-flash`, params mirror GLM-5.3 (text) + image_url content blocks (multimodal).

## Config changes applied (Aug 26)

1. **bifrost config.json**: zai key models += `glm-5.3-flash`; OR key models: `stealth/ox-alpha` → `z-ai/glm-5.3-flash`; routing rule: dead ox-alpha chain (priority 8, model removed from OR/Go) **replaced** by `glm-5.3-flash-failover-chain` (priority 9): zai → **opencode-go/glm-5.3-flash → deepseek/deepseek-v4-flash-vision-exp** (secondary Go usage pool, tertiary multimodal-capable different-family; vision-exp keeps observer capability if zai is down). ⚠️ sqlite config store still holds the old priority-8 ox-alpha rule — file sync conflicts on same priority; flash chain uses 9. Stale store rule is dead weight (no request matches `ox-alpha` anymore).
2. **opencode.jsonc**: added `zai/glm-5.3-flash`, `opencode-go/glm-5.3-flash`, `openrouter/z-ai/glm-5.3-flash` (all multimodal input ["text","image"], 1M ctx, 131K out, variants low/medium/xhigh/max).
3. **oh-my-opencode-slim.jsonc**: orchestrator+fixer → `bifrost/opencode-go/glm-5.3-flash` (quality preset) and `bifrost/zai/glm-5.3-flash` (value preset). Everything else unchanged.
4. **Live-verified** post-restart: `zai/glm-5.3-flash` ✓ (coding plan), `opencode-go/glm-5.3-flash` ✓ (unique-prompt echo), both return reasoning; `openrouter/z-ai/glm-5.3-flash` listed in bifrost catalog (OR credits were ≈0 as of Aug 25 — top up before using OR route).

## Open items / flags

- **Observer swap (MiniMax-M3 → GLM-5.3-Flash): DONE Aug 26** — controlled vision QA round 3 passed (see addendum below).
- **bifrost restart gotcha**: routing-rule priority collision with sqlite config store — if a future rule edit fatals with "priority N already exists", pick a fresh priority (store keeps stale rules).
- z.ai Coding Plan points-based quota: monitor actual flash burn rate on heavy fixer loads (5-hr/window dynamics unknown for the new system).
- Qwen3.8-Flash-Next: watch OR/Go catalog + AA for API availability; vendor DeepSWE 58.7 is unverified.
- GLM-5.3 open weights expected ≈Aug 28 — re-check then (weights release may change self-host options).

## Vision QA round 3 (Aug 26 — GLM-5.3-Flash added, controlled PNG recreated from spec)

Same spec as rounds 1-2: 4 text lines (`DEEPSWE-VISION-QA-42` / `Score: 67.5` / `GLM-5.3: 66.9` / `GLM-5.3 AA Agentic 59.1`), red circle + blue square + green line, white background. Via bifrost (`zai/glm-5.3-flash`, `minimax/MiniMax-M3`), same prompt (exact transcription + shape type/color/count).

| Criterion | flash-vision-exp (r1) | MiniMax M3 | **GLM-5.3-Flash** |
|---|---|---|---|
| Exact code read (A1) | ❌ OA-42 | ✅ | ✅ `DEEPSWE-VISION-QA-42` |
| A2 / A4 | ✅ | ✅ | ✅ (67.5, 66.9, AA Agentic 59.1 — 4/4 lines exact) |
| Shapes (A3) | ✅ basic | ✅ detailed | ✅ most detailed (positions, unfilled interiors, diagonal rising) |
| Reliability | ❌ 1 empty-content flake | ✅ clean | ✅ clean 2/2 probes (1.6s, 6.8s) |

**Verdict: GLM-5.3-Flash passes — ties M3 on every criterion, half the price ($0.15/$0.50 vs $0.30/$1.20), 1M ctx, stronger general model (AA 57). Observer swapped to flash (variant max, matching QA conditions) in both presets.** M3 remains the documented fallback; k3-256k still the alternative if z.ai quota drains. QA image: `/tmp/opencode/vision-qa-glm53flash.png` (regenerate from spec if needed — original not saved).
