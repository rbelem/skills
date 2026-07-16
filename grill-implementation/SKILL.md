---
name: grill-implementation
description: Grills the user about implementation details the AI is writing — every meaningful if, clause, business rule, validation, or domain operation triggers questions to verify the human understands what was just built. Use when the user says "grill my code", "question me about the implementation", "ask me about what you just wrote", wants the AI to challenge its own implementation choices, asks to be kept honest while code is being generated, mentions Lucas Montano's reverse-review trick, or any "grill my implementation / grill the code" trigger phrase.
---

After writing each meaningful implementation decision — every `if`, switch arm, guard, validation, error branch, business-rule check, or domain operation — pause and question the user to verify their **understanding** before continuing.

A decision is **meaningful** when it encodes a domain rule, a business constraint, or a non-obvious choice the user couldn't recover by skimming the diff. Trivial wiring and standard-library glue do not count.

## What to probe

For each domain branch the AI just created, fire one question at a time, waiting for the user's answer before continuing. Cover:

- **Intent** — why this branch exists; what domain rule it captures
- **Edge cases** — empty / null / boundary / overflow inputs; what the rule says about each
- **Naming** — does the chosen identifier encode the right mental model, or will future readers (including the user) misread it
- **Adjacency** — neighbouring branches and sibling cases; whether the rule is consistent across them
- **Reversal** — if the business changed tomorrow, what would flip; is the branch robust to that

Aim questions at the **user's understanding**, not their code. The AI is reviewing whether the human can explain the branch and its reasoning — not asking the human to re-read the diff.

## Loop until mutual understanding

Ask successive questions until both sides can restate the branch and why it exists. Then provide a one-paragraph summary of what was covered, and only then resume coding.

If a fact about the codebase can be looked up, look it up — do not ask. The **decisions** belong to the user; the **facts** do not.

Do not advance to the next implementation step until the user confirms mutual understanding on the current one.
