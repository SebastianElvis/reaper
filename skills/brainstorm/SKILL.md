---
name: brainstorm
description: "This skill creates and ranks research hypotheses from current findings. You use it after formalization or between investigation batches."
user-invocable: true
argument-hint: "[context-hint]"
license: Apache-2.0
---

# Brainstorm

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

This skill revises ideas without experiments, proof attempts, or literature searches.

## Usage

You invoke this skill by name with an optional quoted direction. Slash-command hosts use `/brainstorm "<hint>"`.

```
brainstorm
brainstorm "explore liveness under partial synchrony"
```

## Inputs

You always read these files:

- `reaper-workspace/notes/problem-statement.md` supplies the model and properties.
- `reaper-workspace/notes/ideas.md` supplies ideas and their status.
- `reaper-workspace/notes/current-understanding.md` supplies current findings.
- `reaper-workspace/notes/results.md` supplies previous outcomes.

If `results.md` has 20 or more rows, you read batch summaries instead of all rows. You look for failure patterns across batches. You use the optional direction from the argument. You read these sources only when a specific idea needs them or progress stops:

- `reaper-workspace/notes/paper-summary.md`
- `reaper-workspace/notes/literature.md`
- `reaper-workspace/notes/clarified-goal.md`
- `reaper-workspace/papers/`

## Process

### 1. Assess Current State

You identify resolved hypotheses and open hypotheses. You identify hypotheses with repeated inconclusive cycles. You look for common causes of discarded cycles. You check whether keep results suggest a new direction.

### 2. Generate Ideas

You select a method from the current evidence:

- **Failed attempts:** You invert the claim, simplify the case, or change the model or property.
- **Confirmed results:** You reuse a proof method, remove an assumption, or test a further implication.
- **Unexplored combinations:** You use `../reaper/references/model.md` to find gaps without a prior investigation result.

You assign each proposed idea to one source category.

After three or more cycles that suggest refutation, you propose a negative claim. You also propose a hypothesis about the weakest assumption that restores the property.

### 3. Check Impossibility Results

You check each candidate against `../reaper/references/impossibility-results.md`. If a known result rules out a candidate, you identify the conflict. You change the candidate to specify additional assumptions or a weaker property. You do not pass a known impossible positive claim to `investigate`.

### 4. Set Priorities

You rank ideas by who needs their answers and why. You use the examples in `../reaper/references/model.md`.

### 5. Write Output

You update `reaper-workspace/notes/ideas.md`. You add new ideas in a new round section. You edit existing ideas in place when their statements or priorities change. You mark ideas that another result already covers.

```markdown
## Ideas — Brainstorm Round N

### H<next>: [Short title]
- **Statement**: [You state a precise claim that evidence can refute.]
- **Success condition**: [You state the evidence that confirms the claim.]
- **Failure condition**: [You state the evidence that refutes the claim.]
- **Priority**: High / Medium / Low
- **Rationale**: [You explain the effect of resolving this claim.]
- **Source**: [Brainstorm-N] [You identify the finding, failure pattern, gap, or prior hypothesis that suggested this idea.]
```

N is one greater than the highest existing brainstorm round, or 1 for the first round. Hypothesis numbers continue from the highest existing H number.

## Quality Criteria

- You add no more than 3-5 ideas per round.
- Each idea tests one claim in one cycle. You split claims that combine properties such as safety and liveness.
- Each idea has explicit success and failure conditions.
- You do not duplicate an unresolved idea.
- You give the user's direction high priority without excluding other useful ideas.
- If `problem-statement.md` or `ideas.md` is missing, you return an error to the orchestrator.

## Report

You report the number of new ideas and the most important new idea. You explain any lower priorities or ideas that other results now cover.
