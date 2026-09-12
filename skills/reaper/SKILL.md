---
name: reaper
description: "This skill runs the full Reaper research pipeline. You use it with a research goal and an optional paper."
user-invocable: true
argument-hint: "\"<research-goal>\" [paper-path] [--codex]"
license: Apache-2.0
compatibility: "This skill requires python3, arxiv, requests, beautifulsoup4, internet access, and PDF reading. Codex review requires an MCP host."
---

# Reaper Research Pipeline

You must read and apply the [language rules](references/language.md) before you write any output.

## Usage

You invoke this skill by name with a quoted research goal. You can add a paper path and `--codex`. Slash-command hosts use `/reaper "..."`.

```
reaper "explore the feasibility of post-quantum threshold signatures"
reaper "determine if the security proof in Section 4 holds under asynchrony" path/to/paper.pdf
reaper "determine if the security proof in Section 4 holds under asynchrony" path/to/paper.pdf --codex
```

The research goal is required. An additional path to an existing PDF or text file identifies the paper. The `--codex` flag enables optional Codex reviews across the pipeline. You follow `references/codex-consultation.md` for that protocol.
Codex review requires an MCP host and a registered Codex MCP server. Hosts without MCP skip those reviews.

You pass `--codex` context to each skill when the flag is present. Each skill uses its specified review point and a shared session ID.

## Peer Skills

The dependency table lists all required skills.
If a skill is missing, you ask the user to run `npx skills add SebastianElvis/reaper`.

## Invocation Convention

You invoke each skill by name with the host's skill mechanism. You read its `SKILL.md` for instructions. Slash-command hosts use `/<name>`. Other hosts discover installed skills or need a pointer to `SKILL.md`. The `/<skill>` form identifies skills in these documents.

## Design Principles

- Each skill has one task. Skills exchange state through workspace files.
- Each cycle returns keep or discard. Only keep findings enter `current-understanding.md`.
- `notes/results.md` records each hypothesis's latest result. Logs preserve previous cycles.
- The pipeline runs to completion. You prefer simple proofs with fewer assumptions.

## Workflow

### Step 1: Initialize the Workspace

You create `reaper-workspace/` with `notes/`, `papers/`, `investigations/`, `feedbacks/`, and `logs/`.

You use these file rules:

| Files | Rule |
|---|---|
| `notes/current-understanding.md`, `notes/results.md`, `notes/ideas.md`, `notes/problem-statement.md`, `notes/literature.md` | One agent edits each file in place per batch. |
| `papers/*-notes.md`, `investigations/*/analysis.md`, `investigations/*/proof.md` | One agent edits each file in place per batch. |
| `logs/cycle-*.md`, `feedbacks/round-*.md`, `feedbacks/codex-consultation-*.md` | You create each file once. You never change it after creation. |
| `notes/paper-summary.md`, `notes/clarified-goal.md`, `report.md` | The responsible skill writes the file. It can regenerate the file on a rerun. Other skills do not edit it. |

The `review-literature` skill creates `notes/literature.md`. The `investigate` skill adds new literature findings in place.

Investigation directories use `NNN-<slug>/` with leading zeros. Cycle logs use `cycle-NNN-<slug>.md`. Feedback files use `round-N.md` or `codex-consultation-N.md`. Paper notes use `<id>-notes.md`.

Early stages read source files directly. Loop stages use `current-understanding.md` as their main source. They read paper summaries and literature only when a hypothesis needs them or progress stops.

You initialize `notes/results.md` with this table:

```markdown
# Investigation Results

| Cycle | Hypothesis | Action | Outcome | Confidence | Status | Description |
|-------|------------|--------|---------|------------|--------|-------------|
```

You initialize `notes/current-understanding.md` with this text:

```markdown
# Current Understanding

The investigation has no completed cycles.
```

### Step 2: Clarify the Goal

You invoke the `clarify-goal` skill with `"<research-goal>"` and the paper path, if available. It asks 3-5 questions when the scope, assumptions, or success criteria need clarification. It writes `notes/clarified-goal.md` directly if the goal is already precise. Later stages use that file for the refined goal.

### Step 3: Establish the Baseline

If the user supplies a paper, you run two independent subagents in parallel:

1. You invoke the `analyze-paper` skill with `<paper-path>` to write `notes/paper-summary.md`.
2. You invoke the `review-literature` skill with the refined goal to write `notes/literature.md`.

You use the host's parallel tool, or sequential execution if that tool is unavailable. You wait for both stages before you continue. Without a paper, you run only `review-literature`. In that mode, the workspace has no `notes/paper-summary.md`.

### Step 4: Formalize the Problem

You invoke the `formalize-problem` skill with the refined goal. It reads `clarified-goal.md`, `literature.md`, and `paper-summary.md` if available. It writes model assumptions, properties, and performance targets to `notes/problem-statement.md`. It writes initial hypotheses to `notes/ideas.md`.

### Step 5: Run the Research Loop

You repeat brainstorm, investigation, and critique stages. You assess complexity before the first brainstorm round.

| Complexity | Scope | Initial cycle plan |
|---|---|---|
| Simple | The goal has 1-3 hypotheses and one narrow claim. | You run two rounds of three cycles and one critique. |
| Moderate | The goal has 3-5 hypotheses or multiple properties. | You run two rounds of five cycles and 1-2 critiques. |
| Complex | The goal has at least five hypotheses or interacting properties. | You run at least three rounds of five cycles and two critiques. |

You invoke `brainstorm`, `investigate N`, `critique --self`, `brainstorm`, then `investigate N`.
With `--codex`, you replace `--self` with `--codex` and add `critique --codex` after the last batch.
N follows the complexity table.

You apply the first matching condition:

- If two consecutive batches contain only high-confidence keep results and no new hypotheses, you proceed to synthesis.
- Otherwise, if critique adds at least three useful hypotheses, you add an investigation batch.
- Otherwise, if all hypotheses resolve early or more than half of a batch has status `discard`, you run `brainstorm`.

The `brainstorm` skill edits `ideas.md` with source tags `[Brainstorm-N]`. The `critique` skill can add ideas with `[Codex-N]` or `[Self-N]`. The next investigation batch selects unresolved ideas. You do not ask whether the user wants the loop to continue.

#### Re-Formalization

If any cycle returns outcome `reformulate`, you take these actions:

1. You preserve results, current understanding, and investigation directories.
2. You rename `notes/problem-statement.md` to `notes/problem-statement-v<N>.md` before the next formalization.
3. You invoke the `formalize-problem` skill with the triggering cycle's `analysis.md` as context.
4. You mark ideas that depend on the old formulation `[superseded by v<N>]`.
5. You add new hypotheses below the preserved ideas.
6. You restart the loop with a new cycle budget.

### Step 6: Synthesize

You invoke the `synthesize` skill. It reads the relevant workspace evidence and writes `report.md`.

### Step 7: Present Results

You read `reaper-workspace/report.md`. You present key findings with links to the report and audit record.

### Step 8: Explain Further Iteration

You explain that quoted feedback to `critique` can start another review. Slash-command hosts can use `/critique "your feedback here"`. You do not wait for a reply. After later critique cycles, you invoke `synthesize` for an updated report.

## Dependencies and Outputs

| Skill | Required input | Output |
|---|---|---|
| `/clarify-goal` | Goal; optional paper | `notes/clarified-goal.md` |
| `/analyze-paper` | Paper; optional goal and output path | `notes/paper-summary.md` or `papers/<id>-notes.md` |
| `/review-literature` | Goal; optional paper summary | `notes/literature.md`, `papers/*` |
| `/formalize-problem` | Clarified goal, literature, optional paper summary | `notes/problem-statement.md`, `notes/ideas.md` |
| `/brainstorm` | Problem, ideas, current understanding, results | Updated `notes/ideas.md` |
| `/investigate` | Problem, ideas, current understanding, results | Updated notes; `investigations/*`, `logs/*` |
| `/critique` | Current understanding, results, problem, ideas | `feedbacks/*`; possible new ideas and cycles |
| `/synthesize` | Current understanding, results, problem, ideas | `report.md` |
| `/search-paper` | Query or paper identifier | Search results, citations, or venue |

## Failure and Context Recovery

If a skill fails, you read its output to identify the cause before you retry. If conversation context is lost, you reconstruct state from workspace files:

1. You check `reaper-workspace/notes/` for existing files.
2. You read `notes/results.md` for cycle progress.
3. You compare `ideas.md` with results to identify unresolved hypotheses.
4. You check `report.md` for completed synthesis.
5. You check `feedbacks/` for later review rounds.

| State | Action |
|---|---|
| The source paper summary is missing. | You run Step 3 if the user supplied a paper. Otherwise, you check the literature review only. |
| The problem statement is missing. | You run Step 4. |
| The results table has no rows. | You run Step 5. |
| Results exist and hypotheses remain open. | You continue Step 5. |
| All hypotheses have results and the report is missing. | You run Step 6. |
| The report exists. | You run Steps 7-8 and check for later feedback. |
