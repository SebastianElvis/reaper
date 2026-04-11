---
name: analyze-paper
description: "Extract structured information from a research paper: system model, theorem statements, proof techniques, complexity claims, and red flags. Use when asked to analyze, summarize, or review an academic paper."
user-invocable: true
argument-hint: "<paper-path>"
---

# Analyze Paper

Extract structured information from an academic paper, producing a comprehensive summary that downstream skills can build on.

## Usage

```
/reaper:analyze-paper path/to/paper.pdf
```

## Instructions

### 1. Read the Paper

Read the paper at the provided path using the Read tool (works for PDFs and text files).

Follow the three-pass strategy from `references/paper-analysis.md`:

- **Pass 1 (skeleton)**: Abstract, introduction, conclusion, theorem statements. Identify the main claims.
- **Pass 2 (construction)**: Protocol details, proof sketches, figures. Understand the key technical idea.
- **Pass 3 (proofs)**: Full formal proofs, appendices, security reductions. Verify logical steps.

### 2. Extract Information

For each section below, extract the relevant information. When extracting theorem statements or formal claims, copy them **verbatim** — do not paraphrase.

**Critical**: Distinguish what the paper *claims* (in the introduction, abstract) from what it *actually proves* (in the theorems, proofs). Note any discrepancies.

### 3. Write Output

Write the extracted information to `reaper-workspace/notes/paper-summary.md` with the following structure:

```markdown
# Paper Summary

## Metadata
- **Title**:
- **Authors**:
- **Venue/Year**:
- **Paper ID**: (ePrint, arXiv, DOI)

## Problem Statement
What problem does this paper solve? Why does it matter?

## System Model
[Extract all model dimensions relevant to the paper's domain. Consult references/model.md for the domain-appropriate dimensions to extract. Every applicable dimension must have a concrete answer.]

## Construction Overview
High-level protocol description. Key technical idea. Building blocks used.

## Claimed Security Properties
List each theorem/claim verbatim:
1. **Theorem X.X**: [exact statement]
   - Model: [exact model under which this is proved]
   - Proof technique: [game-based / simulation / reduction]

## Proof Technique
Overall proof approach. Key lemmas. Reduction chain. Where the corruption threshold and network model are used.

## Complexity Claims
- Communication: 
- Rounds:
- Computation:

## Limitations
What do the authors acknowledge? What assumptions might not hold?

## Key Definitions and Notation
Non-standard notation. Formal definitions referenced by the proofs.

## Red Flags
Any concerns identified during reading (see references/paper-analysis.md for common red flags).
```

### Quality Criteria

- Every theorem statement is copied verbatim, not paraphrased
- The system model section is complete — no missing dimensions (network, adversary, trust, communication, crypto)
- Red flags section is honest — if the paper looks solid, say so; if there are concerns, list them specifically
- The summary is useful standalone — a reader who hasn't seen the paper should understand the key claims and approach
