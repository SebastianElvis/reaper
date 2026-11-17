---
name: reaper
description: "This skill investigates research goals and checks claims from papers. It selects analysis, literature, investigation, and optional publication stages for the requested scope."
user-invocable: true
argument-hint: "\"<research-goal>\" [paper-path] [--codex]"
license: Apache-2.0
compatibility: "Literature search uses Python and internet access. PDF inputs require PDF reading. Optional Codex review requires an MCP host."
---

# Reaper Research Pipeline

You apply the [language rules](references/language.md).
You use [research-state.md](references/research-state.md) as the shared contract for workspace files, budgets, hypotheses, evidence, and recovery.

## Select the Scope

You select stages from the user's goal and requested output:

| Request | Stages |
|---|---|
| Paper summary | You invoke `analyze-paper`. |
| Literature question | You invoke `review-literature`. |
| Narrow claim check | You initialize state, clarify the goal, analyze the required source, formalize the claim, investigate, and critique. You search literature only for missing evidence. |
| Open research goal | You use the research workflow below. |
| Paper or publication output | You add `write-paper` after research. |

You read the required peer `SKILL.md` files and invoke them by name through the host. You use sibling files when native invocation is unavailable.
You report missing required skills. You do not require unused stages.
The optional `--codex` flag selects external review at the critique stage. You follow [codex-consultation.md](references/codex-consultation.md).

## Research Workflow

### 1. Initialize or Resume

You read existing workspace state before creating files. You apply the shared contract without replacing prior work.
For a new run, you create only the directories and notes required by the selected stages.

### 2. Establish the Question and Evidence

You invoke `clarify-goal` with the goal and optional paper path.
For an open research goal with a paper, you run `analyze-paper` and `review-literature` independently. You use parallel subagents when the host supports them, or sequential execution otherwise.
Without a paper, you use the literature review as the baseline.
For a narrow question, you skip literature review when the supplied evidence suffices.
You wait for required source analysis before invoking `formalize-problem`.

### 3. Investigate and Review

You select unresolved hypotheses by relevance and the evidence needed to resolve them.
You invoke `brainstorm` only when existing hypotheses cannot answer the goal.
You invoke `investigate` within the remaining shared budget.
You invoke `critique --self`, or `critique --codex` when requested, to review the findings.
The critique stage returns issues and proposed next actions. The orchestrator schedules any further investigation. It does not schedule the same work twice.
You stop when the goal resolves, the budget ends, or two consecutive batches add no evidence and identify no distinct useful method.
You do not create hypotheses merely to fill a cycle quota.

If a cycle returns `reformulate`, you invoke `formalize-problem` with the triggering analysis. That skill versions the formulation and marks affected claims stale under the shared contract.
You preserve the user's original question. You present changed assumptions as separate alternatives.

### 4. Deliver the Requested Output

For an answer, you state supported findings, evidence links, unresolved claims, and limitations.
For a paper, you invoke `write-paper`. You report the venue audit and build status. You link the PDF only after a successful build.
If the publication audit needs more research, you review the missing result and use the remaining budget. You repeat this research-to-audit loop at most once.
You report unmet publication requirements without inventing results.
You state the stop reason and consumed cycle budget.

## Stage Outputs

| Skill | Output |
|---|---|
| `clarify-goal` | `notes/clarified-goal.md` |
| `analyze-paper` | `notes/paper-summary.md` or `papers/<id>-notes.md` |
| `review-literature` | `notes/literature.md`, `papers/*`, and an optional `notes/venue-bar.md` |
| `formalize-problem` | `notes/problem-statement.md`, `notes/ideas.md` |
| `brainstorm` | Updated `notes/ideas.md` |
| `investigate` | Updated findings and results; investigation files and cycle logs |
| `critique` | Review records in `feedbacks/`; proposed actions and hypotheses |
| `write-paper` | `report/main.tex`, section files, bibliography, build files, and `notes/bar-audit.md` |
| `search-paper` | Search results, downloads, citations, or venue metadata |
