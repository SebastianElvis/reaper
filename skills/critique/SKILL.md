---
name: critique
description: "Provide critique on investigation results via human feedback, Codex consultation, or self-review. Can trigger additional investigation cycles for deepen/explore feedback. Use when iterating on research, requesting AI review, or providing human feedback."
user-invocable: true
argument-hint: "\"<feedback>\" | --codex | --self"
---

# Critique

Provide external perspective on investigation results. Three modes: human feedback, Codex consultation, and self-review. Can trigger additional investigation cycles when feedback requires deeper exploration.

## Usage

```
# Human feedback — iterate on existing results
/reaper:critique "dig deeper into the liveness proof gap under partial synchrony"

# Codex consultation — get AI devil's advocate or inspiration
/reaper:critique --codex

# Self-review — agent reviews its own findings for gaps
/reaper:critique --self
```

## Inputs

Read before starting:
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/results.md` — what's been tried and what happened
- `reaper-workspace/notes/problem-statement.md` — the ideas to investigate

Also reference:
- `reaper-workspace/notes/paper-summary.md` — the source paper
- `reaper-workspace/notes/literature.md` — known prior work
- `reaper-workspace/papers/` — downloaded PDFs and per-paper notes
- `reaper-workspace/feedback/` — prior feedback rounds

## Mode: Human Feedback

When the argument is quoted text, the skill enters human feedback mode. This is used after investigation has produced results and the user wants to refine, deepen, or challenge specific findings.

### 1. Determine the Feedback Round

Check `reaper-workspace/feedback/` for existing `round-*.md` files. The new round number is one greater than the highest existing round, or 1 if none exist.

### 2. Classify and Save Feedback

Classify the user's feedback and write `reaper-workspace/feedback/round-N.md`:

```markdown
# Feedback Round N

**User request**: [the user's feedback, verbatim or lightly paraphrased]

**Category**: [scope | deepen | explore | rewrite]

**Action plan**: [what will be done]
```

Categories:

| Category | Signal | Example |
|---|---|---|
| **scope** | Change assumptions, threat model, or framing | "What if we assume a stronger adversary?" |
| **deepen** | Dig into a specific claim, finding, or proof step | "The proof gap in Theorem 3 — find a concrete counterexample" |
| **explore** | Investigate an area the report didn't cover | "What about liveness under partial synchrony?" |
| **rewrite** | Improve clarity, structure, or presentation only | "Make the contributions more concrete" |

### 3. Execute

**scope**: Return control to the orchestrator — this requires re-running `formalize-problem` before investigation. Do not run cycles yourself; instead, write the feedback file and indicate that re-formalization is needed.

**deepen**: Run `/reaper:brainstorm "context from the user's feedback"` to generate targeted hypotheses based on the feedback, then run `/reaper:investigate 5`.

**explore**: If the area may need additional literature, use the search scripts first and update `literature.md`. Then run `/reaper:brainstorm "context from the user's feedback"` to generate hypotheses for the new area, followed by `/reaper:investigate 5`.

**rewrite**: No investigation cycles needed. Return control to the orchestrator to re-run `synthesize` only.

For **deepen** and **explore**, after completing the cycles, the orchestrator should re-run `synthesize` to produce an updated report.

## Mode: Codex Consultation (`--codex`)

Consult an external AI (OpenAI Codex via MCP) for an independent second opinion on the current investigation state. This establishes an automated feedback loop where Codex plays **devil's advocate** or provides **alternative inspiration**.

**Requires**: The `codex-cli` MCP server registered with Claude Code (see [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server)): `claude mcp add codex-cli -- npx -y codex-mcp-server`.

**Fallback**: If the Codex MCP tools are unavailable (server not registered, connection failure, etc.), skip the consultation step silently and continue. Log a note in the experiment directory that Codex consultation was requested but unavailable.

### Determining the Role

Check `reaper-workspace/experiments/` for existing `codex-consultation-*.md` files. Count them to determine the consultation number N. Alternate roles:

- **Devil's Advocate** (odd N: 1st, 3rd, 5th, ...):
  Ask Codex to challenge the current findings. Send it:
  - The current `current-understanding.md`
  - The latest results from `results.md`
  - The prompt: *"You are reviewing a research investigation. Play devil's advocate: identify the weakest claims, unstated assumptions, logical gaps, or alternative explanations that the investigators may have missed. Be specific — point to exact claims and explain why they might be wrong."*

- **Inspiration / Alternative Angles** (even N: 2nd, 4th, 6th, ...):
  Ask Codex for fresh perspectives. Send it:
  - The current `current-understanding.md`
  - The current `problem-statement.md` (unresolved only)
  - The prompt: *"You are consulting on a research investigation. Suggest alternative proof strategies, related techniques from other fields, or hypotheses the investigators haven't considered. Focus on non-obvious connections and approaches that could break through current blockers."*

### Processing Codex Feedback

1. **Log** the Codex response to `reaper-workspace/experiments/codex-consultation-N.md`.
2. **Triage** the feedback:
   - **Actionable critique**: If Codex identifies a genuine gap or flaw, add a new hypothesis to `problem-statement.md` marked `[Codex-N]`.
   - **Alternative approach**: If Codex suggests a promising technique, add it as a hypothesis marked `[Codex-N]`.
   - **Already addressed**: Note this in the consultation log and move on.
   - **Irrelevant or wrong**: Dismiss with a brief note in the log.
3. **Do not block** on Codex feedback. If the MCP call times out or fails, log the failure and return.

### Session Continuity

Use a single Codex session ID across all consultations within one investigation run. This allows Codex to build context across consultations. Pass the `sessionId` parameter to the `codex` tool, using a consistent ID like `"reaper-critique-<timestamp>"`.

## Mode: Self-Review (`--self`)

The agent reviews its own investigation results for gaps, inconsistencies, or missed angles.

### Process

1. Read `current-understanding.md`, `results.md`, and `problem-statement.md`.
2. Identify:
   - **Weak claims**: Findings with low or medium confidence that haven't been strengthened.
   - **Untested assumptions**: Assumptions listed in hypotheses or proofs that haven't been validated.
   - **Missing angles**: Obvious questions raised by the current findings that haven't been investigated.
   - **Inconsistencies**: Claims in `current-understanding.md` that conflict with each other or with `results.md`.
3. Write the self-review to `reaper-workspace/experiments/self-review-N.md` (where N is one more than the count of existing self-review files).
4. For each actionable finding, add a hypothesis to `problem-statement.md` marked `[Self-N]`.
5. If actionable hypotheses were added, run `/reaper:investigate 3` to address them.

## Quality Criteria

- Every critique mode produces a logged artifact in `reaper-workspace/experiments/` or `reaper-workspace/feedback/`
- Human feedback is classified before action is taken
- Codex consultations alternate between devil's advocate and inspiration roles
- Self-reviews identify specific, actionable gaps — not vague concerns
- New hypotheses generated by critique are tagged with their source (`[Round N]`, `[Codex-N]`, `[Self-N]`)
- When critique triggers investigation cycles, results flow back through the normal investigation pipeline
