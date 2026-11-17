---
name: brainstorm
description: "This skill creates and ranks research hypotheses from current findings. You use it after formalization or between investigation batches."
user-invocable: true
argument-hint: "[context-hint]"
license: Apache-2.0
---

# Brainstorm

You apply the [language rules](../reaper/references/language.md) and [research-state.md](../reaper/references/research-state.md).
You revise research ideas without experiments, proof attempts, or literature searches.
An optional context hint selects a direction.

## Read the Current State

You read `notes/problem-statement.md`, `notes/ideas.md`, `notes/current-understanding.md`, and `notes/results.md` in `reaper-workspace/`.
You use batch summaries for orientation. You inspect individual results before repeating an approach.
You read source notes only when an idea needs them.
If the problem or ideas file is missing, you return the missing prerequisite.

## Generate Useful Alternatives

You identify unresolved questions, repeated failures, and useful methods from verified findings.
You can simplify a case, invert a claim, reuse a technique, or examine an unexplored combination.
These methods generate candidates. An empty combination does not establish novelty or value.
For relevant technical limits, you use `../reaper/references/impossibility-results.md`. You verify the model match before excluding a candidate.
You preserve the original question when proposing changed assumptions. A negative answer can resolve it.
You rank candidates by relevance, consequence, and the evidence needed to test them.
You do not add ideas only to fill a quota.

## Update Ideas

You use the shared hypothesis fields and unused H numbers.
You tag each new idea `[Brainstorm-N]` and identify its source evidence or failure pattern.
N is one greater than the highest existing brainstorm round.
You update priorities and status in place. You create a new hypothesis when the statement or assumptions change materially.
You do not duplicate unresolved ideas. Each hypothesis tests one claim.
You report the new ideas and their priorities, or explain why no distinct useful idea remains.
