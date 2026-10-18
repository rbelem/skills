---
name: setup-pstack
description: Configure the models pstack's multi-model roles use and their reasoning budget. Detects your available models and writes an always-applied rule that overrides the skill defaults. Code, judgment, and reconnaissance run on oh-my-opencode-slim seats and are not configured here. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write `~/.config/opencode/pstack-models.md`, an always-applied rule that sets the model for pstack's multi-model roles: the `why` and `reflect` evidence roles (spawned as `poteto-agent`), the `arena`, `architect`, and `interrogate` panels, and `swarm workers`. Everything else runs on oh-my-opencode-slim seats (`fixer`, `oracle`, `explorer`) whose models live in `oh-my-opencode-slim.jsonc`.

## Steps

### 1. Detect available models

Enumerate the model slugs you can pass to a `Task` subagent in this session. That is the dependable source. If OpenCode also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness. If you cannot detect any, ask the user to paste the slugs they have access to. Never write a real slug you have not confirmed is available. The aliases `inherit-parent` and `auto` are always valid even though they are not detected slugs.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. If `~/.config/opencode/pstack-models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how explorer` or `bug-fix`, is from a retired role or now runs on a seat. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer question over free text. Offer these four options with these exact labels, and name the current budget when the rule records one. With no rule, say that `large` matches the skill defaults.

- `unlimited — top reasoning`
- `large — the shipped levels`
- `medium — one step down`
- `small — floor reasoning`

**(b) Apply it.** Build the working table from the skill defaults, and on a re-run keep any role you changed by family, list, or alias (`inherit-parent`, `auto`). The budget sets the reasoning variant of every real slug, panel entries included. `unlimited` moves each role to the model's top variant (`#max` where the model ships it). `large` keeps the shipped levels. `medium` lowers each role one step. `small` moves each role to the model's floor (`#low`, or the model's lowest). The variant is the `#` suffix on the slug, on the ladder `max` > `xhigh` > `high` > `medium` > `low` (models ship their own subset). When the model ships no variant at the target, use its nearest variant at or below the target. If the result is not a detected slug, use the same family's detected slug at the highest variant at or below the target, else mark the role as needing a choice. `inherit-parent` and `auto` do not change. So `unlimited` turns `opencode-go/deepseek-v4.1-flash#high` into `opencode-go/deepseek-v4.1-flash#max` and `opencode-go/muse-spark-1.3-contributor#high` into `opencode-go/muse-spark-1.3-contributor#xhigh` (its top). `large` keeps the defaults. `medium` turns `opencode-go/glm-5.3#max` into `opencode-go/glm-5.3#high` (no `xhigh` on its ladder). `small` turns them into `opencode-go/deepseek-v4.1-flash#low` and `opencode-go/muse-spark-1.3-contributor#minimal`.

**(c) Show the roles and confirm.** Show every role with its model, marking any real slug not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model, which is how Auto users stay on Auto) as the options. Prefer question over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count; each entry spawns a seat (`fixer` for runners and workers, `oracle` for judges and reviewers) with that `model`. `arena cross-judge pool` is also a list, but Arena selects one value from it whose model family differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real slug written must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen real slug is not available, stop and ask again.

### 5. Write the rule

Write `~/.config/opencode/pstack-models.md` with `alwaysApply: true`, a `# budget` line with the chosen label and its recorded target (`top`, `shipped`, `one step down`, `floor`), and one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape (seat roles are deliberately absent; they run on their `fixer`/`oracle`/`explorer` chains):

```
---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration for the multi-model roles. One line per role. Delete a line to fall back to the skill default.
# Seat roles (code, judgment, `how` explorers and explainer) are not listed; they run on their oh-my-opencode-slim chains.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# budget: large (shipped)
why investigators: opencode-go/muse-spark-1.3-contributor#high
why synthesizer: opencode-go/glm-5.3#max
reflect tooling: opencode-go/muse-spark-1.3-contributor#high
reflect judgment, divergent, synthesizer: opencode-go/glm-5.3#max
arena runners: opencode-go/glm-5.3#max, opencode-go/deepseek-v4.1-flash#high
arena cross-judge pool: opencode-go/glm-5.3#max, opencode-go/deepseek-v4.1-flash#high
swarm workers: opencode-go/deepseek-v4.1-flash#high
architect runners: opencode-go/glm-5.3#max, opencode-go/deepseek-v4.1-flash#high
interrogate reviewers: opencode-go/glm-5.3#max, opencode-go/deepseek-v4.1-flash#high
```

### 6. Confirm

Tell the user the rule was written and that it applies to new sessions. Re-running this skill updates it. Mention that the seat roles (`fixer`, `oracle`, `explorer`) take their models from `oh-my-opencode-slim.jsonc`, not this rule.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin). On no, move on without pushing.
