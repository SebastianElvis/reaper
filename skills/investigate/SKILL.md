---
name: investigate
description: "Run investigation cycles that test hypotheses through proof verification, counterexample search, or security analysis, with keep-or-discard discipline. Use when asked to investigate, verify, prove, or disprove claims, or when iterating on research based on human feedback."
user-invocable: true
argument-hint: "[number-of-cycles] [--codex] or \"<feedback>\" [--codex]"
---

# Investigate

The core research loop. Run N investigation cycles, each testing a hypothesis and applying keep-or-discard discipline. Also handles human feedback for iterating on completed research.

## Usage

```
# Initial investigation
/reaper:investigate 10

# With Codex consultation — get AI feedback between cycles
/reaper:investigate 10 --codex

# Human feedback — iterate on existing results
/reaper:investigate "dig deeper into the liveness proof gap under partial synchrony"

# Human feedback with Codex consultation
/reaper:investigate "dig deeper into the liveness proof gap under partial synchrony" --codex
```

Default: 5 cycles if no argument given. If the argument is quoted text (not a number), it is treated as human feedback (see Feedback Mode below).

### The `--codex` Flag

When `--codex` is passed, the skill consults an external AI (OpenAI Codex via MCP) after each batch's merge phase for an independent second opinion. This establishes an automated feedback loop where Codex plays **devil's advocate** or provides **alternative inspiration**, supplementing human feedback.

**Requires**: The `codex-cli` MCP server registered with Claude Code (see [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server)): `claude mcp add codex-cli -- npx -y codex-mcp-server`.

**Fallback**: If the Codex MCP tools are unavailable (server not registered, connection failure, etc.), skip the consultation step silently and continue the investigation loop as normal. Log a note in the experiment directory that Codex consultation was requested but unavailable.

## Inputs

Read before starting:
- `reaper-workspace/notes/hypotheses.md` — the testable claims
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
    Plan:     read hypotheses.md + results.md → dependency graph → batch of independent hypotheses
    Dispatch: spawn one subagent per hypothesis (parallel, in one message)
    Merge:    collect results → append to results.md → integrate "keep" insights into current-understanding.md
    Consult:  [if --codex] ask Codex for critique or inspiration → triage → add hypotheses
```

### Plan Batch

1. Read `hypotheses.md` and `results.md`
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

#### Proof Techniques Catalog

Choose the proof technique that matches the claim type. The technique determines the proof structure — don't mix paradigms within a single argument.

**Cryptographic proof techniques** (see Shoup [ePrint 2004/332] for game-based proofs and Lindell [ePrint 2016/046] for simulation-based proofs):

| Technique | When to Use | Core Idea | Key Pitfalls |
|-----------|-------------|-----------|--------------|
| **Game-based (sequence of games / game hopping)** | Proving IND-CPA, IND-CCA, EUF-CMA, and similar computational security notions | Define a sequence of games G₀, G₁, ..., Gₖ where G₀ is the real security game and Gₖ is trivially secure. Bound the distinguishing advantage between each consecutive pair. Total advantage ≤ Σ advantages. | Each hop must be justified (syntactic change, computational assumption, or statistical argument). The sum of advantages must remain negligible. Don't lose track of which game you're in. |
| **Simulation-based (ideal/real paradigm)** | Proving security of MPC protocols, commitment schemes, zero-knowledge proofs — any setting where "security" means "the adversary learns nothing beyond the output" | Construct a simulator S that, given only the ideal-world output, produces a view indistinguishable from the adversary's real-world view. Security means: for every PPT adversary A, there exists PPT simulator S such that REAL_A ≈ IDEAL_S. | The simulator must handle ALL adversary behaviors including abort. Simulator must run in expected PPT. Rewinding is allowed in standalone but NOT in UC. The simulation must be indistinguishable — state precisely whether computationally, statistically, or perfectly. |
| **UC (Universal Composability)** | Proving security that holds under arbitrary concurrent composition with other protocols | Define an ideal functionality F. Prove that for every environment Z and adversary A, there exists a simulator S such that Z cannot distinguish the real protocol from the ideal interaction with F and S. | No rewinding allowed — use equivocation or straight-line extraction instead. The environment Z is the distinguisher and is the most powerful entity. Composition theorem gives security for free but proving UC security is strictly harder than standalone. |
| **Reduction** | Proving hardness-based security — "breaking the scheme implies solving a hard problem" | Given adversary A that breaks property P with advantage ε, construct algorithm B that solves hard problem H with advantage related to ε. | Check tightness (see Reduction Quality Gate). Reduction must handle ALL oracle queries. Watch for exponential security loss in multi-instance settings. Programming random oracle / CRS must produce correct distribution. |
| **Hybrid argument** | Bounding advantage across many instances or many rounds | Define hybrid distributions H₀, ..., Hₙ that interpolate between two endpoints. Show adjacent hybrids are indistinguishable. | Security loss is typically linear in the number of hybrids (n). For n exponential in security parameter, the argument gives nothing useful. Consider tight reductions or complexity leveraging. |

**Distributed computing proof techniques:**

| Technique | When to Use | Core Idea | Key Pitfalls |
|-----------|-------------|-----------|--------------|
| **Safety by invariant** | Proving agreement, consistency, validity | Define a predicate Inv over global states. Show: (1) Inv holds initially, (2) every protocol step preserves Inv, (3) Inv implies the safety property. | The invariant must be inductive — it must be preserved by EVERY possible step, including adversarial ones. A common error is proving the invariant holds for honest steps but not for Byzantine behavior. |
| **Liveness by eventual argument** | Proving termination, progress, fairness | Show that under the timing/fault assumptions, some progress measure eventually increases or some good event eventually occurs. Often: after GST, honest messages arrive within Δ, so a decision is reached within f(Δ, n, t) time. | Liveness proofs under partial synchrony must be explicit about what happens before GST (nothing is guaranteed) vs after GST. Don't assume synchrony holds globally. FLP means you need randomization or partial synchrony — be clear which you use. |
| **Indistinguishability / partitioning** | Proving impossibility results, lower bounds | Construct two executions that are indistinguishable to some party or set of parties, yet require different outputs — a contradiction. Classic: partition n parties into groups that can't tell which partition they're in. | The indistinguishability argument must account for ALL information available to the parties, including message timing in synchronous models. |
| **Bivalence / valency** | Proving FLP-style impossibility | Show that an initial configuration is bivalent (both 0 and 1 are reachable). Show that every deterministic step from a bivalent configuration leads to another bivalent configuration or a contradiction with fault tolerance. | Only applies to deterministic protocols. Randomized protocols circumvent FLP via probabilistic termination. |
| **Counting / quorum intersection** | Proving properties of quorum-based protocols | Show that any two quorums intersect in enough honest parties to guarantee consistency. For n = 3t+1: any two sets of 2t+1 intersect in t+1, of which at least 1 is honest. | The intersection argument fails if the corruption threshold is violated. Be precise about whether you need "at least one honest in intersection" vs "honest majority in intersection." |

When selecting a technique, state it explicitly in the proof header. If the chosen technique doesn't work after a genuine attempt, this is useful information — log which technique failed and why, then try an alternative technique in the next cycle.

Requirements for formal proofs:

- **Properties** (correctness, liveness, safety, fairness, etc.): State the property as a formal predicate. Prove it holds under the stated assumptions. If the property holds conditionally, state the conditions precisely.
- **Performance metrics** (time complexity, communication complexity, round complexity, storage, etc.): State the bound as a formal claim (e.g., "The protocol terminates in O(f(n)) rounds"). Prove the bound by construction or by reduction to known results. Distinguish between worst-case, average-case, and amortized bounds.
- **Security properties** (via reduction): State the security definition, construct the simulator/reduction, and prove the bound on advantage. Make the reduction tight or state the tightness gap.
- **Impossibility results**: State what is being shown impossible, under which model. Prove by contradiction or by reduction to a known impossibility.

If a proof attempt fails or has gaps:
- Document exactly where the proof breaks down
- State what additional assumption would close the gap
- Log the cycle as `inconclusive` with the gap described

Do not claim a property or metric holds without a proof. Conjectures are acceptable but must be clearly labeled as such, with evidence for and against.

#### Reduction Quality Gate

Every reduction-based argument must answer ALL of the following before being marked `confirmed`. If any answer is "unclear" or "not applicable" without justification, the cycle outcome must be `inconclusive`, not `confirmed`.

1. **Embedding**: How is the challenge instance embedded in the protocol? Is the embedding perfect, statistical, or computational?
2. **Simulation**: Does the simulator handle ALL adversary queries? List the query types (signing, corruption, random oracle, etc.) and how each is answered.
3. **Extraction**: How is the solution extracted from a successful adversary? Does extraction work for ALL winning conditions in the security game?
4. **Tightness**: What is the concrete security loss? Express as ε_scheme ≤ f(ε_assumption, q, ...). Is f polynomial in all parameters? If the loss is superpolynomial, the reduction gives no meaningful concrete security.
5. **Rewinding**: Does the reduction rewind the adversary? If yes, is rewinding valid in the stated composition model? (Rewinding is NOT valid in UC.)
6. **Abort analysis**: What happens if the adversary aborts mid-protocol? Does the reduction still extract or must it restart?
7. **Programming**: Does the reduction program the random oracle / CRS? If so, is the programmed distribution indistinguishable from the real one?

#### Performance Sanity Checks

Before accepting any performance or complexity claim:

- **Lower bounds**: Compare against known lower bounds for the problem class. A claim of O(n) communication for Byzantine agreement without threshold signatures contradicts Dolev-Reischuk (Ω(n²)).
- **Concrete instantiation**: Plug in small concrete values (n=4, n=10, n=100). Does the concrete number make sense? Does it exceed trivially achievable bounds?
- **Comparison**: Compare against the performance of existing solutions to the same problem under the same model. A claimed improvement must actually improve.
- **Units**: Check units carefully — bits vs words vs field elements; per-round vs total; per-decision vs amortized; worst-case vs expected.

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
3. **Check for new hypotheses** generated by the batch (subagents may propose them). Add to `hypotheses.md`.
4. **Re-read updated state** and plan the next batch.

### Codex Consultation (when `--codex` is active)

After the merge phase and before planning the next batch, consult Codex for an independent critique. This step only runs when `--codex` was passed.

#### How It Works

Use the `codex` MCP tool to send a structured consultation request. Alternate between two roles each batch:

**Devil's Advocate** (odd batches: 1st, 3rd, 5th, ...):
Ask Codex to challenge the current findings. Send it:
- The current `current-understanding.md`
- The latest batch's results from `results.md`
- The prompt: *"You are reviewing a research investigation. Play devil's advocate: identify the weakest claims, unstated assumptions, logical gaps, or alternative explanations that the investigators may have missed. Be specific — point to exact claims and explain why they might be wrong."*

**Inspiration / Alternative Angles** (even batches: 2nd, 4th, 6th, ...):
Ask Codex for fresh perspectives. Send it:
- The current `current-understanding.md`
- The current `hypotheses.md` (unresolved only)
- The prompt: *"You are consulting on a research investigation. Suggest alternative proof strategies, related techniques from other fields, or hypotheses the investigators haven't considered. Focus on non-obvious connections and approaches that could break through current blockers."*

#### Processing Codex Feedback

1. **Log** the Codex response to `reaper-workspace/experiments/codex-consultation-batch-N.md` (where N is the batch number).
2. **Triage** the feedback — not all suggestions will be actionable:
   - **Actionable critique**: If Codex identifies a genuine gap or flaw, add a new hypothesis to `hypotheses.md` marked `[Codex-B<N>]` to be investigated in the next batch.
   - **Alternative approach**: If Codex suggests a promising technique, add it as a hypothesis marked `[Codex-B<N>]`.
   - **Already addressed**: If the point was already covered in prior cycles, note this in the consultation log and move on.
   - **Irrelevant or wrong**: Codex may hallucinate or misunderstand the domain. Dismiss with a brief note in the log.
3. **Do not block** on Codex feedback. If the MCP call times out or fails, continue to the next batch.

#### Session Continuity

Use a single Codex session ID across all consultations within one investigation run. This allows Codex to build context across batches rather than starting fresh each time. Pass the `sessionId` parameter to the `codex` tool, using a consistent ID like `"reaper-investigate-<timestamp>"`.

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

## Feedback Mode

When the argument is quoted text instead of a number, the skill enters feedback mode. This is used after a pipeline run has produced a report and the user wants to refine, deepen, or challenge specific findings.

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

**deepen**: Add targeted hypotheses to `hypotheses.md` marked with `[Round N]`, then run 5 investigation cycles (the standard loop above).

**explore**: Add new hypotheses to `hypotheses.md` marked with `[Round N]`. If the area may need additional literature, run the search scripts first and update `literature.md`. Then run 5 investigation cycles.

**rewrite**: No investigation cycles needed. Return control to the orchestrator to re-run `synthesize` only.

For **deepen** and **explore**, after completing the cycles, the orchestrator should re-run `synthesize` to produce an updated report.

## Quality Criteria

- Every cycle has a row in `results.md` — no exceptions
- `current-understanding.md` only changes on keep cycles
- Each experiment directory has an `analysis.md` with full reasoning
- The "one ping" test: every cycle's outcome can be stated in one sentence
- No cycles wasted on tangential exploration that doesn't serve the research goal
- When stuck, the 9-step protocol is followed before giving up on a hypothesis
- Independent hypotheses are batched in parallel by default; sequential only when dependencies exist
- `current-understanding.md` is written only by the main agent during the merge phase, never by subagents
- When `--codex` is active: every batch has a consultation log in `reaper-workspace/experiments/codex-consultation-batch-N.md`, and actionable feedback is tracked as hypotheses in `hypotheses.md`
