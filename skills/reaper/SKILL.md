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

The first argument is the path to the paper (PDF or text). Everything after it in quotes is the research goal. Pass `--codex` to enable automated Codex consultation during investigation (requires [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server)).

## Workflow

### Step 1: Initialize Workspace

Create the workspace directory structure:

```
reaper-workspace/
├── notes/
│   ├── current-understanding.md    # Initialize empty — "branch tip"
│   └── scratchpad.md               # Initialize empty
├── papers/                         # Downloaded PDFs and per-paper notes
├── experiments/
├── feedback/
├── results.md                      # Initialize with table header
└── log.md                          # Initialize empty
```

Initialize `reaper-workspace/results.md` with:
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

Run **`/reaper:formalize-problem "<research-goal>"`** — reads the baseline outputs (including `clarified-goal.md`) and produces `notes/problem-statement.md` with trust assumptions, security properties, performance goals, and prioritized ideas.

### Step 5: Brainstorm → Investigate → Critique Loop

Run the core research engine: a recurring loop of brainstorm (generate ideas), investigate (execute on ideas), and critique (external perspective). The loop structure depends on whether `--codex` was passed:

**Default (no `--codex`):**
```
/reaper:brainstorm  →  /reaper:investigate 5  →  /reaper:critique --self  →  /reaper:brainstorm  →  /reaper:investigate 5
```

**With `--codex`:**
```
/reaper:brainstorm  →  /reaper:investigate 5  →  /reaper:critique --codex  →  /reaper:brainstorm  →  /reaper:investigate 5  →  /reaper:critique --codex
```

Concretely:
1. Run **`/reaper:brainstorm`** — generate initial ideas based on the formalized problem (supplements the hypotheses from `formalize-problem` with additional angles)
2. Run **`/reaper:investigate 5`** — first batch of investigation cycles
3. Run **`/reaper:critique --codex`** (if `--codex`) or **`/reaper:critique --self`** — critique the findings
4. Run **`/reaper:brainstorm`** — generate new ideas based on what was learned and critique feedback
5. Run **`/reaper:investigate 5`** — second batch, now incorporating new ideas from brainstorm and critique
6. If `--codex`, run **`/reaper:critique --codex`** once more for a final review

Adjust cycle counts based on problem complexity (e.g., 3+3 for simple problems, 5+5 for complex ones). The total should be ~10 cycles of investigation.

The `brainstorm` step reads the current state and appends new ideas to `problem-statement.md` (tagged `[Brainstorm-N]`). The `critique` step may also add hypotheses (tagged `[Codex-N]` or `[Self-N]`). The next `investigate` batch picks up all unresolved ideas automatically.

If `investigate` returns early because all ideas are resolved, run `brainstorm` before deciding whether to continue or move to synthesis.

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
