---
name: formalize-problem
description: "Formalize a research question into precise, testable hypotheses with trust assumptions, security properties, and explicit success/failure conditions. Use when asked to formalize, define, or scope a research problem after paper analysis."
user-invocable: true
argument-hint: "<research-goal>"
---

# Formalize Problem

Transform a research goal into precise, testable hypotheses with explicit success/failure conditions.

## Usage

```
/reaper:formalize-problem "determine if the security proof in Section 4 holds under asynchrony"
```

## Instructions

### 1. Read Inputs

Read these files:
- `reaper-workspace/notes/clarified-goal.md` — refined research goal, scope, assumptions, and success criteria
- `reaper-workspace/notes/paper-summary.md` — what the paper claims and how
- `reaper-workspace/notes/literature.md` — what's already known, what gaps exist
- The research goal from the argument (use the refined goal from `clarified-goal.md` if available)

### 2. Identify the Core Question

What exactly needs to be resolved? Be specific. "Is this protocol secure?" is too vague. "Does the safety proof of Protocol X hold when the adversary is adaptive rather than static?" is testable.

### 3. Pin Down Trust Assumptions (must be unambiguous before hypotheses)

Pin down every dimension of the trust/system model. If any dimension is left vague, the investigation will produce ambiguous results. Complete this checklist — every field must have a concrete answer, not "TBD":

- **Communication**: point-to-point / broadcast / both? Authenticated channels? Reliable delivery?
- **Timing**: synchronous (known Δ) / partially synchronous (unknown Δ, known GST) / asynchronous?
- **PKI/setup**: plain model / PKI / CRS / trusted dealer / random oracle / algebraic group model?
- **Corruption timing**: static (before execution) / adaptive (during execution) / mobile (between epochs)?
- **Corruption power**: crash / omission / Byzantine / covert?
- **Corruption bound**: exact expression (e.g., t < n/3, t < n/2). State whether the bound is strict.
- **Computation**: PPT / information-theoretic (unbounded adversary)?
- **Composition**: standalone / sequential / UC / GUC?
- **Cryptographic assumptions**: e.g., DDH, CDH, LWE, random oracle model. List all.
- **Protocol-specific assumptions**: e.g., honest dealer in setup phase, synchronous bootstrap period.

Every hypothesis must reference these trust assumptions by specifying which parameters it holds under. A hypothesis that says "the protocol is secure" without pinning every dimension is rejected.

### 4. Apply Importance Filter (Hamming)

Not all questions are equally worth investigating. Prioritize by consequence:
- A security proof gap that invalidates a deployed protocol > a tighter constant in a complexity bound
- An impossibility result that rules out an entire approach > an incremental improvement
- A finding that changes how practitioners build systems > a purely theoretical curiosity

Ask: "If we resolved this question, who would care and why?"

### 5. Apply Gap-Finding (Qian)

Map the dimensions of existing work and find unexplored combinations:
- Threat models (static/adaptive × sync/async/partial-sync × corruption thresholds)
- Protocol families (leader-based, leaderless, DAG-based, etc.)
- Security properties (safety, liveness, fairness, accountability, etc.)

Which cells in this matrix are empty? Those are candidate hypotheses.

### 6. Screen Against Known Impossibilities

For each hypothesis, check whether it contradicts a known impossibility or lower bound:

- **FLP** [Fischer, Lynch, Paterson 1985]: No deterministic consensus in asynchrony with even 1 crash fault
- **DLS** [Dwork, Lynch, Stockmeyer 1988]: No partially-synchronous consensus tolerating t ≥ n/3 Byzantine faults
- **Byzantine agreement bound**: Requires t < n/3 without trusted setup (or t < n/2 with PKI + randomization)
- **Dolev-Strong**: Authenticated broadcast requires t < n
- **Fischer-Lynch-Merritt**: k-set agreement impossible with t ≥ k crash faults in async
- **Communication lower bounds**: Ω(n²) for deterministic Byzantine agreement without threshold signatures (Dolev-Reischuk)
- **Authenticated channels**: Many impossibilities disappear with a PKI — check whether the paper's model includes one

If a hypothesis asks to prove something that an impossibility result rules out:
1. **Flag it explicitly** in the hypothesis with a warning
2. **Reformulate**: "Under what additional assumptions does this become possible?" or "What weaker property can be achieved?"
3. Do NOT leave it as a hypothesis for the investigate skill to waste cycles on

### 7. Enforce Definitional Hygiene

Each security property listed in the output must be stated as one of:
- A **formal predicate** over executions/views (e.g., "For all executions E, if honest parties p_i and p_j both output, then output(p_i) = output(p_j)")
- A **game-based definition** (e.g., "For all PPT adversaries A, Pr[Game^A = 1] ≤ negl(λ)")
- A **simulation-based definition** (e.g., "There exists a PPT simulator S such that REAL ≈_c IDEAL")
- A **reference** to a specific definition in a specific paper (e.g., "Agreement as defined in [CKPS01, Definition 2]")

"Safety" or "liveness" without a formal definition is NOT acceptable. Different papers define these differently — pin it down. If the paper under analysis uses informal definitions, formalize them explicitly and note that you are doing so.

### 8. Write Output

Write to `reaper-workspace/notes/problem-statement.md`:

```markdown
# Problem Statement

## Research Goal
[Restate the goal precisely]

## Trust Assumptions
- Communication:
- Timing:
- PKI/setup:
- Corruption timing:
- Corruption power:
- Corruption bound:
- Computation:
- Composition:
- Cryptographic assumptions:
- Protocol-specific assumptions:

## Security Properties Under Investigation
[What must hold? List each property with its formal definition or reference.]
1. **[Property name]**: [formal definition or citation]
2. ...

## Performance Metrics
[Concrete targets, if applicable]
- Communication complexity:
- Round complexity:
- Other:

## Ideas

### H1: [Short descriptive title]
- **Statement**: [Precise, falsifiable claim — specific enough that a reader could disagree]
- **Success condition**: [What evidence would confirm this?]
- **Failure condition**: [What evidence would refute this?]
- **Priority**: High / Medium / Low
- **Rationale**: [Why this priority? What's the consequence of resolving it?]

### H2: [Short descriptive title]
...
```

### Quality Criteria

- Every hypothesis is **falsifiable** — a reader could disagree with it
- Every hypothesis has **explicit** success and failure conditions — not "we'll know it when we see it"
- Priorities are justified by consequence, not convenience
- Trust assumptions are complete — no missing dimensions
- The hypotheses collectively cover the research goal — resolving all of them would answer the original question
- At most 5-7 hypotheses — focus beats breadth. If you have more, merge or drop the low-priority ones
