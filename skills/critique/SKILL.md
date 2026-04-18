---
name: critique
description: "Provide critique on investigation results via human feedback, Codex consultation, or self-review. Can trigger additional investigation cycles for deepen/explore feedback. Use when iterating on research, requesting AI review, or providing human feedback."
user-invocable: true
argument-hint: "\"<feedback>\" | --codex | --self"
---

# Critique

Provide external perspective on investigation results. Three modes: human feedback, Codex consultation, and self-review. Can trigger additional investigation cycles when feedback requires deeper exploration.

## Usage

Invoke this skill by name; pass either feedback as a quoted string, `--codex`, or `--self`. On slash-command hosts, prefix with `/reaper:` (e.g. `/reaper:critique "<feedback>"`).

```
# Human feedback — iterate on existing results
critique "dig deeper into the liveness proof gap under partial synchrony"

# External-model consultation — get AI devil's advocate or inspiration (requires MCP host)
critique --codex

# Self-review — agent reviews its own findings for gaps
critique --self
```

## Path Resolution Protocol

This skill references files in sibling skills. **`{{REAPER_SKILL_DIR}}`** below is a template placeholder — **you MUST substitute it with the absolute install path of the `/reaper` skill before reading, or the read will fail.** Common install locations:

- `~/.claude/skills/reaper/` (Claude Code)
- `~/.cursor/skills/reaper/` (Cursor)
- `~/.agents/skills/reaper/` (Codex CLI, Cline, Gemini CLI, Copilot, OpenCode, Warp, Goose, Replit — universal target)
- `~/.continue/skills/reaper/` (Continue)
- `~/.windsurf/skills/reaper/` (Windsurf)
- `<repo-root>/skills/reaper/` (during repo development)

**Sibling-skill dependency**: This skill assumes the full `/reaper` package was installed together (`npx skills add SebastianElvis/reaper`). Single-skill installs will fail to resolve sibling references.

## Inputs

**Always read** before starting:
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/notes/results.md` — what's been tried and what happened
- `reaper-workspace/notes/problem-statement.md` — model assumptions and property definitions
- `reaper-workspace/notes/ideas.md` — the ideas to investigate
- `reaper-workspace/feedbacks/` — prior feedback rounds

**Lazy-load only when needed:**
- `reaper-workspace/notes/paper-summary.md` — the source paper (if provided)
- `reaper-workspace/notes/literature.md` — known prior work
- `reaper-workspace/papers/` — downloaded PDFs and per-paper notes

## Mode: Human Feedback

When the argument is quoted text, the skill enters human feedback mode. This is used after investigation has produced results and the user wants to refine, deepen, or challenge specific findings.

### 1. Determine the Feedback Round

Check `reaper-workspace/feedbacks/` for existing `round-*.md` files. The new round number is one greater than the highest existing round, or 1 if none exist.

### 2. Classify and Save Feedback

Classify the user's feedback and write `reaper-workspace/feedbacks/round-N.md`:

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

**scope**: Return control to the orchestrator — this requires re-running `/formalize-problem` before investigation. Do not run cycles yourself; instead, write the feedback file and indicate that re-formalization is needed.

**deepen**: Invoke the `/brainstorm` skill with `"context from the user's feedback"` to generate targeted hypotheses based on the feedback, then invoke the `/investigate` skill with argument `5`.

**explore**: If the area may need additional literature, use the search scripts first and update `literature.md`. Then invoke the `/brainstorm` skill with `"context from the user's feedback"` to generate hypotheses for the new area, followed by the `/investigate` skill with argument `5`.

**rewrite**: No investigation cycles needed. Return control to the orchestrator to re-run `/synthesize` only.

For **deepen** and **explore**, after completing the cycles, the orchestrator should re-run `/synthesize` to produce an updated report.

## Mode: Codex Consultation (`--codex`)

Consult an external AI (OpenAI Codex via MCP) for an independent second opinion on the current investigation state. This establishes an automated feedback loop where Codex plays **devil's advocate** or provides **alternative inspiration**.

See `{{REAPER_SKILL_DIR}}/references/codex-consultation.md` (placeholder defined in the Path Resolution Protocol section above) for MCP setup, fallback behavior, session continuity, and context compression rules. The critique skill's Codex mode is the most thorough consultation — other skills have lighter-weight checkpoint consultations.

### Determining the Role

Check `reaper-workspace/feedbacks/` for existing `codex-consultation-*.md` files. Count them to determine the consultation number N. Alternate roles:

- **Devil's Advocate** (odd N: 1st, 3rd, 5th, ...):
  Ask Codex to challenge the current findings. Send it a **compressed context** (not full files):
  - The **last 5 findings** from `current-understanding.md` (extract the most recent insights, ~500 words — not the full file)
  - A **summary row** from `notes/results.md` (e.g., "Last 10 cycles: 6 keep, 4 discard; key patterns: [list]")
  - The prompt: *"You are reviewing a research investigation. Play devil's advocate: identify the weakest claims, unstated assumptions, logical gaps, or alternative explanations that the investigators may have missed. Be specific — point to exact claims and explain why they might be wrong."*

- **Inspiration / Alternative Angles** (even N: 2nd, 4th, 6th, ...):
  Ask Codex for fresh perspectives. Send it a **compressed context**:
  - The **last 5 findings** from `current-understanding.md` (~500 words)
  - The **unresolved hypotheses only** from `ideas.md` (skip resolved ones)
  - The prompt: *"You are consulting on a research investigation. Suggest alternative proof strategies, related techniques from other fields, or hypotheses the investigators haven't considered. Focus on non-obvious connections and approaches that could break through current blockers."*

**Context efficiency**: Sending compressed context (~800 words) to Codex instead of full files (~5000 words) reduces latency and improves response quality by focusing Codex on what matters most.

### Processing Codex Feedback

1. **Log** the Codex response to `reaper-workspace/feedbacks/codex-consultation-N.md`.
2. **Triage** the feedback:
   - **Actionable critique**: If Codex identifies a genuine gap or flaw, add a new hypothesis to `ideas.md` with the next available H-number (continuing from the highest existing H# in `ideas.md`), tagged `[Codex-N]` in the Source field.
   - **Alternative approach**: If Codex suggests a promising technique, add it as a hypothesis marked `[Codex-N]`.
   - **Already addressed**: Note this in the consultation log and move on.
   - **Irrelevant or wrong**: Dismiss with a brief note in the log.
3. **Do not block** on Codex feedback. If the MCP call times out or fails, log the failure and return.

### Session Continuity

Use a single Codex session ID across all consultations within one investigation run. This allows Codex to build context across consultations. Pass the `sessionId` parameter to the `codex` tool, using a consistent ID like `"reaper-critique-<timestamp>"`.

## Mode: Self-Review (`--self`)

The agent reviews its own investigation results for gaps, inconsistencies, or missed angles.

### Process

1. Read `current-understanding.md`, `notes/results.md`, and `ideas.md`.
2. Identify:
   - **Weak claims**: Findings with low or medium confidence that haven't been strengthened.
   - **Untested assumptions**: Assumptions listed in hypotheses or proofs that haven't been validated.
   - **Missing angles**: Obvious questions raised by the current findings that haven't been investigated.
   - **Inconsistencies**: Claims in `current-understanding.md` that conflict with each other or with `notes/results.md`.
3. For each actionable finding, add a hypothesis to `ideas.md` with the next available H-number, tagged `[Self-N]` in the Source field (where N is one more than the count of existing self-review rounds).
4. If actionable hypotheses were added, invoke the `/investigate` skill with argument `3` to address them. The self-review findings are recorded as part of the cycle logs in `reaper-workspace/logs/` — no separate self-review file is needed.

## Quality Criteria

- Each investigate-critique loop produces a cycle log in `reaper-workspace/logs/` (append-only)
- Human feedback is classified before action is taken
- Codex consultations alternate between devil's advocate and inspiration roles
- Self-reviews identify specific, actionable gaps — not vague concerns
- New hypotheses generated by critique are tagged with their source (`[Round N]`, `[Codex-N]`, `[Self-N]`)
- When critique triggers investigation cycles, results flow back through the normal investigation pipeline
