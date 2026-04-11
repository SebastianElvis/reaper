---
name: investigate
description: "Run investigation cycles that test hypotheses through proof verification, counterexample search, or security analysis, with keep-or-discard discipline. Use when asked to investigate, verify, prove, or disprove claims."
user-invocable: true
argument-hint: "[number-of-cycles]"
---

# Investigate

The core research loop. Run N investigation cycles, each testing a hypothesis and applying keep-or-discard discipline.

## Usage

```
# Run 10 investigation cycles
/reaper:investigate 10

# Default: 5 cycles
/reaper:investigate
```

Default: 5 cycles if no argument given.

## Inputs

Read before starting:
- `reaper-workspace/notes/problem-statement.md` — the ideas to investigate
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/results.md` — what's been tried and what happened

Also reference:
- `reaper-workspace/notes/paper-summary.md` — the source paper
- `reaper-workspace/notes/literature.md` — known prior work (organized by same-goal and same-approach)
- `reaper-workspace/papers/` — downloaded PDFs and per-paper notes (`<id>-notes.md`) from the literature review
- `references/methodology.md` — proof/analysis patterns

## The Batch Loop

Investigation runs in **batches**, not sequential cycles. Independent hypotheses are investigated in parallel by default; sequential execution is the fallback when dependencies exist.

### Overview: Plan → Dispatch → Merge → Repeat

```
while cycles_remaining > 0 and not converged:
    Plan:     read problem-statement.md + results.md → dependency graph → batch of independent hypotheses
    Dispatch: spawn one subagent per hypothesis (parallel, in one message)
    Merge:    collect results → append to results.md → integrate "keep" insights into current-understanding.md
```

### Plan Batch

1. Read `problem-statement.md` and `results.md`
2. Identify all **unresolved** hypotheses. Check `results.md` to avoid repeating failed approaches.
3. Build a dependency graph: does resolving H2 require knowing the outcome of H1? If so, H2 depends on H1.
4. Select the largest set of **independent** hypotheses that can run concurrently. Cap the batch size at `cycles_remaining`.
5. Allocate cycle numbers: pre-assign a contiguous range per subagent (e.g., batch 1 gets 001-003, batch 2 gets 004-006). Each subagent gets one or more consecutive numbers from its range.
6. If all remaining hypotheses form a dependency chain, the batch size is 1 — this is the **sequential fallback** (see below).
7. If all hypotheses are resolved, formulate new ones based on what you've learned (see When Stuck, step 7).

### Dispatch Batch

Spawn one subagent per hypothesis in the batch using the Agent tool. **Launch all subagents in a single message** for true parallelism. Each subagent receives:

- Its assigned cycle number(s)
- The hypothesis to investigate
- A snapshot of `current-understanding.md` (read-only for the duration of the batch)
- The full single-cycle protocol (Steps A–E below)
- Instructions to return: cycle rows for `results.md`, keep/discard verdict, and if keep: the insight to merge

Each subagent runs the single-cycle protocol independently:

#### Step A: Create Experiment Directory

Create `reaper-workspace/experiments/NNN-<slug>/` where:
- `NNN` is the assigned zero-padded cycle number (001, 002, ...)
- `<slug>` is a short descriptor (e.g., `proof-lemma3`, `counterex-2party`, `alt-reduction`)

#### Step B: Investigate

Do the actual research. This is the core intellectual work. Depending on the hypothesis:

- **Proof verification**: Check each step of an existing proof. Look for gaps, implicit assumptions, boundary cases. Consult `references/methodology.md` for patterns.
- **Proof attempt**: Try to prove the claim. Start with the simplest approach. If it works, check if a simpler proof exists. All proofs must follow the formal proof structure below.
- **Counterexample search**: Try to disprove the claim. Start small (2 parties, 1 round). Construct a specific adversary strategy and execution trace.
- **Security analysis**: Enumerate threat models, check if reductions go through, verify simulator constructions. Security proofs must follow the formal proof structure below.
- **Comparison**: Compare approaches along specific dimensions (complexity, assumptions, properties).
- **Performance analysis**: Prove complexity bounds, communication costs, round complexity, or other quantitative metrics. All performance claims must follow the formal proof structure below.

Write all work — reasoning, attempts, dead ends, insights — to `reaper-workspace/experiments/NNN-<slug>/analysis.md`.

##### Intra-Cycle Parallelism

Within a single cycle, subagents MAY spawn sub-subagents for concurrent attack:

- **Proof + counterexample race**: When a hypothesis could go either way, run proof-attempt and counterexample-search as parallel sub-subagents. The first to reach a definitive result wins; the other's partial work is logged in the experiment directory.
- **Parallel literature search**: When stuck and searching for related work, run IACR + arXiv + WebSearch as parallel sub-subagents, then merge results.

Use intra-cycle parallelism when the hypothesis is genuinely uncertain. If prior cycles strongly suggest the claim is true (or false), prefer the targeted approach.

##### Formal Proof Structure

For theoretical research (proving properties, security guarantees, or performance metrics), every claim must be stated and proved formally. Write proofs in `reaper-workspace/experiments/NNN-<slug>/proof.md` using this structure:

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

Consult `references/methodology.md` for the proof techniques catalog, reduction quality gate, and performance sanity checks. State the chosen proof technique in the proof header. If it doesn't work after a genuine attempt, log which technique failed and why, then try an alternative in the next cycle.

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

When a security property is confirmed, note the composition implications:
- Does the proof use rewinding? If so, it likely doesn't compose (not UC-secure).
- Does the protocol use a CRS? Is the CRS shared with other protocols?
- Is the result in the standalone model, sequential composition, or UC?
- If the paper claims the protocol is "used as a building block" in a larger system, does the proven security level actually support that usage?

Log composition limitations in the experiment's `analysis.md` even if the original hypothesis didn't ask about composition — this is critical context for the final report.

#### Step D: Log

Prepare a row for `reaper-workspace/results.md`:

```
| NNN | H# | action-type | outcome | confidence | status | one-sentence description |
```

Where:
- **action-type**: proof-verification, proof-attempt, counterexample-search, security-analysis, performance-analysis, comparison, literature-search, reformulation
- **outcome**: confirmed, refuted, partially-confirmed, inconclusive, new-hypothesis
- **confidence**: high, medium, low (see calibration below)
- **status**: keep or discard

Subagents return this row to the main agent rather than appending directly.

##### Confidence Calibration

Default to one level LOWER than your instinct. If you think "high," write "medium" unless every single step is airtight.

- **High**: The argument is complete, every step is justified by definition / assumption / prior lemma / cited result, and you can see no way it could be wrong. You could present this at a seminar and defend every step under questioning. For reductions: the Reduction Quality Gate is fully passed.
- **Medium**: The argument is plausible and mostly complete, but at least one step relies on intuition rather than rigorous justification, or there is a step you believe is correct but haven't fully verified. A careful reviewer might find an issue.
- **Low**: The argument has significant gaps, relies on unverified assumptions, or is based on analogy/heuristic rather than proof. This is a conjecture with supporting evidence, not a result.

#### Step E: Keep or Discard

Determine the verdict:

**keep** — The cycle produced genuine progress. Return the insight to merge into `current-understanding.md`.

**discard** — The cycle was a dead end. The experiment directory stays for the audit trail.

Subagents do NOT write to `current-understanding.md` directly — they return their verdict and insight to the main agent.

### Merge

After all subagents in a batch complete:

1. **Append rows** to `reaper-workspace/results.md`, ordered by cycle number
2. **Integrate "keep" insights** into `reaper-workspace/notes/current-understanding.md` — the main agent writes this, preserving the single-writer constraint. Write as if explaining at a whiteboard — crystallize understanding, don't just append notes. The file should be coherent end-to-end, not a chronological log.
3. **Check for new hypotheses** generated by the batch (subagents may propose them). Add to `problem-statement.md`.
4. **Re-read updated state** and plan the next batch.

### Sequential Fallback

When all remaining hypotheses form a dependency chain (H2 requires H1's result, H3 requires H2's, ...), the batch size is 1. This is equivalent to the traditional sequential loop — no subagents needed, the main agent runs Steps A–E directly and writes to `current-understanding.md` immediately on keep.

### Repeat

Plan the next batch. Do not pause, do not ask if you should continue.

## Never-Stop Policy

Run all N cycles. The only valid early stop is **genuine convergence**: all hypotheses resolved with high confidence, and no new hypotheses worth pursuing. Uncertainty about whether the human wants you to continue is NEVER a reason to stop.

## When Stuck

If a cycle is going nowhere, escalate through these steps:

1. **Re-read the paper.** Look at sections you skimmed earlier. The answer is often in the details you glossed over.
2. **Re-read current-understanding.md.** What assumptions haven't been questioned? What's being taken for granted?
3. **Re-read results.md.** Can two "discard" results be combined into something useful? Patterns in dead ends are informative.
4. **Consult downloaded literature.** Before searching for new work, re-read the per-paper notes in `reaper-workspace/papers/<id>-notes.md`. A technique or result you need may already be in a paper you've downloaded but haven't fully exploited. If a specific section of a downloaded PDF seems relevant, read it directly with the Read tool.

5. **Search for related work** you haven't found yet. Use the search scripts as primary sources:

   ```bash
   # For crypto/security topics — search IACR ePrint
   python skills/search-iacr/search_iacr.py search "<specific question>" --max-results 5

   # For broader CS topics — search arXiv
   python skills/search-arxiv/search_arxiv.py search "<specific question>" --max-results 5 --categories cs.CR,cs.DC

   # For citation context — who builds on or cites a relevant paper
   python skills/search-arxiv/search_arxiv.py citations <arxiv_id> --max-results 10
   ```

   Fall back to WebSearch if the scripts are unavailable or for non-academic sources (blog posts, talks, informal results).

   If you find relevant new papers, **download them** to `reaper-workspace/papers/`, read them, and write per-paper notes (`<id>-notes.md`). Then **append** them to `reaper-workspace/notes/literature.md` under a new section:

   ```markdown
   ## Mid-Investigation Additions (Cycle NNN)

   | # | Title | Authors | Year | Venue | Key Contribution | Category | Local Path |
   |---|-------|---------|------|-------|-----------------|----------|------------|
   ```

   Log the literature search as a cycle with action-type `literature-search` in `results.md`.
6. **Try a radically different approach** to the same hypothesis. If you've been trying direct proof, try reduction. If you've been trying construction, try impossibility.
7. **Formulate a new hypothesis** based on what you've learned so far. The investigation may have revealed that the original question was the wrong question.
8. **Invert the problem (Hamming).** Can't prove it? Try to disprove it. Can't find a counterexample? Ask what minimal assumption would make the proof work. What seems like a blockage often becomes the key insight.
9. **Apply Qian's patterns:**
   - *Fill in the blank*: What combination of assumptions/techniques hasn't been tried?
   - *Start small then generalize*: What's the simplest case? Can you solve it for n=2 first?
   - *Build a hammer*: Can a technique from a previous cycle apply here in a different way?

## Negative Result Protocol

If after 3 cycles a hypothesis trends toward refutation (counterexample attempts partially succeed, proof attempts consistently fail at the same point, or you keep hitting the same structural gap):

1. **Pivot explicitly** to proving the negative. State the impossibility or separation as a new hypothesis: "Protocol X cannot achieve property Y under model Z because..."
2. **Construct the strongest possible negative result.** A clean impossibility result is more valuable than a vague "we couldn't prove it." Show a concrete attack, execution trace, or reduction to a known impossibility.
3. **Identify the minimal fix.** What is the weakest additional assumption that would make the positive result hold? (e.g., "Safety holds if we additionally assume synchronous message delivery in the view-change sub-protocol.")
4. **A clean negative result is a KEEP, not a failure.** It resolves the hypothesis (by refutation) and advances understanding. Log it with outcome `refuted` and status `keep`.

Do not spend 10 cycles attempting minor variations of the same failed proof strategy. Three failures at the same point is a signal to change direction.

## Quality Criteria

- Every cycle has a row in `results.md` — no exceptions
- `current-understanding.md` only changes on keep cycles
- Each experiment directory has an `analysis.md` with full reasoning
- The "one ping" test: every cycle's outcome can be stated in one sentence
- No cycles wasted on tangential exploration that doesn't serve the research goal
- When stuck, the 9-step protocol is followed before giving up on a hypothesis
- Independent hypotheses are batched in parallel by default; sequential only when dependencies exist
- `current-understanding.md` is written only by the main agent during the merge phase, never by subagents
