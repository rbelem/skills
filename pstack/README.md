# pstack (OpenCode port)

Port of the **pstack** Cursor plugin by Lauren Tan ([poteto](https://github.com/poteto)) — source: <https://github.com/cursor/plugins/tree/main/pstack>, v0.15.25, MIT (see `LICENSE.upstream`).

This port targets **OpenCode**. Skill bodies are otherwise verbatim upstream prose with the mechanical substitutions below.

## Substitutions applied

| Upstream (Cursor) | Here (OpenCode) |
|---|---|
| the `Ask…Question` tool (one token upstream) | `question` tool |
| Cursor rules file `pstack-models.md` (Cursor user config `rules` dir) | `~/.config/opencode/pstack-models.md` |
| Cursor skills paths (user-level `~/…cursor…/skills`, workspace `.cursor`-relative) | `~/.config/opencode/skills/` / `.opencode/skills/` |
| "background agent" | "background agent" |
| `generalPurpose` / `general` subagent type | oh-my-opencode-slim seats (`fixer`, `oracle`, `explorer`); `poteto-agent` where a role needs shell or MCP |
| `deslop` skill from `cursor-team-kit` | `stop-slop` skill (`/stop-slop`) |
| direct CLI runs (CLI/TUI verification) | direct CLI runs |
| the `agent-browser` skill / "control skill" (UI verification) | the `agent-browser` skill |
| the `write-a-skill` skill | the `write-a-skill` skill |
| `agent-transcripts/` directory | session transcript store (`opencode` sessions; query via `opencode` session commands, not the filesystem) |
| Leftover Cursor config paths and "Cursor" product references | adapted to OpenCode equivalents |

`skills/unslop/SKILL.md` additionally carries `metadata: opencode/autoinvoke: "true"`.

Skills with `disable-model-invocation: true` are user-invoked on Cursor via the slash menu. OpenCode (this build) does not derive slash commands from skills, so `commands/<name>.md` wraps each such skill (principles and `recall` excluded) in a slash command that loads the skill by exact id. `agents/` and `commands/` install by symlink like the skills below.

## Agent seats and model routing

Subagent spawns route through the oh-my-opencode-slim seats, whose model chains live in `oh-my-opencode-slim.jsonc`:

| Role | Spawn |
|---|---|
| code delegates (`feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`) and ad-hoc helpers | `fixer`, no `model` |
| judgment, prose, and design review (`how` explainer, second opinions, hardest-change design passes) | `oracle`, no `model` |
| read-only reconnaissance (`how` explorers, recall slices, transcript mining) | `explorer`, no `model` |
| evidence roles needing shell + MCP (`why` investigators/synthesizer, `reflect` reviewers/synthesizer) | `poteto-agent` + rule `model` |
| panels (`arena`, `architect`, `interrogate`, `swarm` runners, workers, judges, reviewers) | `fixer` (writers) / `oracle` (judges) + rule `model` |

Multi-model roles keep per-entry models from `~/.config/opencode/pstack-models.md`. `/setup-pstack` writes that rule and its budget (`unlimited` top, `large` shipped, `medium` one step down, `small` floor). Defaults come from the local `benchmark-model-preset` recommendations; the reasoning variant rides the slug as a `#` suffix. Seat chains already pin these same models as their heads, so the seat swap changes nothing about which model leads each role. Upstream's speed modes are dropped. A re-port re-applies this mapping; `pstack-update` step 6 greps for the retired slugs.

## Install

```sh
# skills
ln -s "$PWD/skills/<name>" ~/.config/opencode/skills/<name>   # for each dir under skills/

# agents
ln -s "$PWD/agents/poteto-agent.md" ~/.config/opencode/agent/poteto-agent.md
ln -s "$PWD/agents/comment-sicko.md" ~/.config/opencode/agent/comment-sicko.md

# slash commands (one per user-invocable skill)
ln -s "$PWD/commands/<name>.md" ~/.config/opencode/command/<name>.md   # for each file under commands/
```

## Not ported

- `automations/benny/` (Cursor cloud-automation workflows)
- `docs/guide/` (Cursor-oriented walkthrough)
- `.cursor-plugin/`, plugin manifest, upstream README

These rely on Cursor-plugin infrastructure that has no OpenCode equivalent; port on demand.
