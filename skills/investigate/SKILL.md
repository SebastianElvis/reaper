---
name: investigate
description: "This skill tests hypotheses with proofs, counterexamples, and analysis. You use it to verify, prove, or refute research claims."
user-invocable: true
argument-hint: "[number-of-cycles]"
license: Apache-2.0
compatibility: "The host should support parallel subagents. This skill uses sequential execution when the host cannot run subagents."
---

# Investigate

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

Each cycle tests one hypothesis and returns a keep or discard verdict.
You apply [research-state.md](../reaper/references/research-state.md) before dispatch, merge, and resume.

## Usage

You invoke this skill by name with an optional cycle count. The default count is 5. Slash-command hosts use `/investigate 10`.

```
investigate 10
investigate
```

## Inputs

You always read these files:

- `reaper-workspace/notes/problem-statement.md`
- `reaper-workspace/notes/ideas.md`
- `reaper-workspace/notes/current-understanding.md`
- `reaper-workspace/notes/results.md`

You read these sources only when a hypothesis needs them or progress stops:

- `reaper-workspace/notes/paper-summary.md`, if it exists.
- `reaper-workspace/notes/literature.md`
- `reaper-workspace/papers/`, including `<id>-notes.md` files.
- `../reaper/references/methodology.md`

## Batch Loop

You test independent hypotheses in parallel batches when the host supports subagents. You use sequential execution for dependent hypotheses or hosts without subagents. Each batch has three stages: plan, dispatch, and merge. You repeat batches while cycles remain and unresolved hypotheses exist.

### Plan

1. You read `ideas.md` and `notes/results.md`.
2. You identify unresolved hypotheses. You check previous results to avoid repeated failed approaches.
3. You map dependencies between hypotheses.
4. You select independent hypotheses within the remaining budget and host concurrency limit.
5. You assign consecutive cycle numbers to each subagent without overlap.
6. You use a batch of one if all remaining hypotheses form a dependency chain.
7. If all hypotheses are resolved, you return to the orchestrator. It can invoke `brainstorm` for more ideas.

### Dispatch

You start one subagent per hypothesis with the host's parallel tool. You start the batch in one message when the host permits this. You give each subagent these inputs:

- Its cycle numbers and hypothesis.
- Two or three relevant findings from `current-understanding.md`, usually 200-500 words.
- A pointer to `current-understanding.md` for additional context.
- The single-cycle procedure in Steps A-E.
- A request for result rows, a verdict, and any keep finding to merge.

You do not send the full current-understanding file to every subagent. Subagents read shared notes without changing them during the batch.

### Step A: Create the Investigation Directory

For a new hypothesis, you create `reaper-workspace/investigations/NNN-<slug>/`. `NNN` is the assigned cycle number with leading zeros, such as `001`. `<slug>` is a short description, such as `proof-lemma3`.

For a repeated hypothesis, you reuse its existing directory. You keep the original directory number. You edit `analysis.md` and `proof.md` in place. The result row uses the new cycle number.

### Step B: Investigate

You select the method for the hypothesis's immediate task:

- **Proof verification:** You check an existing proof for missing steps, hidden assumptions, and boundary errors.
- **Counterexample search:** You construct an execution that violates a claim. You start with small cases.
- **Comparison:** You compare approaches under the same specified conditions.
- **New proof:** You construct an argument for a claim without an existing proof to check or a counterexample to build.

For a new proof, you use `security-analysis` for security claims and `performance-analysis` for cost claims.
You use `proof-attempt` for other claims. You check whether the proof can use fewer steps or assumptions.

You draft the claim and a small example in `analysis.md` before developing the argument. You label unresolved parts. You record reasoning, attempts, failed approaches, and findings in that file. On a revisit, you revise the existing text to show the current understanding.

#### Parallel Work Within a Cycle

If the result is uncertain, you can start separate proof and counterexample subagents with distinct output paths. You collect both results within the cycle budget. You verify each result and resolve conflicts under the shared contract. You record incomplete work and unresolved conflicts without accepting either outcome. You can also search IACR, arXiv, and the web in parallel when progress stops.
If evidence already strongly favors one outcome, you use the corresponding method.

#### Formal Proof Structure

You write formal claims and proofs in `reaper-workspace/investigations/NNN-<slug>/proof.md`.
Each entry uses `## Theorem/Lemma/Proposition N: <name>` and these fields:

- **Statement:** You give the exact mathematical claim.
- **Assumptions:** You list every model, hardness, and network assumption.
- **Proof:** You number logical steps and justify each with a definition, assumption, lemma, or source. You end with ∎.
- **Proof technique:** You name the method, such as reduction, induction, simulation, or hybrid argument.

You use the proof methods, Reduction Quality Gate, and performance checks in `../reaper/references/methodology.md`. You state the selected method in the proof header. If an attempt fails, you record the method and cause. You try another method in the next cycle.

You state precise properties and model assumptions for every proof.
Security proofs use the selected definition. Reduction arguments also state their advantage bounds and loss.
Performance proofs distinguish worst-case, average, and amortized costs.
Impossibility proofs specify the excluded behavior and use contradiction or reduction.

If a proof has a gap, you identify the exact step. You state any additional assumption that closes the gap. You log an incomplete proof attempt as `inconclusive`. You label unproven claims as conjectures.

### Step C: Evaluate

A cycle makes progress through a changed answer, a new question, a simpler argument, or an error correction.
A changed answer can confirm, refute, or narrow a hypothesis.
You describe each finding once, even when it has multiple effects.

You prefer a proof with fewer assumptions or fewer steps for the same result. You exclude findings that do not support the research goal. You state the cycle outcome in one sentence.
If the outcome needs multiple claims, you record that issue for the next cycle.

#### Classify Proof Issues

| Issue | Meaning | Outcome |
|---|---|---|
| Gap (unverified) | The proof lacks a justified step. A plausible repair does not establish the claim. | `inconclusive` |
| Gap (structural) | The proof method cannot establish the claim as written. You test an alternative proof. | `inconclusive` |
| Counterexample | A concrete counterexample or execution trace violates the claim. | `refuted` |
| Overclaim | The proof establishes a weaker claim. You state the exact weaker result. | `partially-confirmed` |

#### Check Composition

When you confirm a core property, you check its effect on composition. You use `../reaper/references/definitional-standards.md` for relevant conditions, such as rewinding or shared setup. You record composition limits in `analysis.md`, even if the hypothesis did not request this check.

### Step D: Log

You use the result fields and cycle-log format in the shared contract.
You set Action to `proof-verification`, `proof-attempt`, `counterexample-search`, `security-analysis`, `performance-analysis`, `comparison`, `literature-search`, or `reformulation`.
Workers return result rows and evidence links to the main agent. They do not change shared notes.
You use high confidence only for evidence that you verified within its stated scope. You label unchecked arguments and conjectures explicitly.

### Step E: Keep or Discard

You return `keep` and the finding when Step C shows progress. Otherwise, you return `discard`. You retain every investigation directory for the audit record. Subagents do not write to `current-understanding.md`.

### Merge

The main agent waits for all subagents in the batch. It performs these actions:

1. It updates existing hypothesis rows in `notes/results.md`.
2. It adds rows only for new hypotheses. It orders rows by hypothesis number.
3. It verifies evidence links and merges keep findings with claim IDs, assumptions, dependencies, status, and limits. It marks affected dependent claims stale.
4. It adds new hypotheses from the batch to `ideas.md`.
5. It updates resolved, lower-priority, or covered ideas in place.
6. It adds a batch summary after the results table.
7. It reads the updated state before it plans another batch.

The summary uses `## Batch Summary (Cycles NNN-MMM)`.
It lists Keep findings and Discard patterns with one sentence per finding or pattern.

Only the main agent writes shared notes during merge. The `brainstorm` and `write-paper` skills use batch summaries to reduce file reading. For a batch of one, the main agent can run Steps A-E directly.

## Completion

You run at most N cycles within the shared budget. You return when the goal resolves, no useful method remains, the budget ends, or reformulation is required. You report unresolved claims and the stop reason.

## When Progress Stops

You select a useful option from "When Progress Stops" in `../reaper/references/methodology.md`. You use `../reaper/references/search-tools.md` for search commands. You invoke `/search-paper` to execute the applicable `arxiv.py` or `iacr.py` command. Workers return the command result or execution error with their findings.

You download relevant new papers to `reaper-workspace/papers/`. You write `<id>-notes.md` for each paper. Workers return literature findings to the main agent. The main agent integrates them into the existing sections of `notes/literature.md`. You do not create a separate section for additions during investigation. You log the search with action-type `literature-search`.

If no distinct useful method remains, you log `inconclusive` and return. The orchestrator can invoke `brainstorm` after the batch.

## Negative Results

You accept a verified counterexample immediately. Repeated proof failure alone does not refute a claim. You change method when an attempt provides no new evidence.

1. You attempt a concrete attack, execution trace, or reduction to a known impossibility.
2. You identify the weakest additional assumption that restores the positive claim.
3. You record a supported negative result as outcome `refuted` and status `keep`.
4. You state the result and its implications in the cycle description for later brainstorming.

You do not repeat minor changes to the same failed proof method.

## Re-Formalization Protocol

If a cycle finds incorrect model assumptions, a wrong core question, or incorrect property definitions, you request reformulation.

1. You log outcome `reformulate` and status `keep`.
2. You add `## Re-Formalization Signal` to the cycle's `analysis.md`.
3. That section states the error, evidence, and proposed correction.
4. You start the result description with `REFORMULATE`, followed by a one-sentence explanation.
5. You stop further batches and return the signal to the orchestrator.

The orchestrator invokes `formalize-problem` with this evidence before investigation resumes.
