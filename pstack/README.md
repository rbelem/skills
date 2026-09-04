# pstack (OpenCode port)

Port of the **pstack** Cursor plugin by Lauren Tan ([poteto](https://github.com/poteto)) — source: <https://github.com/cursor/plugins/tree/main/pstack>, v0.14.8, MIT (see `LICENSE.upstream`).

This port targets **OpenCode**. Skill bodies are otherwise verbatim upstream prose with the mechanical substitutions below.

## Substitutions applied

| Upstream (Cursor) | Here (OpenCode) |
|---|---|
| the `Ask…Question` tool (one token upstream) | `question` tool |
| Cursor rules file `pstack-models.md` (Cursor user config `rules` dir) | `~/.config/opencode/pstack-models.md` |
| Cursor skills paths (user-level `~/…cursor…/skills`, workspace `.cursor`-relative) | `~/.config/opencode/skills/` / `.opencode/skills/` |
| "background agent" | "background agent" |
| `general` subagent type | `general` |
| `deslop` skill from `cursor-team-kit` | `stop-slop` skill (`/stop-slop`) |
| direct CLI runs (CLI/TUI verification) | direct CLI runs |
| the `agent-browser` skill / "control skill" (UI verification) | the `agent-browser` skill |
| the `write-a-skill` skill | the `write-a-skill` skill |
| `agent-transcripts/` directory | session transcript store (`opencode` sessions; query via `opencode` session commands, not the filesystem) |
| Leftover Cursor config paths and "Cursor" product references | adapted to OpenCode equivalents |

`skills/unslop/SKILL.md` additionally carries `metadata: opencode/autoinvoke: "true"`.

## Install

```sh
# skills
ln -s "$PWD/skills/<name>" ~/.config/opencode/skills/<name>   # for each dir under skills/

# agents
ln -s "$PWD/agents/poteto-agent.md" ~/.config/opencode/agent/poteto-agent.md
ln -s "$PWD/agents/comment-sicko.md" ~/.config/opencode/agent/comment-sicko.md
```

## Not ported

- `automations/benny/` (Cursor cloud-automation workflows)
- `docs/guide/` (Cursor-oriented walkthrough)
- `.cursor-plugin/`, plugin manifest, upstream README

These rely on Cursor-plugin infrastructure that has no OpenCode equivalent; port on demand.
