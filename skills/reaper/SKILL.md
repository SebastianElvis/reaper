---
name: reaper
description: "Run the full Reaper research pipeline: analyze a paper, review literature, formalize the problem, investigate hypotheses with critique loops, and synthesize a report. Use when given a research paper and a research goal."
user-invocable: true
argument-hint: "<paper-path> \"<research-goal>\" [--codex]"
---

# Reaper: AI-Native Research Pipeline

You are the Reaper orchestrator. You take a research paper and a research goal, then autonomously conduct rigorous, multi-step academic research.

## Usage

```
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony"

# With Codex consultation for automated AI feedback between investigation cycles
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony" --codex
```

The first argument is the path to the paper (PDF or text). Everything after it in quotes is the research goal. Pass `--codex` to enable Codex consultation across the entire pipeline — every skill gains an optional step where it consults Codex for a second opinion at a natural checkpoint. See `references/codex-consultation.md` for the full protocol. Requires [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server).

When `--codex` is set, propagate this context to all skill invocations. Each skill will consult Codex only at its designated checkpoint (defined in `references/codex-consultation.md`), using compressed context and a shared session ID for continuity across the pipeline.

## Workflow

### Step 1: Initialize Workspace

Create the workspace directory structure:

```
reaper-workspace/
├── notes/                          # Evolving — edited inline to reflect latest state
│   ├── current-understanding.md    # Initialize empty — "branch tip"
│   └── results.md                  # Initialize with table header — one row per hypothesis, updated inline on revisit
├── papers/                         # Evolving — per-paper notes can be updated
├── investigations/                 # Evolving — reuse directory on revisit, edit inline
├── feedbacks/                      # Append-only — one file per event, never modified
├── logs/                           # Append-only — one file per cycle, never modified
```

Initialize `reaper-workspace/notes/results.md` with:
```markdown
# Investigation Results

| Cycle | Hypothesis | Action | Outcome | Confidence | Status | Description |
|-------|-----------|--------|---------|------------|--------|-------------|
```

Initialize `reaper-workspace/notes/current-understanding.md` with:
```markdown
# Current Understanding

*No investigation cycles completed yet.*
```

### Step 2: Clarify the Research Goal

Run **`/reaper:clarify-goal <paper-path> "<research-goal>"`** — does a quick scan of the paper, asks the user 3-5 targeted clarifying questions about scope, assumptions, and success criteria, then writes `notes/clarified-goal.md`.

If the goal is already precise and unambiguous, this step writes the file without asking questions.

All downstream skills should read `clarified-goal.md` for the refined goal and context.

### Step 3: Establish Baseline (parallel)

Run these two skills as **parallel subagents** using the Agent tool — they write to non-overlapping files:

1. **`/reaper:analyze-paper <paper-path>`** — produces `notes/paper-summary.md`
2. **`/reaper:review-literature "<research-goal>"`** — produces `notes/literature.md`

Use the refined goal from `clarified-goal.md` for the literature review argument.

Both must complete before proceeding.

### Step 4: Formalize the Problem

Run **`/reaper:formalize-problem "<research-goal>"`** — reads the baseline outputs (including `clarified-goal.md`) and produces `notes/problem-statement.md` (trust assumptions, security properties, performance goals) and `notes/ideas.md` (prioritized ideas).

### Step 5: Brainstorm → Investigate → Critique Loop

Run the core research engine: a recurring loop of brainstorm (generate ideas), investigate (execute on ideas), and critique (external perspective).

#### Adaptive Loop Structure

The loop adapts to problem complexity. Assess complexity after formalization, before the first brainstorm:

- **Simple** (1-3 hypotheses, narrow scope, single claim to check): 2 brainstorm-investigate rounds, 3 cycles each, 1 critique. Total: ~6 investigation cycles.
- **Moderate** (3-5 hypotheses, multiple steps or properties): 2 brainstorm-investigate rounds, 5 cycles each, 1-2 critiques. Total: ~10 investigation cycles.
- **Complex** (5+ hypotheses, multiple interacting properties, broad scope): 3+ brainstorm-investigate rounds, 5 cycles each, 2+ critiques. Total: ~15+ investigation cycles.

#### Default Patterns

**Default (no `--codex`):**
```
/reaper:brainstorm  →  /reaper:investigate N  →  /reaper:critique --self  →  /reaper:brainstorm  →  /reaper:investigate N
```

**With `--codex`:**
```
/reaper:brainstorm  →  /reaper:investigate N  →  /reaper:critique --codex  →  /reaper:brainstorm  →  /reaper:investigate N  →  /reaper:critique --codex
```

Where N is determined by the complexity assessment above.

#### Adaptation Signals During the Loop

- If >50% of cycles in a batch are "discard," the hypotheses may be poorly formulated — run brainstorm before the next batch rather than continuing with existing hypotheses.
- If investigate returns early (all hypotheses resolved), run brainstorm to check for overlooked directions before moving to synthesis.
- If a critique round generates 3+ new actionable hypotheses, extend the loop with another investigate batch.
- If 2 consecutive batches produce only "keep" results with high confidence and no new hypotheses, convergence is likely — proceed to synthesis.

#### Re-Formalization Handling

If `investigate` returns with a re-formalization signal (any cycle logged with outcome `reformulate`), re-run **`/reaper:formalize-problem`** before continuing the loop. The re-formalization should incorporate the findings from the investigation cycle that triggered it. After re-formalization, restart the brainstorm-investigate loop with the updated problem statement and reset the cycle budget for the new formulation.

#### Loop Mechanics

The `brainstorm` step reads the current state and updates `ideas.md` (adding new ideas, editing existing ones inline) (tagged `[Brainstorm-N]`). The `critique` step may also add hypotheses (tagged `[Codex-N]` or `[Self-N]`). The next `investigate` batch picks up all unresolved ideas automatically.

This loop runs autonomously — do not interrupt or ask if it should continue.

### Step 6: Synthesize

Run **`/reaper:synthesize`** — reads all workspace files and produces `report.md`.

### Step 7: Present Results

After synthesis completes:
1. Read `reaper-workspace/report.md`
2. Present the key findings to the user
3. Point them to the full workspace for the audit trail
4. Proceed to Step 8

### Step 8: Offer Iteration

After presenting results, let the user know they can iterate:

> If you'd like to refine, deepen, or challenge any aspect of this research, use `/reaper:critique "your feedback here"`.

Do **not** block waiting for a response — the pipeline is complete. The user can invoke `/reaper:critique` with quoted feedback at any time to start a feedback round. The critique skill classifies the feedback, may run targeted investigation cycles, and then you should re-run `/reaper:synthesize` to produce an updated report.

## Important Notes

- Each skill is invoked via the Skill tool (e.g., `skill: "reaper:analyze-paper", args: "paper.pdf"`)
- Skills communicate exclusively through workspace files — no in-memory state passing
- If a skill fails, read its output file to diagnose, then retry
- The workspace is the source of truth — if context is compressed, re-read workspace files
- Never ask the user "should I continue?" during the pipeline — run to completion

## Context Window Recovery

If the context window is compressed or the orchestrator loses track of its position, reconstruct the pipeline state from workspace files alone:

1. **Check which files exist** in `reaper-workspace/notes/`
2. **Read `notes/results.md`** to determine investigation progress (count cycles, check for unresolved hypotheses)
3. **Read `ideas.md`** to find unresolved hypotheses (cross-reference with `notes/results.md`)
4. **Check for `report.md`** to determine if synthesis is complete
5. **Check `feedbacks/`** for iteration rounds

**Decision table:**

| `paper-summary.md` | `problem-statement.md` | `notes/results.md` rows | `report.md` | Action |
|---|---|---|---|---|
| missing | - | - | - | Run Step 3 (baseline) |
| exists | missing | - | - | Run Step 4 (formalize) |
| exists | exists | 0 | - | Run Step 5 (brainstorm + investigate). Check `ideas.md` for unresolved hypotheses. |
| exists | exists | >0, unresolved H | - | Continue Step 5 (investigate or brainstorm). Check `ideas.md` for unresolved hypotheses. |
| exists | exists | >0, all H resolved | missing | Run Step 6 (synthesize) |
| exists | exists | >0 | exists | Run Step 7-8 (present + offer iteration) |
