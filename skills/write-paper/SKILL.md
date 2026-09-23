---
name: write-paper
description: "This skill writes a formal LaTeX research paper from investigation results. You use it to present findings with definitions, claims, and proofs."
user-invocable: true
argument-hint: ""
license: Apache-2.0
---

# Write Paper

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

This skill writes a LaTeX research paper in `reaper-workspace/report/`.
You create `main.tex`, one `sections/NN-<name>.tex` file for each section, `references.bib`, `Makefile`, and `.gitignore`. You do not write a Markdown paper.

## Usage

You invoke this skill by name without arguments. Slash-command hosts use `/write-paper`.

```
write-paper
```

## Instructions

### 1. Read Workspace State

You use workspace files rather than conversation memory. You always read these files:

- `reaper-workspace/notes/current-understanding.md`
- `reaper-workspace/notes/results.md`, including batch summaries.
- `reaper-workspace/notes/problem-statement.md`
- `reaper-workspace/notes/ideas.md`

You read `notes/clarified-goal.md` when it exists for scope and venue requirements.
You read Problem Statement and Red Flags in `paper-summary.md` if that file exists. You read Landscape Summary and Key Prior Results in `literature.md`. You read batch summaries before individual investigation files. You read `investigations/*/analysis.md` only for hypotheses with status `keep`.
You can omit an analysis file when its batch summary supplies enough detail. You read `proof.md` when the report needs a specific proof step.

### 2. Identify the Main Result

You select the most important finding as the paper's central result. You preserve its confidence level when you state it.

### 3. Write the Paper

You use the `article` class unless the user specifies a venue template.
You follow the venue template's theorem and citation conventions when they differ from the defaults below.
You use LaTeX section commands and automatic numbering. You select technical sections for the result type.
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
| Appendix A: Investigation Log | You convert the `notes/results.md` table to LaTeX. You retain cycle identifiers for reproducibility. |

You state contributions as specific informal results in the introduction.
The introduction must contain Figure 1 and Table 1. Figure 1 shows the main architecture of the proposed approach. You draw it with TikZ.
Table 1 compares this paper with the Same-Goal Works in `notes/literature.md`. Its columns are the assumptions, properties, and costs that the papers share. Its last row is this paper.
You use `amsthm` environments for numbered definitions, lemmas, theorems, propositions, and conjectures.
You use the `proof` environment for complete proofs. Each proof names its technique and justifies every step.
The `proof` environment supplies the end marker. You label incomplete arguments as proof sketches and state each gap.
Each Counterexample gives parameter values, an adversary strategy, and a concrete execution trace.
You use `(preprint)` with an archive URL when the venue is unknown.

You select the technical sections by result type:

| Result type | Technical sections |
|---|---|
| Construction or protocol | Construction; Security Analysis; Performance Analysis. |
| Proof gap or attack | The Claimed Result; The Gap/Attack; Implications and Fixes. |
| Impossibility | The Impossibility; Proof of Impossibility; Additional Assumptions. |
| Comparison | Framework; Analysis of Each Approach; Comparison. |

### 4. Create the LaTeX Project

- You write each section, including the abstract and each appendix, in its own file `sections/NN-<name>.tex`. `NN` is the order of the section in the paper, for example `sections/01-introduction.tex`.
- You write `main.tex` with the document class, package declarations, title, and document environment. Its body contains only `\maketitle`, `\input{sections/NN-<name>}` commands in section order, `\appendix` before the first appendix, and the bibliography commands.
- You define each theorem environment before use. You load `amsmath` and `amssymb` for mathematics, `tikz` for figures, and `hyperref` for links.
- You use LaTeX math, lists, and tables. You escape reserved characters in prose, paths, and bibliography fields.
- You create `references.bib` from verified entries in `notes/literature.md`. You preserve authors, titles, and venues. You include DOI or URL fields. With the `plain` style, you also put a `\url{}` link in the `note` field so the reference displays the link. You do not invent missing metadata.
- You use `\cite{key}` for citations, `\bibliographystyle{plain}`, and `\bibliography{references}`. Each citation key must match a bibliography entry.
- You use unique `\label{}` keys and `\ref{}` for section, theorem, and equation references.
- You make the default `Makefile` target run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. You add a `clean` target that runs `latexmk -C`. You use a tab for each recipe line.
- You write a `.gitignore` that ignores LaTeX build files: `*.aux`, `*.bbl`, `*.blg`, `*.fdb_latexmk`, `*.fls`, `*.log`, `*.out`, `*.synctex.gz`, `*.toc`, and `main.pdf`.

### 5. Apply Writing Rules

- You state the central result early in the abstract and introduction.
- You give concrete examples before general theorems.
- You support technical claims with formal arguments. Each proof supplies its assumptions, technique, and step justifications.
- You order the main sections by problem, importance, result, evidence, and comparison.
- You remove statements that do not describe a specific contribution.
- You use the terms that the related work in `notes/literature.md` uses for each concept. If sources use different terms, you use the most common term.
- You do not make a new term for a known concept. You avoid jargon. If you must add a new term, you define it at first use and name the nearest term from related work.
- You do not use Reaper workflow terms, such as cycle, batch, or hypothesis status, outside Appendix A.

### 6. Validate the Paper

You run `make` from `reaper-workspace/report/` when LaTeX tools are available.
You fix compilation errors, missing citations, and unresolved references. You rebuild after each correction.
You inspect `main.pdf` for clipped equations, table overflow, and unreadable text when PDF inspection is available.
You report the build result and link to the source files. You link to `main.pdf` only after a successful build.
If a tool or package is missing, you deliver the source files and name the missing dependency. You state which checks you could not complete.

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
- Figure 1 shows the main architecture. Table 1 compares Same-Goal Works with this paper.
- Proven claims have complete proofs. Unproven claims retain their gap or conjecture labels.
- Definitions use precise predicates. Counterexamples include concrete execution traces.
- Terms match the related work. Each new term has a definition at first use.
- Open questions specify concrete problems or conjectures.
- Each reference names a real venue or uses `(preprint)`.
