---
name: analyze-paper
description: "Extract structured information from a research paper: system model, theorem statements, proof techniques, complexity claims, and red flags. Use when asked to analyze, summarize, or review an academic paper."
user-invocable: true
argument-hint: "<paper-path> [--output <path>] [--goal \"<goal>\"]"
license: Apache-2.0
compatibility: "Requires PDF reading capability for the paper under analysis."
---

# Analyze Paper

Extract structured information from an academic paper, producing a comprehensive summary that downstream skills can build on.

## Usage

Invoke this skill by name with the paper path (and optional flags). On slash-command hosts, prefix with `/` (e.g. `/analyze-paper <args>`).

```
# Analyze the primary paper under study
analyze-paper path/to/paper.pdf

# Analyze a literature paper with research goal as context
analyze-paper reaper-workspace/papers/2024-1234.pdf --goal "post-quantum threshold signatures" --output reaper-workspace/papers/2024-1234-notes.md
```

**Argument parsing:** The first non-flag argument is the paper path. Optional flags:
- `--output <path>`: Write output to the given path instead of the default `reaper-workspace/notes/paper-summary.md`.
- `--goal "<text>"`: The research goal as additional context. When provided, the output includes a **Relevance** section assessing how the paper relates to this goal, and reading depth is calibrated by relevance (see Step 1).


## Instructions

### 1. Read the Paper

Read the paper at the provided path using your host's file-read primitive (works for PDFs and text files on hosts that support PDF reading; otherwise extract text first).

Follow the three-pass strategy from `../reaper/references/paper-analysis.md`:

- **Pass 1 (skeleton)**: Abstract, introduction, conclusion, theorem statements. Identify the main claims.
- **Pass 2 (construction)**: Protocol details, proof sketches, figures. Understand the key technical idea.
- **Pass 3 (proofs)**: Full formal proofs, appendices, security reductions. Verify logical steps.

When `--goal` is provided, calibrate depth by relevance to the goal: Pass 1 for all papers; Pass 2 for medium-relevance; all three passes for high-relevance papers.

### 2. Extract Information

For each section below, extract the relevant information. When extracting theorem statements or formal claims, copy them **verbatim** — do not paraphrase.

**Critical**: Distinguish what the paper *claims* (in the introduction, abstract) from what it *actually proves* (in the theorems, proofs). Note any discrepancies.

### 3. Write Output

Write the extracted information to `reaper-workspace/notes/paper-summary.md` (or the path specified by `--output`) with the following structure:

```markdown
# Paper Summary: [Paper Title]

## Metadata
- **Title**:
- **Authors**:
- **Venue/Year**:
- **Paper ID**: (ePrint, arXiv, DOI)
- **Link**: (e.g., https://arxiv.org/abs/XXXX.XXXXX or https://eprint.iacr.org/YYYY/NNNN)

## Problem Statement
What problem does this paper solve? Why does it matter?

## System Model
[Extract all model dimensions relevant to the paper's domain. Consult `../reaper/references/model.md` for the domain-appropriate dimensions to extract. Every applicable dimension must have a concrete answer.]

## Construction Overview
High-level protocol description. Key technical idea. Building blocks used.

## Key Results
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

## Strengths
[Label each major/minor: novelty, methodology fit, proof rigor, evaluation quality, clarity.]

## Weaknesses
[Label each major/minor/fatal: broken methodology, missing proofs, unjustified claims, unfair comparisons, unclear writing, overclaimed results.]

## Key Definitions and Notation
Non-standard notation. Formal definitions referenced by the proofs.

## Red Flags
Any concerns identified during reading (see `../reaper/references/paper-analysis.md` for common red flags).

## Relevance
[Present ONLY when --goal is provided. Tag one or more: *problem definition*, *formalization*, *solution technique*, *negative result*, *literature/context*, *writing model*. One sentence per tag explaining how this paper relates to the research goal.]
```

Sections should be **proportional to what the paper warrants**. If a paper has no complexity claims, omit that section. If the proof technique is trivial, keep it brief. The template is a guide, not a form to fill in mechanically.

### Quality Criteria

- Every theorem statement is copied verbatim, not paraphrased
- The system model section is complete — no missing dimensions (network, adversary, trust, communication, crypto)
- Strengths and weaknesses are labeled with severity (major/minor/fatal) and are honest — if the paper looks solid, say so; if there are concerns, list them specifically
- Red flags section is honest — no concerns is a valid answer
- The summary is useful standalone — a reader who hasn't seen the paper should understand the key claims and approach
- When `--goal` is provided, relevance tags are specific to the goal, not generic ("related to our topic")
- If the PDF is unreadable, try page-by-page with the `pages` parameter. If it still fails, report the error — do not fabricate a summary
