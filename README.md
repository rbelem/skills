# skills

Agent skills for OpenCode. One folder per skill; each has a `SKILL.md` with
YAML frontmatter (`name`, `description`).

## Guardrail: secret scan

Every commit and PR is scanned for credentials.

- **Local (pre-commit):** `git config core.hooksPath .githooks` installs the
  hook. It runs `gitleaks git --staged -c .gitleaks.toml` — gitleaks from
  PATH, else `nix run nixpkgs#gitleaks`. Commit normally; do not pass
  `-c core.hooksPath=...` to bypass it.
- **CI (push + PR):** `.github/workflows/gitleaks.yml`.

Policy for allowlist entries lives in `.gitleaks.toml`: add an entry only for
a provable non-secret, with a comment naming why.
