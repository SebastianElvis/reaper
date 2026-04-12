---
name: brainstorm
description: "Generate, prioritize, and refine research ideas based on current investigation state. Use when the pipeline needs new or better hypotheses — after formalization, between investigation batches, or when all current ideas are resolved."
user-invocable: true
argument-hint: "[context-hint]"
---

# Brainstorm

The recurring ideation step. Reads the current research state and proposes new or refined ideas for investigation. This skill is lightweight and fast — it generates ideas, not experiments.

## Usage

```
# Generate ideas based on current state
/reaper:brainstorm

# With a hint about what direction to explore
/reaper:brainstorm "explore liveness under partial synchrony"
```

## Relationship to Other Skills

- **`formalize-problem`** handles *initial* formalization: pinning down trust assumptions, the core question, definitional hygiene, and the first set of hypotheses. It runs once.
- **`brainstorm`** handles *recurring* ideation: generating additional ideas as the investigation progresses. It runs many times.
- **`investigate`** handles *execution*: deep-diving into specific ideas. It does not generate new hypotheses.

## Inputs

**Always read** before starting:
- `reaper-workspace/notes/problem-statement.md` — model assumptions and property definitions
- `reaper-workspace/notes/ideas.md` — the current ideas and their resolution status
- `reaper-workspace/notes/current-understanding.md` — the "branch tip" of accumulated knowledge
- `reaper-workspace/notes/results.md` — what's been tried and what happened. **If the file is long (20+ rows), read the batch summaries at the end instead of every individual row.** Look for patterns in failures across batches, not individual cycle details.

**Lazy-load only when needed** (skip these unless you're stuck or exploring a specific direction):
- `reaper-workspace/notes/paper-summary.md` — the source paper
- `reaper-workspace/notes/literature.md` — known prior work
- `reaper-workspace/notes/clarified-goal.md` — refined research goal and scope
- `reaper-workspace/papers/` — downloaded PDFs and per-paper notes
- The optional context hint from the argument

## Process

### 1. Assess Current State

Read all inputs and build a picture of:
- **Resolved ideas**: Which hypotheses have been confirmed, refuted, or are no longer worth pursuing?
- **Unresolved ideas**: Which are still open? Are any stuck (multiple inconclusive cycles)?
- **Patterns in failures**: Do discarded cycles cluster around a common obstacle? A pattern in dead ends is itself informative.
- **Emerging themes**: Have "keep" results revealed a direction that wasn't anticipated in the original formalization?

### 2. Generate New Ideas

Apply these techniques systematically. Not all will produce ideas every time — use the ones that fit the current state.

#### Gap-Finding (Qian: Fill in the Blank)

Map the dimensions of existing work and find unexplored combinations. Consult `references/model.md` for the domain-appropriate gap-finding matrix dimensions. Which cells in this matrix are empty? Those are candidate hypotheses.

#### Problem Inversion (Hamming)

For each stuck or failed hypothesis, invert it:
- Can't prove it? Try to disprove it.
- Can't find a counterexample? Ask what minimal assumption would make the proof work.
- Can't achieve a property? Ask what weaker property is achievable, or what stronger model is needed.

What seems like a blockage often becomes the key insight.

#### Qian's Patterns

- **Start small then generalize**: What's the simplest case (n=2, 1 round, crash-only)? Can you solve it there first, then lift?
- **Build a hammer**: Can a technique from a previous cycle apply here in a different way? Look at "keep" results for reusable proof strategies.
- **Expansion**: Take a confirmed result and ask what happens when you relax one assumption.

#### Follow the Evidence

What do the "keep" results *imply* that hasn't been stated as a hypothesis yet? If you proved safety holds under X, does that suggest liveness might fail under X? If you found a gap in the proof, does the same gap appear in related protocols?

#### Negative Result Escalation

If a hypothesis has trended toward refutation over 3+ cycles (counterexample attempts partially succeed, proof attempts consistently fail at the same point):
- Propose a new hypothesis that *proves* the negative: "Protocol X cannot achieve property Y under model Z because..."
- Propose a "minimal fix" hypothesis: "What is the weakest additional assumption that restores property Y?"

### 3. Screen Against Known Impossibilities

For each candidate idea, check whether it contradicts a known impossibility or lower bound. Consult `references/impossibility-results.md` for the domain-relevant impossibility results and lower bounds.

If a candidate contradicts a known impossibility:
1. Flag it explicitly with a warning
2. Reformulate: "Under what additional assumptions does this become possible?" or "What weaker property can be achieved?"
3. Do NOT leave it as a hypothesis for investigate to waste cycles on

### 4. Prioritize (Hamming: Importance Filter)

Not all ideas are equally worth investigating. Rank by consequence — ask: "If we resolved this idea, who would care and why?" Consult `references/model.md` for domain-specific examples of how to rank by importance.

### 5. Write Output

Update `reaper-workspace/notes/ideas.md`:
- **New ideas**: Add under a clearly marked section.
- **Existing ideas**: If an idea should be deprioritized, marked as subsumed, or have its statement refined based on new understanding, **edit it inline** rather than leaving stale entries.

New ideas use this format:

```markdown
## Ideas — Brainstorm Round N

### H<next>: [Short descriptive title]
- **Statement**: [Precise, falsifiable claim — specific enough that a reader could disagree]
- **Success condition**: [What evidence would confirm this?]
- **Failure condition**: [What evidence would refute this?]
- **Priority**: High / Medium / Low
- **Rationale**: [Why this priority? What's the consequence of resolving it?]
- **Source**: [What prompted this idea — a pattern in failures, a gap in the matrix, an inversion of H<x>, etc.]
```

Where N is one more than the highest existing brainstorm round (or 1 if none exist). Use hypothesis numbers that continue from the highest existing H number.

**Constraints**:
- At most 3-5 new ideas per round — focus beats breadth
- Every idea must be **falsifiable** — a reader could disagree with it
- Every idea must have **explicit** success and failure conditions
- Do not duplicate existing unresolved ideas — check `ideas.md` first
- If the context hint from the argument suggests a direction, weight it heavily but don't ignore other promising directions

### 6. Report

After writing, briefly summarize to the orchestrator:
- How many new ideas were added
- What the highest-priority new idea is and why
- Whether any existing ideas should be deprioritized or marked as subsumed

## Quality Criteria

- Every new idea is falsifiable with explicit success/failure conditions
- Ideas are screened against known impossibilities before being added
- Priorities are justified by consequence, not convenience
- No duplication of existing unresolved ideas
- The source/motivation for each idea is documented
- At most 3-5 ideas per round — if you have more, merge or drop the low-priority ones
- The brainstorm round is fast — no experiments, no proof attempts, no literature searches within this skill
