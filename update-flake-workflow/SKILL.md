---
name: update-flake-workflow
description: |
  Step-by-step procedure for bumping nix flake package versions in devbox-global's devbox.d/<name>/flake.nix files. Covers: running 'devbox global run update-flake' to detect available updates, categorizing updates by hash type (simple fetchurl hash, srcHash+nodeModulesHash, npmDepsHash, fetchPnpmDeps hash), the fakeHash → build → capture-real-hash → paste loop, and updating version strings + URLs. Use when the user asks to 'update the nix flakes' or 'update flake packages' in devbox-global.
created_by: autolearn
created_at: "2026-07-13"
---

# Update Flake Workflow

Step-by-step procedure for bumping nix flake package versions in devbox-global's devbox.d/<name>/flake.nix files. Covers: running 'devbox global run update-flake' to detect available updates, categorizing updates by hash type (simple fetchurl hash, srcHash+nodeModulesHash, npmDepsHash, fetchPnpmDeps hash), the fakeHash → build → capture-real-hash → paste loop, and updating version strings + URLs. Use when the user asks to 'update the nix flakes' or 'update flake packages' in devbox-global.

## Instructions

- See the full procedure in the body section below. The workflow has 5 steps: detect updates → categorize by hash type → bump versions + set fakeHash → build + capture hashes → sync + commit.
## body

- ## When to use

User asks to "update the nix flakes", "update flake packages", or
"bump flake versions" in devbox-global. This skill covers the full
procedure from detecting available updates to committing the bumps.

## Prerequisites

1. **gh must be authenticated.** Run `gh auth status` first. If not
   logged in, `gh auth login` — the update-flake script silently
   swallows auth errors via `2>/dev/null || true`, making ALL packages
   show "unknown". (See memory: gh-silent-failure-debug skill.)
2. **Sync repo to global.** Run `devbox global run config-sync -- --sync`
   if the repo has uncommitted changes from a prior session.

- 3. **Flag interception by devbox.** When invoking scripts via `devbox global run <script> -u ...` or `--flag ...`, devbox's cobra parser CONSUMES the flag before it reaches the script. Observed: `devbox global run update-flake -u agent-browser` fails with `unknown shorthand flag: u in -u`. The same interception happens with `-a` (shorthand for `--all`): `devbox global run update-flake -a` fails identically because devbox swallows `-a` before the script sees it. WORKAROUNDS, in order of preference: (a) use positional args where the script accepts them — `devbox global run update-flake agent-browser` (no flag, list packages positionally); (b) use `--` separator to bypass devbox's parser — `devbox global run update-flake -- -a` (corrects the long-standing incorrect claim that '-a shorthand works' — it does NOT, both `-u` and `-a` are intercepted); (c) bypass devbox entirely — `$(devbox global path)/bin/update-flake -a`. See memory #23 (CLI flag workarounds: always verify they actually work before committing to docs) and #100/#121.
## Step 1: Detect available updates

```bash
devbox global run update-flake
```

This parses each `devbox.d/<name>/flake.nix` for the version string +
GitHub source, queries `gh api` for the latest release, and prints a
color table showing Installed vs Latest. Packages with updates show
a version delta.

**If all packages show "unknown":** gh is not authenticated (NOT a
PATH issue — see gh-silent-failure-debug skill). Run `gh auth status`
to confirm, `gh auth login` to fix.

### What "latest" means (the release line)

A flake tracks one *line* of upstream versions: a tag prefix plus a major
version (`v` + `0` for `bsk` is `cli-v` + `0`, `v` + `2026` for
`hermes-agent`). The newest version in the line is the newest **release**
in it — a release published *before* the installed version does not count
(`microsoft/playwright-cli` carries playwright's own releases next to the
CLI's, and the older one sorts higher by semver) — plus the **tags**
inside the series of those releases, when a tag is newer than what we have
(`zvec-ai/zvec-grep` tags v0.2.2 but only released v0.2.0). A flake that
downloads a release asset cannot use a tag without a release: there is no
asset to download.

A version counts as a pre-release when its own name says so (`-rc.2`,
`-alpha.1`) or when the release object is flagged as one; the name wins.

Two kinds of flake are reported but never updated automatically, because
bumping the version alone would leave the flake claiming a version its
source does not have:

| Reported as | Why |
|---|---|
| `?? (sha-pinned)` | the source is pinned to a commit SHA (deepseek-harness) |
| `?? (dynamic-version)` | the version attribute is interpolated (skillranker) |

A flake whose package is not enabled in `devbox.json` is skipped outright:
the script lists it under "not enabled in devbox.json (skipped)" and never
looks at it. A commented-out entry counts as disabled, so turning a package
off takes it out of the sweep — and out of the contract, which then needs
the row dropped from `tests/detection/expected.tsv` and the name added to
`tests/detection/expected-skipped.txt`.

The rules live in `devbox-global/tests/detection/README.md`, and the table
the script prints is pinned by a contract in
`devbox-global/tests/detection/expected.tsv` — check it after a bump:

```bash
bash devbox-global/tests/run-checks.sh   # every check, offline
```

## Step 2: Categorize updates by hash type

Read each `devbox.d/<name>/flake.nix` to determine which hashes need
recalculation. Three categories:

### Category A: Simple fetchurl hash (binary-release packages)

Packages using `pkgs.fetchurl` to download a prebuilt binary
(e.g. open-code-review, agent-browser, herdr, strix, hunk).

- Bump: version string + release URL (version in the URL path)
- Hash to update: the `sha256` in the `systemToHash` map or the
  single `sha256` arg to fetchurl
- Pattern: see devbox-binary-flake skill for the flake structure

### Category B: Source override with multiple hashes (npm/pnpm packages)

Packages using `fetchFromGitHub` + `buildNpmPackage`/`buildPnpmPackage`
or `fetchPnpmDeps` (e.g. opencode, skills, omniroute, codegraph,
graphify).

- Bump: version string in the `inputs.<name>.url` or the `version`
  attribute in the derivation
- May need to update the GitHub source URL ref (e.g. `ref =
  "v1.17.19"`)
- Hashes to update: `srcHash` (sha256 of the fetched tarball),
  `nodeModulesHash` / `npmDepsHash` / `npmDistHash` / `fetchPnpmDeps`
  hash — depends on which the flake uses

- **Python package bumps: audit propagatedBuildInputs for new runtime deps.** When bumping a Python package (`buildPythonApplication` or any `buildPythonPackage` flake), upstream may have added NEW runtime dependencies between versions (typical for LLM-tooling packages adding optional providers — e.g. skillspector 2.9.4 → 2.9.5 added langchain-anthropic). The build succeeds because deps are LAZY-imported at runtime, not at build time, so the missing dep surfaces only on first CLI invocation as `ModuleNotFoundError: No module named '<X>'`. PRE-BUMP CHECK: (1) fetch upstream `pyproject.toml` or `setup.py` for the new version (curl the release tarball, untar, grep `[project.dependencies]` / `[tool.poetry.dependencies]` / `install_requires`), (2) diff against the prior version's deps list, (3) any new dep → add `python3Packages.<dep-name>` (hyphenated in nixpkgs) to `propagatedBuildInputs` BEFORE bumping the version, (4) build + invoke the CLI + verify the previously-failing import now resolves. Do NOT trust that a clean build = a working package — for Python flakes, the import-time dep check is mandatory. nixpkgs has most langchain-* and openai-* providers as `python3Packages.<name>`; if a needed dep is missing from nixpkgs, fall back to `buildPythonPackage { ... propagatedBuildInputs = [ (python3Packages.buildPythonPackage { ... }) ]; }` or vendor it. Observed 2026-08-17 devbox-global skillspector 2.9.4→2.9.5 bump; observed 2026-10-13 graphify 0.9.76→0.9.88 (added rapidfuzz + tree-sitter floor bump).

## Step 3: Bump version strings + set fakeHash

For each package, edit `devbox.d/<name>/flake.nix`:

1. Change the version string (e.g. `"1.7.7"` → `"1.7.8"`)
2. Update any URLs that embed the version (e.g. GitHub release tarball
   URL: `.../releases/download/v1.7.8/...`)
3. For npm/pnpm packages, update the `ref` in the GitHub fetch URL if
   it pins a tag
4. Replace ALL hash values that need recalculation with `lib.fakeHash`
   (or `lib.fakeSha256`)

**fakeHash value:** `sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=`

This is the standard Nix trick: set a known-fake hash, attempt the
build, nix reports the real hash in the error message, paste it back.

Batch all version bumps + fakeHash replacements in parallel — they
are independent files.

## Step 4: Build → capture real hashes → paste back

```bash
devbox global install
```

The build will fail with a hash mismatch error for each fakeHash. The
error message contains the **correct hash**:

```
specified: sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
specified: sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
got:       sha256-<REAL_HASH_HERE>
```

**`update-flake` automates this loop.** When you bump a package via
`update-flake -u <pkg>` or `update-flake --all`, the script's
`resolve_hashes()` function does the build→capture→paste→rebuild
cycle automatically (max 10 attempts per package) before exiting.
You only need the manual workflow below when:

- The script's auto-resolution hits max retries (rare; usually
  transient — `nix store gc` and retry)
- You're debugging a specific hash mismatch
- You're not using `update-flake` and edited `flake.nix` by hand

**Iterative process (manual fallback):**
1. Read the error output, extract the `got:` hash
2. Paste it into the corresponding flake.nix (replace the fakeHash)
3. Re-run `devbox global install`
4. Repeat until all hashes are resolved

**Multiple packages failing at once:** If several packages have
fakeHash, the build stops at the first failure. Fix that one, re-run,
fix the next, etc. This is sequential by nature — cannot parallelize
hash capture.

**Multi-arch norm:** hash verification on the x86_64 builder resolves
only x86_64 entries; other-arch `systemToHash` entries remaining
`fakeHash` is the accepted norm, not a defect.

**Alternative for individual packages:**
```bash
nix build ./devbox.d/<name>#<name> 2>&1 | grep "got:"
```
This builds a single package and shows the hash mismatch, allowing
faster iteration per-package. **NOTE:** use the path-prefix form
(`./devbox.d/<name>#<name>` or `path:./devbox.d/<name>#<name>`), NOT
the bare `.#<name>` form — dcg (destructive_command_guard) blocks
`nix build .#<attr>` patterns in devbox-global. The devbox-global
repo root has no flake.nix, so the path-prefix form is also the
correct invocation for any local flake build verification.

## Decision: edit-in-repo vs edit-via-script

`update-flake` edits `$(devbox global path)/devbox.d/<name>/flake.nix`
**directly** (line 58: `DEVBOX_D="$DEVBOX_GLOBAL_PATH/devbox.d"`).
Manual edits to the repo are ALSO valid — but the two paths
require different downstream actions:

| Edit path                   | Then run                                                                                   |
|-----------------------------|--------------------------------------------------------------------------------------------|
| `update-flake -u <pkg>`     | `config-sync --reverse --sync` to pull changes back to repo, then commit                  |
| Manually editing repo flake | `config-sync -- --sync` to push changes to global, then `devbox global install` to verify |
| `update-flake --all`        | `config-sync --reverse --sync` to pull everything back, then commit                       |

**Do not mix the two paths in the same workflow** — see Step 5 mandatory order.

**Lock refresh note for input changes:** in the flake
dir run `nix flake lock --update-input <repo>-src`, then verify with
`nix build path:./devbox.d/<repo>#<repo>`. **NOTE:** the path-prefix
form is REQUIRED in devbox-global because (a) the repo root has no
flake.nix — every flake is in devbox.d/<repo>/flake.nix, AND (b) dcg
blocks the bare `nix build .#<repo>` pattern. Skip this verification if
you can rely on `devbox global install` to surface the build error.

## Step 5: Sync + commit

**MANDATORY ORDER — pull back before pushing forward.** `update-flake -u`
edits `$(devbox global path)/devbox.d/<name>/flake.nix` (global side).
Any later `config-sync -- --sync` pushes the WHOLE devbox.d tree
repo→global and silently CLOBBERS those bumps with the stale repo
copies (observed twice: 2026-08-27 dcg + open-code-review, 2026-08-28
dcg + open-code-review — re-running update-flake each time). So:

```bash
# 1. FIRST: pull update-flake's global bumps back into the repo
devbox global run config-sync -- --reverse --sync

# 2. THEN: push your own manual repo edits (opencode-v2, forks, etc.)
#    to global — safe now, repo == global for update-flake's files
devbox global run config-sync -- --sync

# Stage ONLY the flake files that changed (NOT devbox.lock unless
# explicitly updating lock files — see note below)
git add devbox.d/*/flake.nix devbox.d/*/flake.lock devbox.json

# Verify the diff
git diff --cached

# Commit with conventional commit style
git commit -m "chore(flakes): bump <list of packages>"
```

If you forward-synced first and clobbered the bumps (symptom: package
still shows old version after install; global flake.nix has old
version string), recovery = re-run `bin/update-flake -u <pkgs>`, then
`--reverse --sync` immediately.

**Lock files:** `devbox global install` (or `shellenv --recompute`)
updates `flake.lock` files. Commit these alongside the version bumps
— they pin the resolved input revisions. Stage them with the
flake.nix files.

**Surgical staging:** never `git add -A` or `git add .` — the repo
has many generated/lock files. Stage only the specific flake files
that were bumped.

## Quick reference: hash fields by package (fields, not versions - the versions move)

| Package | Hash fields to update |
|---|---|
| graphify | SPECIAL input-only (buildPythonApplication, src via `graphify-src` input tag `v${ver}`) — bump version + input tag, `nix flake lock --update-input graphify-src`, NO fakeHash |
| rtk | B/Rust dual-hash: `hash` (src) + `cargoHash`, rev `v${version}` |
| impeccable | B/npm: fetchFromGitHub `hash` (rev `cli-v${version}`, release-prefix `cli-v`) + `fetchNpmDeps hash`; the vendored package-lock.json must follow upstream's bun.lock (see the flake's comment) or `npm ci` refuses to install |
| herdr, pi, firecrawl, bsk, hunk, open-code-review, dcg, agent-browser, strix | A/fetchurl `systemToHash` (or `perArchSha256`); the map is outside pkgs scope so use a literal SRI string, NOT `pkgs.lib.fakeHash` |
| steel-takeoff (ezdwg) | SPECIAL input-only + cargo: bump `ezdwg-src` input tag + ezdwg `version`, fakeHash `fetchCargoVendor hash`, `nix flake lock --update-input ezdwg-src`; steelpy untouched |
| cua, cua-driver | A/fetchurl: a single `hash` for the linux-x64 asset |
| deepseek-harness | HELD - the source is pinned to a commit SHA, not a tag. Resolve the SHA for the target release before bumping; dual-hash `srcHash` + `pnpmDepsHash` |

**The multi-architecture hashes do not need a download.** Every binary flake
sets `dontUnpack = true`, so its `fetchurl` hash is the flat sha256 of the
uploaded file - which the GitHub release API exposes as `assets[].digest`:

```bash
gh api "repos/<owner>/<repo>/releases/tags/<tag>" \
  --jq '.assets[] | "\(.name) \(.digest)"'
# sha256:<hex> -> SRI:  nix hash to-sri --type sha256 <hex>
```

The method reproduces the hashes already in the repo (checked against bsk and
hunk), so it is the fast path for every multi-arch flake. The build loop is
still the fallback for a fetcher whose hash is not the flat file hash (a
fetchPnpmDeps / fetchNpmDeps / fetchCargoVendor hash covers the fetched
dependency set, not one file).

**bsk is no longer held.** It used to be flagged "HELD - update-flake may
report the ext-vX stream" because the detection took the first release it saw
in the repository. The detection now reads the release line from the flake's
own artifact (`cli-v`), so bsk reports the `cli-v` line and can be bumped
like any other binary flake.

- **graphify (as of 2026-10-13)**: `buildPythonApplication` Python package, source via flake input `graphify-src` (upstream `safishamsi/graphify` tag). NO flake-level hashes for graphify itself. Bumping graphify = (1) bump `version = "..."` string + input tag URL in `flake.nix`, (2) `nix flake lock --update-input graphify-src` in the devbox.d/graphify dir, (3) `nix build path:./devbox.d/graphify#graphify`. NO fakeHash dance — don't try to set fakeHash on graphify, there's nothing to fakeHash. Known packaging quirk fixed 2026-10-13: graphify re-execs `[sys.executable, "-m", "graphify"]` (PYTHONHASHSEED pinning), which drops the wrapper's site.addsitedir bootstrap — the flake carries `makeWrapperArgs` exporting PYTHONPATH so child interpreters resolve deps; if rebuilds fail with "No module named 'tree_sitter'", that arg was lost.

## Common pitfalls

1. **gh not authenticated → all "unknown"**: not a PATH issue. Run
   `gh auth status`.
2. **Not committing flake.lock**: lock files pin resolved revisions;
   commit them with the version bumps.
3. **`git add -A` sweeping unrelated files**: stage only the changed
   flake files surgically.
4. **Forward-syncing before reverse-syncing**: see Step 5 mandatory order
   (`--reverse --sync` FIRST, then `--sync`).
5. **fakeHash on packages with multiple hashes**: some packages have
   3+ hashes (e.g. omniroute: srcHash + npmDepsHash + npmDistHash).
   Set ALL of them to fakeHash — the build will fail on each
   sequentially.
## CRITICAL: Sync before install (most-missed step)

`devbox global install` reads from `$(devbox global path)`, NOT from the repo.
If you edit `devbox.d/<name>/flake.nix` in the repo but DON'T sync first:

- `devbox global install` silently uses the OLD cached flakes
- It reports SUCCESS (no hash mismatch errors)
- No packages are actually updated
- Installed versions remain unchanged

**Correct ordering:**
1. Edit `devbox.d/<name>/flake.nix` in repo (version + fakeHash)
2. Sync repo → global: `devbox global run config-sync` (dry-run) → then `-- --sync`
3. NOW run `devbox global install` — it will hit the fakeHash and report real hashes

If `devbox global install` succeeds without any hash mismatch errors after
you set fakeHash, you forgot to sync. This is the #1 workflow gap.

## Diagnostic: unchanged hash between versions

When the build error shows:
```
specified: sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
got:       sha256-<SOME_HASH>
```
And `<SOME_HASH>` equals the ORIGINAL hash (before you replaced it with
fakeHash), the hash did NOT change between versions — the dependency tree
is identical. Restore the original hash and move on. This commonly happens
with `npmDepsHash` on minor bumps that don't change package-lock. `srcHash`
almost always changes; `npmDepsHash`/`npmDistHash` may not.

Do NOT paste the original hash back as if it were new — it's the same value
you started with. Just restore it and re-run to capture remaining hashes for
other packages.

## nix-store-cache-staleness

After replacing fakeHash with the correct hash AND re-syncing (config-sync --sync) to the global path, the build can STILL fail reporting the OLD fakeHash as 'specified:'. Three possible causes, check in order:

1. **SYNC didn't work** — verify by reading the global path file directly:
   ```bash
   cat "$(devbox global path)/devbox.d/<name>/flake.nix" | grep hash
   ```
   Confirm the new hash is actually there. If not, re-run config-sync --sync.

2. **NIX EVAL CACHE** — nix caches flake.nix evaluation results. Force re-evaluation:
   ```bash
   nix build --no-eval-cache .#<name>
   ```
   Or:
   ```bash
   nix path-info --derivation .#<name>
   ```

3. **NIX STORE FIXED-OUTPUT DERIVATION CACHE** — the old fakeHash derivation stays in /nix/store/ as a fixed-output derivation. Fixed-output derivations bake the hash into the derivation path (e.g. `sc2f4wqjnav3bfbbrcv53pl80acyyca0-source.drv`). The build error output shows the stale .drv path. Delete it:
   ```bash
   nix-store --delete /nix/store/<stale-hash>-source.drv
   ```
   Or clear all stale fixed-output derivations:
   ```bash
   nix-collect-garbage
   ```

**Multiple hash fields:** Flakes with multiple hash fields (srcHash + nodeModulesHash, srcHash + pnpmDepsHash, srcHash + npmDepsHash) must have EACH hash resolved sequentially — fixing srcHash doesn't resolve the others. Re-sync (config-sync --sync) after EACH hash fix before rebuilding.

## Stale derivation debugging

After replacing fakeHash with the correct hash AND syncing (config-sync --sync),
the build can STILL fail reporting the OLD fakeHash as 'specified:'. This means
a stale fixed-output derivation (.drv) is cached in /nix/store. Debug in order:

### 1. Verify sync worked
Read the global path file directly:
```bash
cat "/home/rodrigo/.local/share/devbox/global/default/devbox.d/<name>/flake.nix" | grep hash
```
Confirm the new hash is actually there. If not, re-run config-sync --sync.

### 2. Try --no-eval-cache (safe, no side effects)
```bash
nix build --no-eval-cache .#<name>
```
This bypasses the flake eval cache but may NOT clear stale fixed-output derivations.

### 3. Try deleting the stale .drv (may fail with referrers)
```bash
nix-store --delete /nix/store/<stale-hash>-source.drv
```
If it has referrers, this fails. Do NOT force-delete — referrers mean something
else depends on that path.

### 4. Last resort: update flake.lock (CAUTION — may break things)
```bash
nix flake lock --update-input nixpkgs
```
This forces nix to re-evaluate ALL derivations by changing the nixpkgs input.
**Risk:** brings LATEST nixpkgs which may break package compatibility:
- pnpm fetcherVersion 3 unsupported by newer nixpkgs pnpm (use fetcherVersion 4)
- Other API changes in buildNpmPackage/buildPnpmPackage

If --update-input nixpkgs breaks something, revert:
```bash
git checkout flake.lock
```
Then try updating only the specific input that the package depends on, or
manually update the lock file entry.

### 5. GC roots check
```bash
nix-store --query --roots /nix/store/<stale-hash>-source.drv
```
If GC roots exist, they may be from a devbox-managed profile. Running
'devbox global install' after the lock update should regenerate them.

## ## Multiple hashes: which .drv failed

- When a flake has MULTIPLE hashes (e.g. skills: fetchFromGitHub src hash + fetchPnpmDeps hash; opencode: srcHash + nodeModulesHash), the build error 'hash mismatch in fixed-output derivation \'/nix/store/<id>-<suffix>.drv\'' tells you WHICH hash to fix by the .drv suffix:\n\n- **'-source.drv'** suffix → the fetchFromGitHub/fetchurl SRC hash (the 'src' attribute)\n- Other derivation names → other fetchers (fetchPnpmDeps, fetchNpmDeps, etc)\n\nThe 'specified:' value is what's currently in the flake.nix for THAT derivation only. The 'got:' value is the real hash for THAT derivation only. Do NOT confuse a 'got' hash with a hash from a different field in the same flake.\n\n### Shortcut: compute fetchFromGitHub src hash directly\n\nSkip the fakeHash → build → capture loop for src hashes:\n\n\n\nThis is faster for src hashes. pnpmDeps/npmDeps/nodeModules hashes still need the fakeHash build loop because they depend on the package-lock content.\n\n### Diagnostic: same hash for src and pnpmDeps\n\nIf 'nix-prefetch-url --unpack' returns the SAME hash that's already in the pnpmDeps field, the src hash and pnpmDeps hash are DIFFERENT things that happened to get the same value — unlikely but possible. More likely: you computed the src hash and confused it with the pnpmDeps hash. Check which .drv failed to know which field to update.

## Manual hash resolution for multi-platform binary-release flakes

- Manual hash resolution for multi-platform binary-release flakes

When `update-flake` reports 'max retries reached' on a binary-release flake (e.g. open-code-review, agent-browser, herdr, strix, hunk) AND the file has fakeHash on multiple system targets, the script's resolve_hashes() function has likely mis-pasted one or more hashes (captures first got: from build output and pastes into first fakeHash line in file — not necessarily matching systems). Verify by reading the file: if any systemToHash entry differs from the got: value shown in the build error, the script mis-pasted it.

**Manual fallback recipe:**

1. **Read the systemToTarget / systemToHash map** from `devbox.d/<name>/flake.nix`. Convention used by these flakes:
   - `x86_64-linux` maps to `linux-amd64` (release asset suffix)
   - `aarch64-linux` maps to `linux-arm64`
   - `x86_64-darwin` maps to `darwin-amd64`
   - `aarch64-darwin` maps to `darwin-arm64`

2. **Download each platform binary** from the upstream GitHub release page using curl -sL with the release asset URL pattern from the flake.nix fetchurl block.

3. **Compute SRI hash for each binary** (single command, returns sha256-... SRI format directly):
   ```
   nix hash file /tmp/<pkg>-linux-amd64
   nix hash file /tmp/<pkg>-linux-arm64
   nix hash file /tmp/<pkg>-darwin-amd64
   nix hash file /tmp/<pkg>-darwin-arm64
   ```

4. **Paste hashes in systemToHash map order** (matching the file's key order). Cross-reference with the build's got: values — if your computed hash differs from got:, your download URL is wrong (check asset name in upstream release).

5. **Verify with `devbox global install`** — should succeed without hash mismatch on the current host platform.

**Shortcut: SHA256SUMS file.** Some upstream repos ship `SHA256SUMS.txt` alongside the release assets (e.g. dcg). If present, `curl + awk` extracts all platform hashes in one shot — see devbox-binary-flake skill for the pattern.

**When to use manual path vs script auto-resolve:**
- Script succeeds (single-platform or all-platforms-on-host): use script output directly
- Script hits max-retries AND file has hashes that differ from build got: values: manual fallback required
- Cross-platform builds impossible (e.g. ARM/Darwin on Linux x86_64 host): manual fallback MANDATORY

## Hash attribute coverage gap (sed allowlist)

The sed at update-flake line 332-335 has a KNOWN COVERAGE GAP that affects real flakes:

```bash
# Line 332 — matches bare attrs ONLY for: hash, srcHash, cargoHash, npmDepsHash, nodeModulesHash, outputHash
sed -ri "s/((^|[[:space:]])(hash|srcHash|cargoHash|npmDepsHash|nodeModulesHash|outputHash)[[:space:]]*=[[:space:]]*)\"(sha256-[^\"]+)\"/\1\"fakeHash\";" "$flake_nix"
# Line 335 — catches ANY quoted attr name (e.g. "x86_64-linux" = "sha256-...")
sed -ri "s/(\"[^\"]+\"[[:space:]]*=[[:space:]]*)\"(sha256-[^\"]+)\"/\1\"fakeHash\";/" "$flake_nix"
```

**What slips through:** compound bare attribute names that contain "hash" but are not in the alternation, e.g. `bunHash`, `iiiHashes`. They are NOT quoted either, so neither sed matches them.

**Real flake examples:**
- ~~`devbox.d/opencode/flake.nix` bunHash~~ OBSOLETE 2026-10-13: the opencode flake was rewritten for the v2 release line; bun now comes from the locked `opencode-bun` flake input (devbox.d/bun), so there is no bunHash field anymore. Hashes today: `srcHash` + `nodeModulesHash` only, both auto-resettable bare attrs.
- `devbox.d/agentmemory/flake.nix:31` — `iiiHashes = { "x86_64-linux" = "sha256-..."; ... };`. The OUTER `iiiHashes` attr name is NOT reset, but the INNER quoted platform hashes ARE reset by line 335 (because they match the quoted-attr pattern).

**Practical impact when bumping:**
- ~~opencode bunHash step~~ OBSOLETE 2026-10-13: no bunHash field exists anymore (bun comes from the locked opencode-bun flake input). opencode bumps: edit `version` + `rev` (v2.0.x tag), fakeHash `srcHash` + `nodeModulesHash`, build, paste. Note `releases/latest` upstream still serves the v1 line — check `v2*` tags instead.
- agentmemory: no action needed — inner platform hashes reset correctly; only the outer `iiiHashes` attr name stays (it does not need resetting — the inner values are what matter).

**If a new flake uses another compound bare hash attr name** (e.g. `cargoLockHash`, `nodeDepsHash`, `pnpmHash`), recognize the gap before running the script — manually set the value to `pkgs.lib.fakeHash` if the auto-reset is needed.

## Quick reference: hash field names by package (EXTENDED)

The sed allowlist covers bare `hash|srcHash|cargoHash|npmDepsHash|nodeModulesHash|outputHash` and any quoted attr. Compound bare names like `bunHash` and `iiiHashes` (outer) are NOT auto-reset by update-flake — see diagnostic above.

| Package | Hash fields |
|---|---|
| open-code-review | `sha256` in systemToHash map |
| agent-browser | `sha256` in systemToHash map |
| opencode | `srcHash`, `nodeModulesHash` |
| skills | `fetchPnpmDeps` hash |
| omniroute | `srcHash`, `npmDepsHash`, `npmDistHash` |
| codegraph | `npmDepsHash` |
| graphify | no flake-level hashes (Python build, source via flake input) |
| **agentmemory** | **`iiiHashes` (attr set of platform hashes)** — only inner quoted platform hashes auto-reset |
| docling | source URL version in `inputs.docling-src` |
| herdr, strix, hunk | `sha256` in systemToHash map |

- ## Script maintenance: FIXME residue cleanup architecture

The update-flake script's resolve_hashes() function uses a three-layer approach to clean up the \ audit comments it injects during the fakeHash reset step (lines 340-341) — those comments document the original hash but must not survive past successful resolution.

**Layer 1 — Inline strip at line 397:** during each successful build iteration, the same sed that replaces fakeHash with the real hash also strips the trailing FIXME comment, scoped via `sed -i -E -e "0,/\"\"/{s/;[[:space:]]*#[[:space:]]*FIXME:[[:space:]]*was[[:space:]]*\"sha256-[^\"]*\"//}"`. Single-line scope = first occurrence only.

**Layer 2 — Final cleanup pass at line 407:** at the end of resolve_hashes(), a global idempotent sed runs: `sed -i -E 's/;[[:space:]]*#[[:space:]]*FIXME:[[:space:]]*was[[:space:]]*\"[^\"]*\"//g' "" 2>/dev/null || true`. Catches residue from previous bumps where one platform's hash couldn't be resolved (e.g. multi-arch flakes built only on host arch).

**Layer 3 — Manual one-liner:** the exact same sed from Layer 2 can be run directly against any devbox.d/<name>/flake.nix as a maintenance one-liner, without invoking resolve_hashes. Useful when no update is available to trigger the script but stuck residue is observed from prior bumps.

**Diagnostic — find stuck residue:**
```bash
rtk grep -rn 'FIXME: was' devbox.d/
```
Anything listed is residue from a prior incomplete bump. Apply the Layer 3 one-liner per file (idempotent, safe to re-run).

**Why residue accumulates:** multi-arch binary-release flakes (herdr, strix, hunk, open-code-review, agent-browser) have systemToHash maps with 4 entries (x86_64-linux, aarch64-linux, x86_64-darwin, aarch64-darwin). On a single-arch host, the script resolves only one arch's hash and the other 3 stay as fakeHash forever (can't build aarch64/darwin on x86_64). When the user later edits the file (sync, manual edit, etc.) the leftover `# FIXME: was` comments become inline noise.

- TABLE CORRECTION 2026-07-27: open-code-review and codecanary use perArchSha256 (compound bare hash attr set) NOT systemToHash. The compound bare attr name slips through both seds (see Hash attribute coverage gap section above).
## Editing bin/update-flake itself

When modifying the script (e.g. adding new hash types to the sed allowlist, extending preflight checks, fixing PCRE portability):
1. Run `bash -n bin/update-flake` after each edit cluster to catch syntax errors early (stray fi from prior incomplete refactors is a common bug — the script uses nested if/else with multiple exit paths).
2. The script runs under `set -u` (line 60 declares colors BEFORE preflight for this reason). New local variables that may or may not be assigned in different code paths need \ defensive expansion when referenced after the conditional.
3. `grep -oP\ (POSIX ERE) for portability across the target systems.

## ## Auto-chained post-install

- ## Auto-chained post-install (added 2026-07-16)

`bin/update-flake` is wired to automatically invoke `bin/post-install` after a successful update. This is by design — the user wants post-install to ALWAYS follow any flake update attempt, so downstream artifacts (e.g. regenerated skill files for graphify) refresh without manual intervention.

**When it fires (gated by `[[ \${#TARGETS[@]} -gt 0 ]]` in update-flake):**

| Invocation                            | Post-install fires? |
|---------------------------------------|---------------------|
| `update-flake` (status only)          | no                  |
| `update-flake --help`                 | no                  |
| `update-flake --all` (no updates available) | no             |
| `update-flake --all` (updates applied) | yes                 |
| `update-flake graphify` (graphify has update) | yes        |
| `update-flake graphify` (already at latest)  | no         |

So the full chain after a successful script-driven bump becomes:
1. `update-flake -u <pkg>` (or `--all`)
2. Script resolves hashes inside `resolve_hashes()`
3. Script emits "All updates applied."
4. **Script calls `bin/post-install` automatically**
5. `post-install` runs any per-tool refresh hooks (graphify skill regen, etc.)

If post-install unexpectedly fires after an `update-flake` run, it was intentional — not a bug. If you need to silence it for testing, comment out the call in update-flake lines after "All updates applied.".

## Edit precision when bumping (single file, multiple attrs)

- ## Edit precision when bumping (single file, multiple attrs)

When bumping one `flake.nix` that has version + src + srcHash + npmDepsHash
attributes SPREAD across the file (not adjacent), do SEPARATE Edit calls
per attribute:

```bash
# Three independent edits, each anchored on ONE line + minimal context
edit(oldString='version = "0.9.15";', newString='version = "0.9.16";')
edit(oldString='srcHash = "sha256-OLD...";', newString='srcHash = lib.fakeHash;')
edit(oldString='npmDepsHash = "sha256-OLD...";', newString='npmDepsHash = lib.fakeHash;')
```

DO NOT try to replace a wide multi-line block containing all the attrs at
once — the Edit tool will collapse them and destroy adjacent lines (e.g.
the version line alone cannot replace 17 lines that include src, srcHash,
npmDepsHash).

**If the file gets destroyed anyway** (Edit reports success but read shows
wiped content), recover with `git checkout <file>` then re-apply the edits.
After checkout, RE-READ the file to confirm restore worked — initial reads
can show stale content; verify with `git status` that the file matches HEAD.

## Sed delimiter bug in bin/update-flake line 398

- 
## Bug: sed delimiter collision breaks hash replacement for hashes containing '/'

The auto-resolve loop in `bin/update-flake` (line 398) uses sed with `/` as both the address-range delimiter and the s-command delimiter:

```bash
sed -i -e "0,/\"${FAKE_HASH}\"/{s/\"${FAKE_HASH}\"/\"${got_hash}\"/}" "$flake_nix"
```

SRI hashes use base64 charset which includes `+/=`. **Most real hashes contain `/`**, which collides with sed's `/` delimiter and produces errors like:

```
sed: -e expression #1, char 17: unknown command: 'K'
```

(The `K` is downstream noise — the real cause is `/` in `${got_hash}` being eaten by sed.)

**Effect:** when the computed hash contains `/`, the sed paste-back FAILS silently. The file remains at `fakeHash` while the script happily continues iterating, capturing the same `got_hash` every time, eventually reporting "max retries reached" with the file still containing `fakeHash`.

**Diagnostic:** after `update-flake -u <pkg>` reports success or max-retries, verify the file was actually updated:

```bash
rtk grep fakeHash devbox.d/<pkg>/flake.nix
```

If any `fakeHash` lines remain, the sed bug ate the replacement.

**Workarounds (in preference order):**

1. **SHA256SUMS shortcut for binary releases** (jcode, dcg, etc.): fetch the upstream `SHA256SUMS` file, convert hex → SRI with `nix hash to-sri --type sha256 <hex>`, paste real hashes for all platforms directly. Skip the script. See `devbox-binary-flake` skill "SHA256SUMS shortcut" section.

2. **NPM registry pre-computation** (agentmemory, etc. using `pkgs.fetchurl` from `registry.npmjs.org`): compute `srcHash` directly with `nix-prefetch-url --unpack <url>` or `nix hash to-sri --type sha256 $(curl -sSL <url> | sha256sum | cut -d' ' -f1)`. Paste SRI directly. `npmDepsHash` / `nodeModulesHash` still needs the fakeHash loop (lockfile-dependent, no shortcut).

3. **Escape hatch — manual edit:** after the script captures `got_hash` from build output but the sed paste fails, manually `Edit` the `fakeHash` → `got_hash` line yourself. Avoids sed entirely.

4. **Permanent fix (script edit):** change both sed calls at line 398-399 to use `|` as delimiter: `sed -i -e "0,|\"${FAKE_HASH}\"|{s|\"${FAKE_HASH}\"|\"${got_hash}\"|}"`. Same for the FIXME-strip sed at line 399.

**Observed 2026-07-20:** jcode v0.53.0 build returned hash `sha256-YOG4/Kiw5SjGQF8FMLjjERJLtjTJ6famWILPxO2ftoA=` for linux-x86_64 — sed broke, all 4 systemToHash entries stuck at fakeHash. Resolved by fetching upstream SHA256SUMS and pasting all 4 hashes directly.

## Devbox CLI flag interception beyond --all

## Devbox CLI flag interception — known intercepted flags


- Both `--all` and `-a` are intercepted by devbox's cobra/pflag parser (verified 2026-07-22: `devbox global run update-flake -a` returns the same 'unknown flag' error as `--all`). The actual workaround is the `--` separator that tells devbox to pass everything after it to the script verbatim.

**Verified intercepted (2026-07-22):**
- `--all` → intercepted
- `-a` (shorthand for --all) → also intercepted
- `-u` (update-flake's 'update specific packages' flag) → intercepted

**Symptom (any of these = flag interception):**
```
Error: unknown shorthand flag: 'a' in -a
Error: unknown shorthand flag: 'u' in -u
Error: unknown flag: --all
```

**Workarounds for update-flake flag-passing failures (preference order):**

1. **Use `--` separator (universal fix for intercepted flags):** `devbox global run update-flake -- -a`, `devbox global run update-flake -- -u agent-browser` — passes everything after `--` to the script verbatim, bypasses devbox's flag parser. WORKS for any intercepted flag.

2. **Prefer positional args (cleanest path):** `devbox global run update-flake agent-browser`, `devbox global run update-flake hunk jcode` — passes pkg names positionally, no flag needed. Best when you only need to update specific packages.

3. **Bypass devbox entirely (escape hatch):** invoke script directly via `$(devbox global path)/bin/update-flake -a` or `$(devbox global path)/bin/update-flake -u agent-browser` — skips devbox's flag parser, full script flag set available. Use when positional args don't apply (e.g. the only entry point is a flag).

**Rule of thumb:** NEVER use `devbox global run update-flake -a` — it's intercepted. Either use positional args, the `--` separator, or invoke the script directly via `$(devbox global path)/bin/update-flake`. If you see 'unknown shorthand flag' or 'unknown flag' errors from any devbox script, the fix is `--` separator, not a different short flag.

**Generalize:** same flag interception pattern likely affects other devbox scripts (config-sync, secrets-setup, etc.). If `devbox global run <script> --<flag>` or `devbox global run <script> -<flag>` fails with 'unknown shorthand flag' or 'unknown flag', use `devbox global run <script> -- -<flag>` (with `--` separator) or positional args or direct script invocation via `$(devbox global path)/bin/<script>`. The `--` separator is the canonical fix; positional args are preferred when applicable; direct script invocation is the escape hatch when neither works.
## Sed delimiter collision (FIXED 2026-07-20, commit eac4c9b)

- **Status: FIXED.** Lines 398-399 of bin/update-flake now bash-escape forward slashes before passing hashes to sed. Fix replaces ${FAKE_HASH} with ${FAKE_HASH//\//\\/} and similarly for ${got_hash} in both lines. Bash parameter expansion ${var//\//\\/} substitutes every / with \/ so sed treats the literal slash as escaped, not as delimiter. Works for any base64 SRI hash (jcode v0.53.0 linux-x86_64 got 'sha256-YOG4/Kiw5SjGQF8FMLjjERJLtjTJ6famWILPxO2ftoA=' — sed no longer breaks on the embedded /). Diagnostic if regression hits: rtk grep fakeHash devbox.d/<pkg>/flake.nix after update-flake -u <pkg> — if fakeHash lines remain, the escape regressed. The four workarounds previously listed below (SHA256SUMS shortcut, npm pre-computation, manual edit, switch delimiter to |) are NO LONGER NEEDED for the slash-collision case. They may still apply to other hash-resolution problems (e.g. SHA256SUMS shortcut remains useful for multi-arch binary-release flakes), so retain the SHA256SUMS advice elsewhere in the skill. Historical: the original problem was sed with / as both address-range delimiter (0,/PATTERN/) and s-command delimiter (s/PATTERN/REPL/) — any / in got_hash ended the address or replacement prematurely, silently leaving fakeHash in place while the script reported success.

## Lock regen after flake inputs schema change

- After any change to a flake's inputs declaration (adding or removing an input, e.g. dropping a bun-src input after rewriting for canary), refresh the flake.lock before the next nix build. Symptom of stale lock: 'function outputs called with unexpected argument X' pointing at the outputs opening line — misread as syntax bug, actually a stale lock. Fix in the flake dir: nix flake update (refreshes all declared inputs) OR nix flake lock --update-input nixpkgs. Pairs with memory entry 'flake inputs schema change leads to outputs called with unexpected argument'.

## ## Running install session doesn't pick up synced hash fixes mid-build

- When 'devbox global install' is running in a tmux session and you fix hashes in devbox.d/*/flake.nix then run config-sync --sync, the sync works but the running install does NOT re-evaluate the per-flake lock files. Nix loads flake locks at build start; once a build is running, it has the OLD lock file for the lifetime of that process. SYMPTOM (observed 2026-07-21 devbox-global): install fails with the EXACT same specified hash mismatch you just fixed, even after config-sync --sync reports success. Sync worked, file contains new hash, but the running build does not see it. FIX: kill the current tmux session and start a NEW devbox global install so nix re-evaluates flake locks at startup. The new build will pick up all synced hash fixes in one pass. Generalizes to ANY long-running nix build, not just devbox install. Distinct from Memory 135/150 (post-build nix-store fixed-output cache) and the 'Lock regen after flake inputs schema change' section.

## ## Cross-flake hash grep diagnostic

- When devbox global install fails with a hash mismatch and the package in the derivation path does not match the obvious flake you expect, grep for the SPECIFIED hash across ALL devbox.d/*/flake.nix files. The first hit is the actual owner. Command: 'rtk grep -F <specified-hash> devbox.d/*/flake.nix'. WHY THIS HAPPENS (observed 2026-07-21 devbox-global): a single devbox global install invocation may build 10-20 paths at once. The error message names a derivation like 'c35k9zpqdhx5ndvgj4mypm37sh7m38hy-codegraph-1.4.1-perl.drv' but this is a SUB-derivation pulled in by one of the listed paths. The parent flake that owns the failing hash may be completely different (e.g. agentmemory). Sub-derivation names often include the upstream project name even when the failing hash lives in another flake that depends on it. DIAGNOSTIC: (1) Copy the specified hash from the build error, (2) Run rtk grep across all devbox.d/*/flake.nix, (3) First match = the actual flake to fix, (4) Update that flake hash, sync, restart install. Dont burn turns grepping the obvious package from the derivation name. When to apply: any time a hash mismatch error references a derivation path whose package name is ambiguous or different from the listed build paths.

## Display legend (status column)

- The status column in the update-flake table uses this legend (user-declared convention, 2026-07-21):

| Symbol | Color   | Meaning                                                              |
|--------|---------|----------------------------------------------------------------------|
| ✓      | green   | Up to date — installed == latest                                     |
| ↓      | red     | Installed is OLDER than latest → update available (triggers -u/-a)   |
| ↑      | yellow  | Installed is AHEAD of upstream (e.g. fork with custom version)       |
| ??     | yellow  | Unknown (gh not authenticated, no GitHub release, parse failure)     |

Arrow direction metaphor: ↓ = installed sits BELOW the available one (needs to come up); ↑ = installed sits ABOVE upstream (fork has bumped past). Do NOT swap or invent new glyphs without confirming with the user — this is a stable UI convention across the devbox-global toolchain.

## Comparison logic

Version comparison uses a  helper (semantic-version numeric compare), NOT string equality/inequality. Bash lex compare on semver strings gives wrong answers (e.g. "1.10.0" lex-greater than "1.2.3" but semantically newer, or "1.2.10" lex-less than "1.2.9" but semantically newer). The  function splits on '.' and compares component-by-component numerically. UPGRADABLE selection rule: a package is upgradable when  (latest is greater than installed). When the strings are equal, no update. When installed > latest, the fork-ahead symbol ↑ applies.

## Step 0: Preflight — dirty-state detection (BEFORE running update-flake)

Before invoking `update-flake`, the repo AND the global state must be
clean. Half-applied state from prior aborted sessions produces silent
"update succeeds but nothing actually changed" failures or halts the
script with conflicts the assistant must triangulate by hand.

### 0a. Local repo state — `git status`

```bash
git status --short
```

Categorize every reported path:

| Status | Meaning | Action |
|---|---|---|
| `M <file>` (unstaged) | prior in-progress edit, never committed | BLOCK — ask user to keep / discard / commit |
| `MM <file>` | staged + unstaged on same file (conflict-in-progress) | BLOCK — must resolve before update-flake |
| `A <file>` | newly staged (likely from prior `git add`) | BLOCK — likely partial commit |
| `<file>` untracked | new file not yet committed | usually OK (e.g. agent-reach/flake.lock after first add) |

**`MM` (mixed staged + unstaged) is the most dangerous case** —
signals an aborted prior session with conflicting edits. Example
observed 2026-07-21 in devbox-global: `devbox.d/skills/flake.nix`
had staged `pnpm_9 + fetcherVersion 4 + fakeHash` AND unstaged
`pnpm_10 + fetcherVersion 4 + real hash`. update-flake cannot decide
which to act on; it would touch the file but leave the contradictory
state in place.

### 0b. Repo vs global sync state

```bash
DEVBOX_GLOBAL="$(devbox global path)"
diff -qr devbox.d "$DEVBOX_GLOBAL/devbox.d" | head -50
diff -q devbox.json "$DEVBOX_GLOBAL/devbox.json"
```

If files diverge between repo and global, decide direction BEFORE
running update-flake (the script edits the GLOBAL files). Options:

- **Repo ahead of global** (uncommitted local edits): commit first,
  then `config-sync -- --sync` to push to global
- **Global ahead of repo** (script ran on a previous machine and
  never synced back): `config-sync --reverse --sync` to pull into
  repo, then commit
- **Both diverged** (conflict): BLOCK — config-sync will warn and
  refuse; resolve before proceeding

### 0c. Script freshness check

`bin/update-flake` runs from `$(devbox global path)/bin/update-flake`,
NOT from the repo's working copy. If you've just edited the script
in the repo:

```bash
diff -q bin/update-flake "$DEVBOX_GLOBAL/bin/update-flake"
```

Non-empty output → your script edits haven't taken effect yet.
Sync first: `config-sync -- --sync` (only safe when other state is
clean — see 0b).

### 0d. When to halt-and-ask vs auto-resolve

| State | Action |
|---|---|
| Clean working tree, clean global sync, fresh script | proceed to Step 1 |
| Untracked files only, no diffs | proceed (untracked is harmless) |
| Staged-only edits on flake files (no unstaged) | commit first, then proceed |
| Unstaged edits in repo, global clean | commit then sync; otherwise `config-sync -- --sync` will overwrite them |
| `MM` on any file | **HALT** — must resolve with user |
| Repo↔global both diverged | **HALT** — config-sync will warn; resolve direction with user |

**Why this matters:** update-flake's `resolve_hashes()` modifies
files in place and reports "All updates applied" even when the
underlying state was already mid-edit. Running it on top of dirty
state yields files that compile but contain the union of unresolved
prior edits plus the new bumps — silently wrong, no error path.

## Preflight one-liner

```bash
git status --short && \
  diff -qr devbox.d "$(devbox global path)/devbox.d" | head -20 && \
  diff -q bin/update-flake "$(devbox global path)/bin/update-flake"
```

If all three output nothing: clean to proceed. If any output:
classify per table above before running update-flake.

## STALE package-lock recovery (memory #203)

- When a flake update build fails AFTER hashes were resolved (no fakeHash in flake.nix, no sync issue) with an npm/pnpm install-phase error like 'ENOTCACHED', 'Lockfile does not contain pattern', 'Cannot resolve dependency X', or 'ERR_PNPM_LOCKFILE_CONFIG_MISMATCH' AND the npmDepsHash/nodeModulesHash stayed the same as the prior version, FIRST-CHECK memory #203 (stale package-lock recovery). The diagnostic chain below (peer-deps, offline mode, makeCacheWritable, npm cache writable) is NOT the right path — #203 says the upstream bumped their deps in the release but didn't regenerate package-lock.json/pnpm-lock.yaml to match. RECOVERY: revert version + srcHash to the prior values via 'git show HEAD:devbox.d/<pkg>/flake.nix'; LEAVE npmDepsHash/nodeModulesHash AS-IS (typically identical between versions since it derives from the unchanged lockfile). Lockfile regeneration is a SEPARATE TASK, not a side-task during multi-package updates. Anti-pattern observed 2026-07-23 in devbox-global impeccable 3.2.0→3.3.1: agent burned 4-5 turns doing peer-dep / fetchNpmDeps / offline-mode reasoning before arriving at #203's conclusion. Skip the multi-turn reasoning loop — go straight to git show HEAD + revert + re-sync + rebuild. Token-efficiency: skipping the 4-6 turn diagnostic saves ~3-5 minutes per occurrence. Cross-reference memory #174 (docling flake NOT-category-X pattern) — same anti-pattern shape.

## LEGITIMATE npm peer-dep + optional-dep fix (when STALE package-lock recovery is not enough)

When memory #203 (stale lockfile via revert) fails to resolve a persistent cycle
across multiple update attempts — typically because upstream DID regenerate their
lockfile but it includes optional platform-specific deps that fetchNpmDeps v1
can't fetch — the FORWARD fix is a THREE-PART pattern. Verified working 2026-07-25
on devbox-global devbox.d/impeccable/flake.nix 3.3.1.

**Symptoms:**
- After lockfile is fresh, fetchNpmDeps fails with a transient HTTP error on
  optional deps like `@anthropic-ai/claude-agent-sdk-linux-arm64-musl` (or any
  package-with-platform-specific-optionals)
- `npmFlags = ["--legacy-peer-deps"]` alone does NOT help (npmFlags apply AFTER
  the metadata-fetch step, which is where the failure happens)
- `optionalDependencies` in package.json cause the package-lock metadata to
  include optional deps that don't exist on the registry for the build's target

**Step 1 — Regenerate package-lock.json with --omit=optional:**
```bash
mkdir -p /tmp/npm-cache
curl -sL <url-to-upstream-tarball> | tar xJ
cd <extracted-pkg-dir>
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps --omit=optional --cache /tmp/npm-cache
cp package-lock.json "$DEVBOX_GLOBAL/devbox.d/<pkg>/"
```
The `--omit=optional` flag is CRITICAL — without it, the lockfile grows to
include optional platform-specific deps that fetchNpmDeps will then try to fetch.

**Step 2 — Set npmFlags in buildNpmPackage:**
```nix
buildNpmPackage {
  npmFlags = ["--legacy-peer-deps"];
  ...
}
```
Does NOT fix the metadata-fetch issue (npmFlags apply at install time, not at
metadata resolution), but it IS needed for the install phase to skip strict
peer-dep resolution.

**Step 3 — CRITICAL closing fix: bump npmDepsFetcherVersion to 2:**
```nix
buildNpmPackage {
  npmDepsFetcherVersion = 2;
  ...
}
```
`fetcherVersion=1` fetches ALL deps in the lockfile (including optional deps).
`fetcherVersion=2` SKIPS optional deps entirely. This is the piece that turns a
"transient registry HTTP error" on claude-agent-sdk-linux-arm64-musl into a
clean build. Without this step, the build keeps failing on optional deps even
after a clean lockfile regen.

**Step 4 — Reset npmDepsHash to fakeHash and rebuild:**
After all three changes, npmDepsHash MUST change (lockfile content changed), so
reset to fakeHash, run `devbox global install`, capture the real hash from the
build error, paste it back.

**Diagnostic chain (anti-pattern to avoid):**
- Try npmFlags alone → still fails (npmFlags too late)
- Regenerate lockfile without --omit=optional → lockfile includes optional deps
- Regenerate lockfile WITH --omit=optional → fetchNpmDeps v1 still fails on
  whatever optional deps remain in the lockfile metadata
- Add `npmDepsFetcherVersion = 2` → clean build (THIS IS THE FIX)

**Token-efficiency:** the agent burned 5+ turns converging on this. The next
session should jump directly to the triple pattern: `--omit=optional` + npmFlags
+ `npmDepsFetcherVersion = 2`. Skip the single-flag trials.

Pairs with memory #203 (stale package-lock recovery via revert) and memory #207
(lockfile regen procedure). #203 is the FIRST check; this is the SECOND when #203
doesn't resolve.

## Re-entry / resume pattern

- When the user issues the standard 4-step workflow ('update the nix flakes, build, refresh-global, and upload') followed by a terse 'retry', they are approving a checkpoint and want to RESUME the destructive workflow from the current system state — NOT continue deliberating about uncommitted changes, NOT re-do the recon. Correct move on 'retry':
1. Quick reconfirmation (git status --short, diff -q repo vs global) — ONE tool call, not a deliberation loop
2. Decide FAST on uncommitted changes:
   - Noise (reformatting, whitespace, trailing commas) → drop or stash, do not mix with the workflow commit
   - User work unrelated to the current workflow (e.g. a new package directory) → either bundle in a separate chore commit, or stash for the user to handle later
   - User work in scope of the current workflow → keep and commit together
3. Apply Step 0 Preflight (0a-0d) before update-flake if dirty state remains
4. Execute the workflow steps (update-flake → build → config-sync → commit → push)
Anti-pattern: spending 4-5 turns deliberating about uncommitted changes BEFORE the user said 'retry' (observed 2026-07-25 in devbox-global: agent deliberated about adding a 'goose' package directory across multiple turns before 'retry' arrived — context waste). The user's 'retry' is the checkpoint approval — apply it, don't re-question it. Pairs with user-pref #21 (one-line direct execution = minimal-latency action) and recon-first downgrade convention.

### Push after commit ("upload the build")

- Standard update-flake workflow ends with three sequential ops: config-sync --reverse --sync to pull changes back to the repo, surgical git add of touched flake.nix + flake.lock files, then conventional commit AND 'git push origin master'. The user uses casual phrasing 'upload the build' to mean 'push the committed changes to GitHub' - NOT 'devbox cache upload' (which is bin/upload-flakes, a different Jetify-cache concern). Confirmation: 'after finishing [update-flake], upload the build' = commit + push origin. When the user issues this directive, do NOT stop after committing - finish with push. Distinct from memory #20 (commit-only default when user says 'commit'): 'upload the build' / 'push' / 'git push' are explicit push directives. Distinct from memory #40 (oracle-review-then-ship): update-flake bumps don't need oracle review - just commit + push.

## Transitioning from main-tracking (commit SHA) to tagged releases

- Some devbox.d/<name>/flake.nix files track main because the upstream project did not tag releases at the time of integration. The version string uses a placeholder like '0-unstable-<date>' and rev is a commit SHA. When upstream starts tagging releases, switching improves update-flake detection (status moves from ?? to ✓).

**Recipe (verified 2026-07-27, skillspector 0-unstable-2026-06-10 → 2.5.0):**

1. **Find the latest tag** matching the upstream project's release cadence:
   
   If no GitHub release but tags exist:
   

2. **Bump version to clean semver**: drop the '0-unstable-<date>' placeholder and use the real tag (e.g. '2.5.0').

3. **Change rev from commit SHA to tag template**:  (or whatever prefix the project uses — most are 'v' but check first). The templating matters: it ties rev to version so future bumps auto-track. A literal rev like 'v2.5.0' would also work but loses the auto-tracking property.

4. **Regenerate srcHash via fakeHash → build → capture loop** — even if the tag's commit SHA equals the old main-tracking rev, the tarball at the tag differs from the archive fetched at the commit (tag fetches include the cleaned source tree at the tagged commit, not the working tree). Set srcHash to lib.fakeHash, run devbox global install, capture the real hash from the build error, paste it back.

5. **Verify update-flake now sees the package**:
   [1;33mNote: 11 flake(s) in devbox.d/ are not enabled in devbox.json (skipped):[0m
  - agent-reach
  - aicommits
  - beads
  - codecanary
  - compiledb
  - docling
  - firecrawl
  - herdr
  - iii-engine
  - opencommit
  - playwright-chromium-deps


[1m[0;36m═══ Devbox Global Flake Packages ═══[0m

[1mPACKAGE         SOURCE                    INSTALLED       LATEST          STATUS  [0m
─────── ──────        ───────── ────── ──────
neovim          nix-community/neovim-nightly-overlay flake           master          [1;33m??[0m
tree-sitter-perl tree-sitter-perl/tree-sitter-perl 1.2.1           1.2.1           [0;32m✓[0m
blesh           akinomyoga/ble.sh         0.4.0-devel3    0.4.0-devel3    [0;32m✓[0m
openspec        Fission-AI/OpenSpec       1.6.0           1.6.0           [0;32m✓[0m
bun             oven-sh/bun               1.4.0-canary    1.3.14          [1;33m↑[0m
open-code-review alibaba/open-code-review  1.7.17          1.7.17          [0;32m✓[0m
opencode        anomalyco/opencode        1.18.7          1.18.7          [0;32m✓[0m
graphify        rbelem/graphify           0.9.28-perl     0.9.28          [0;32m✓[0m
skills          vercel-labs/skills        1.5.20          1.5.20          [0;32m✓[0m
rtk             rtk-ai/rtk                0.44.0          0.44.0          [0;32m✓[0m
agent-browser   vercel-labs/agent-browser 0.33.0          0.33.0          [0;32m✓[0m
playwright-cli  microsoft/playwright-cli  0.1.17          0.1.17          [0;32m✓[0m
codeburn        getagentseal/codeburn     0.9.19          0.9.19          [0;32m✓[0m
codegraph       rbelem/codegraph          1.5.0-perl      1.5.0           [0;32m✓[0m
whichllm        Andyyyy64/whichllm        0.5.15          0.5.15          [0;32m✓[0m
agentmemory     rohitg00/agentmemory      0.9.28          0.9.28          [0;32m✓[0m
impeccable      pbakaus/impeccable        3.3.1           3.3.1           [0;32m✓[0m
skillspector    NVIDIA/SkillSpector       2.5.0           2.5.0           [0;32m✓[0m
strix           usestrix/strix            1.4.0           1.4.0           [0;32m✓[0m
hunk            modem-dev/hunk            0.17.6          0.17.6          [0;32m✓[0m
omniroute       diegosouzapw/OmniRoute    3.8.48          3.8.48          [0;32m✓[0m
dcg             Dicklesworthstone/destructive_command_guard 0.6.7           0.6.7           [0;32m✓[0m
wigolo          KnockOutEZ/wigolo         0.2.1           0.2.1           [0;32m✓[0m
jcode           1jehuang/jcode            0.61.0          0.61.0          [0;32m✓[0m
goose           aaif-goose/goose          1.44.0          1.44.0          [0;32m✓[0m

[1m[0;36m═══ Nixpkgs Packages ═══[0m

[1mPACKAGE              INSTALLED       SOURCE  [0m
─────── ───────── ──────
atuin                18.17.0         nixpkgs
bitwarden-cli        2026.6.0        nixpkgs
cargo                1.96.1          nixpkgs
chezmoi              2.70.5          nixpkgs
dconf                0.49.0          nixpkgs
delta                0.19.2          nixpkgs
difftastic           0.69.0          nixpkgs
doggo                1.2.0           nixpkgs
dos2unix             7.5.5           nixpkgs
evtest               1.36            nixpkgs
fd                   10.4.2          nixpkgs
file                 5.48            nixpkgs
fzf                  0.74.0          nixpkgs
gcc                  16.1.0          nixpkgs
gh                   2.96.0          nixpkgs
ghq                  1.10.1          nixpkgs
git-credential-manager 2.7.3           nixpkgs
git-credential-oauth 0.17.2          nixpkgs
gitFull              2.54.0          nixpkgs
glibcLocales         2.42-67         nixpkgs
go                   1.26.4          nixpkgs
htop                 3.5.1           nixpkgs
jdk21                21+35           nixpkgs
jq                   1.8.2           nixpkgs
libsecret            0.21.7          nixpkgs
libuuid              2.42.2          nixpkgs
luarocks             3.9.1           nixpkgs
nerd-fonts.fira-code 3.4.0+6.2       nixpkgs
nerd-fonts.hack      3.4.0+3.003     nixpkgs
nerd-fonts.noto      3.4.0           nixpkgs
nix-prefetch-git     26.11           nixpkgs
nix-search-cli       0.3-unstable-2025-12-03 nixpkgs
nodejs               26.5.0          nixpkgs
p7zip                17.06           nixpkgs
perl5Packages.PerlTidy 20250711        nixpkgs
podman               5.8.4           nixpkgs
python314            3.14.4          nixpkgs
ripgrep              15.2.0          nixpkgs
sesh                 2.27.0          nixpkgs
starship             1.26.0          nixpkgs
statix               0.5.8-unstable-2026-07-10 nixpkgs
tig                  2.6.1           nixpkgs
tmux                 3.7             nixpkgs
tree                 2.3.2           nixpkgs
tree-sitter          0.26.9          nixpkgs
unzip                6.0             nixpkgs
uv                   0.11.28         nixpkgs
wl-clipboard         2.3.0           nixpkgs
xxd                  9.0.0609        nixpkgs
zenity               4.2.2           nixpkgs
zoxide               0.10.0          nixpkgs

[0;32m✓[0m = up to date  [0;31m↓[0m = older (update available)  [1;33m↑[0m = ahead of latest  [1;33m??[0m = unknown
   Status should be ✓ (was ?? before). If still ?? after the switch, check that the version string matches what gh api returns and that the rev tag format matches the project's actual tag naming.

**Why srcHash differs even when the commit SHA is the same:**
- main-tracking fetch: fetchFromGitHub at a specific commit SHA → nix-prefetch-git produces a NAR hash of the working tree as of that commit (includes uncommitted files, submodule blobs, etc).
- tag-based fetch: fetchFromGitHub at a tag → fetches the archive zip/tarball that GitHub generated for the tag (clean tree, no submodule artifacts).
- The two fetch paths produce different store paths, so the same commit SHA gives different srcHash values depending on whether you reference it by SHA or by tag.

**Why use 'v${version}' instead of literal 'v2.5.0':**
- update-flake's version comparator reads the  attribute from flake.nix and queries gh for the latest release.
- If rev is literal 'v2.5.0' and version is '2.5.0', a future bump to 2.6.0 will leave rev pointing at the old tag → build mismatch.
- 'v${version}' keeps rev in lockstep with version: bumps work transparently.

**Commit message convention** (matches the standard chore pattern):

Example: 

**One-shot detection heuristic:** when scanning devbox.d/<name>/flake.nix, the presence of '0-unstable-<date>' in the version string OR a 7-40 char hex string as the rev value (with no 'v' prefix) signals a main-tracking flake that may benefit from this transition. Worth checking gh api releases for the upstream project before assuming it stays main-only.

## ## Commit-pinned fork source: commit must be on the flake URL

- When a flake uses `pkgs.fetchFromGitHub { owner = "<fork>"; repo = "<name>"; rev = "<commit-sha>"; ... }` and the `<fork>` is a personal/organization fork (e.g. owner = "rbelem", repo = "bitw" — the rbelem fork of mvdan/bitw) rather than the upstream maintainer, the commit SHA MUST be reachable on github.com/<fork>/<name>/archive/<sha>.tar.gz before `nix build` succeeds. Local branches on the user clone are irrelevant — fetchFromGitHub only fetches from the GitHub URL the flake declares.

SYMPTOM (NOT a hash mismatch): `nix build` fails with HTTP 404 when trying to download the tarball: `error: unable to download ... archive/<sha>.tar.gz` or `error: HTTP error 404`. The build never reaches the hash-comparison stage — it dies at the fetch step.

DIAGNOSTIC: `git ls-remote https://github.com/<fork>/<name>.git <sha>` returns empty when the commit is not on the remote. The local clone may have the commit checked out on a feature branch (e.g. `feat/reorder-client-creds`) but `origin` may not have it if the user only committed locally and forgot to push.

FIX: push the local branch containing the commit to the fork remote first:
```
cd "$(ghq root)/github.com/<fork>/<name>"
git push origin <branch>
```
Then re-run `nix build` and capture the real hash. The "Do NOT push" rule from typical devbox-global destructive workflows applies to the devbox-global repo commit, NOT to the upstream project fork — pushing the fork is a prerequisite for the nix build to fetch the source.

WORKFLOW ADDITION for commit-pinned fork flakes (insert BEFORE Step 4 build→capture-hash):

1. Verify the new rev SHA is reachable on github.com:
   `git ls-remote https://github.com/<fork>/<name>.git <new-sha>`
2. If empty, push the local branch containing the commit to origin first
3. Only then run `nix build` to capture the hash

Observed 2026-07-30 in devbox-global/devbox.d/bitw flake bump (rev 9bb2335 on local feat/reorder-client-creds branch but not on rbelem/bitw origin → nix build 404 → after push, build succeeded and captured real hash sha256-+mr49JbACWSl/a109SmT5JL9+WZSoRzci19Xs6In80Y=).

## EXTENDED hash-field quick reference table

- | docling | source URL version in `inputs.docling-src` |
| herdr, strix, hunk | `sha256` in systemToHash map |
| **bitw** | `hash` (fetchFromGitHub src), `vendorHash` (buildGoModule Go modules) — see buildGoModule sequential hash note below |

## buildGoModule sequential hash resolution

- ## buildGoModule sequential hash resolution (bitw pattern)

When a flake uses `pkgs.buildGoModule` with both a `src = pkgs.fetchFromGitHub { ... hash = ...; }` AND a `vendorHash = ...;` field (e.g. devbox.d/bitw/flake.nix — Go projects without a vendor/ directory require the `vendorHash`), the two hashes resolve **sequentially**, NOT in parallel:

1. First build fails on the `hash` (source) field with `-source.drv` mismatch — paste the real source hash, rebuild.
2. Second build fails on the `vendorHash` field — paste the real vendorHash, rebuild.
3. Third build succeeds.

This is the SAME pattern as npm/pnpm's `srcHash` + `nodeModulesHash` (see "Multiple hashes: which .drv failed" above) but with buildGoModule-specific field names. The derivation-name suffix disambiguates: `bitw-0.1.0-source.drv` = source hash, `bitw-0.1.0-go-modules.drv` = vendorHash. Do NOT expect both hashes in one fakeHash→build→paste cycle — the build only progresses past the source-hash failure when the source hash is correct, then it reports the vendorHash failure on the next iteration.

**Shortcut:** when bumping a buildGoModule flake, the source hash can be pre-computed with `nix-prefetch-url --unpack https://github.com/<owner>/<repo>/archive/<rev>.tar.gz` (per memory #192 — fetchFromGitHub.hash expects NAR hash, which is what nix-prefetch-url --unpack returns). Set the source hash directly; let the build loop only resolve the vendorHash. Saves one build iteration per bump. Apply to any future devbox.d/<name>/ flake using buildGoModule + fetchFromGitHub (bitw, future Go projects).

## Step 3: Bump version strings + set fakeHash — lib.fakeHash SCOPE GOTCHA

- Many devbox-global flakes (bitw, opencode, agent-browser, agentmemory, skills, iii-engine) do NOT bind `lib = nixpkgs.lib` in their outputs function's `let` block — they only bind `systems` and `forAllSystems` (and sometimes `pkgs` inside the system lambda). The skill's blanket 'use lib.fakeHash' recipe produces `error: undefined variable 'lib'` at eval time on these flakes. CORRECT substitutions by lexical position: (a) inside the outer outputs `let` block (no pkgs in scope) → use `nixpkgs.lib.fakeHash`. (b) inside the `forAllSystems (system: let pkgs = ...)` lambda → use `pkgs.lib.fakeHash`. (c) only when the flake explicitly binds `lib = nixpkgs.lib` in its let block → the bare `lib.fakeHash` works. Quick check before writing the edit: `rtk grep -n '^[[:space:]]*lib =\|^[[:space:]]*let\|^[[:space:]]*systems' devbox.d/<name>/flake.nix` to see what's bound. Same scoping rules apply to any `lib.xxx` reference (licenses, fakeSha256, maintainers, etc.) the skill or any flake edit might introduce. Observed 2026-08-03 bitw v0.1.1 bump — bare `hash = lib.fakeHash` failed at flake.nix:140; substituted to `nixpkgs.lib.fakeHash` (the outer outputs let doesn't bind `lib` or `pkgs`, only `systems` and `forAllSystems`), build proceeded. The skill's recipes assume a canonical flake shape that the repo's actual flakes don't all conform to; verify scope BEFORE writing the edit, not after the eval error.

## Multi-derivation flake version detection pitfall

- ## Multi-derivation flake version detection pitfall

The version-detection grep in `bin/update-flake` line 141 picks the
FIRST `version = "..."` attribute in `flake.nix`. For flakes with
multiple `mkDerivation` blocks (e.g. `devbox.d/valkey-search/flake.nix`
which has `highwayhash` defined as a sub-derivation BEFORE the main
`valkey-search` derivation), this can return the SUB-derivation version
(`0-unstable-2026-08-04`) instead of the main package version
(`1.2.1`).

**Symptom in `devbox global run update-flake` table:**
- Installed version shows a date-based / unstable suffix (e.g. `0-unstable-2026-08-04`)
- The actual main package version (in the flake's outer derivation with
  `pname = "<flake-name>"`) is already at the latest GitHub release tag
- The `↓` arrow still appears because the FIRST version is OLDER than
  the upstream release

**Diagnostic when this happens:**
1. `grep -n 'version =' devbox.d/<name>/flake.nix` — list all version attrs
2. Identify which `mkDerivation` block each belongs to
3. The MAIN version is in the block whose `pname` matches the flake
   directory name (e.g. `pname = "valkey-search"` for
   `devbox.d/valkey-search/flake.nix`)
4. If the main version already matches the latest tag — the update
   suggestion is a false positive from the script's parsing. Skip.

**Until the script is fixed** (line 141 should prefer the LAST
`version = "..."` or specifically target the derivation matching
`pname = "<flake-name>"`), manual triage is required for any
multi-derivation flake. Common examples to watch: valkey-search
(highwayhash sub-derivation), any flake that builds static libs as
prerequisites (ICU, abseil, protobuf).

**Pairs with:** memory entry 'update-flake script version detection bug
for multi-derivation flakes' — script-level fix is pending; until then
manual triage.





**update-flake report:** status = ??. There is no versioned release to query (the input is a moving target on a community overlay's master branch). update-flake cannot detect upgrades and will never propose one.

**Manual update path (recipe):**

1. Refresh the locked input in the per-flake flake.lock:
   `cd "$(devbox global path)/devbox.d/<name>"; nix flake lock --update-input <input-name>` (e.g. neovim-nightly-overlay)
2. Confirm the new store path exists:
   `nix build path:./devbox.d/<name>#default` (or path:./devbox.d/<name>#<attr>)
3. **Profile refresh trap** — see the 'Overlay-package profile-dedupe trap' diagnostic section. devbox global install + shellenv --recompute may NOT swap the global profile to the new build, because the derivation attr name is unchanged across rev bumps — devbox's nix-profile install considers it already installed.

**Known Category E packages in this repo (as of 2026-08-10):**

- devbox.d/neovim/flake.nix — wraps nix-community/neovim-nightly-overlay via wrapNeovim + symlinkJoin { name = 'neovim-with-vimdiff'; ... }.
- Future: any devbox.d/<name>/flake.nix whose packages.<system>.default uses a fixed string in the name attribute of symlinkJoin / writeShellScriptBin / wrapProgram that wraps an upstream overlay input.

## ## VENDORED files (not flake.nix) require separate handling

- When a flake bumps to a new version AND that flake vendors source files inside devbox.d/<pkg>/ (e.g. devbox.d/prime-agent/package-lock.json + coding-agent-package.json — a common pattern for npm monorepo flakes where the upstream lockfile is broken by npm/cli#6301 and the flake ships a regenerated lockfile), the update-flake script does NOT touch these vendored files. It only edits flake.nix hashes. The vendored files must be:

1. Regenerated against the new upstream (see devbox-npm-flake skill 'npm monorepo vendored-lockfile regeneration procedure' for the full recipe)
2. Copied to BOTH repo (devbox.d/<pkg>/) AND global (/home/rodrigo/.local/share/devbox/global/default/devbox.d/<pkg>/) — use `devbox global run config-sync -- --sync` to propagate
3. Verified in sync: `diff -q devbox.d/<pkg>/package-lock.json "\$(devbox global path)/devbox.d/<pkg>/package-lock.json"`

If you only update the repo, the build picks up the OLD lockfile at the global path and fails with ETARGET errors (e.g. 'No matching version found for @biomejs/biome@2.5.5' when lockfile pins 2.3.5). If you only update the global path, your work is lost on next config-sync (unless --reverse).

Project: devbox-global. Affected packages: prime-agent, impeccable, omniroute, agentmemory, and any other flake that vendors source files for build consumption. Pairs with devbox-npm-flake skill and memory #1311 (lockfile drift pattern).

**FILE-ORDER vs DEPENDENCY-ORDER paste bug in resolve_hashes():**
When a flake has multiple hashes set to fakeHash (e.g. npmDepsHash on line 22, src0 hash on line 28), the script's resolve_hashes() function captures the FIRST 'got:' from the build error and pastes it into the FIRST fakeHash line in the file. But nix evaluates hashes in DEPENDENCY order, not file order — fetchFromGitHub (src0 hash) is evaluated BEFORE npmDepsHash (which depends on src0). Result: both hashes end up with the SRC hash value; npmDepsHash is silently wrong.

**Diagnostic:** after 'update-flake -u <pkg>' reports success, run `rtk grep hash devbox.d/<pkg>/flake.nix` and compare each hash field's value to the build-error log. If multiple hashes are identical AND they should differ (src hash vs npmDepsHash typically differ), the script mis-pasted.

**Workaround:** manually Edit each hash field to the correct value from the build log (the FIRST got: was the src hash, the SECOND got: in a subsequent build was npmDepsHash). Or invoke the script with only one hash set to fakeHash at a time — resolve it, then reset the next hash to fakeHash and run again.

Project: devbox-global. Observed 2026-08-13 prime-agent 0.7.1→0.7.2 bump (both src hash and npmDepsHash ended up with rOKFkKo = src hash value). Pairs with the 'Multiple hashes: which .drv failed' section in this skill (which addresses MANUAL resolution).
- **From-scratch rule (memory #1314 — NEW 2026-08-13):** When regenerating a vendored package-lock.json against an upstream version bump, the EXISTING upstream lockfile in the extracted tarball MUST be removed BEFORE running 'npm install --package-lock-only'. With existing lockfile, npm 11 MERGES into it keeping entries without integrity/resolved from the upstream's bad metadata (e.g. npm/cli#6301-era). Without the existing lockfile (rm -f package-lock.json bun.lock first), npm resolves fresh and produces ONLY the entries that legitimately lack integrity — which for npm monorepos are workspace-local 'packages/*' entries (non-published, no registry integrity needed). The regenerated lockfile's missing-integrity count should MATCH the old vendored baseline; if it's higher, you skipped the rm. Diagnostic: 'rg -c "\"resolved\":" devbox.d/<pkg>/package-lock.json' should equal 'rg -c "\"integrity\":" devbox.d/<pkg>/package-lock.json', and both should be (total entries - workspace-local count). WORKING REGEN COMMAND (post-rm): 'HOME=$TMPDIR npm install --package-lock-only --ignore-scripts --legacy-peer-deps --no-audit --no-fund' (from devbox.d/agentmemory/flake.nix:88). Observed 2026-08-13 prime-agent 0.7.1→0.7.2: first run with upstream lockfile = 42 missing; second run after rm = 8 missing (matching vendored baseline).

If you only update the repo, the build picks up the OLD lockfile at the global path and fails with ETARGET errors (e.g. 'No matching version found for @biomejs/biome@2.5.5' when lockfile pins 2.3.5). If you only update the global path, your work is lost on next config-sync (unless --reverse).
## ## End-to-end `update-flake -a` run expectations (user-declared workflow)

When the user issues `update-flake -a` as a fully-specified run (typical shape: "Run the devbox-global flake updater end to end on the LIVE global config and report results"), apply these expectations:

1. **Classification: routine mechanical command work.** Do NOT manually edit any flake.nix, hash, or version string outside what the script does. The script's `resolve_hashes()` function handles the fakeHash → build → capture → paste loop internally. The agent's job is to RUN it and REPORT results, not to second-guess the bumps.

2. **Bash timeout: 30+ minutes.** A 6-package `-a` run can take 15-30+ minutes total (each `nix build --no-link .#default` may take up to ~10 min for source builds like whichllm's Python package; fetchurl packages are faster but the aggregate is non-trivial). Default bash timeout for this command must be 1800000 ms or higher. Never use the 120000 ms default — it will SIGTERM the run mid-flight.

3. **Don't interrupt on per-package failure.** The script handles per-package failures internally (continues to the next package, surfaces all failures at end). Letting the run finish means you get a complete picture: which packages succeeded, which failed, and which need manual intervention. Killing early on the first failure leaves the rest un-tested.

4. **Capture the FULL output.** The user wants verbatim output, not a paraphrase. Pipe to a log file or use bash output capture — do not summarize mid-stream.

5. **Expected-set vs actual verification.** When the user pre-specifies an expected update set (e.g. "Expected update set (6 packages): open-code-review 1.9.2→1.9.3, whichllm 0.5.15→0.5.16, impeccable 3.5.0→3.6.0, dcg 0.10.0→0.11.0, pdf-inspector 0.7.0→1.14.2, pi 0.84.1→0.84.2. Anything else bumped = unexpected, report it"), the verification step is a SET DIFF:
   - **Expected + bumped**: success — list as confirmed
   - **Expected + NOT bumped**: failure or pre-existing-up-to-date — call out
   - **NOT expected + bumped**: unexpected — call out as deviation (might be a flaky skip, a parallel bump, or a stale detection)
   - **Expected + failed**: per-package failure — list with the script's error excerpt

6. **No manual sync-back until the run completes.** After `-a` finishes successfully, sync global → repo (`config-sync -- --reverse --sync`) and verify the diff. Do NOT run sync-back mid-run (the global state is mid-edit; sync-back would copy incomplete state).

**Trigger phrases for this workflow shape:**
- "Run the devbox-global flake updater end to end on the LIVE global config"
- "update-flake -a ... report results"
- "update all flakes and report what changed"

**Anti-patterns observed:**
- Setting bash timeout to 120s default → SIGTERM mid-build → wasted 120s, partial output, no rollback
- Interrupting the run on first per-package failure → miss later results, may leave global state half-edited
- Manually editing flake.nix hashes mid-run to "fix" a perceived failure → races with the script's resolve_hashes() loop, corrupts state
- Reporting only successes and skipping the failure list → user can't triage without it

**Pair with memory #130** (just-dispatch long-running commands, no pre-flight polling) and **memory #94** (structured MECHANICAL TASK workflow templates). The end-to-end -a run is the mechanical-task variant for flake updates.

Project: devbox-global. Observed: 2026-08-14 devbox-global session, user-issued end-to-end spec for 6-package run (open-code-review 1.9.3, whichllm 0.5.16, impeccable 3.6.0, dcg 0.11.0, pdf-inspector 1.14.2, pi 0.84.2).

## ## Category E: Vendored Cargo.lock with cargoLock (Rust buildRustPackage)

Packages using `pkgs.rustPlatform.buildRustPackage` with vendored `cargoLock = { lockFile = ./Cargo.lock; }` + `postPatch = 'cp ${./Cargo.lock} Cargo.lock'` (e.g. pdf-inspector, any Rust source-build flake where upstream doesn't commit a Cargo.lock).

**Difference from npm/pnpm Categories B/D:** Rust flakes do NOT have a single cargoHash equivalent to npmDepsHash. Instead, the vendored Cargo.lock + optional `outputHashes` map pin all dep versions. When upstream source moves a dep from a git fork to crates.io (or vice versa) across versions, BOTH the Cargo.lock AND the outputHashes set go stale together. Stale outputHashes from the fork-version cause 'candidate versions found which didn't match: X' failures; stale Cargo.lock causes 'perhaps a crate was updated and forgotten to be re-vendored'.

**Bump + fix procedure (4 steps):**

1. `curl -sSL https://github.com/<owner>/<repo>/archive/refs/tags/v<X.Y.Z>.tar.gz | tar xz` into /tmp/<pkg>-src
2. `cd /tmp/<pkg>-src && cargo generate-lockfile` (needs network ONCE for crates.io)
3. Audit git sources in new lock: `grep -nE 'source = "git\+"' Cargo.lock` — zero hits = all crates.io, no outputHashes needed
4. Replace `devbox.d/<pkg>/Cargo.lock` with the freshly generated one; in flake.nix ADD or REMOVE `outputHashes` entries to match the git-dep set (presence of outputHashes when zero git deps = build failure; absence when git deps exist = build failure)

**Diagnostic when this category is suspected:**
- Build error: 'candidate versions found which didn't match: <X>' in cargoSetupPostPatchHook
- Build error: 'perhaps a crate was updated and forgotten to be re-vendored' from cargoBuildHook
- Either error AFTER a successful version bump = stale vendored Cargo.lock

**Real case 2026-08-14 (devbox.d/pdf-inspector 1.14.2):** old Cargo.lock had lopdf as J-F-Liu/lopdf fork @ 7a05512 (v0.40.0) requiring `outputHashes['lopdf-0.40.0']`; new v1.14.2 uses lopdf 0.42.0 from crates.io — REMOVED outputHashes entry, REPLACED vendored lock. Verified the audit with `grep -cE 'source = "git\+"' Cargo.lock` returning 0 before removing outputHashes.

**Cross-reference:** distinct from Category D (fork input-pin no in-flake hashes) — Category D has NO Cargo.lock because the source comes from a flake input. Category E has a vendored Cargo.lock in the flake dir + postPatch copy. Use `grep -l 'cargoLock' devbox.d/*/flake.nix` to enumerate Category E flakes.

**Quick reference (Rust buildRustPackage flakes):**

| Package | Hash fields | Special handling |
|---|---|---|
| pdf-inspector | vendored Cargo.lock + optional outputHashes | Category E |
| rtk | cargoHash + src hash (no vendored lock) | simple — fakeHash on cargoHash + src |
| goose | upstream flake | not Category E (consume aaif-goose/goose) |

**Gotcha — fakeHash dance does NOT apply to Category E:** the build does not capture a hash from the error message; the fix is regenerating the lockfile and adjusting outputHashes. `nix build .#<pkg>` failures in this category point at dep-resolution mismatches, not hash mismatches to paste back.

- ## Category E: Vendored Cargo.lock (buildRustPackage with cargoLock)

## ## Python package bump gotchas (sourced from real bumps)

- - **Python package with hyphenated name: pkgs.fetchPypi will 404 even though the sdist exists.** PyPI re-uploads new sdists with PEP-625-normalized names (underscores replacing hyphens), but fetchPypi constructs the download URL from the package's pname (hyphenated). Result: 404 on files.pythonhosted.org despite the package being live. EXAMPLE (2026-08-19, devbox.d/llm-verifier/flake.nix): pname='llm-verifier' but actual sdist served at /packages/.../llm_verifier-0.2.0.tar.gz (underscore). fetchPypi URL was .../llm-verifier-0.2.0.tar.gz → 404. RECIPE (definitively solves the trap): (1) GET the real URL from PyPI JSON: 'curl -s https://pypi.org/pypi/<pname-with-hyphens>/json | jq -r '.urls[].url'' returns the PEP-625-normalized URL. (2) PASTE that URL into a pkgs.fetchurl call with sha256 from PyPI JSON's '.urls[].digists.sha256' (convert to SRI via 'nix hash to-sri --type sha256 <hex>'). (3) DO NOT use pkgs.fetchPypi for hyphenated Python package names — fetchPypi's URL construction does not know about PEP-625 normalization. WHY fakeHash dance fails here: the URL is wrong, not just the hash, so fakeHash loops forever with 404. ROOT-CAUSE TEST: 'curl -sI https://files.pythonhosted.org/packages/.../<pname-with-hyphens>-<v>.tar.gz' returns 404 BUT 'curl -sI https://files.pythonhosted.org/packages/.../<pname-with-underscores>-<v>.tar.gz' returns 200 → PEP-625 trap confirmed. WHEN THIS APPLIES: ANY Python package whose project name contains hyphens (llm-verifier, open-code-review, deep-search, etc.). Always check PyPI JSON for the real sdist filename before reaching for fetchPypi. Companion to memory #544 (pre-compute srcHash for fetchurl — same curl+sha256sum recipe).
