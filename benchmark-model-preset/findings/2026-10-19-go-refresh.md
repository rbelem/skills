# Go Refresh — Oct 19, 2026 (M3.1 Flash launch + dead-model sweep)

Trigger: `/benchmark-model-preset` — "new models were released today, worth
updating the config?"

Sources: `https://opencode.ai/docs/go/` (live HTML, Go + Go Plus tables),
models.dev `api.json` (providers `opencode-go`, `opencode`), OpenRouter
catalog (`created` timestamps), Artificial Analysis, MiniMax launch blog.
Probes: `probe-model.sh` per id (message-API = applied model), plus a
controlled vision/tool smoke test.

## 1. What was released today

**MiniMax M3.1 Flash** — 2026-10-19, OpenRouter id
`minimax/minimax-m3.1-flash:free` (created 03:12 UTC).

| Datum | Value | Source |
|---|---|---|
| Go id | `opencode-go/minimax-m3.1-flash-free` — **Free, Unlimited reqs**, "limited time" | Go docs (live) |
| Console id | `opencode/minimax-m3.1-flash-free` — also live (probe UP, cost 0) | probe |
| AA Intelligence Index | **42** (M3 = 29.2, M2.7 = 22.8) | artificialanalysis.ai (independent) |
| AA Coding / Agentic sub-index | not published yet | — |
| DeepSWE v1.1 | 73.7 **vendor-reported** (DS V4.1 Flash-1017 = 77.0) | MiniMax blog |
| Terminal-Bench 4.0 | 38.1 vendor-reported (weak) | MiniMax blog |
| Context | 1M (512K output) | models.dev |
| Modalities | text+image+video in, text out — **multimodal** | MiniMax docs |
| Reasoning | always-on, 5 efforts (low…max), `thinking.type=disabled` → 400 | MiniMax docs |
| Tool calling | supported (Anthropic + OpenAI compatible) | OR capability list |
| Architecture | 428B total / ~23B active MoE, sparse attention, native visual encoder | vendor |
| Weights | closed; "released later", ~Oct 23 | vendor |
| Privacy (Go) | model training **Not used**, data retention **0 days** | Go docs privacy table |
| Regions | free previews excluded in ~20 countries | Go docs |

Also new-ish on Go (not today): `minimax-m2.7` ($0.30/$1.20, 204K ctx) —
the Oct-16 "not yet on Go" note is stale.

**Live probes (Oct 19):** `opencode-go/minimax-m3.1-flash-free` UP at
#low/#medium/#high (cost 0). `opencode/minimax-m3.1-flash-free` UP at #high.

**Smoke test** (`opencode-go/minimax-m3.1-flash-free#low`):
- tool call: 1 bash call, completed, exact output returned; 2-step shell
  (`pwd` + `ls | head -3`) executed correctly → **PASS**
- vision: 3 shapes read exactly (red filled circle / blue filled square /
  black unfilled circle, correct order + fill state); the text token
  `VQA-7319-M3F` was misread as `V0A-7319-M3F` (Q→0) → **partial**. Not
  observer-grade (the GLM-5.3-Flash bar is 4/4 exact).

## 2. Dead / broken entries found (all probed live, pre-edit)

The head-only probe (`probe-heads.sh`) hides mid-chain rot. A full
**every-entry** probe found eight broken entries the Oct-16 refresh missed:

| Seat | Entry | Verdict | Cause |
|---|---|---|---|
| orchestrator | `mimo-v2.6-flash` (bare) | DOWN | bare string inherits seat variant `high`; mimo has **no** reasoning options |
| oracle | `space-bunny#high` | DOWN | model retired from Go ("Model unavailable") |
| oracle | `kimi-k3#high` | DOWN | kimi-k3 supports **only** `max` |
| explorer | `mimo-v2.6-flash` (bare) | DOWN | same variant inheritance (seat `low`) |
| designer | `qwen3.8-max#high` | DOWN | qwen3.8-max efforts are low/medium/**xhigh** |
| fixer | `space-bunny#high` | DOWN | retired from Go |
| fixer | `mimo-v2.6-flash` (bare) | DOWN | variant inheritance |
| council | `mimo-v2.6-pro` (bare) | DOWN | seat variant `max` inherited |
| explorer | `opencode/glm-5.3-flash-free#high` | FAILOVER | Console gate flaky — UP for librarian#low in the same run, FAILOVER here; retry hook steered to deepseek (paid) |
| opencode.jsonc | title/compaction/summary = `opencode/space-bunny-free` | DOWN | space-bunny retired from Go entirely |

Rule learned: **a bare-string model entry inherits the seat-level variant,
and an unsupported variant = resolution error (no assistant message).**
Models with `reasoning_options: []` (mimo-v2.6-*) must carry
`"variant": "default"`; `none` is also rejected.

Console-attested `opencode/*-free` ids remain **intermittent** (they need a
signed-in OpenCode Console). Go-gated `opencode-go/*-free` ids did not
fail once all session.

## 3. Config edits applied

`oh-my-opencode-slim.jsonc` (`presets.default` + `council.presets.default` +
root agents):

| Seat | Before | After |
|---|---|---|
| orchestrator | deepseek#high → muse#high → glm-5.3-flash#high → mimo | same, mimo `#default` |
| oracle | glm-5.3#max → space-bunny#high → kimi-k3#high | glm-5.3#max → **kimi-k3#max** → **deepseek-v4.1-flash#max** |
| librarian | opencode/glm-5.3-flash-free#low → beam-free → gpt-6-luna → deepseek | **opencode-go/minimax-m3.1-flash-free#low** (head) → opencode/glm-5.3-flash-free#low → beam-free#low → gpt-6-luna#low → deepseek#low |
| explorer | muse#low → opencode/glm-5.3-flash-free#high → beam-free#high → mimo | muse#low → **minimax-m3.1-flash-free#low** → opencode/glm-5.3-flash-free#high → beam-free#high → mimo `#default` |
| designer | qwen3.8-max#high → glm-5.3-flash#high | **qwen3.8-max#xhigh** → **qwen3.8-flash#xhigh** → glm-5.3-flash#high (seat variant `xhigh`) |
| fixer | deepseek#high → muse-1.3#high → glm-5.3-flash#high → space-bunny#high → mimo | deepseek#high → muse-1.3#high → glm-5.3-flash#high → **muse-spark-1.2-contributor#high** → mimo `#default` |
| observer | glm-5.3-flash#high | unchanged (M3.1 Flash not observer-grade: Q→0 token misread) |
| council | glm-5.3#max → mimo-v2.6-pro (bare) | glm-5.3#max → mimo-v2.6-pro `#default` |
| council.alpha | kimi-k3#max | kimi-k3#max → **glm-5.3** (K3 429 fallback) → reverted to **kimi-k3#max only** (user call: an alpha fallback is not wanted) |
| council.delta | mimo-v2.6-pro (no variant) | + explicit `"variant": "default"` |
| council.epsilon | — | **new seat**: `opencode-go/minimax-m3.1-flash-free` at `variant: max` (free 5th voice; user call) |
| fast-generic | opencode/glm-5.3-flash-free#high → beam-free#high → haiku#low → glm-5.3-flash#low | **opencode-go/minimax-m3.1-flash-free#high** (head) → beam-free#high → opencode/glm-5.3-flash-free#high → haiku#low → glm-5.3-flash#low |
| investigator | glm-5.3#high → deepseek#high → muse#high | same + **minimax-m3.1-flash-free#low** (free last-resort, read-only seat) |

`opencode.jsonc`: title / compaction / summary moved off the dead
`opencode/space-bunny-free` → `opencode-go/minimax-m3.1-flash-free`
(free, unlimited, 1M ctx, no training, 0-day retention). Root session model
left on `opencode-go/muse-spark-1.3-contributor`.

**Writers stay off free tiers** (stop-not-overflow policy): orchestrator and
fixer keep paid heads. M3.1 Flash is free-only on Go, so it cannot be a
writer head anyway, and its only coding signal is vendor-reported.

**Why the free Go model leads the read-only seats:** the Console-gated
`opencode/*-free` path is flaky and its failover steered to a *paid*
deepseek run for a lookup task. A Go-gated free head is always live, costs
$0, and has no Console dependency; the Console-gated AA-57 model stays in
the chain for when it is signed in.

## 4. Go catalog deltas (live Oct 19)

- **Gone from the Go model list:** `space-bunny` (paid) and
  `space-bunny-free`, `cat-jam-free`, `step-5-preview-free`. models.dev still
  lists `space-bunny` — the catalog lags the server.
- **New:** `minimax-m3.1-flash-free` (free, unlimited, limited time).
- Unchanged: glm-5.3/5.3-flash/5.2, kimi-k3/k2.7-code, deepseek-v4.1-flash
  ($80 cap, 173,330 req/mo) / v4-pro, mimo-v2.6-flash/pro + v2.5 pair,
  muse-spark-1.3/1.2-contributor ($60, 226,600 req/mo), qwen3.8-max/flash,
  qwen3.7-plus, hy4-preview, hy3, grok-4.7, gpt-6-luna, gpt-5.6-luna,
  claude-haiku-5-5, gemini-4-argon-contributor, longcat-2.0 + 2.5-free,
  step-5-preview (paid), beam-free, minimax-m3, minimax-m2.7.
- `qwen3.8-max` is capped at **810 req/mo** ($15 bucket) — that is why
  `qwen3.8-flash` (27,000 req/mo, $30) was added as the designer fallback.

## 5. Validation (post-edit)

- `bunx oh-my-opencode-slim doctor --json` → `ok: true`, preset `default` ok.
- Full every-entry probe of the edited config: **38/38 entries UP, 0 down**
  (pre-edit baseline was 30 up / 8 down + 1 failover).
- Live delegation: `@fast-generic` ran on
  `opencode-go/minimax-m3.1-flash-free` (variant=low, **cost 0**), made one
  completed bash tool call, returned the exact expected output.
- Live council seat: `councillor-alpha` dispatched on
  `opencode-go/kimi-k3` variant=max (cost $0.02) and answered — the new
  2-model alpha chain resolves through `_modelArray` as designed.
- `opencode-go/minimax-m3.1-flash-free` probed UP at #low/#medium/#high and
  with no variant (the `opencode.jsonc` title/compaction/summary form).
- Persisted: `chezmoi add` of `oh-my-opencode-slim.jsonc` + `opencode.jsonc`
  (chezmoi commit 8133697); skill repo commit `c5544f1`.

### Council follow-up (user call, later Oct 19)

- `council.presets.default.alpha` → single model `opencode-go/kimi-k3` (`max`);
  the glm-5.3 fallback added earlier in the day was reverted.
- **New seat `epsilon`** = `opencode-go/minimax-m3.1-flash-free` at
  `variant: max` — free fifth voice (probe UP at #max, cost 0).
- Roster is now 5 seats: alpha (K3) · beta (GLM-5.3) · gamma (qwen3.8-max) ·
  delta (mimo-v2.6-pro) · epsilon (M3.1 Flash Free).
- **A new seat needs a host restart to be dispatchable.** The v2 host freezes
  the agent registry at server start — a config edit refreshes model chains
  for new child dispatches but does NOT add agents
  (`src/v2/config-change-coordinator.ts`: "There is deliberately no
  host-registry reload here — session prompt/tool surfaces stay frozen").
  Dispatching `councillor-epsilon` in the running session returned
  "Unknown agent: councillor-epsilon"; that is the freeze, not a config
  error. Restart opencode (TUI or server) to register the seat.

## 6. Open items
- AA has not published a Coding/Agentic sub-index for M3.1 Flash yet.
  Re-check in a few days; if AA Coding lands near glm-5.3-flash, the free
  model can take more seats.
- M3.1 Flash weights ~Oct 23 (license undisclosed) — a self-host route may
  change the economics.
- Observer stays on glm-5.3-flash until a vision model reads an exact token
  4/4.
- The root session model in `opencode.jsonc` is still
  `opencode-go/muse-spark-1.3-contributor`; the *current* session runs
  `opencode-go/minimax-m3.1-flash-free` (picked in the TUI). Flipping the
  root to the free model costs $0 and removes the Meta-training tier, at the
  price of AA 42 vs Muse's unverified index.

## 7. Retro fixes (same session, after `/retro`)

Nine findings from the retro, all closed:

| # | Finding | Fix |
|---|---|---|
| 1 | `doctor` checks shape, not resolvability — it passed a dead designer seat | **`scripts/lint-preset.py`** — free, offline: variant validity, model existence, bare-string entries, seat-vs-chain[0] variant mismatch, empty chains. Live config: 0 errors, 0 warnings, 15 seats |
| 2 | Liveness checks spent paid quota on free facts | **ladder in SKILL.md Step 3**: lint (free) → catalog diff (free) → probe only what survives. `probe-all-entries.sh` now skips catalog-retired ids (reported RETIRED, `--probe-retired` overrides) |
| 3 | The Go catalog parser was re-derived inline every refresh | **`scripts/go-catalog.py`** — parses the live docs HTML into JSON / `--table` / `--ids` / `--diff-models-dev`; `scripts/out/` cached, gitignored |
| 4 | See Also could not reach the probe tools | See Also now lists every script with its "use when" branch |
| 5 | Session-record shape undiscoverable (`parts` vs `content`) | shape documented in Step 6; `scripts/session-report.py` prints it |
| 6 | REFERENCE.md was a stale price cache the skill pointed at as truth | Go plan table, OpenRouter price columns and the Zen table cut; pricing rules rewritten to the live Go-only policy; AA/ELO tables kept as dated archive; Design Arena relabelled a snapshot |
| 7 | Two style systems in the global AGENTS.md, one never firing | "Caveman Mode" load instruction removed; "terse by default" folded into the clarity rules, with the `caveman` skill as the explicit mode |
| 8 | The skills repo's secret-scan guardrail was unwired | `.githooks/pre-commit` (canonical, gitleaks via PATH or nix), `.pre-commit-config.yaml` calls the same script, CI workflow committed, `core.hooksPath .githooks` installed, README documents it. Verified: a staged fake AWS key and GitHub token are blocked (exit 1) |
| 9 | AGENTS.md lines that restate existing checks | "Commit Identity" trimmed to what identity-guard does not enforce; the zvec-grep block deleted (the server injects its own rules); Step 1 gained `chezmoi diff` |

### Cross-checks that came out of the new tooling

- `go-catalog.py --diff-models-dev`: models.dev lists 4 ids the live Go
  catalog dropped — `cat-jam-free`, `minimax-m2.7`, `space-bunny`,
  `step-5-preview-free`. models.dev is a candidate list, not liveness.
- `lint-preset.py` caught a real mismatch in the live config: the
  orchestrator chain head was written `#max` while the seat variant said
  `high` — the seat variant wins at runtime, so the head ran at `high`.
  Seat variant aligned to `max` (the written intent).
- The user moved `opencode-go/minimax-m3.1-flash-free#max` to the head of
  the orchestrator chain. That is a writer seat, so it overrides the
  "free tiers stay off writers" rule — recorded, not silently accepted.
