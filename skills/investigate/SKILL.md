---
name: investigate
description: "Run investigation cycles that test hypotheses through proof verification, counterexample search, or security analysis, with keep-or-discard discipline. Use when asked to investigate, verify, prove, or disprove claims."
user-invocable: true
argument-hint: "[number-of-cycles]"
---

# Investigate

The core research loop. Run N investigation cycles, each testing a hypothesis and applying keep-or-discard discipline.

## Usage

Invoke this skill by name with an optional cycle count. On slash-command hosts, prefix with `/` (e.g. `/investigate 10`).

```
# Run 10 investigation cycles
investigate 10

# Default: 5 cycles
investigate
```

Default: 5 cycles if no argument given.

## Inputs

**Always read** before starting:
- `reaper-workspace/notes/problem-statement.md` — model assumptions and property definitions
- `reaper-workspace/notes/ideas.md` — the ideas to investigate
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/notes/results.md` — what's been tried and what happened

**Lazy-load only when needed** (do not read upfront — load only if a cycle's hypothesis requires it or the "when stuck" protocol calls for it):
- `reaper-workspace/notes/paper-summary.md` — the source paper (if provided)
- `reaper-workspace/notes/literature.md` — known prior work (organized by same-goal and same-approach)
- `reaper-workspace/papers/` — downloaded PDFs and per-paper notes (`<id>-notes.md`) from the literature review
- `{{REAPER_SKILL_DIR}}/references/methodology.md` — proof/analysis patterns

## Path Resolution Protocol

This skill references files in sibling skills. **`{{REAPER_SKILL_DIR}}`** above and below is a template placeholder — **you MUST substitute it with the absolute install path of the `/reaper` skill before reading, or the read will fail.** Common install locations:

- `~/.claude/skills/reaper/` (Claude Code)
- `~/.cursor/skills/reaper/` (Cursor)
- `~/.agents/skills/reaper/` (Codex CLI, Cline, Gemini CLI, Copilot, OpenCode, Warp, Goose, Replit — universal target)
- `~/.continue/skills/reaper/` (Continue)
- `~/.windsurf/skills/reaper/` (Windsurf)
- `<repo-root>/skills/reaper/` (during repo development)

**Sibling-skill dependency**: This skill assumes the full `/reaper` package was installed together (`npx skills add SebastianElvis/reaper`). Single-skill installs will fail to resolve sibling references.

## The Batch Loop

Investigation runs in **batches**, not sequential cycles. Independent hypotheses are investigated in parallel by default; sequential execution is the fallback when dependencies exist.

### Overview: Plan → Dispatch → Merge → Repeat

```
while cycles_remaining > 0 and not converged:
    Plan:     read ideas.md + notes/results.md → dependency graph → batch of independent hypotheses
    Dispatch: spawn one subagent per hypothesis (parallel, in one message)
    Merge:    collect results → update notes/results.md → integrate "keep" insights into current-understanding.md
```

### Plan Batch

1. Read `ideas.md` and `notes/results.md`
2. Identify all **unresolved** hypotheses. Check `notes/results.md` to avoid repeating failed approaches.
3. Build a dependency graph: does resolving H2 require knowing the outcome of H1? If so, H2 depends on H1.
4. Select the largest set of **independent** hypotheses that can run concurrently. Cap the batch size at `cycles_remaining`.
5. Allocate cycle numbers: pre-assign a contiguous range per subagent (e.g., batch 1 gets 001-003, batch 2 gets 004-006). Each subagent gets one or more consecutive numbers from its range.
6. If all remaining hypotheses form a dependency chain, the batch size is 1 — this is the **sequential fallback** (see below).
7. If all hypotheses are resolved, **stop and return control** to the orchestrator. The orchestrator will call `/brainstorm` to generate new ideas if needed.

### Dispatch Batch

Spawn one subagent per hypothesis in the batch using your host's parallel-subagent mechanism (e.g. Claude Code's `Agent` tool, or the equivalent task/spawn primitive on other hosts; if the host has no parallel primitive, fall back to sequential execution). **Launch all subagents in a single message** for true parallelism. Each subagent receives:

- Its assigned cycle number(s)
- The hypothesis to investigate
- A **hypothesis-relevant excerpt** of `current-understanding.md` (read-only for the duration of the batch) — extract only the 2-3 findings most relevant to this subagent's hypothesis, not the full file. This keeps subagent context lean. Include a note: "For additional context, see current-understanding.md."
- The full single-cycle protocol (Steps A–E below)
- Instructions to return: cycle rows for `notes/results.md`, keep/discard verdict, and if keep: the insight to merge

**Context efficiency**: Do NOT send the full `current-understanding.md` to every subagent. Instead, read it once in the main agent, identify which findings are relevant to each hypothesis, and send only those. A typical excerpt is 200-500 words vs 2000-5000 for the full file.

Each subagent runs the single-cycle protocol independently:

#### Step A: Create Investigation Directory

If this cycle revisits a hypothesis that already has an investigation directory, **reuse that directory** — update its `analysis.md` and `proof.md` inline rather than creating a new directory. The cycle number in the directory name stays the same (the original); the `notes/results.md` row will be updated with the new cycle number.

For a new hypothesis, create `reaper-workspace/investigations/NNN-<slug>/` where:
- `NNN` is the assigned zero-padded cycle number (001, 002, ...)
- `<slug>` is a short descriptor (e.g., `proof-lemma3`, `counterex-2party`, `alt-reduction`)

#### Step B: Investigate

Do the actual research. This is the core intellectual work. Depending on the hypothesis:

- **Proof verification**: Check each step of an existing proof. Look for gaps, implicit assumptions, boundary cases. Consult `{{REAPER_SKILL_DIR}}/references/methodology.md` for patterns.
- **Proof attempt**: Try to prove the claim. Start with the simplest approach. If it works, check if a simpler proof exists. All proofs must follow the formal proof structure below.
- **Counterexample search**: Try to disprove the claim. Start small (2 parties, 1 round). Construct a specific adversary strategy and execution trace.
- **Security analysis**: Enumerate threat models, check if reductions go through, verify simulator constructions. Security proofs must follow the formal proof structure below.
- **Comparison**: Compare approaches along specific dimensions (complexity, assumptions, properties).
- **Performance analysis**: Prove complexity bounds, communication costs, round complexity, or other quantitative metrics. All performance claims must follow the formal proof structure below.

Write all work — reasoning, attempts, dead ends, insights — to `reaper-workspace/investigations/NNN-<slug>/analysis.md`. If revisiting, **edit the existing `analysis.md` inline** — update conclusions, revise reasoning, and integrate new findings into the existing structure rather than appending a new section. The file should always reflect the current best understanding of this hypothesis.

##### Intra-Cycle Parallelism

Within a single cycle, subagents MAY spawn sub-subagents for concurrent attack:

- **Proof + counterexample race**: When a hypothesis could go either way, run proof-attempt and counterexample-search as parallel sub-subagents. The first to reach a definitive result wins; the other's partial work is logged in the investigation directory.
- **Parallel literature search**: When stuck and searching for related work, run IACR + arXiv + WebSearch as parallel sub-subagents, then merge results.

Use intra-cycle parallelism when the hypothesis is genuinely uncertain. If prior cycles strongly suggest the claim is true (or false), prefer the targeted approach.

##### Formal Proof Structure

For theoretical research (proving properties, security guarantees, or performance metrics), every claim must be stated and proved formally. Write proofs in `reaper-workspace/investigations/NNN-<slug>/proof.md` using this structure:

```markdown
## Theorem/Lemma/Proposition N: <name>

**Statement.** <precise mathematical statement of the claim>

**Assumptions.**
- <each assumption listed explicitly, e.g., threat model, computational hardness, network model>

**Proof.**
<the proof body — each logical step explicit and justified>

1. <step>  *(by <justification: definition / assumption / prior lemma / cited result>)*
2. <step>  *(by ...)*
...

∎

**Proof technique:** <e.g., reduction, induction, simulation, hybrid argument, game hopping>
```

Consult `{{REAPER_SKILL_DIR}}/references/methodology.md` for the proof techniques catalog, reduction quality gate, and performance sanity checks. State the chosen proof technique in the proof header. If it doesn't work after a genuine attempt, log which technique failed and why, then try an alternative in the next cycle.

Requirements for formal proofs:

- **Properties**: State as a formal predicate. Prove under stated assumptions.
- **Performance metrics**: State as a formal claim. Prove by construction or reduction. Distinguish worst/average/amortized.
- **Security properties**: State the definition, construct the reduction, prove the bound. Make it tight or state the gap.
- **Impossibility results**: State what's impossible, under which model. Prove by contradiction or reduction.

If a proof attempt fails or has gaps:
- Document exactly where the proof breaks down
- State what additional assumption would close the gap
- Log the cycle as `inconclusive` with the gap described

Do not claim a property or metric holds without a proof. Conjectures must be clearly labeled as such.

<!-- TODO: Add Lean-based formal verification step. When proofs are complete, translate them into Lean 4 and machine-check them. This would replace confidence levels with verified/unverified status and catch subtle gaps that manual proofs miss. Requires: Lean 4 toolchain, a library of common crypto/protocol primitives in Lean, and a skill or subscript to invoke the Lean checker. -->

#### Step C: Evaluate

Did this cycle produce **genuine progress**? A cycle counts as progress if it:

- Confirms or refutes a hypothesis (fully or partially)
- Narrows the search space on an important question
- Identifies a new important question not previously considered
- Simplifies an existing argument (fewer assumptions, shorter proof)
- Corrects a prior error in understanding

**Simplicity criterion**: A proof that achieves the same result with fewer assumptions is better. Replacing a 3-page case analysis with a one-paragraph reduction is progress even if the "result" is unchanged. Don't accumulate tangential findings that don't serve the research goal.

**One "ping" per cycle**: The cycle's outcome should be statable in a single sentence. If it can't be, the cycle tried to do too much — note this and decompose in the next cycle.

##### Classify Proof Issues Precisely

When a proof issue is found, do not just say "found a gap." Classify it:

- **Gap (fillable)**: A step is missing but the overall approach is sound. The gap can likely be closed with additional argument. Log as `partially-confirmed`.
- **Gap (structural)**: The proof strategy fundamentally cannot work as written — e.g., the simulator doesn't handle a class of adversary behaviors, the reduction has exponential loss, the induction hypothesis is too weak. Log as `inconclusive` and pivot to whether the theorem itself is true via an alternative proof.
- **Error (theorem likely false)**: The proof fails because the claimed property actually doesn't hold — you can construct a concrete counterexample or execution trace that violates it. Log as `refuted`.
- **Overclaim**: The proof is correct but proves something strictly weaker than what's claimed — e.g., the paper claims adaptive security but the proof only handles static corruption, or claims async but requires partial synchrony. Log as `partially-confirmed` with the precise weakening stated.

##### Composition Awareness

When a core property is confirmed, note the composition implications. Consult `{{REAPER_SKILL_DIR}}/references/definitional-standards.md` for domain-specific composition considerations (e.g., rewinding, shared setup, standalone vs compositional security).

Log composition limitations in the investigation's `analysis.md` even if the original hypothesis didn't ask about composition — this is critical context for the final report.

#### Step D: Log

Prepare a row for `reaper-workspace/notes/results.md`:

```
| NNN | H# | action-type | outcome | confidence | status | one-sentence description |
```

Where:
- **action-type**: proof-verification, proof-attempt, counterexample-search, security-analysis, performance-analysis, comparison, literature-search, reformulation
- **outcome**: confirmed, refuted, partially-confirmed, inconclusive, new-hypothesis, reformulate
- **confidence**: high, medium, low (see calibration below)
- **status**: keep or discard

**Update-in-place rule**: If this cycle revisits a hypothesis that already has a row in `notes/results.md`, the subagent should flag this as an update (not a new row). The main agent will update the existing row inline during the merge phase rather than appending a duplicate. The cycle number, outcome, confidence, and description should all reflect the latest result. The previous investigation directory remains in `investigations/` for the audit trail.

Subagents return this row to the main agent rather than appending directly.

**Cycle log**: After preparing the results row, write a cycle log to `reaper-workspace/logs/cycle-NNN-<slug>.md` (using the same NNN and slug as the investigation directory). This is an append-only snapshot — never modify it after creation. Include:

```markdown
# Cycle NNN: <hypothesis title>

- **Hypothesis**: H# — <statement>
- **Action**: <action-type>
- **Outcome**: <outcome> (confidence: <confidence>)
- **Verdict**: keep / discard

## Summary
<1-3 paragraph narrative: what was attempted, what was found, why the verdict>
```

When revisiting a hypothesis, create a new log file with the new cycle number (e.g., `cycle-005-proof-lemma3.md` even if `cycle-001-proof-lemma3.md` already exists). The slug may differ if the approach changed.

##### Confidence Calibration

Default to one level LOWER than your instinct. If you think "high," write "medium" unless every single step is airtight.

- **High**: The argument is complete, every step is justified by definition / assumption / prior lemma / cited result, and you can see no way it could be wrong. You could present this at a seminar and defend every step under questioning. For reductions: the Reduction Quality Gate is fully passed.
- **Medium**: The argument is plausible and mostly complete, but at least one step relies on intuition rather than rigorous justification, or there is a step you believe is correct but haven't fully verified. A careful reviewer might find an issue.
- **Low**: The argument has significant gaps, relies on unverified assumptions, or is based on analogy/heuristic rather than proof. This is a conjecture with supporting evidence, not a result.

#### Step E: Keep or Discard

Determine the verdict:

**keep** — The cycle produced genuine progress. Return the insight to merge into `current-understanding.md`.

**discard** — The cycle was a dead end. The investigation directory stays for the audit trail.

Subagents do NOT write to `current-understanding.md` directly — they return their verdict and insight to the main agent.

### Merge

After all subagents in a batch complete:

1. **Update or append rows** in `reaper-workspace/notes/results.md`. If a cycle revisits a hypothesis that already has a row, **update the existing row inline** with the new cycle number, outcome, confidence, and description — do not append a duplicate. Only append a new row for hypotheses appearing in the table for the first time. Keep rows ordered by hypothesis number.
2. **Integrate "keep" insights** into `reaper-workspace/notes/current-understanding.md` — the main agent writes this, preserving the single-writer constraint. Write as if explaining at a whiteboard — crystallize understanding, don't just append notes. The file should be coherent end-to-end, not a chronological log.
3. **Check for new hypotheses** generated by the batch (subagents may propose them). Add to `ideas.md`. If a hypothesis's status changed (resolved, deprioritized, subsumed), **update it inline** in `ideas.md`.
4. **Write batch summary** to `reaper-workspace/notes/results.md` after the row table:
   ```markdown
   ## Batch Summary (Cycles NNN-MMM)
   Keep findings:
   - [1 sentence per keep cycle: what was found and why it matters]
   Discard patterns:
   - [1 sentence summarizing why cycles were discarded, if any pattern emerges]
   ```
   These summaries serve two purposes: (a) `/brainstorm` can read summaries instead of full investigation directories, and (b) `/synthesize` can read summaries instead of loading all `analysis.md` files.
5. **Re-read updated state** and plan the next batch.

### Sequential Fallback

When all remaining hypotheses form a dependency chain (H2 requires H1's result, H3 requires H2's, ...), the batch size is 1. This is equivalent to the traditional sequential loop — no subagents needed, the main agent runs Steps A–E directly and writes to `current-understanding.md` immediately on keep.

### Repeat

Plan the next batch. Do not pause, do not ask if you should continue.

## Never-Stop Policy

Run all N cycles. The only valid early stop is **genuine convergence**: all hypotheses resolved with high confidence, and no new hypotheses worth pursuing. Uncertainty about whether the human wants you to continue is NEVER a reason to stop.

## When Stuck

If a cycle is going nowhere, follow the escalation protocol in `{{REAPER_SKILL_DIR}}/references/methodology.md` (section "When Stuck: 8-Step Escalation"). The steps progress from re-reading existing materials, through searching for new literature (see `{{REAPER_SKILL_DIR}}/references/search-tools.md` for search commands, which use the `arxiv.py` and `iacr.py` scripts in the `/search-paper` skill), to trying radically different approaches.

When searching for new literature mid-investigation, download relevant papers to `reaper-workspace/papers/`, write per-paper notes (`<id>-notes.md`), and **integrate findings into `reaper-workspace/notes/literature.md` inline** — add new entries to the appropriate existing sections rather than appending a separate "Mid-Investigation Additions" section. Log the search as a cycle with action-type `literature-search` in `notes/results.md`.

If all escalation tactics are exhausted and the hypothesis remains stuck, log the cycle as `inconclusive` and continue to the next hypothesis. The orchestrator will call `/brainstorm` after the batch to generate new ideas based on the pattern of failures.

## Negative Result Protocol

If after 3 cycles a hypothesis trends toward refutation (counterexample attempts partially succeed, proof attempts consistently fail at the same point, or you keep hitting the same structural gap):

1. **Pivot explicitly** to proving the negative. Construct the strongest possible negative result — a concrete attack, execution trace, or reduction to a known impossibility. A clean impossibility result is more valuable than a vague "we couldn't prove it."
2. **Identify the minimal fix.** What is the weakest additional assumption that would make the positive result hold? (e.g., "Safety holds if we additionally assume synchronous message delivery in the view-change sub-protocol.")
3. **A clean negative result is a KEEP, not a failure.** It resolves the hypothesis (by refutation) and advances understanding. Log it with outcome `refuted` and status `keep`.
4. **Signal for new ideas.** Note in the cycle's result description that the hypothesis was refuted and what was learned. The orchestrator will call `/brainstorm` to generate follow-up hypotheses (e.g., proving the impossibility formally, exploring the minimal fix).

Do not spend 10 cycles attempting minor variations of the same failed proof strategy. Three failures at the same point is a signal to change direction.

## Re-Formalization Protocol

If an investigation cycle reveals that the problem formulation itself is wrong (not just that a hypothesis failed, but that the model assumptions, core question, or property definitions are mis-specified), trigger re-formalization:

1. Log the cycle with outcome `reformulate` and status `keep`.
2. In the cycle's `analysis.md`, write a section `## Re-Formalization Signal` containing:
   - What is wrong with the current formulation
   - What evidence from this cycle demonstrates the problem
   - What the corrected formulation should look like (proposed changes to model assumptions, core question, or properties)
3. Write `REFORMULATE` as the first line of the cycle description in `notes/results.md`, followed by a one-sentence summary.
4. **Stop the current investigation batch** and return control to the orchestrator. Do not continue investigating hypotheses based on a known-incorrect formulation.

The orchestrator will re-invoke the `/formalize-problem` skill incorporating the re-formalization signal before resuming investigation.

If any cycle in a batch returns outcome `reformulate`, stop dispatching further batches and return control to the orchestrator with a re-formulation signal.

## Quality Criteria

- Every hypothesis has exactly one row in `notes/results.md` reflecting its latest state — revisits update inline, not append
- `current-understanding.md` only changes on keep cycles
- Each investigation directory has an `analysis.md` reflecting the current best understanding (edited inline on revisit)
- The "one ping" test: every cycle's outcome can be stated in one sentence
- No cycles wasted on tangential exploration that doesn't serve the research goal
- When stuck, the 8-step protocol is followed before giving up on a hypothesis
- Independent hypotheses are batched in parallel by default; sequential only when dependencies exist
- `current-understanding.md` is written only by the main agent during the merge phase, never by subagents
