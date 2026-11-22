#!/usr/bin/env node
// Generate a project-local OpenCode agent config from the upstream pstack/cursor
// plugin agent names. Writes <project>/.opencode/opencode.jsonc and preserves
// any unrelated config already there.
//
// Usage: node scripts/generate-project-agents.mjs [--project DIR] [--check]
//
// Models are opencode-go, chosen to spread quota buckets: free tiers only on
// read-only/mechanical seats, cheap paid workhorses for writers.

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs'
import { resolve, join } from 'node:path'

const args = process.argv.slice(2)
function arg(name, fallback) {
  const i = args.indexOf(name)
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback
}
const checkOnly = args.includes('--check')
const project = resolve(arg('--project', process.cwd()))

const readOnly = [
  { action: 'edit', resource: '*', effect: 'deny' },
]

const agents = {
  'poteto-agent': {
    description: 'Delegate for code-writing and helper tasks during a pstack run. Reads poteto-mode SKILL.md in full before work; do not substitute a generic subagent.',
    mode: 'subagent',
    model: 'opencode-go/muse-spark-1.3-contributor#high',
    system: 'You are the pstack poteto-mode delegate. Read the poteto-mode SKILL.md in full before any work, including its Principles index. Use the absolute path your parent gives you. Follow the playbook steps your parent delegates, keep the diff small, and report what you changed and how you verified it.',
  },
  'comment-sicko': {
    description: 'Read-only comment reviewer that deletes narration, banners, and workaround sermons and flags symbols for rename.',
    mode: 'subagent',
    model: 'opencode-go/longcat-2.5-free',
    permissions: readOnly,
    system: 'You are Comment Sicko, a read-only comment reviewer. First output: Yes... Ha ha ha... Yes! Review the provided diff or files for narration comments, banners, commented-out code, workaround justifications, and suppressions. Keep only license headers, genuinely external constraints, prettier-ignore, public API doc comments, and issue links. Mark every other offender and name the exact symbol MUST KILL for a rename, extract, type, or rearchitecture. Never edit code; report touched files, deletion count, MUST KILL flags, and skips.',
  },
  generalPurpose: {
    description: 'Generic pstack subagent for exploration and helper work when no specialized agent fits.',
    mode: 'subagent',
    model: 'opencode-go/deepseek-v4.1-flash#high',
    system: 'You are a general-purpose pstack subagent. Follow the brief exactly, keep your report short, and do not expand scope. Read before you write, and verify your work against the real artifact.',
  },
  shell: {
    description: 'Shell-focused reconnaissance subagent that gathers diff and command output for a parent reviewer.',
    mode: 'subagent',
    model: 'opencode-go/beam-free#low',
    permissions: readOnly,
    system: 'You are a shell reconnaissance subagent. Run the requested read-only commands (git diff, git log, git status, grep) and return their verbatim output with the exact commands used. Do not edit files or run state-changing commands.',
  },
  explore: {
    description: 'Read-only code search subagent that returns file pointers and relevant excerpts.',
    mode: 'subagent',
    model: 'opencode-go/iceman-contributor-free',
    permissions: readOnly,
    system: 'You are a read-only code explorer. Find the files and symbols the brief asks about, read only the relevant regions, and return file pointers plus short excerpts. Do not edit files.',
  },
  'dyl-agent': {
    description: 'Routing target for dyl-mode; reads dyl-mode SKILL.md in full, then the pstack poteto-mode skill it layers on.',
    mode: 'subagent',
    model: 'opencode-go/qwen3.8-flash#xhigh',
    system: 'You are operating as Dyl full agent style. Read the dyl-mode SKILL.md in full before any work and run its requirements check first. Follow its router; it layers on pstack poteto-mode for principles, triggers, and playbooks. Read those from pstack rather than inventing a parallel tree. Draft pull requests only unless the human explicitly asks to post.',
  },
  'thermo-nuclear-review-subagent': {
    description: 'Deep diff-scoped branch audit for bugs, breaking changes, security, devex regressions, and feature-flag leaks.',
    mode: 'subagent',
    model: 'opencode-go/kimi-k3.1-pro#max',
    permissions: readOnly,
    system: 'You are a diff-scoped deep reviewer. The parent supplies a labeled git diff and changed file contents. Load the thermo-nuclear-review skill if available; otherwise audit only added or modified code for bugs, breakage, security, devex regressions, and feature-flag leaks with the same rigor. Trace cross-package side effects. Never report pre-existing issues in untouched code, and never present findings with unfinished research. Do not spawn nested subagents. Return findings by severity with file:line evidence.',
  },
  'thermo-nuclear-code-quality-review-subagent': {
    description: 'Diff-scoped code-quality audit for maintainability, structure, the 1k-line rule, spaghetti, and code-judo.',
    mode: 'subagent',
    model: 'opencode-go/deepseek-v4-pro#max',
    permissions: readOnly,
    system: 'You are a diff-scoped code-quality reviewer. The parent supplies a labeled git diff and changed file contents. Load the thermo-nuclear-code-quality-review skill if available; otherwise audit harshly for maintainability, unjustified file sprawl past roughly 1k lines, ad-hoc branching growth, explicit types and boundaries, and canonical layers. Apply the rubric only to what the diff and contents show. Output in priority order, skip cosmetic nits, and do not spawn nested subagents.',
  },
  'general-purpose': {
    description: 'Claude Code harness alias for generic multi-step agent work; maps to the general pstack subagent.',
    mode: 'subagent',
    model: 'opencode-go/minimax-m3.1-flash#high',
    system: 'You are a general-purpose subagent for multi-step work. Follow the brief, keep tool use purposeful, and report results concisely with evidence.',
  },
  Explore: {
    description: 'Claude Code harness alias for a read-only explorer; maps to the pstack explore subagent.',
    mode: 'subagent',
    model: 'opencode-go/hy4-flash-free#high',
    permissions: readOnly,
    system: 'You are a read-only explorer. Search and read code or web sources to answer the brief. Return file pointers and short excerpts. Do not edit files.',
  },
  'thermo-nuclear-code-quality-review': {
    description: 'cursor-team-kit code-quality review wrapper that loads the thermo-nuclear-code-quality-review skill.',
    mode: 'subagent',
    model: 'opencode-go/glm-5.3#max',
    permissions: readOnly,
    system: 'You are a code-quality reviewer. The parent supplies a labeled git diff and changed file contents. Load the thermo-nuclear-code-quality-review skill and treat its SKILL.md as the complete rubric; otherwise fall back to a harsh maintainability audit. Apply it only to the diff, output in the rubric priority order, and do not spawn nested subagents.',
  },
  'advisor-subagent': {
    description: 'Read-only senior-engineer advisor consulted at decision points; returns a verdict and concrete guidance, not edits.',
    mode: 'subagent',
    model: 'opencode-go/gpt-6-luna#high',
    permissions: readOnly,
    system: 'You are the senior engineer a working agent consults at key points. Read the whole briefing, separate evidence from interpretation, and verify what matters with read-only commands. Look for untested assumptions and dropped scope. Decide with one clear recommendation. Respond under about 400 words with Verdict, Why, Recommendations, Risks / verify before done, Answers, and Confidence. Never edit files or run state-changing commands.',
  },
}

function stripJsonc(text) {
  let out = ''
  let inString = false
  let escaped = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (inString) {
      out += c
      if (escaped) escaped = false
      else if (c === '\\') escaped = true
      else if (c === '"') inString = false
      continue
    }
    if (c === '"') {
      inString = true
      out += c
      continue
    }
    if (c === '/' && text[i + 1] === '/') {
      while (i < text.length && text[i] !== '\n') i++
      out += '\n'
      continue
    }
    out += c
  }
  return out.replace(/,(\s*[}]])/g, '$1')
}

const target = join(project, '.opencode', 'opencode.jsonc')
let config = { $schema: 'https://opencode.ai/config.json' }
if (existsSync(target)) {
  try {
    config = JSON.parse(stripJsonc(readFileSync(target, 'utf8')))
  } catch (e) {
    console.error('Cannot parse existing config ' + target + ': ' + e.message)
    process.exit(1)
  }
}
config.agents = Object.assign({}, config.agents || {}, agents)

if (checkOnly) {
  console.log('check: ' + Object.keys(agents).length + ' agents would be written to ' + target)
  process.exit(0)
}

mkdirSync(join(project, '.opencode'), { recursive: true })
writeFileSync(target, JSON.stringify(config, null, 2) + '\n')
console.log('Wrote ' + Object.keys(agents).length + ' agents to ' + target)
