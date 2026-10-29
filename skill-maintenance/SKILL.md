---
name: skill-maintenance
description: Maintain, update, and clean up installed OpenCode skills across the three skill homes on this box — ~/.agents/skills/ (skills CLI), ~/.config/opencode/skills/ (opencode + plugin-synced), and ~/.autolearn/personas/default/skills/ (our own local copies). Use when users want to update skills, check for updates, remove duplicates, audit the skill inventory, find a skill to install, scan skills for security, or resolve stale or manually-installed skill folders.
---

# Skill Maintenance

This skill covers how to update, audit, install, and remove skills in the skill
systems on this OpenCode setup.

There are three homes, plus one authoring source. Do not confuse them:

| Home | Path | Manager | Update path |
|---|---|---|---|
| 1. CLI-managed | `~/.agents/skills/` | `skills` CLI (v1.7.4) | `skills update --global --yes` |
| 2. OpenCode-local | `~/.config/opencode/skills/` | hand-installed + opencode plugin discovery | per skill, by hand |
| 3. Persona copies | `~/.autolearn/personas/default/skills/` | autolearn persona sync | per skill, by hand |
| Authoring source | `~/Workspace/github.com/rbelem/skills/` | git repo | commit + push, then install from GitHub |

## Home 1: `~/.agents/skills/`

Managed by the `skills` CLI.

### Lock file

```text
~/.agents/.skill-lock.json
```

Currently **165 skills from 32 GitHub sources**. Read the counts from the lock
rather than trusting this sentence — the file is the authority:

```bash
python3 -c "
import json, collections
d = json.load(open('/home/rodrigo/.agents/.skill-lock.json'))['skills']
c = collections.Counter(v.get('source') for v in d.values())
print(len(d), 'skills,', len(c), 'sources')
"
```

Each entry contains `source`, `sourceType`, `sourceUrl`, `skillPath`,
`skillFolderHash`, `installedAt`, `updatedAt`.

### Commands

Install skill(s) globally from a GitHub repo:

```bash
skills add <github-repo> -g
```

Install all skills for all agents without prompting:

```bash
skills add <github-repo> -g --skill '*' --agent '*' -y
```

List available skills in a repo before installing:

```bash
skills add <github-repo> -l
```

Update all global skills to their latest upstream versions:

```bash
skills update --global --yes
```

Without `--yes`, the command prompts for scope.

Two silent no-ops to rule out before believing an update ran (v1.7.4):

- **`--agent` is not an update flag.** `skills update` takes only
  `-g`/`-p`/`-y`; `skills update -g --agent opencode` swallows `--agent` and
  reads `opencode` as a *skill-name filter*, then prints
  `No installed skills found matching: opencode` and exits 0 having done
  nothing. Use `skills update -g -y`.
- **`XDG_STATE_HOME` moves the lock.** The CLI resolves its lock as
  `$XDG_STATE_HOME/skills/.skill-lock.json`, else `~/.agents/.skill-lock.json`,
  and treats a missing file or one below lock version 3 as empty. This
  environment exports `XDG_STATE_HOME=~/.local/state`, so a plain
  `skills update -g -y` reports `No global skills tracked in lock file` while
  the managed lock at `~/.agents/.skill-lock.json` holds the real entries.
  Run `env -u XDG_STATE_HOME skills update -g -y` (and the same for
  `skills add`), or the CLI writes a second, stale lock into
  `~/.local/state/skills/`.

Known failure mode (skills CLI v1.6.x): the bulk update can report
`✗ Failed to update <name>` for every entry it finds. Its apply phase
re-clones with shallow discovery and misses skills stored below the repo
root. Fall back to one `skills add` per source, naming the skills
explicitly:

```bash
skills add <github-repo>.git --skill <name> <name2> --full-depth -g -y < /dev/null
```

Redirect stdin so the CLI's prompt machinery cannot consume the next
command in a list. A non-zero exit citing `PromptScript: PromptScript does
not support global skill installation` is a per-agent-target limitation,
not a copy failure. Trust the `✓ <name> (copied)` line, then verify the
folder mtime and the lock file's `updatedAt`.

Remove a global skill:

```bash
skills remove <name> -g
```

Remove all global skills without prompting:

```bash
skills remove <name> -g --skill '*' --agent '*' -y
```

List installed global skills with paths, scopes, and target agents:

```bash
skills list --global --json
```

### Finding a skill to install

Do not hunt GitHub, npm, and the web for a skill. Two lookups cover it:

```bash
# Interactive search across the published registry
skills find <query>

# One-shot JSON list of every published skill matching the query
curl -s -o /tmp/skills-search.json "https://skills.sh/api/search?q=<query>"
python3 -c "import json; [print(s['id'], s.get('installs')) for s in json.load(open('/tmp/skills-search.json'))['skills']]"
```

`skills find` prints the top hits with install counts; the skills.sh API
returns the whole match set with the same counts. Both name the
`owner/repo` to pass to `skills add`. A skill is usually already published
— `skills find webmcp` returned 100+ candidates, far more than any search
engine surfaced.

### Untracked entries

Skills physically present in `~/.agents/skills/` but not listed in
`~/.agents/.skill-lock.json` were installed manually, not via `skills add`.
`skills update` will not touch them. Two shapes exist here:

- **Symlinks into the persona home** (42 entries):
  `~/.agents/skills/<name> -> ~/.autolearn/personas/default/skills/<name>`.
  These are our own local skills. The persona home is a copy, not the
  source — edit `~/Workspace/github.com/rbelem/skills/<name>/` and keep the
  copy in step.
- **Symlinks into the workspace repo** (e.g. `webmcp`):
  `~/.agents/skills/<name> -> ~/Workspace/github.com/rbelem/skills/<name>`.
  Live edits, no copy step.

Check for breakage with `find ~/.agents/skills -maxdepth 1 -xtype l` — a
dangling symlink silently removes the skill from the agent's context.

## Home 2: `~/.config/opencode/skills/`

Not a lock-managed system. It holds skills opencode discovers by directory,
plus symlinks into the workspace repo. Current contents:

| Entry | Kind |
|---|---|
| `cua-driver`, `graphify` | plain directories, installed by hand |
| `benchmark-model-preset` | symlink into `~/Workspace/github.com/rbelem/skills/` |

The `oh-my-opencode-slim` plugin used to keep a manifest here at
`~/.config/opencode/.oh-my-opencode-slim/skills-manifest.json`. That
directory no longer exists and the plugin no longer syncs skills into this
folder — do not look for a manifest, and do not describe one in a report.
The plugin's own skills (`simplify`, `codemap`, `clonedeps`, `deepwork`,
`reflect`, `oh-my-opencode-slim`, `release-smoke-test`, `worktrees`,
`benchmark-model-preset`, `graphify`, `loop-engineering`) are documented by
the `oh-my-opencode-slim` skill, not here.

## Home 3: `~/.autolearn/personas/default/skills/`

Copies of our own local-only skills, kept in sync with the workspace repo
by the autolearn persona. Not in the lock, never touched by the `skills`
CLI. Editing a skill here edits the copy; the source of truth is
`~/Workspace/github.com/rbelem/skills/<name>/`.

Our published skills (the 60 the lock attributes to `rbelem/skills`) install
from GitHub instead, so a published skill has two copies on this box:
the git checkout and the CLI-installed copy under `~/.agents/skills/`.
Edit the checkout, then refresh the installed copy:

```bash
skills add rbelem/skills --skill <name> -g --full-depth -y < /dev/null
```

## Publishing our own skills

1. Author in `~/Workspace/github.com/rbelem/skills/<name>/SKILL.md`.
2. Commit and push.
3. Install for this box: `skills add rbelem/skills --skill <name> -g --full-depth -y < /dev/null`.

Until a local-only skill is committed, it exists only in this checkout. A
`git clean -fd` in the repo deletes untracked skill directories — check
`git status` before cleaning anything.

## Security scan (skillspector)

Every skill runs with the agent's full permissions. NVIDIA's
[SkillSpector](https://github.com/NVIDIA/SkillSpector) scans a skill for
prompt injection, data exfiltration, privilege escalation, supply chain and
rogue-agent patterns.

```bash
skillspector scan ./some-skill --no-llm          # static analysis
skillspector scan ./some-skill --no-llm --format sarif --output report.sarif
skillspector baseline ./some-skill -o .skillspector-baseline.yaml   # accept current findings
```

`--no-llm` keeps the scan static and offline. The binary comes from
devbox-global (`devbox.d/skillspector`); inside the devbox shell, run it as
`skillspector`. Outside one, the uv tool copy at `~/.local/bin/skillspector`
needs a clean `PYTHONPATH`:

```bash
env -u PYTHONPATH -u PYTHONHOME ~/.local/bin/skillspector scan ./some-skill --no-llm
```

The `rbelem/skills` repo runs it as a pre-commit hook and a CI job — see
`.githooks/pre-commit` and `.github/workflows/skillspector.yml`. A finding
there is a real signal, not noise: read the finding, fix the skill.

## Skill-to-Agent Assignment

Agent skill assignments live in:

```text
~/.config/opencode/oh-my-opencode-slim.jsonc
```

The active preset's agent blocks define which skills each agent can use.

Syntax:

- `["*"]` — all skills
- `["simplify", "code-review"]` — explicit allow list
- `["*", "!find-skills"]` — all skills except the excluded ones

Before removing a skill, always check `oh-my-opencode-slim.jsonc` for references. If a skill name appears in an agent's `"skills"` array, deleting the skill folder will break that agent. Update the config first to remove the reference, then delete the folder.

Example: `diagnose` was referenced in the `oracle` agent's skills list. Before deleting the `diagnose/` folder, the config was updated to reference `diagnosing-bugs` (the upstream-canonical name) instead.

## Duplicate Detection and Removal Workflow

1. **List all installed skills**
   - Home 1: `skills list --global --json`
   - Home 2: `ls ~/.config/opencode/skills/`
   - Home 3: `ls ~/.autolearn/personas/default/skills/`

2. **Check lock file coverage**
   - Compare installed folder names in `~/.agents/skills/` against keys in `~/.agents/.skill-lock.json`.
   - Anything installed but not in the lock file was installed manually and will not auto-update.

3. **Identify duplicates**
   - Group skills by semantic overlap, for example `review` vs `code-review`, `compress` vs `caveman-compress`, `diagnose` vs `diagnosing-bugs`.
   - Check the `description` field in each `SKILL.md` frontmatter. Identical or near-identical descriptions signal duplicates.

4. **Verify upstream**
   - Before removing, confirm which name exists upstream.
   - Use the GitHub API (unauthenticated, public repos):

     ```bash
     curl -s -o /tmp/repo-contents.json "https://api.github.com/repos/<owner>/<repo>/contents/<path>"
     python3 -c "import json; [print(x['name']) for x in json.load(open('/tmp/repo-contents.json')) if x['type']=='dir']"
     ```

   - Keep the name that exists upstream; the other is a stale local copy.

5. **Check config references**
   - Search the skill name in `~/.config/opencode/oh-my-opencode-slim.jsonc`.
   - If referenced, update the config to use the canonical name before deleting the folder.

6. **Remove the stale copy**
   - For manually installed skills: `rm -rf ~/.agents/skills/<stale-name>`
   - For lock-file-tracked skills: `skills remove <stale-name> -g`

7. **Verify**
   - Confirm the canonical version still exists and the stale one is gone.

## Key Files Reference

| Path | Purpose |
|---|---|
| `~/.agents/skills/` | Global skills (Home 1, `skills` CLI) |
| `~/.agents/.skill-lock.json` | Lock file tracking Home 1 skills (165 skills, 32 sources) |
| `~/.config/opencode/skills/` | Home 2 — opencode-discovered skills plus workspace symlinks |
| `~/.autolearn/personas/default/skills/` | Home 3 — persona copies of our local skills |
| `~/Workspace/github.com/rbelem/skills/` | Authoring source (git) for our own skills |
| `~/.config/opencode/oh-my-opencode-slim.jsonc` | Plugin config: presets, agent models, skill/MCP assignments |
| `~/.config/opencode/opencode.jsonc` | OpenCode core config: plugins, providers, MCP servers |
| `~/.config/opencode/AGENTS.md` | Global steering rules |
| `~/.config/opencode/docs/` | Topic docs (`web-wigolo.md`, `web-webmcp.md`, `session-transcripts.md`) |

## When to Use This Skill

Use this skill when the user asks to:

- update skills
- check for skill updates
- remove or clean up skills
- find or install a skill
- scan skills for security
- find duplicate skills
- check which skills need removal
- maintain or manage installed skills
- audit the skill inventory

Do NOT use this skill for:

- Writing new skills (use the `write-a-skill` skill instead)
- Configuring agent models or MCPs (use the `oh-my-opencode-slim` skill instead)
- Creating custom agents (use the `oh-my-opencode-slim` skill instead)

## Safety Rules

1. **Never delete a skill referenced in `oh-my-opencode-slim.jsonc` without updating the config first.**
2. **Always verify upstream before removing a "duplicate."** The locally older name might be canonical if the upstream repo renamed.
3. **Do not touch `~/.config/opencode/skills/` blindly.** Entries there are either hand-installed or symlinks into the workspace repo — check the link target before replacing one.
4. **Check all three homes before reporting a skill as "missing" or "orphaned."** A skill may exist in one home but not the others.
5. **Restart OpenCode after config changes** for them to take effect.
