---
name: critique
description: "This skill reviews research findings with user feedback, Codex, or self-review. You use it to check results or direct more investigation."
user-invocable: true
argument-hint: "\"<feedback>\" | --codex | --self"
license: Apache-2.0
compatibility: "Codex mode requires a host with available Codex MCP review tools. Other modes need no additional tools."
---

# Critique

You apply the [language rules](../reaper/references/language.md) and [research-state.md](../reaper/references/research-state.md).
You review findings and return proposed actions. You do not start investigation cycles from this skill.

## Inputs and Modes

You read `notes/current-understanding.md`, `notes/results.md`, `notes/problem-statement.md`, `notes/ideas.md`, and previous feedback in `reaper-workspace/`.
You inspect source papers and proof files for the specific claims under review.
Quoted feedback selects human review. `--self` selects self-review. `--codex` selects external review.

## Human Feedback

You preserve the user's exact feedback in `feedbacks/round-N.md`.
You split mixed requests and classify each request:

| Category | Proposed action |
|---|---|
| `scope` | The orchestrator invokes `formalize-problem` before further investigation. |
| `deepen` | The orchestrator investigates a specific evidence gap. |
| `explore` | The orchestrator searches or brainstorms only when existing evidence and ideas do not cover the request. |
| `rewrite` | The orchestrator revises the requested answer or paper without new research. |

## Self-Review

You check incompatible claims, unsupported assumptions, proof gaps, source errors, and stale dependencies.
You distinguish a failed proof from a false theorem. You require evidence before accepting a proposed correction.
You record findings in `feedbacks/round-N.md` with mode `self`.

## External Review

You follow [codex-consultation.md](../reaper/references/codex-consultation.md) for evidence, session continuity, logging, and fallback.
You ask the reviewer to check the exact claim and its supporting argument.
You request alternative approaches only for unresolved questions where alternatives could help.
You use the next unused consultation number. You do not choose a review role by odd or even numbering.

## Record and Return

You choose N as one greater than the highest existing number for the selected feedback filename prefix.
Each record contains the mode, claims reviewed, evidence, issues, proposed actions, and limitations.
You add only distinct, actionable hypotheses under the shared hypothesis rules. You tag their source `[Round N]`, `[Self-N]`, or `[Codex-N]`.
You explain why prior evidence rejects or already covers a suggestion.
Review records do not consume investigation cycles. Any new proof attempt, counterexample search, or experiment belongs to a reserved investigation cycle.
You return the proposed actions to the orchestrator. For standalone use, you report them to the user without starting a research loop.
