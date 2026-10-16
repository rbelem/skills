# Go Refresh — Oct 16, 2026 (budget preset)

Trigger: `/benchmark-model-preset` — new Go + free models review.
Sources: `https://opencode.ai/docs/go/` (live), models.dev `api.json`
provider `opencode-go` (32 models), live `opencode run` probes.

## Retired server-side (were in budget chains)

| Model | Used by | Probe |
|---|---|---|
| `cat-jam-free` | explorer, fast-generic | "Model unavailable" |
| `step-5-preview-free` | librarian | "Model unavailable" |

Still listed in models.dev but dead on the wire (same pattern as
`space-bunny-free` in Sep). Both seats had already failed over to paid
fallbacks via the retry hook — including this session's own @librarian
lane, which errored at spawn twice.

## New since Oct-15 snapshot

| Model | Price I/O | Cap | Req/mo | Note |
|---|---|---|---|---|
| **beam-free** (Reflection Beam, 501B MoE/23B act) | free | ∞ | ∞ | limited time; BR not region-excluded. Vendor: SWE-Bench Pro 65.5, TB 2.1 80.1 (unverified, weights pending). Probed: 391 math in 1.26s; `#low` + `#high` resolve |
| **muse-spark-1.2-contributor** | $0.10/$0.20 | $60 | 226,600 | older Muse sib; 1.3 stays primary (vendor DeepSWE 75.4 vs 1.2 unscoped). Separate $60 bucket → quota-spread fallback. `#high` resolves |
| **step-5-preview** (paid) | $1.00/$2.70 | $15 | ~8,520 (4× promo) | no strong coding signal; skipped |
| **mimo-v2.5 / v2.5-pro** | same as v2.6 pair | $60/$15 | 150,400/16,300 | older gen, v2.6 newer; skipped. (Catalog id is `mimo-v2.5`, no `-flash` suffix.) |
| **minimax-m2.7** | in models.dev, absent from Go docs | ? | ? | not yet on Go; watch |
| gpt-6-luna / haiku-5.5 | cheap, ~20K req/mo on $15 | — | — | no verified coding benchmarks; deepseek-v4.1-flash ($80 cap, 173K req/mo) already covers paid fallback. Skipped |

Gone from docs: grok-4.6 (only 4.7 now). `longcat-2.5-preview-free`
still alive (slowest, 21.9s, no benchmarks) — kept out of chains.

## Preset changes (`presets.budget`, doctor ok, all ids+variants probed live)

- orchestrator: muse-1.3#high → **muse-1.2#high** → glm-5.3-flash#high → …
- fixer: muse-1.3#high → **muse-1.2#high** → glm-5.3-flash#high → …
- librarian: **beam-free#low** → deepseek-v4.1-flash#low → qwen3.8-flash#low
- explorer: muse#high → **beam-free#high** → mimo-v2.6-flash
- fast-generic: **beam-free#high** → glm-5.3-flash#low
- Unchanged: oracle, designer (qwen3.8-max still best open-tier design),
  observer (glm-5.3-flash vision-passed), council + councillors.

Rule kept: free previews only on read-only/mechanical seats; writers keep
paid heads with free nowhere in chain.

## Follow-up — Oct 16: glm-5.3-flash-free, gpt-6-luna, haiku-5.5

- **glm-5.3-flash-free: LIVE under `opencode/`, not `opencode-go/`.**
  Correct id `opencode/glm-5.3-flash-free` (free, $0, low/high/max). First
  probe failed over to Muse = Console signed out; after user reconnected,
  serves directly (verified via message API: providerID `opencode`,
  cost 0). Siblings also live: `muse-spark-1.3-contributor-free`,
  `deepseek-v4.1-flash-free`, `mimo-v2.6-flash-free` (deepseek confirmed
  via message API; others via serving header). Wired as heads of
  librarian (`#low`), explorer (`#high`), fast-generic (`#high`) —
  each chain now mixes Console-gated (`opencode/*`) + Go-gated
  (`opencode-go/*`) entries, so either gate dropping still leaves a free
  then paid path. 200k-ctx claim unverified (models.dev shows no ctx).
  Writers untouched: free stays out of orchestrator/fixer (stop-not-overflow
  policy). Dropped qwen3.8-flash librarian tail (unknown scores, redundant
  behind deepseek $80 backstop).
- **gpt-6-luna: yes, as librarian fallback.** Vendor DeepSWE 66.6 (max),
  VERIFIED AA intel 38, Arena +1.6%, 123 tok/s; weak TB4.0 (12.6%) but that
  hardly matters for lookup seats. Live-probed `#low` tool call OK.
  Chain: beam-free#low → **gpt-6-luna#low** → deepseek-v4.1-flash#low → …
- **claude-haiku-5.5: yes, as fast-generic fallback.** VERIFIED AA index 43,
  TB 33–39%, strong tool use + instruction following, fast; DeepSWE unknown,
  weak at long autonomous loops — exactly the fast-generic-shaped profile
  (short bounded shell/git/test tasks). Live-probed `#low` tool call OK.
  Chain: beam-free#high → **haiku-5-5#low** → glm-5.3-flash#low.
- **Quota-burn check:** both sit on $15/mo caps (5h = 20%: luna ~4,230 req,
  haiku ~3,850 req; monthly ~21K/19K). Librarian/fast-generic do dozens of
  reqs per session at most — normal use is hundreds/day, an order of
  magnitude under the 5h budget. Safe **only** on these low-volume seats;
  never promote either to writer seats (fixer/orchestrator would eat a $15
  bucket in hours).
