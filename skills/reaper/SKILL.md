---
name: reaper
description: "Run the full Reaper research pipeline: analyze a paper, review literature, formalize the problem, investigate hypotheses, and synthesize a report. Use when given a research paper and a research goal."
user-invocable: true
argument-hint: "<paper-path> \"<research-goal>\""
---

# Reaper: AI-Native Research Pipeline

You are the Reaper orchestrator. You take a research paper and a research goal, then autonomously conduct rigorous, multi-step academic research.

## Usage

```
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony"
```

The first argument is the path to the paper (PDF or text). Everything after it in quotes is the research goal.

## Workflow

### Step 1: Initialize Workspace

Create the workspace directory structure:

```
reaper-workspace/
├── notes/
│   ├── current-understanding.md    # Initialize empty — "branch tip"
│   └── scratchpad.md               # Initialize empty
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

### Step 2: Establish Baseline (parallel)

Run these two skills as **parallel subagents** using the Agent tool — they write to non-overlapping files:

1. **`/reaper:analyze-paper <paper-path>`** — produces `notes/paper-summary.md`
2. **`/reaper:review-literature "<research-goal>"`** — produces `notes/literature.md`

Both must complete before proceeding.

### Step 3: Formalize the Problem

Run **`/reaper:formalize-problem "<research-goal>"`** — reads the baseline outputs and produces `notes/hypotheses.md` with trust assumptions, security properties, performance goals, and prioritized testable claims.

### Step 4: Investigate

Run **`/reaper:investigate 10`** — executes 10 investigation cycles (adjust based on problem complexity). Each cycle:
- Tests a hypothesis from `hypotheses.md`
- Logs results to `results.md`
- Updates `current-understanding.md` only on keep

This is the core research loop. It runs autonomously — do not interrupt or ask if it should continue.

### Step 5: Synthesize

Run **`/reaper:synthesize`** — reads all workspace files and produces `report.md`.

### Step 6: Present Results

After synthesis completes:
1. Read `reaper-workspace/report.md`
2. Present the key findings to the user
3. Point them to the full workspace for the audit trail

## Important Notes

- Each skill is invoked via the Skill tool (e.g., `skill: "reaper:analyze-paper", args: "paper.pdf"`)
- Skills communicate exclusively through workspace files — no in-memory state passing
- If a skill fails, read its output file to diagnose, then retry
- The workspace is the source of truth — if context is compressed, re-read workspace files
- Never ask the user "should I continue?" during the pipeline — run to completion
