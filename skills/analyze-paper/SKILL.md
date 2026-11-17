---
name: analyze-paper
description: "This skill extracts claims, models, proofs, and limitations from a research paper. You use it to analyze or summarize an academic paper."
user-invocable: true
argument-hint: "<paper-path> [--output <path>] [--goal \"<goal>\"]"
license: Apache-2.0
compatibility: "The host must read PDFs or extract their text."
---

# Analyze Paper

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

## Usage

You invoke this skill by name with a paper path. Slash-command hosts use `/analyze-paper <args>`.

```
analyze-paper path/to/paper.pdf
analyze-paper reaper-workspace/papers/2024-1234.pdf --goal "post-quantum threshold signatures" --output reaper-workspace/papers/2024-1234-notes.md
```

The first argument without a flag gives the paper path.

- `--output <path>` sets the output path. The default path is `reaper-workspace/notes/paper-summary.md`.
- `--goal "<text>"` supplies the research goal. This flag requires a Relevance section.

## Instructions

### 1. Read the Paper

You read the paper with the host's file tool or extract its text.
You select reading depth under [paper-analysis.md](../reaper/references/paper-analysis.md). You use the goal to select relevant sections.
You record which sections and proof steps remain unchecked. A summary does not require a new research investigation.

### 2. Extract Information

You preserve exact mathematical claims needed for the task. You distinguish quotations from paraphrases and cite source locations. You record supported differences between claims and proofs.

### 3. Write Output

You write the summary to the default path or the `--output` path.
The title is `# Paper Summary: [Paper Title]`.
You use these level-two sections:

| Section | Content |
|---|---|
| Metadata | You copy Title, Authors, Venue/Year, Paper ID, and Link. |
| Problem Statement | You explain the problem and its importance. |
| System Model | You give concrete answers for every applicable dimension in `../reaper/references/model.md`. |
| Construction Overview | You describe the protocol, technique, and components. |
| Key Results | You state the relevant claims with source locations, model, and evidence status. |
| Proof Technique | You explain lemmas, reductions, and steps that use the corruption threshold or network model. |
| Complexity Claims | You state communication, round, and computation costs. |
| Strengths | You assess novelty, methods, proofs, evaluation, and clarity. You label each strength major or minor. |
| Weaknesses | You identify incorrect methods, missing proofs, unsupported claims, unfair comparisons, and unclear text. You label each weakness major, minor, or fatal. |
| Key Definitions and Notation | You explain unusual notation and definitions that the proofs use. |
| Red Flags | You state specific concerns from `../reaper/references/paper-analysis.md`, or you state that you found none. |
| Relevance | You include this section when a research goal is supplied. You explain each applicable tag in one sentence. |

Relevance tags are `problem definition`, `formalization`, `solution technique`, `negative result`, `literature/context`, and `writing model`.

You adjust section length to the paper's content. You omit sections that do not apply, such as absent complexity claims.

## Quality Criteria

- You cover every applicable model dimension: network, adversary, trust, communication, and cryptography. You omit System Model only when unnecessary.
- The summary explains the claims and approach without the source paper.
- If PDF reading fails, you use available page extraction or rendering tools. If reading still fails, you report an error without an invented summary.
