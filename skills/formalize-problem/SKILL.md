---
name: formalize-problem
description: "Formalize a research question into precise, testable hypotheses with model assumptions, core properties, and explicit success/failure conditions. Use when asked to formalize, define, or scope a research problem after paper analysis."
user-invocable: true
argument-hint: "<research-goal>"
license: Apache-2.0
---

# Formalize Problem

Transform a research goal into precise, testable hypotheses with explicit success/failure conditions.

## Usage

Invoke this skill by name with the research goal as a quoted string. On slash-command hosts, prefix with `/` (e.g. `/formalize-problem "<goal>"`).

```
formalize-problem "determine if the security proof in Section 4 holds under asynchrony"
```


## Instructions

### 1. Read Inputs

**Always read:**
- `reaper-workspace/notes/clarified-goal.md` — refined research goal, scope, assumptions, and success criteria
- `reaper-workspace/notes/paper-summary.md` — what the paper claims and how. **If this file does not exist** (paper-less mode), proceed without it — use the literature review and clarified goal as primary inputs instead.
- The research goal from the argument (use the refined goal from `clarified-goal.md` if available)

**Read selectively from:**
- `reaper-workspace/notes/literature.md` — focus on the "Key Prior Results" and "Gaps Identified" sections, not the full paper tables. Only deep-read individual paper entries if a specific prior result is needed for hypothesis screening. **In paper-less mode, this becomes the primary technical context** — read it more thoroughly.

### 2. Identify the Core Question

What exactly needs to be resolved? Be specific. "Is this protocol secure?" is too vague. "Does the safety proof of Protocol X hold when the adversary is adaptive rather than static?" is testable.

### 3. Pin Down Model Assumptions (must be unambiguous before hypotheses)

Pin down every dimension of the system/trust model. If any dimension is left vague, the investigation will produce ambiguous results. Consult `../reaper/references/model.md` for the domain-appropriate checklist of dimensions that must be specified. Every field must have a concrete answer, not "TBD".

Every hypothesis must reference these model assumptions by specifying which parameters it holds under. A hypothesis that states a claim without pinning every relevant dimension is rejected.

### 4. Apply Importance Filter (Hamming)

Not all questions are equally worth investigating. Prioritize by consequence — ask: "If we resolved this question, who would care and why?" Consult `../reaper/references/model.md` for domain-specific examples of how to rank by importance.

### 5. Apply Gap-Finding (Qian)

Map the dimensions of existing work and find unexplored combinations. Consult `../reaper/references/model.md` for the domain-appropriate gap-finding matrix dimensions. Which cells in this matrix are empty? Those are candidate hypotheses.

### 6. Screen Against Known Impossibilities

For each hypothesis, check whether it contradicts a known impossibility or lower bound. Consult `../reaper/references/impossibility-results.md` for the domain-relevant impossibility results and lower bounds.

If a hypothesis asks to prove something that an impossibility result rules out:
1. **Flag it explicitly** in the hypothesis with a warning
2. **Reformulate**: "Under what additional assumptions does this become possible?" or "What weaker property can be achieved?"
3. Do NOT leave it as a hypothesis for the investigate skill to waste cycles on

### 7. Enforce Definitional Hygiene

Each core property listed in the output must be stated precisely. Consult `../reaper/references/definitional-standards.md` for the domain-appropriate acceptable definition forms. Informal or ambiguous terms without formal definitions are NOT acceptable — different papers define the same terms differently, so pin it down. If the paper under analysis uses informal definitions, formalize them explicitly and note that you are doing so.

### 8. Write Output

Write to `reaper-workspace/notes/problem-statement.md`:

```markdown
# Problem Statement

## Research Goal
[Restate the goal precisely]

## Model Assumptions
[One field per dimension from `../reaper/references/model.md`. Every dimension must have a concrete answer.]

## Security Properties Under Investigation
[What must hold? List each property with its formal definition or reference.]
1. **[Property name]**: [formal definition or citation]
2. ...

## Performance Metrics
[Concrete targets, if applicable]
- Communication complexity:
- Round complexity:
- Other:
```

Write ideas to a separate file `reaper-workspace/notes/ideas.md`:

```markdown
# Ideas

## Initial Ideas

### H1: [Short descriptive title]
- **Statement**: [Precise, falsifiable claim — specific enough that a reader could disagree]
- **Success condition**: [What evidence would confirm this?]
- **Failure condition**: [What evidence would refute this?]
- **Priority**: High / Medium / Low
- **Rationale**: [Why this priority? What's the consequence of resolving it?]

### H2: [Short descriptive title]
...
```

### Relationship to Brainstorm

`/formalize-problem` handles *initial* formalization: pinning down trust assumptions, the core question, definitional hygiene, and the first set of hypotheses. It runs once at the start of the pipeline. The `/brainstorm` skill handles *recurring* ideation — generating additional ideas as the investigation progresses, applying Hamming/Qian heuristics to current state, and proposing follow-up hypotheses based on patterns in results. `/brainstorm` updates the `ideas.md` that this skill creates (adding new ideas and editing existing ones inline).

### Quality Criteria

- Every hypothesis is **falsifiable** — a reader could disagree with it
- Every hypothesis has **explicit** success and failure conditions — not "we'll know it when we see it"
- Priorities are justified by consequence, not convenience
- Trust assumptions are complete — no missing dimensions
- The hypotheses collectively cover the research goal — resolving all of them would answer the original question
- At most 5-7 hypotheses — focus beats breadth. If you have more, merge or drop the low-priority ones
- `clarified-goal.md` is always required — return an error if missing. `paper-summary.md` is optional (absent in paper-less mode) — if missing, rely on `literature.md` and `clarified-goal.md` instead
