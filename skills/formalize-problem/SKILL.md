---
name: formalize-problem
description: "Formalize a research question into precise, testable hypotheses with trust assumptions, security properties, and explicit success/failure conditions. Use when asked to formalize, define, or scope a research problem after paper analysis."
user-invocable: true
argument-hint: "<research-goal>"
---

# Formalize Problem

Transform a research goal into precise, testable hypotheses with explicit success/failure conditions.

## Usage

```
/reaper:formalize-problem "determine if the security proof in Section 4 holds under asynchrony"
```

## Instructions

### 1. Read Inputs

Read these files:
- `reaper-workspace/notes/clarified-goal.md` — refined research goal, scope, assumptions, and success criteria
- `reaper-workspace/notes/paper-summary.md` — what the paper claims and how
- `reaper-workspace/notes/literature.md` — what's already known, what gaps exist
- The research goal from the argument (use the refined goal from `clarified-goal.md` if available)

### 2. Identify the Core Question

What exactly needs to be resolved? Be specific. "Is this protocol secure?" is too vague. "Does the safety proof of Protocol X hold when the adversary is adaptive rather than static?" is testable.

### 3. Apply Importance Filter (Hamming)

Not all questions are equally worth investigating. Prioritize by consequence:
- A security proof gap that invalidates a deployed protocol > a tighter constant in a complexity bound
- An impossibility result that rules out an entire approach > an incremental improvement
- A finding that changes how practitioners build systems > a purely theoretical curiosity

Ask: "If we resolved this question, who would care and why?"

### 4. Apply Gap-Finding (Qian)

Map the dimensions of existing work and find unexplored combinations:
- Threat models (static/adaptive × sync/async/partial-sync × corruption thresholds)
- Protocol families (leader-based, leaderless, DAG-based, etc.)
- Security properties (safety, liveness, fairness, accountability, etc.)

Which cells in this matrix are empty? Those are candidate hypotheses.

### 5. Write Output

Write to `reaper-workspace/notes/hypotheses.md`:

```markdown
# Research Hypotheses

## Research Goal
[Restate the goal precisely]

## Trust Assumptions
[What is the system model for this investigation?]
- Network model:
- Adversary model:
- Corruption threshold:
- Cryptographic assumptions:
- Other assumptions:

## Security Properties Under Investigation
[What must hold? List each property with its formal definition or reference.]
1. **[Property name]**: [formal definition or citation]
2. ...

## Performance Metrics
[Concrete targets, if applicable]
- Communication complexity:
- Round complexity:
- Other:

## Testable Claims

### H1: [Short descriptive title]
- **Statement**: [Precise, falsifiable claim — specific enough that a reader could disagree]
- **Success condition**: [What evidence would confirm this?]
- **Failure condition**: [What evidence would refute this?]
- **Priority**: High / Medium / Low
- **Rationale**: [Why this priority? What's the consequence of resolving it?]

### H2: [Short descriptive title]
...
```

### Quality Criteria

- Every hypothesis is **falsifiable** — a reader could disagree with it
- Every hypothesis has **explicit** success and failure conditions — not "we'll know it when we see it"
- Priorities are justified by consequence, not convenience
- Trust assumptions are complete — no missing dimensions
- The hypotheses collectively cover the research goal — resolving all of them would answer the original question
- At most 5-7 hypotheses — focus beats breadth. If you have more, merge or drop the low-priority ones
