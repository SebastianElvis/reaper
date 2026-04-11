---
name: investigate
description: "Run investigation cycles that test hypotheses through proof verification, counterexample search, or security analysis, with keep-or-discard discipline. Use when asked to investigate, verify, prove, or disprove claims from a formalized research problem."
user-invocable: true
argument-hint: "[number-of-cycles]"
---

# Investigate

The core research loop. Run N investigation cycles, each testing a hypothesis and applying keep-or-discard discipline.

## Usage

```
/reaper:investigate 10
```

Default: 5 cycles if no argument given.

## Inputs

Read before starting:
- `reaper-workspace/notes/hypotheses.md` — the testable claims
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/results.md` — what's been tried and what happened

Also reference:
- `reaper-workspace/notes/paper-summary.md` — the source paper
- `reaper-workspace/notes/literature.md` — known prior work
- `references/methodology.md` — proof/analysis patterns

## The Loop

For each cycle (1 to N):

### Step 1: Select Hypothesis

Pick the highest-priority **unresolved** hypothesis from `hypotheses.md`. Check `results.md` to avoid repeating failed approaches on the same hypothesis. If all hypotheses are resolved, formulate new ones based on what you've learned (see When Stuck, step 6).

### Step 2: Create Experiment Directory

Create `reaper-workspace/experiments/NNN-<slug>/` where:
- `NNN` is the zero-padded cycle number (001, 002, ...)
- `<slug>` is a short descriptor (e.g., `proof-lemma3`, `counterex-2party`, `alt-reduction`)

### Step 3: Investigate

Do the actual research. This is the core intellectual work. Depending on the hypothesis:

- **Proof verification**: Check each step of an existing proof. Look for gaps, implicit assumptions, boundary cases. Consult `references/methodology.md` for patterns.
- **Proof attempt**: Try to prove the claim. Start with the simplest approach. If it works, check if a simpler proof exists.
- **Counterexample search**: Try to disprove the claim. Start small (2 parties, 1 round). Construct a specific adversary strategy and execution trace.
- **Security analysis**: Enumerate threat models, check if reductions go through, verify simulator constructions.
- **Comparison**: Compare approaches along specific dimensions (complexity, assumptions, properties).

Write all work — reasoning, attempts, dead ends, insights — to `reaper-workspace/experiments/NNN-<slug>/analysis.md`.

### Step 4: Evaluate

Did this cycle produce **genuine progress**? A cycle counts as progress if it:

- Confirms or refutes a hypothesis (fully or partially)
- Narrows the search space on an important question
- Identifies a new important question not previously considered
- Simplifies an existing argument (fewer assumptions, shorter proof)
- Corrects a prior error in understanding

**Simplicity criterion**: A proof that achieves the same result with fewer assumptions is better. Replacing a 3-page case analysis with a one-paragraph reduction is progress even if the "result" is unchanged. Don't accumulate tangential findings that don't serve the research goal.

**One "ping" per cycle**: The cycle's outcome should be statable in a single sentence. If it can't be, the cycle tried to do too much — note this and decompose in the next cycle.

### Step 5: Log

Append a row to `reaper-workspace/results.md`:

```
| NNN | H# | action-type | outcome | confidence | status | one-sentence description |
```

Where:
- **action-type**: proof-verification, proof-attempt, counterexample-search, security-analysis, comparison, literature-search, reformulation
- **outcome**: confirmed, refuted, partially-confirmed, inconclusive, new-hypothesis
- **confidence**: high, medium, low
- **status**: keep or discard

### Step 6: Keep or Discard

**keep** — The cycle produced genuine progress:
- Update `reaper-workspace/notes/current-understanding.md` with the new insight
- Write as if explaining at a whiteboard — crystallize understanding, don't just append notes
- The updated file should be coherent end-to-end, not a chronological log

**discard** — The cycle was a dead end:
- The experiment directory stays for the audit trail
- Do NOT touch `current-understanding.md`
- The row in `results.md` is the only trace in the running state

### Repeat

Go to Step 1 for the next cycle. Do not pause, do not ask if you should continue.

## Never-Stop Policy

Run all N cycles. The only valid early stop is **genuine convergence**: all hypotheses resolved with high confidence, and no new hypotheses worth pursuing. Uncertainty about whether the human wants you to continue is NEVER a reason to stop.

## When Stuck

If a cycle is going nowhere, escalate through these steps:

1. **Re-read the paper.** Look at sections you skimmed earlier. The answer is often in the details you glossed over.
2. **Re-read current-understanding.md.** What assumptions haven't been questioned? What's being taken for granted?
3. **Re-read results.md.** Can two "discard" results be combined into something useful? Patterns in dead ends are informative.
4. **Search for related work** you haven't found yet. Use WebSearch for specific technical questions that arose during investigation.
5. **Try a radically different approach** to the same hypothesis. If you've been trying direct proof, try reduction. If you've been trying construction, try impossibility.
6. **Formulate a new hypothesis** based on what you've learned so far. The investigation may have revealed that the original question was the wrong question.
7. **Invert the problem (Hamming).** Can't prove it? Try to disprove it. Can't find a counterexample? Ask what minimal assumption would make the proof work. What seems like a blockage often becomes the key insight.
8. **Apply Qian's patterns:**
   - *Fill in the blank*: What combination of assumptions/techniques hasn't been tried?
   - *Start small then generalize*: What's the simplest case? Can you solve it for n=2 first?
   - *Build a hammer*: Can a technique from a previous cycle apply here in a different way?

## Parallel Investigation

When multiple **independent** hypotheses exist and haven't been explored, you MAY spawn parallel subagents (using the Agent tool) to investigate them concurrently. Each subagent:
- Gets its own experiment directory (use non-overlapping cycle numbers)
- Follows the same loop protocol
- Writes to its own experiment directory and appends to `results.md`
- Only the main agent updates `current-understanding.md` (to avoid write conflicts)

Use parallel investigation when hypotheses are truly independent. If hypothesis H2 depends on the result of H1, investigate sequentially.

## Quality Criteria

- Every cycle has a row in `results.md` — no exceptions
- `current-understanding.md` only changes on keep cycles
- Each experiment directory has an `analysis.md` with full reasoning
- The "one ping" test: every cycle's outcome can be stated in one sentence
- No cycles wasted on tangential exploration that doesn't serve the research goal
- When stuck, the 8-step protocol is followed before giving up on a hypothesis
