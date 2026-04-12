---
name: synthesize
description: "Generate a research paper from investigation results, structured as a formal academic paper with definitions, theorems, lemmas, and proofs. Use when asked to synthesize, summarize, or write up research findings after investigation cycles."
user-invocable: true
argument-hint: ""
---

# Synthesize

Generate a formal research paper from all investigation results. The output should read like a publishable academic paper — not a consulting report or investigation diary.

## Usage

```
/reaper:synthesize
```

## Instructions

### 1. Re-read Workspace State (Efficiently)

Do NOT rely on context window. Re-read workspace files, but **load selectively** to stay within context limits:

**Always read:**
- `reaper-workspace/notes/current-understanding.md` — the accumulated findings (primary source)
- `reaper-workspace/notes/results.md` — the cycle-by-cycle record including batch summaries
- `reaper-workspace/notes/problem-statement.md` — model assumptions and property definitions
- `reaper-workspace/notes/ideas.md` — the ideas and their resolution status

**Read for background (skim, don't deep-read):**
- `reaper-workspace/notes/paper-summary.md` — focus on "Problem Statement" and "Red Flags" sections
- `reaper-workspace/notes/literature.md` — focus on "Landscape Summary" and "Key Prior Results" sections

**Load investigation directories selectively:**
- Read `notes/results.md` batch summaries first — these provide a condensed view of each batch's findings
- Only read `investigations/*/analysis.md` for **keep hypotheses** (check the "Status" column in `notes/results.md`). Skip discard investigations entirely. Each `analysis.md` reflects the latest state of its hypothesis (edited inline on revisit).
- If batch summaries are present and sufficient, you may skip individual `analysis.md` files for cycles already summarized
- For investigations with formal proofs (`proof.md`), only read if the report needs to cite a specific proof step

### 2. Identify the Central Result

If the investigation yielded multiple results, identify the **single most important one**. This is the main theorem of the paper. Ask: "If the reader remembers only one thing, what should it be?"

### 3. Write the Paper

Write to `reaper-workspace/report.md` following the structure of a formal academic paper. The exact sections depend on the nature of the results (new construction, impossibility, proof gap, analysis), but the general template is:

```markdown
# [Title: Descriptive, Not Generic]

## Abstract

[Problem, approach, main result(s), significance. State the main theorem informally here. No more than 350 words — be concise. Split into multiple short paragraphs if needed for readability.]

## 1. Introduction

### 1.1 Problem and Motivation
[What problem does this address? Why does it matter?]

### 1.2 Our Results
[Informal statement of main results. Each contribution must be specific and refutable — a reader could disagree.]

- **Theorem 1 (informal).** [Main result in plain language]
- **Theorem 2 (informal).** [Secondary result, if any]

NOT: "We analyze protocol X" or "We study the security of Y"

### 1.3 Related Work
[How this relates to prior work. What was known before. What gap this fills.]

### 1.4 Paper Organization
[Brief roadmap of remaining sections.]

## 2. Preliminaries

### 2.1 Notation
[Notation conventions used throughout.]

### 2.2 Model
[Formal system/threat model. Every dimension pinned down — consult the problem-statement.md model assumptions. State these as a definition if appropriate.]

### 2.3 Definitions
[Formal definitions of properties, security notions, or concepts used in theorems. Use Definition environments.]

**Definition 1** (Property Name). [Formal definition]

## 3. [Main Technical Content]

This is the core of the paper. Structure depends on the type of result:

**For new constructions or protocols:**
- Section 3: Construction (protocol description)
- Section 4: Security Analysis (theorems + proofs)
- Section 5: Performance Analysis (complexity claims + proofs)

**For proof gaps or attacks:**
- Section 3: The Claimed Result (what the original paper claimed)
- Section 4: The Gap/Attack (where and why it fails, with concrete example first)
- Section 5: Implications and Fixes (what this means, minimal repairs if any)

**For impossibility results:**
- Section 3: The Impossibility (theorem statement)
- Section 4: Proof of Impossibility
- Section 5: Circumventing the Impossibility (what additional assumptions restore possibility)

**For comparative analysis:**
- Section 3: Framework (dimensions of comparison)
- Section 4: Analysis of Each Approach (with formal claims)
- Section 5: Comparison (theorems about relative strengths/weaknesses)

Within each section, organize results as a logical chain of definitions, lemmas, theorems, and proofs:

**Lemma 1.** [Precise statement with all assumptions explicit]

*Proof.* [Step-by-step argument. Each step justified by definition, assumption, or prior lemma. End with ∎]

**Theorem 1.** [Main result — precise mathematical statement]

*Proof.* [May reference lemmas. Proof technique stated. Complete argument.]

For counterexamples and attacks, use a concrete execution trace:

**Claim 1.** [The property that fails]

*Counterexample.* Consider n = [specific value], with adversary strategy... [Concrete execution trace showing the violation.] ∎

## 4. Discussion

[Implications, limitations, comparison to prior understanding. What assumptions could be relaxed or strengthened.]

## 5. Open Questions

[Specific, actionable open problems — not "more work is needed." State each as a concrete question or conjecture.]

**Conjecture 1.** [Precise statement of what you believe but did not prove]

## References

[Papers cited during the investigation, formatted consistently. For each paper, attach a link to its PDF (e.g., arXiv, IACR ePrint, or publisher PDF URL).]

## Appendix A: Investigation Log

[Summary table from notes/results.md — the full cycle-by-cycle record for reproducibility.]
```

### 4. Writing Principles

**Structure of a formal paper, not a report:**
- Every claim is backed by a definition, theorem, lemma, or proof — not just prose assertions
- Concrete examples (execution traces, adversary strategies) appear *before* general theorems, motivating the formal result
- The logical chain must be self-contained: a reader should be able to verify each proof step from the definitions and assumptions stated in the paper

**Peyton Jones principles still apply:**
- **One "ping"**: the paper has one clear main theorem stated upfront in the abstract and introduction
- **Every claim is refutable**: if a sentence could appear in any paper about any topic, it's too vague — cut it or formalize it
- **Problem → why it matters → what we found → evidence → comparison** — NOT a chronological diary of the investigation

**Formal rigor:**
- Every theorem/lemma states its assumptions explicitly
- Proofs cite the proof technique used (reduction, simulation, induction, game-hopping, etc.)
- Distinguish between what is proven and what is conjectured — label conjectures clearly
- If a proof has gaps (e.g., a step that relies on intuition), state this honestly as a remark

### Confidence Handling

Preserve confidence levels from `notes/results.md` exactly as logged — do not upgrade. The investigate skill defaults one level lower than instinct; synthesize must not undo that calibration. Map to paper constructs: **high** → theorems with full proofs, **medium** → propositions with explicit gap statements, **low** → clearly labeled conjectures.

### Failure Recovery

If `current-understanding.md` is empty or missing, reconstruct from `results.md` batch summaries and `investigations/*/analysis.md` before writing. If both are empty, return an error — there is nothing to synthesize.

### Quality Criteria

- Main result is stated as a formal theorem in the introduction (informal) and body (formal)
- Every non-trivial claim has a corresponding theorem/lemma with proof
- Definitions are precise — no informal "safety" or "liveness" without formal predicate
- Counterexamples include concrete execution traces, not just "this can fail"
- The paper is self-contained — a reader unfamiliar with the investigation can follow the argument
- No chronological narration ("first we tried X, then we tried Y") — present the clean logical chain
- Open questions are stated as conjectures or precise problems, not vague future work
