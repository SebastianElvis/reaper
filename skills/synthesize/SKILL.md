---
name: synthesize
description: "Generate a structured research report from investigation results, with a central finding, refutable contributions, and concrete examples. Use when asked to synthesize, summarize, or write up research findings after investigation cycles."
user-invocable: true
---

# Synthesize

Generate a structured research report from all investigation results.

## Usage

```
/reaper:synthesize
```

## Instructions

### 1. Re-read Everything

Do NOT rely on context window. Re-read all workspace files:
- `reaper-workspace/notes/paper-summary.md`
- `reaper-workspace/notes/literature.md`
- `reaper-workspace/notes/problem-statement.md`
- `reaper-workspace/notes/current-understanding.md`
- `reaper-workspace/results.md`
- All `reaper-workspace/experiments/*/analysis.md` files

### 2. Identify the Central Finding

If the investigation yielded multiple findings, identify the **single most important one**. This leads the report. Ask: "If the reader remembers only one thing, what should it be?"

### 3. Write the Report

Write to `reaper-workspace/report.md` with this structure:

```markdown
# [Title: Descriptive, Not Generic]

**Central finding**: [One sentence — the single most important result]

## Contributions

[Bulleted list of specific, refutable claims. Each must be concrete enough that a reader could disagree.]

- We show that [specific claim] because [specific reason]
- We identify [specific gap/issue] in [specific location]
- We demonstrate that [specific property] holds/fails under [specific conditions]

NOT: "We analyze protocol X" or "We study the security of Y"

## Background

[Problem context. Why does this matter? What was known before this investigation?]

## Approach

[Brief: how was the investigation conducted? What methodology? How many cycles?]

## Findings

### [Finding 1: Most Important]

[Start with a CONCRETE EXAMPLE — a specific execution trace, a specific adversary strategy, a specific proof step that fails. Make the reader see the problem before explaining it abstractly.]

[Then: the general argument. Why does this happen? Under what conditions?]

[Evidence: point to specific experiments and results that support this finding.]

### [Finding 2]
...

## Discussion

- How do these findings compare to prior understanding?
- What are the implications for practitioners?
- What are the limitations of this analysis?
- What assumptions did we make that could be wrong?

## Open Questions

[Unresolved hypotheses, promising directions identified during investigation, questions that emerged but weren't pursued.]

## Appendix: Investigation Log

[Summary table from results.md — the full cycle-by-cycle record]
```

### 4. Narrative Principles (Peyton Jones)

- **Problem → why it matters → what we found → evidence → comparison**. NOT a chronological diary of the investigation.
- **Examples before generality**: always introduce a finding with a concrete case before the general argument.
- **Every claim is refutable**: if a sentence could appear in any paper about any topic, it's too vague. Cut it or make it specific.
- **One "ping"**: the report has one clear central finding stated upfront. Everything else supports or qualifies it.

### Quality Criteria

- Central finding is stated in one sentence at the top
- Every contribution is specific and refutable
- Each finding starts with a concrete example
- The report is useful standalone — a researcher who reads only this report understands the results and their significance
- No chronological narration ("first we tried X, then we tried Y") — use narrative flow instead
- Open questions are specific and actionable, not "more work is needed"
