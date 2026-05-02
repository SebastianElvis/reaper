---
name: reaper
description: "Run the full Reaper research pipeline: analyze a paper (optional), review literature, formalize the problem, investigate hypotheses with critique loops, and synthesize a report. Use when given a research goal, optionally with a paper."
user-invocable: true
argument-hint: "\"<research-goal>\" [paper-path] [--codex]"
license: Apache-2.0
compatibility: "Requires python3 with arxiv, requests, beautifulsoup4 packages, internet access, and PDF reading capability. The --codex flag requires an MCP-capable host."
---

# Reaper: AI-Native Research Pipeline

You are the Reaper orchestrator. You take a research goal — optionally with a research paper — and autonomously conduct rigorous, multi-step academic research.

## Usage

Invoke the `/reaper` skill with a research goal (quoted string), optionally followed by a paper path and/or `--codex`. Examples below use a generic name-based form; the slash-command form `/reaper "..."` works on hosts with slash-command routing (e.g. Claude Code).

```
# Without a paper — pure goal-driven research
reaper "explore the feasibility of post-quantum threshold signatures"

# With a paper
reaper "determine if the security proof in Section 4 holds under asynchrony" path/to/paper.pdf

# With external-model consultation for automated AI feedback between investigation cycles
reaper "determine if the security proof in Section 4 holds under asynchrony" path/to/paper.pdf --codex
```

**Argument parsing:** The research goal (quoted string) is required. If a path to an existing file (PDF or text) is also provided, treat it as the paper. Pass `--codex` to enable external-model consultation across the entire pipeline — every skill gains an optional step where it consults an external model for a second opinion at a natural checkpoint. See `references/codex-consultation.md` for the full protocol. Requires a host with MCP support and a registered Codex MCP server (e.g. [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server)); silently no-op on hosts without MCP.

When `--codex` is set, propagate this context to all skill invocations. Each skill will consult Codex only at its designated checkpoint (defined in `references/codex-consultation.md`), using compressed context and a shared session ID for continuity across the pipeline.

## Peer Skills

This orchestrator chains 8 sub-skills that must be installed alongside it: `/clarify-goal`, `/analyze-paper`, `/review-literature`, `/formalize-problem`, `/brainstorm`, `/investigate`, `/critique`, `/synthesize`. One more (`/search-paper`) is called transitively by `/review-literature` and `/investigate`. The `/<skill>` form is the canonical display convention used in these docs; substitute the host-native invocation form (slash command, auto-discovery, manual `SKILL.md` pointer) when actually running them.

If any of these are missing from your agent's skills folder, ask the user to reinstall the full Reaper package (`npx skills add SebastianElvis/reaper`).

## Invocation Convention

References below to running a sub-skill use the host-agnostic phrase "invoke the `<name>` skill" — invoke each sub-skill by its `name` using your host's native skill-loading mechanism. The loaded `SKILL.md` provides the full instructions for that stage. Concrete invocation form varies by host:

- **Slash-command hosts** (e.g. Claude Code): `/<sub>` (e.g. `/clarify-goal`)
- **Auto-discovery hosts** (e.g. Cursor, Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, OpenCode): the agent loads peer `SKILL.md` files from the skills folder and routes by `name` + `description` match.
- **Manual invocation hosts**: explicitly point the agent at the installed skill's `SKILL.md` (typical paths: `~/.claude/skills/<name>/SKILL.md`, `~/.cursor/skills/<name>/SKILL.md`, `~/.agents/skills/<name>/SKILL.md`, `~/.continue/skills/<name>/SKILL.md`, `~/.windsurf/skills/<name>/SKILL.md`, or `<repo-root>/skills/<name>/SKILL.md` during development — substitute `<name>` with the sub-skill directory name like `clarify-goal`).

## Design Principles

1. **Separation of concerns**: Each skill has one job. Skills communicate through workspace files, not shared memory.
2. **Fixed evaluation signal**: Every investigation cycle produces a binary keep/discard verdict.
3. **Structured results log**: `notes/results.md` is the single source of truth for what has been tried and what happened.
4. **Keep-or-discard loop**: Only "keep" findings flow into `current-understanding.md`. Discards stay in the audit trail.
5. **Never stop**: The pipeline runs to completion. Uncertainty about user intent is never a reason to pause.
6. **Clarity and simplicity**: Prefer simpler proofs, fewer assumptions, shorter arguments.

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

**File mutation rules:**

| Category | Files | Policy |
|----------|-------|--------|
| Evolving (inline edit) | `notes/current-understanding.md`, `notes/results.md`, `notes/ideas.md`, `notes/problem-statement.md`, `notes/literature.md`, `papers/*-notes.md`, `investigations/*/analysis.md`, `investigations/*/proof.md` | Edit in place. Single writer per file per batch. `notes/literature.md` is created by `/review-literature` and extended inline by `/investigate` during mid-cycle literature search. |
| Append-only | `logs/cycle-*.md`, `feedbacks/round-*.md`, `feedbacks/codex-consultation-*.md` | Create once, never modify. |
| Write-once | `notes/paper-summary.md`, `notes/clarified-goal.md`, `report.md` | Created by one skill. May be regenerated on re-run but not incrementally edited by other skills. |

**File naming conventions:** Investigation dirs: `NNN-<slug>/` (zero-padded). Cycle logs: `cycle-NNN-<slug>.md`. Feedback: `round-N.md`, `codex-consultation-N.md`. Paper notes: `<id>-notes.md`.

**Lazy-load protocol:** Early-pipeline skills (`/formalize-problem`, `/analyze-paper`) read source files eagerly. Loop skills (`/brainstorm`, `/investigate`, `/critique`, `/synthesize`) use `current-understanding.md` as primary source and lazy-load `paper-summary.md` and `literature.md` only when stuck or when a specific hypothesis requires it.

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

**If a paper was provided:**
Invoke the **`/clarify-goal`** skill with arguments `"<research-goal>" <paper-path>` — it does a quick scan of the paper, asks the user 3-5 targeted clarifying questions about scope, assumptions, and success criteria, then writes `notes/clarified-goal.md`.

**If no paper was provided:**
Invoke the **`/clarify-goal`** skill with argument `"<research-goal>"` — it asks the user 3-5 targeted clarifying questions based on the goal alone (no paper scan), then writes `notes/clarified-goal.md`.

If the goal is already precise and unambiguous, this step writes the file without asking questions.

All downstream skills should read `clarified-goal.md` for the refined goal and context.

### Step 3: Establish Baseline (parallel)

**If a paper was provided**, run these two skills as **parallel subagents** using your host's parallel-spawn primitive (e.g. Claude Code's `Agent` tool, or the equivalent on your host; if the host has no parallel primitive, run them sequentially) — they write to non-overlapping files:

1. Invoke **`/analyze-paper`** with `<paper-path>` — produces `notes/paper-summary.md`
2. Invoke **`/review-literature`** with `"<research-goal>"` — produces `notes/literature.md`

Use the refined goal from `clarified-goal.md` for the literature review argument. Both must complete before proceeding.

**If no paper was provided**, run only:

1. Invoke **`/review-literature`** with `"<research-goal>"` — produces `notes/literature.md`

Skip `/analyze-paper` entirely — there is no paper to analyze. The pipeline proceeds without `notes/paper-summary.md`.

### Step 4: Formalize the Problem

Invoke **`/formalize-problem`** with `"<research-goal>"` — it reads the baseline outputs (`clarified-goal.md`, `literature.md`, and `paper-summary.md` if available) and produces `notes/problem-statement.md` (trust assumptions, security properties, performance goals) and `notes/ideas.md` (prioritized ideas).

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
brainstorm  →  investigate N  →  critique --self  →  brainstorm  →  investigate N
```

**With `--codex`:**
```
brainstorm  →  investigate N  →  critique --codex  →  brainstorm  →  investigate N  →  critique --codex
```

Where N is determined by the complexity assessment above.

#### Adaptation Signals During the Loop

- If >50% of cycles in a batch are "discard," the hypotheses may be poorly formulated — run brainstorm before the next batch rather than continuing with existing hypotheses.
- If investigate returns early (all hypotheses resolved), run brainstorm to check for overlooked directions before moving to synthesis.
- If a critique round generates 3+ new actionable hypotheses, extend the loop with another investigate batch.
- If 2 consecutive batches produce only "keep" results with high confidence and no new hypotheses, convergence is likely — proceed to synthesis.

#### Re-Formalization Handling

If `/investigate` returns with a re-formalization signal (any cycle logged with outcome `reformulate`):

1. **Preserve state**: Do NOT clear `notes/results.md`, `notes/current-understanding.md`, or existing investigation directories.
2. **Archive old formulation**: Rename `notes/problem-statement.md` to `notes/problem-statement-v<N>.md` before re-running.
3. **Re-run `/formalize-problem`**: It reads the reformulation signal from the triggering cycle's `analysis.md`.
4. **Reset ideas selectively**: In `ideas.md`, mark hypotheses that depended on the old formulation as `[superseded by v<N>]`. Add new hypotheses below.
5. **Restart loop**: Fresh cycle budget for the new formulation.

#### Loop Mechanics

The `/brainstorm` step reads the current state and updates `ideas.md` (adding new ideas, editing existing ones inline) (tagged `[Brainstorm-N]`). The `/critique` step may also add hypotheses (tagged `[Codex-N]` or `[Self-N]`). The next `/investigate` batch picks up all unresolved ideas automatically.

This loop runs autonomously — do not interrupt or ask if it should continue.

### Step 6: Synthesize

Invoke the **`/synthesize`** skill — it reads all workspace files and produces `report.md`.

### Step 7: Present Results

After synthesis completes:
1. Read `reaper-workspace/report.md`
2. Present the key findings to the user
3. Point them to the full workspace for the audit trail
4. Proceed to Step 8

### Step 8: Offer Iteration

After presenting results, let the user know they can iterate:

> If you'd like to refine, deepen, or challenge any aspect of this research, invoke the `/critique` skill with your feedback as a quoted string. (Slash-command hosts: `/critique "your feedback here"`.)

Do **not** block waiting for a response — the pipeline is complete. The user can invoke `/critique` with quoted feedback at any time to start a feedback round. The critique skill classifies the feedback, may run targeted investigation cycles, and then you should re-invoke `/synthesize` to produce an updated report.

## Skill Dependency Graph

```
/clarify-goal ──► /analyze-paper ──┐
             (if paper provided)   ├──► /formalize-problem ──► /brainstorm ◄──► /investigate ◄──► /critique
                /review-literature ┘                                                              │
                  (calls /analyze-paper                                     /synthesize ◄──────────┘
                   for each paper)
```

| Skill | Requires | Produces |
|-------|----------|----------|
| `/clarify-goal` | (paper path, optional) | `notes/clarified-goal.md` |
| `/analyze-paper` | (paper path) — **skipped at top level if no paper**; also called by `/review-literature` for each downloaded paper | `notes/paper-summary.md` or `papers/<id>-notes.md` (when `--output` is specified) |
| `/review-literature` | (research goal); calls `/analyze-paper --goal` per downloaded paper | `notes/literature.md`, `papers/*` |
| `/formalize-problem` | `clarified-goal.md`, `literature.md`, `paper-summary.md` (optional) | `problem-statement.md`, `ideas.md` |
| `/brainstorm` | `problem-statement.md`, `ideas.md`, `current-understanding.md`, `results.md` | Updates `ideas.md` |
| `/investigate` | `problem-statement.md`, `ideas.md`, `current-understanding.md`, `results.md` | Updates `results.md`, `current-understanding.md`, `ideas.md`; creates `investigations/*`, `logs/*` |
| `/critique` | `current-understanding.md`, `results.md`, `problem-statement.md`, `ideas.md` | `feedbacks/*`; may update `ideas.md` |
| `/synthesize` | `current-understanding.md`, `results.md`, `problem-statement.md`, `ideas.md` | `report.md` |
| `/search-paper` | (query) | stdout — search results, citations, or resolved venue |

## Important Notes

- Sub-skills are invoked using the host agent's native skill mechanism — by `name` plus arguments. The exact API differs per host (e.g. Claude Code's `Skill` tool with `skill: "analyze-paper", args: "paper.pdf"`; Cursor/Codex/Cline auto-route based on the loaded `SKILL.md`). Refer to the host's skill documentation for the exact form.
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
| missing | - | - | - | Run Step 3 (baseline). If no paper was provided, this is normal — proceed with literature review only. |
| exists or N/A | missing | - | - | Run Step 4 (formalize) |
| exists or N/A | exists | 0 | - | Run Step 5 (brainstorm + investigate). Check `ideas.md` for unresolved hypotheses. |
| exists or N/A | exists | >0, unresolved H | - | Continue Step 5 (investigate or brainstorm). Check `ideas.md` for unresolved hypotheses. |
| exists or N/A | exists | >0, all H resolved | missing | Run Step 6 (synthesize) |
| exists or N/A | exists | >0 | exists | Run Step 7-8 (present + offer iteration) |
