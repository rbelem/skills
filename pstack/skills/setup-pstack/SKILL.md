---
name: setup-pstack
description: Configure optional model overrides for pstack's multi-model roles and their reasoning budget. Detects your available models and writes an always-applied rule. Every pstack subagent runs on its oh-my-opencode-slim seat (`fixer`, `oracle`, `explorer`) or the `investigator` evidence agent, and no model names ship in the skills. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write `~/.config/opencode/pstack-models.md`, an always-applied rule with optional per-role model overrides. Every pstack subagent runs on an oh-my-opencode-slim seat (`fixer`, `oracle`, `explorer`) or on `investigator` for the `why`/`reflect` evidence roles, and passes no `model` unless this rule sets one. The rule exists for one need: specific models on the multi-model roles (the `why` and `reflect` evidence roles, the `arena`, `architect`, and `interrogate` panels, and `swarm workers`); skip this skill when the seats' own choices suit you.

## Steps

### 1. Detect available models

Enumerate the model slugs you can pass to a `Task` subagent in this session. That is the dependable source. If OpenCode also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness. If you cannot detect any, ask the user to paste the slugs they have access to. Never write a real slug you have not confirmed is available. The aliases `inherit-parent` and `auto` are always valid even though they are not detected slugs.

### 2. Load current state

If `~/.config/opencode/pstack-models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. If it does not, start from an empty slate: no role has an override. A line whose role is not in step 5, such as `how explorer` or `bug-fix`, is from a retired role or now runs on a seat. Drop it.

### 3. Ask, map, and confirm

**(a) Ask which roles get overrides.** Prefer question over free text. List the nine role lines from step 5 and ask which, if any, should get a specific model. If the user wants none, stop here: every role runs on its seat chain or agent default (remove the role lines from an existing rule, or delete it).

**(b) Pick models.** For each chosen role, offer the detected models plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model, which is how Auto users stay on Auto). Prefer question over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count; each entry spawns a seat (`fixer` for runners and workers, `oracle` for judges and reviewers) with that `model`. `arena cross-judge pool` is also a list, but Arena runs one judge. It tries only values from a family other than the parent's, in list order, so order it by preference. An `inherit-parent` or `auto` value never judges. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm. A multi-model panel needs two or more entries with different families.

**(c) Ask for a budget** when any role got a real model. Offer these four options with these exact labels, and name the current budget when the rule records one.

- `unlimited — top reasoning`
- `large — as picked`
- `medium — one step down`
- `small — floor reasoning`

**(d) Apply the budget.** The budget sets the reasoning variant of every real slug in the working table, panel entries included. `unlimited` moves each model to its top variant (`#max` where the model ships it). `large` keeps the picked levels. `medium` lowers each model one step. `small` moves each model to its floor (`#low`, or the model's lowest). The variant is the `#` suffix on the slug, on the ladder `max` > `xhigh` > `high` > `medium` > `low` (models ship their own subset). When the model ships no variant at the target, use its nearest variant at or below the target. If the result is not a detected slug, use the same family's detected slug at the highest variant at or below the target, else mark the role as needing a choice. `inherit-parent` and `auto` do not change.

**(e) Show the roles and confirm.** Show every override with its model, marking any real slug not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles.

### 4. Validate

Every real slug written must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen real slug is not available, stop and ask again.

### 5. Write the rule

Write `~/.config/opencode/pstack-models.md` with `alwaysApply: true`, a `# budget` line with the chosen label and its recorded target (`top`, `as picked`, `one step down`, `floor`), and one line per overridden role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. The role lines to choose from, in order: `why investigators`, `why synthesizer`, `reflect tooling`, `reflect judgment, divergent, synthesizer`, `arena runners`, `arena cross-judge pool`, `swarm workers`, `architect runners`, `interrogate reviewers`. Shape (write only the chosen roles; `<model>` stands for a detected slug, and panel roles take a comma-separated list):

```
---
description: pstack per-role model overrides (unlisted roles run on their seat or agent default)
alwaysApply: true
---
# pstack model overrides for the multi-model roles. One line per overridden role; delete a line to fall back to the seat chain or the agent default.
# Seat roles (code, judgment, `how` explorers and explainer) are not listed; they run on their oh-my-opencode-slim chains.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# budget: <label>
why investigators: <model>
arena runners: <model>, <model>
```

### 6. Confirm

Tell the user the rule was written and that it applies to new sessions. Re-running this skill updates it. Roles not listed run on their oh-my-opencode-slim agent (`fixer`, `oracle`, `explorer`, or `investigator`); the seat chains live in `oh-my-opencode-slim.jsonc`.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin). On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, invoke `/create-formal-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin). On no, move on without pushing.
