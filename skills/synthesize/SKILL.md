---
name: synthesize
description: "Generate a research paper from investigation results, structured as a formal academic paper with definitions, theorems, lemmas, and proofs. Use when asked to synthesize, summarize, or write up research findings after investigation cycles."
user-invocable: true
argument-hint: ""
---

# Synthesize

Generate a formal research paper from investigation results. Output a publishable academic paper — not a report or investigation diary.

## Usage

```
/reaper:synthesize
```

## Instructions

### 1. Re-read Workspace State

Re-read workspace files (do NOT rely on context window). Load selectively:

**Always read:** `current-understanding.md`, `results.md`, `problem-statement.md`, `ideas.md` (all under `reaper-workspace/notes/`).

**Skim for background:** `paper-summary.md` (Problem Statement + Red Flags), `literature.md` (Landscape Summary + Key Prior Results). Skip if absent.

**Investigations:** Read `results.md` batch summaries first. Only load `investigations/*/analysis.md` for **keep** hypotheses. Skip discards. Only read `proof.md` files when citing a specific proof step.

If `current-understanding.md` is empty/missing, reconstruct from `results.md` and `analysis.md` files. If both are empty, return an error.

### 2. Identify the Central Result

Find the **single most important result** — the main theorem. Ask: "If the reader remembers only one thing, what should it be?"

### 3. Write the Paper

Write to `reaper-workspace/report.md`. Structure as a formal academic paper:

```markdown
# [Title: Descriptive, Not Generic]

## Abstract
[Problem, approach, main result, significance. State the main theorem informally. ≤350 words.]

## 1. Introduction

### 1.1 Problem and Motivation

### 1.2 Our Results
- **Theorem 1 (informal).** [Main result in plain language]
- **Theorem 2 (informal).** [Secondary result, if any]
Each contribution must be specific and refutable. NOT: "We analyze X" or "We study Y."

### 1.3 Related Work

### 1.4 Paper Organization

## 2. Preliminaries
Notation, formal model (pin down every dimension from problem-statement.md), definitions used in theorems.

## 3–N. Technical Sections
[See section structure rules below.]

## Discussion
Implications, limitations, what assumptions could be relaxed.

## Open Questions
Concrete conjectures or precise problems — not "more work is needed."

## References
[With PDF links (arXiv, IACR ePrint, etc.)]

## Appendix A: Investigation Log
[Summary table from results.md.]
```

#### Technical section structure

The number and topic of technical sections depends on the result type (construction, impossibility, proof gap, comparative analysis), but every technical section must follow the same rule:

**Each section is centered around exactly one main theorem.** The section title hints at the theorem's content. The body builds toward it: definitions → concrete motivating example → lemmas → theorem → proof. Ancillary results serve as stepping stones. If a section lacks a main theorem, merge it into an adjacent section or restructure until one emerges.

For counterexamples and attacks, lead with a concrete execution trace, then state the general claim.

### 4. Writing Rules

- Every claim is backed by a definition, theorem, lemma, or proof — no prose assertions
- Concrete examples appear *before* general theorems to motivate the formal result
- One clear main theorem stated in abstract and introduction ("one ping")
- Every claim is refutable — if it could appear in any paper, cut it or formalize it
- Problem → motivation → results → evidence → comparison — not chronological narration
- Every theorem/lemma states assumptions explicitly; proofs cite the technique used
- Distinguish proven results from conjectures; flag proof gaps honestly as remarks

### 5. Confidence Mapping

Preserve confidence levels from `results.md` exactly — do not upgrade. Map: **high** → theorems with full proofs, **medium** → propositions with explicit gap statements, **low** → conjectures.

### 6. Quality Checklist

- Main result is a formal theorem in both introduction (informal) and body (formal)
- Every technical section is organized around exactly one main theorem
- Every non-trivial claim has a theorem/lemma with proof
- Definitions are precise — no informal predicates
- Counterexamples include concrete execution traces
- Paper is self-contained for a reader unfamiliar with the investigation
- No chronological narration
- Open questions are conjectures or precise problems
