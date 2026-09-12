---
name: synthesize
description: "This skill writes a formal research paper from investigation results. You use it to present findings with definitions, claims, and proofs."
user-invocable: true
argument-hint: ""
license: Apache-2.0
---

# Synthesize

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

This skill writes a formal research paper to `reaper-workspace/report.md`.

## Usage

You invoke this skill by name without arguments. Slash-command hosts use `/synthesize`.

```
synthesize
```

## Instructions

### 1. Read Workspace State

You use workspace files rather than conversation memory. You always read these files:

- `reaper-workspace/notes/current-understanding.md`
- `reaper-workspace/notes/results.md`, including batch summaries.
- `reaper-workspace/notes/problem-statement.md`
- `reaper-workspace/notes/ideas.md`

You read Problem Statement and Red Flags in `paper-summary.md` if that file exists. You read Landscape Summary and Key Prior Results in `literature.md`. You read batch summaries before individual investigation files. You read `investigations/*/analysis.md` only for hypotheses with status `keep`.
You can omit an analysis file when its batch summary supplies enough detail. You read `proof.md` when the report needs a specific proof step.

### 2. Identify the Main Result

You select the most important finding as the paper's central result. You preserve its confidence level when you state it.

### 3. Write the Paper

You select technical sections for the result type. You number sections in their final order.
You use this structure:

| Section | Content |
|---|---|
| Title | You name the specific result. |
| Abstract | You state the problem, approach, main result, and importance in no more than 350 words. |
| 1. Introduction | You include Problem and Motivation, Our Results, Related Work, and Paper Organization. |
| 2. Preliminaries | You define notation, model assumptions, and properties with numbered Definition entries. |
| 3. Main Technical Content | You connect definitions, lemmas, theorems, and proofs in logical order. |
| Discussion | You explain implications, limits, comparisons, and possible changes to assumptions. |
| Open Questions | You state precise problems and numbered conjectures. |
| References | You copy authors, titles, and venues from `notes/literature.md`. You include a PDF, DOI, or publisher link. |
| Appendix A: Investigation Log | You include the `notes/results.md` table and retain cycle records for reproducibility. |

You state contributions as specific informal results in the introduction.
You use numbered Lemma and Theorem entries for exact claims and assumptions.
Each Proof names its technique, justifies every step, and ends with ∎.
Each Counterexample gives parameter values, an adversary strategy, and a concrete execution trace.
Unknown venues use `(preprint)` with an archive URL.

You select the technical sections by result type:

| Result type | Technical sections |
|---|---|
| Construction or protocol | Construction; Security Analysis; Performance Analysis. |
| Proof gap or attack | The Claimed Result; The Gap/Attack; Implications and Fixes. |
| Impossibility | The Impossibility; Proof of Impossibility; Additional Assumptions. |
| Comparison | Framework; Analysis of Each Approach; Comparison. |

### 4. Apply Writing Rules

- You state the central result early in the abstract and introduction.
- You give concrete examples before general theorems.
- You support technical claims with formal arguments. Each proof supplies its assumptions, technique, and step justifications.
- You order the main sections by problem, importance, result, evidence, and comparison.
- You remove statements that do not describe a specific contribution.

## Confidence

You preserve confidence levels from `notes/results.md` without an increase.

| Confidence | Paper form |
|---|---|
| `high` | You state the result as a theorem with a complete proof. |
| `medium` | You state the result as a proposition with explicit proof gaps. |
| `low` | You label the result as a conjecture. |

The confidence rule also applies to the central result and the abstract.

## Failure Recovery

If `current-understanding.md` is empty or missing, you reconstruct findings from batch summaries and kept investigations. If those sources also lack findings, you return an error.

## Quality Criteria

- The introduction gives an informal result. The body gives the formal claim.
- Proven claims have complete proofs. Unproven claims retain their gap or conjecture labels.
- Definitions use precise predicates. Counterexamples include concrete execution traces.
- Open questions specify concrete problems or conjectures.
- Each reference names a real venue or uses `(preprint)`.
