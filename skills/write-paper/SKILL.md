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
The paper targets the requested venue requirements. You report unmet requirements honestly. The paper separates supported results from conjectures and limitations.
You create `main.tex`, one `sections/NN-<name>.tex` file for each section, one `figures/<name>.tex` file for each figure, one `tables/<name>.tex` file for each table, `references.bib`, `Makefile`, and `.gitignore`. You do not write a Markdown paper.

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

You read `notes/clarified-goal.md` when it exists for scope.
You read Problem Statement and Red Flags in `paper-summary.md` if that file exists. You read Landscape Summary and Key Prior Results in `literature.md`. You read batch summaries before individual investigation files. You read `investigations/*/analysis.md` only for hypotheses with status `keep`.
You apply [research-state.md](../reaper/references/research-state.md). You check the evidence record for each report claim. You inspect its proof or test before presenting it as a result. You exclude stale claims from accepted conclusions. You record report section and theorem labels in each claim record in `notes/current-understanding.md`.

### 2. Read the Venue Bar

You read `reaper-workspace/notes/venue-bar.md`. The `review-literature` skill writes this file. It gives the target venue rules, the exemplar papers, and the bar checklist. You assess each checklist item. A missing result remains an unmet item.
If the file is missing, you invoke the `review-literature` skill before you continue.

### 3. Identify the Main Result

You select the most important finding as the paper's central result. You preserve its confidence level when you state it.
You compare the result with the contribution and novelty items of the bar checklist. You write the contributions so that each one states its difference from the nearest exemplar or Same-Goal Work.

### 4. Write the Paper

You use the template of the target venue from `venue-bar.md`. You use the `article` class only if the venue has no template.
You follow the venue template's section, theorem, and citation conventions when they differ from the defaults below. You add each mandatory section of the venue.
You use LaTeX section commands and automatic numbering. You select technical sections for the result type.
You use this structure:

| Section | Content |
|---|---|
| Title | You name the specific result. |
| Abstract | You state the problem, approach, main result, and importance in no more than 350 words. |
| 1. Introduction | You explain the problem and contributions. You link claims to the sections that support them. |
| 2. Preliminaries | You define notation, model assumptions, and properties with numbered Definition entries. |
| 3. Main Technical Content | You connect definitions, lemmas, theorems, and proofs in logical order. |
| Discussion | You explain implications, limits, comparisons, and possible changes to assumptions. |
| Open Questions | You state precise problems and numbered conjectures. |
| References | You copy authors, titles, and venues from `notes/literature.md`. You include a PDF, DOI, or publisher link. |

You state contributions as specific informal results in the introduction.
You add an architecture figure only when the result proposes an architecture. You add a comparison table when shared assumptions, properties, or costs support a useful comparison.
Before you make a figure or a plot, you read and apply [figures.md](../reaper/references/figures.md).
You use `amsthm` environments for numbered definitions, lemmas, theorems, propositions, and conjectures.
You use the `proof` environment for complete proofs. Each proof names its technique and justifies every step.
The `proof` environment supplies the end marker. You label incomplete arguments as proof sketches and state each gap.
Each Counterexample gives parameter values, an adversary strategy, and a concrete execution trace.
You preserve verified publication status. You label an unresolved venue `(unknown)` rather than assuming preprint status.

You select the technical sections by result type:

| Result type | Technical sections |
|---|---|
| Construction or protocol | Construction; Security Analysis; Performance Analysis. |
| Proof gap or attack | The Claimed Result; The Gap/Attack; Implications and Fixes. |
| Impossibility | The Impossibility; Proof of Impossibility; Additional Assumptions. |
| Comparison | Framework; Analysis of Each Approach; Comparison. |

### 5. Report Only Final Results

The workspace records the research process. The paper presents only the final results.

- You do not include cycle numbers, batch numbers, hypothesis labels such as `H3`, keep or discard status, idea source tags, or the results table.
- You do not describe the research history. Examples are early runs, abandoned designs, superseded definitions, discarded hypotheses, and corrections between versions.
- You present the final definitions, design, proofs, and evaluation protocol. For repeated experiments, you report the evaluation protocol, variation across relevant runs, and exclusions. You do not select only the best or final run.
- You state a refuted claim only as a final result, such as a counterexample or an impossibility theorem.
- You describe code, data, and commands for reproducibility in an artifact section or appendix. That section describes the final artifact, not the process.

### 6. Create the LaTeX Project

- You write each section, including the abstract and each appendix, in its own file `sections/NN-<name>.tex`. `NN` is the order of the section in the paper, for example `sections/01-introduction.tex`.
- You write `main.tex` with the document class, package declarations, title, and document environment. Its body contains only `\maketitle`, `\input{sections/NN-<name>}` commands in section order, `\appendix` before the first appendix, and the bibliography commands.
- You write each figure in its own file `figures/<name>.tex` and each table in its own file `tables/<name>.tex`. Each file contains the complete `figure` or `table` environment with its caption and label. The section file includes it with `\input{figures/<name>}` or `\input{tables/<name>}`. You do not write a `figure` or `table` environment in `main.tex` or in a section file.
- You define each theorem environment before use. You load `amsmath` and `amssymb` for mathematics, `tikz` for figures, `pgfplots` for plots, and `hyperref` for links.
- You use LaTeX math, lists, and tables. You escape reserved characters in prose, paths, and bibliography fields.
- You create `references.bib` from verified entries in `notes/literature.md`. You preserve authors, titles, and venues. You include DOI or URL fields. With the `plain` style, you also put a `\url{}` link in the `note` field so the reference displays the link. You do not invent missing metadata.
- You use the venue's citation and bibliography conventions. Without venue requirements, you use `\cite{key}`, `\bibliographystyle{plain}`, and `\bibliography{references}`. Each citation key must match a bibliography entry.
- You use unique `\label{}` keys and `\ref{}` for section, theorem, and equation references.
- You make the default `Makefile` target run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. You add a `clean` target that runs `latexmk -C`. You use a tab for each recipe line.
- You write a `.gitignore` that ignores LaTeX build files: `*.aux`, `*.bbl`, `*.blg`, `*.fdb_latexmk`, `*.fls`, `*.log`, `*.out`, `*.synctex.gz`, `*.toc`, and `main.pdf`.

### 7. Apply Writing Rules

- You state the central result early in the abstract and introduction.
- You give concrete examples before general theorems.
- You support technical claims with formal arguments. Each proof supplies its assumptions, technique, and step justifications.
- You order the main sections by problem, importance, result, evidence, and comparison.
- You remove statements that do not describe a specific contribution.
- You use the terms that the related work in `notes/literature.md` uses for each concept. If sources use different terms, you use the most common term.
- You do not make a new term for a known concept. You avoid jargon. If you must add a new term, you define it at first use and name the nearest term from related work.
- You do not use Reaper workflow terms, such as cycle, batch, hypothesis status, or investigation.

### 8. Validate the Paper

You run `make` from `reaper-workspace/report/` when LaTeX tools are available.
You fix compilation errors, missing citations, and unresolved references. You rebuild after each correction.
You inspect `main.pdf` for clipped equations, table overflow, and unreadable text when PDF inspection is available.
You search the PDF text for the patterns `cycle [0-9]`, `batch`, `H[0-9]+`, `hypothes`, `investigation`, and `Reaper`. You remove each match that describes the research process.

### 9. Audit Against the Venue Bar

You check the paper against each item of the bar checklist. You write `reaper-workspace/notes/bar-audit.md` with one row per item: the item number, `PASS`, `PARTIAL`, or `FAIL`, and the evidence.
You fix each format, structure, and writing failure in the paper. You then rebuild and audit again.
You do not invent results to pass an item. If an item needs a new result, you mark it `FAIL` and name the missing result.

### 10. Report

You report the target venue, the audit count for each status, and each item that needs a new result. You suggest the `critique` skill with that item as feedback.
You report the build result and link to the source files. You link to `main.pdf` only after a successful build.
If a tool or package is missing, you deliver the source files and name the missing dependency. You state which checks you could not complete.

## Confidence

You preserve confidence levels from `notes/results.md` without an increase.

| Confidence | Paper form |
|---|---|
| `high` | You use a theorem only for a verified complete proof. You report tests as tests with their scope. |
| `medium` | You label the claim unproven and state each proof gap. |
| `low` | You label the result as a conjecture. |

The confidence rule also applies to the central result and the abstract.

## Failure Recovery

If `current-understanding.md` is empty or missing, you reconstruct findings from batch summaries and kept investigations. If those sources also lack findings, you return an error.
