# Codex Consultation Protocol

Shared protocol for consulting an external AI model (OpenAI Codex via MCP) from any skill in the pipeline. When the `--codex` flag is set, every skill may optionally consult Codex at a natural checkpoint — after its main work but before writing final output.

## Setup

**Requires**: The `codex-cli` MCP server registered with Claude Code (see [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server)):
```
claude mcp add codex-cli -- npx -y codex-mcp-server
```

## Fallback

If the Codex MCP tools are unavailable (server not registered, connection failure, timeout), **skip silently and continue**. Log a note in the skill's output file that Codex consultation was requested but unavailable. Never block the pipeline on Codex.

## Session Continuity

Use a single Codex session ID across all consultations within one pipeline run. This allows Codex to build context across skills and consultations. Pass the `sessionId` parameter to the `codex` tool, using a consistent ID like `"reaper-<timestamp>"`.

## Context Compression

Always send **compressed context** to Codex — never full workspace files. Each skill defines what to send (see per-skill sections below), but the general rules are:

- **Cap at ~800 words** of input context per consultation
- Extract only the information Codex needs to answer the specific question
- Include a 1-sentence framing of the research goal for orientation
- Prefer summaries over raw data (batch summaries over full results.md rows, key findings over full current-understanding.md)

## Logging

Log every Codex consultation to the skill's own output file (e.g., a `## Codex Consultation` section at the end) with:
- Timestamp
- What was asked
- Summary of response (1-2 sentences)
- Whether any action was taken (e.g., hypothesis added, output revised)

## Per-Skill Consultation Patterns

### analyze-paper
**When**: After extracting paper information, before writing `paper-summary.md`.
**Ask**: "Here is a summary of a research paper's claims and proof techniques. What red flags or claims-vs-proofs discrepancies might I have missed?"
**Send**: The draft system model + claimed properties + red flags sections (~400 words).
**Act on**: Add any flagged issues to the Red Flags section of `paper-summary.md`.

### review-literature
**When**: After merging search results, before writing `literature.md`.
**Ask**: "Given this research goal and the related work I found, are there important papers, authors, or search terms I may have missed?"
**Send**: Research goal (1 sentence) + list of found paper titles (~300 words).
**Act on**: Run additional searches for any suggested terms; add results to the literature survey.

### formalize-problem
**When**: After drafting hypotheses, before writing `ideas.md`.
**Ask**: "Here are the hypotheses I plan to investigate for this research goal. Are any poorly formed, redundant, or obviously contradicting known results? Am I missing an important angle?"
**Send**: Research goal (1 sentence) + model assumptions summary + hypothesis list (~500 words).
**Act on**: Revise, merge, or add hypotheses based on feedback. Tag any Codex-suggested hypotheses `[Codex-F]`.

### brainstorm
**When**: After generating candidate ideas, before appending to `ideas.md`.
**Ask**: "Given these investigation results so far and the new ideas I'm considering, what non-obvious angles or cross-domain connections am I missing?"
**Send**: Last 3 batch summaries from `results.md` + candidate ideas (~500 words).
**Act on**: Add promising suggestions as hypotheses tagged `[Codex-B]`. Discard obvious or redundant ones.

### investigate
**When**: Within a cycle, only when the "when stuck" protocol has been partially exhausted (after steps 1-4 of the escalation, before steps 5-6).
**Ask**: "I'm stuck on this hypothesis. Here is what I've tried and where I'm blocked. What proof technique, counterexample strategy, or reframing might help?"
**Send**: Hypothesis statement + what was tried + where it's blocked (~400 words).
**Act on**: Try the suggested approach in the current cycle. Log whether it helped.

### critique
**When**: This skill has its own dedicated Codex consultation mode (`--codex`). See the critique SKILL.md for the full devil's advocate / inspiration protocol.

### synthesize
**When**: After drafting the report, before writing final `report.md`.
**Ask**: "Here is the central finding and contributions of a research report. Are the claims clearly stated and well-supported? Any logical gaps or unclear arguments?"
**Send**: Central finding + contributions list + 1-sentence summary of each finding (~500 words).
**Act on**: Revise contributions for clarity; strengthen or qualify claims based on feedback.
