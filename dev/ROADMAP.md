# Reaper Development Roadmap

## Vision

**Reaper is an AI-native scientific research pipeline.** It takes a research paper and a research goal as input, and autonomously conducts rigorous, multi-step academic research — the kind a PhD student would do over days or weeks, compressed into hours.

### Value Proposition

Today, AI can answer questions about papers. Reaper goes further: it *does research*. Given a paper on a new consensus protocol and the goal "determine if this is secure under asynchrony," Reaper will read the paper, search arXiv and IACR ePrint for related work, formalize the problem, attempt a proof or construct a counterexample, seek feedback from other AI models, and produce a structured research report with full reasoning traces.

The key insight: research is a *pipeline* of distinct, composable activities (read, search, formalize, analyze, verify, synthesize), not a monolithic task. Reaper decomposes this pipeline into individual skills that can be invoked independently or orchestrated together, and leverages parallel subagents and multi-model feedback to approximate the quality of collaborative human research.

### Heritage: Karpathy's autoresearch

Reaper is inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — a system that gives an AI agent a small LLM training setup and lets it experiment autonomously overnight. The agent modifies `train.py`, trains for 5 minutes, checks if val_bpb improved, keeps or discards the change, and repeats — ~100 experiments while you sleep.

Autoresearch works because of disciplined constraints: one file to modify (`train.py`), one file to steer (`program.md`), one metric (`val_bpb`), one fixed evaluation harness (`prepare.py`), and a tight keep-or-discard loop that runs indefinitely without human intervention.

Reaper adapts this methodology from ML experimentation to theoretical academic research. The domain is different — proofs instead of training runs, hypotheses instead of hyperparameters — but the core loop discipline is the same.

---

## Methodology

Reaper's research loop is built on six principles that ensure autonomous, disciplined, high-quality investigation.

### Principle 1: Separation of Concerns

The AI and the human have non-overlapping territories:

- **AI writes to `workspace/`** — notes, experiments, results, reports. This is the AI's exclusive working space.
- **Human writes the research goal prompt** — the paper to analyze and what to investigate. This is the sole steering mechanism.
- **SKILL.md files and workspace file contracts are fixed** — they define the pipeline, evaluation criteria, and interfaces between skills. Neither the AI nor the human modifies them during a run.

| Role | What |
|------|------|
| AI modifies | `workspace/` (notes, experiments, report) |
| Human provides | Research goal prompt (paper + what to investigate) |
| Fixed harness | SKILL.md files + workspace file contracts |

### Principle 2: Fixed Evaluation Signal

Before investigation begins, the problem must be precisely defined with concrete evaluation criteria. This happens in two stages:

**Stage 1: Establish baseline.** Before formalizing the problem, `analyze-paper` and `review-literature` establish what is already known — the paper's claims, existing approaches, and the state of the art. This grounds the investigation in reality rather than starting from a vacuum.

**Stage 2: Formalize the problem.** `formalize-problem` then produces a problem statement in `notes/hypotheses.md` containing:

- **Trust assumptions**: What is the system model? Who is honest, who is adversarial, what can the adversary do? (e.g., "static adversary corrupting up to t < n/3 parties in a partially synchronous network")
- **Security properties**: What must hold? (e.g., "agreement, termination, and external validity under the stated threat model")
- **Performance metrics/goals**: What are the concrete targets? (e.g., "O(n) communication complexity per decision, finality in 3 rounds")
- **Testable claims**: Derived from the above — specific hypotheses with explicit success/failure conditions

Every investigation cycle is then evaluated against these fixed criteria — did the cycle make progress toward confirming or refuting a specific claim?

Progress is tracked in `results.md` (see Principle 3).

### Principle 3: Structured Results Log

`workspace/results.md` logs every investigation cycle in a structured table:

```markdown
| Cycle | Hypothesis | Action | Outcome | Confidence | Status | Description |
|-------|-----------|--------|---------|------------|--------|-------------|
| 001 | H1 | Proof verification | Refuted | High | keep | Found gap in Lemma 3.2 — simulator doesn't handle abort |
| 002 | H2 | Counterexample search | Inconclusive | Low | discard | Tried 2-party case, no counterexample found, approach too narrow |
| 003 | H1 | Alternative proof | Confirmed | Medium | keep | Constructed fix for Lemma 3.2 using rewinding |
```

- **keep**: The cycle produced a meaningful advance in understanding. Findings propagate to `notes/current-understanding.md`.
- **discard**: The cycle was a dead end. It stays logged in `results.md` and its experiment directory, but does not update the running state.

This is the ground-truth scoreboard. Every cycle gets a row, no exceptions.

### Principle 4: Keep-or-Discard Loop

`notes/current-understanding.md` is the "branch tip." It represents the best current understanding of the research question. After each investigation cycle:

- If the cycle produced genuine progress (new finding, resolved hypothesis, corrected error) → **keep**: update `current-understanding.md` with the new insight.
- If the cycle was unproductive (dead end, inconclusive without useful narrowing, redundant with prior work) → **discard**: log it in `results.md`, leave the experiment directory for the audit trail, but do not touch `current-understanding.md`.

The AI always works from the best-known state. This prevents accumulation of noise in the working state while preserving the full history for audit.

### Principle 5: Never Stop

Run all N cycles without asking "should I continue?" The only valid early stop is genuine convergence — all hypotheses resolved with high confidence. If stuck:

1. Re-read the paper. Look at sections you skimmed earlier.
2. Re-read `notes/current-understanding.md`. What assumptions haven't been questioned?
3. Re-read `results.md`. Can two "discard" results be combined into something useful?
4. Search for related work you haven't found yet.
5. Try a radically different approach to the same hypothesis.
6. Formulate a new hypothesis based on what you've learned so far.

Uncertainty about whether the human wants you to continue is *never* a reason to stop. The human will interrupt when they want you to stop.

### Principle 6: Simplicity Criterion

- A proof that achieves the same result with fewer assumptions is better.
- Replacing a 3-page case analysis with a one-paragraph reduction is progress, even if the "result" is unchanged.
- If removing a hypothesis and still reaching the same conclusion, that's a simplification win — keep it.
- Don't accumulate tangential findings that don't serve the research goal. Depth on the core question beats breadth across distractions.

When evaluating whether a cycle produced progress, weight clarity and elegance alongside novelty.

---

## Project Structure

### Skill Repository (this repo)

```
autoresearch/
├── .claude/skills/reaper/
│   ├── SKILL.md                        # Orchestrator — composes the pipeline
│   ├── skills/
│   │   ├── analyze-paper/SKILL.md      # /reaper:analyze-paper
│   │   ├── review-literature/SKILL.md  # /reaper:review-literature
│   │   ├── formalize-problem/SKILL.md  # /reaper:formalize-problem
│   │   ├── investigate/SKILL.md        # /reaper:investigate (proof/analysis cycles)
│   │   ├── cross-verify/SKILL.md       # /reaper:cross-verify (multi-model feedback)
│   │   └── synthesize/SKILL.md         # /reaper:synthesize (report generation)
│   └── references/
│       ├── methodology.md              # Research methodology patterns
│       ├── paper-analysis.md           # How to read/extract from papers
│       └── mcp-tools.md               # Available MCP tools and when to use them
├── dev/
│   ├── ROADMAP.md                      # This file
│   └── test-papers/                    # Papers for testing
├── evals/
│   └── evals.json                      # Test cases for skill evaluation
└── README.md
```

### User's Workspace (generated at runtime)

When a user invokes `/reaper`, this structure is created in their working directory:

```
reaper-workspace/
├── notes/
│   ├── paper-summary.md                # Structured extraction from the paper
│   ├── literature.md                   # Related work found during search
│   ├── hypotheses.md                   # Problem statement + testable claims
│   ├── current-understanding.md        # "Branch tip" — only advances on keep
│   └── scratchpad.md                   # Free-form reasoning
├── experiments/
│   └── NNN-<name>/                     # One directory per investigation cycle
├── feedback/                           # Cross-model review responses
├── results.md                          # Structured cycle log (keep/discard per cycle)
├── log.md                              # Append-only timestamped narrative log
└── report.md                           # Final synthesized output
```

---

## Horizons

Each horizon enriches a specific stage of the methodology pipeline. H1 builds the decomposed pipeline from day one. H2 enriches the baseline stage. H3 strengthens the evaluation signal. H4 expands what kinds of research the pipeline can do.

```
Methodology stage:     Baseline → Formalize → Investigate → Synthesize
                         │           │            │             │
H1 The Pipeline:       paper + web  ✓            ✓             ✓
H2 The Library:        + arXiv/ePrint MCP         + mid-loop search
H3 The Committee:                                 + multi-model review
H4 The Lab:            + multi-paper              + computation   + LaTeX
```

### Horizon 1: The Pipeline

**Methodology stage:** All four stages, decomposed into independent skills from day one.

**Goal:** Build the full research pipeline as composable sub-skills that each map 1:1 to a methodology stage. Each skill is independently useful, has a clear file contract, and can be composed by the orchestrator with subagent parallelism. Literature search uses WebSearch initially (MCP servers come in H2).

**What success looks like:** `/reaper paper.pdf "check if the security proof in Section 4 holds under asynchrony"` produces a workspace with:
- `notes/hypotheses.md` containing a precise problem statement (trust assumptions, security properties, performance goals)
- `results.md` showing cycle-by-cycle progression with keep/discard decisions
- `current-understanding.md` with the accumulated findings
- `report.md` that a researcher would find genuinely useful

And each skill works standalone: `/reaper:analyze-paper paper.pdf` for just a structured summary, `/reaper:formalize-problem` for just a problem statement, etc.

#### Skills and File Contracts

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/reaper:analyze-paper` | Stage 1a: Baseline (paper) | Input paper | `notes/paper-summary.md` |
| `/reaper:review-literature` | Stage 1b: Baseline (literature) | Goal prompt, `notes/paper-summary.md` | `notes/literature.md` |
| `/reaper:formalize-problem` | Stage 2: Formalize | `notes/paper-summary.md`, `notes/literature.md`, goal prompt | `notes/hypotheses.md` (trust assumptions, security properties, performance goals, testable claims) |
| `/reaper:investigate` | Stage 3: Investigate (one cycle) | `notes/hypotheses.md`, `notes/current-understanding.md` | `experiments/NNN-<name>/`, appends to `results.md`, conditionally updates `current-understanding.md` |
| `/reaper:synthesize` | Stage 4: Synthesize | All `notes/`, `experiments/`, `results.md` | `report.md` |
| `/reaper` | Orchestrator | Paper + goal prompt | Full workspace |

#### Subagent Parallelism

- **Orchestrator**: Run `analyze-paper` and `review-literature` as parallel subagents (Stage 1a and 1b are independent)
- **`review-literature`**: Spawn parallel subagents to search different sources simultaneously, then merge results
- **`investigate`**: When multiple independent hypotheses exist, spawn parallel subagents to explore them concurrently

#### Tasks

- [x] Write `references/methodology.md` (proof verification, security analysis, protocol extension, comparison, counterexample patterns)
- [x] Write `references/paper-analysis.md` (extraction guide for crypto/distributed systems/blockchain papers)
- [ ] Define the workspace file contract between skills (the table above, formalized)
- [ ] Build `/reaper:analyze-paper`; test independently
- [ ] Build `/reaper:review-literature` (WebSearch only for now); test independently
- [ ] Build `/reaper:formalize-problem`; test that it produces trust assumptions + security properties + performance goals
- [ ] Build `/reaper:investigate` with full loop discipline:
  - `results.md` structured log with keep/discard per cycle (Principle 3)
  - `current-understanding.md` that only advances on keep (Principle 4)
  - Never-stop and when-stuck guidance (Principle 5)
  - Simplicity criterion for evaluating cycles (Principle 6)
- [ ] Build `/reaper:synthesize`; test independently
- [ ] Build the `/reaper` orchestrator that composes them with subagent parallelism
- [ ] Test full pipeline end-to-end with 3 real papers:
  - A cryptographic construction with a known proof gap
  - A consensus protocol paper (e.g., compare HotStuff variants)
  - A blockchain paper with questionable security claims
- [ ] Iterate on skills based on test results (using skill-creator eval framework)
- [ ] Tune skill descriptions for reliable triggering

### Horizon 2: The Library

**Methodology stage:** Enriches Stage 1b (establish baseline from literature) with real academic paper servers.

**Goal:** Upgrade `review-literature` from generic web search to structured academic search via MCP — arXiv, IACR ePrint, citation graph traversal. Also enable `investigate` to pull in new references mid-loop when a cycle reveals a gap in context.

**What success looks like:** `/reaper:review-literature "post-quantum threshold signatures"` automatically searches arXiv and IACR ePrint, downloads and reads the top results, traces forward/backward citations, and produces a structured literature survey with precise references.

#### MCP Servers

| Server | Repository | Capabilities |
|--------|-----------|--------------|
| arxiv-mcp-server | https://github.com/blazickjp/arxiv-mcp-server | `search_papers`, `download_paper`, `read_paper`, `list_papers`, `semantic_search`, `citation_graph` |
| eprint-mcp-server | https://github.com/heewon-chung/eprint-mcp-server | `search_papers`, `get_paper`, `get_recent_papers`, `download_paper`, `get_paper_url` |

#### Tasks

- [ ] Install and configure arxiv-mcp-server; document setup in README
- [ ] Install and configure eprint-mcp-server; document setup in README
- [ ] Write `references/mcp-tools.md` — catalog of available MCP tools with usage patterns and examples
- [ ] Update `review-literature` skill to use MCP tools as primary search, WebSearch as fallback
- [ ] Add citation graph traversal pattern (forward + backward citation chasing via Semantic Scholar integration)
- [ ] Add "recent papers" monitoring pattern (eprint-mcp-server's `get_recent_papers`)
- [ ] Enable `investigate` to trigger ad-hoc literature search mid-cycle when context is missing
- [ ] Test: given a seed paper, can Reaper find and summarize the 10 most relevant related works?
- [ ] Handle graceful degradation when MCP servers are unavailable

### Horizon 3: The Committee

**Methodology stage:** Strengthens the evaluation signal in Stage 3 (investigate) by adding multi-model adversarial review.

**Goal:** After investigation cycles, send the analysis to other AI models for adversarial feedback — finding flaws, suggesting alternative approaches, sanity-checking conclusions. This compensates for the lack of an objective numeric metric by adding independent perspectives, analogous to peer review in human research.

**What success looks like:** Reaper sends its proof that "protocol X is insecure under asynchrony" to external models. One catches a flaw in the reduction argument. The feedback goes through keep-or-discard — it improves `current-understanding.md`, so it's kept. The final report includes the correction.

#### Architecture

```
investigate ──> workspace/experiments/001/analysis.md
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  Codex MCP        Gemini MCP       (future)
  "find flaws"   "alternative
                  approach?"
        │               │               │
        └───────┬───────┘───────────────┘
                ▼
      workspace/feedback/
      ├── codex-review.md
      └── gemini-review.md
                │
                ▼
      keep-or-discard: does the feedback
      improve current-understanding.md?
```

#### New Skill

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/reaper:cross-verify` | Stage 3 sub-step: adversarial review | `experiments/NNN/analysis.md` + review prompt | `feedback/*.md` |

#### MCP Servers

| Server | Repository | Purpose |
|--------|-----------|---------|
| codex-mcp-server | https://github.com/tuannvm/codex-mcp-server | Route queries to OpenAI Codex/o3 for adversarial review |
| (others TBD) | | Gemini, Grok, open-source models |

#### Tasks

- [ ] Install and configure codex-mcp-server; document setup
- [ ] Build `/reaper:cross-verify` skill:
  - Takes an analysis file + a review prompt
  - Sends to one or more external models via MCP
  - Collects responses into `workspace/feedback/`
  - Spawns parallel subagents (one per external model) for concurrent feedback
- [ ] Define feedback prompt templates:
  - "Adversarial review" — find flaws in this reasoning
  - "Alternative approach" — how would you tackle this problem differently?
  - "Sanity check" — does this conclusion follow from the premises?
- [ ] Integrate cross-verify into the orchestrator (after investigate cycles, before synthesize)
- [ ] Apply keep-or-discard to external feedback
- [ ] Update `synthesize` to incorporate feedback into the report
- [ ] Test: does multi-model feedback catch errors that single-model analysis misses?

### Horizon 4: The Lab

**Methodology stage:** Expands what kinds of research the pipeline can handle — multiple papers, surveys, computational verification, publication-ready output.

**Goal:** Support sophisticated research workflows beyond single-paper analysis: multi-paper comparative studies, systematic literature surveys, research agenda generation, computational verification, and collaborative human-AI research sessions.

**What success looks like:** "Survey all post-quantum signature schemes on ePrint from 2023-2025, compare their security assumptions and efficiency, and identify open problems" produces a comprehensive, publication-ready survey with LaTeX output.

#### New Capabilities

| Capability | Methodology stages affected | How |
|-----------|---------------------------|-----|
| Multi-paper input | Stage 1a | `analyze-paper` runs in parallel subagents across all papers |
| Systematic survey | Stage 1a + 1b + 4 | search → filter → parallel read → cross-compare → synthesize |
| Research agenda generation | Stage 4 | After investigation, propose open problems with feasibility assessments |
| Interactive mode | Stage 3 | User checkpoints between cycles — "dig deeper into Theorem 3" |
| LaTeX output | Stage 4 | Publication-ready reports alongside Markdown |
| Computation support | Stage 3 | SageMath, Python, formal verification (EasyCrypt, Tamarin) for checking proofs computationally |

#### Tasks

- [ ] Extend orchestrator to accept multiple papers as input
- [ ] Build systematic survey workflow (search → filter → parallel read → cross-compare → synthesize)
- [ ] Add research agenda generation as a synthesis option
- [ ] Add interactive mode with user checkpoints between cycles
- [ ] Add LaTeX report template alongside Markdown
- [ ] Add `references/computation.md` — when and how to use SageMath, symbolic math, formal verification
- [ ] Explore integration with Semantic Scholar MCP for large-scale citation analysis

---

## Design Decisions

### Methodology Heritage

Reaper's loop discipline comes directly from [karpathy/autoresearch](https://github.com/karpathy/autoresearch). The adaptation from ML experimentation to theoretical research required rethinking what "evaluation" and "improvement" mean when there's no single numeric metric, but the core insight carries over perfectly: **constrain the loop enough that the AI can iterate autonomously at high speed, with a clear signal of what constitutes progress.** The structured results log, keep-or-discard mechanism, never-stop policy, and simplicity criterion are all direct adaptations.

The key difference: autoresearch has `val_bpb` as an objective oracle. Reaper must rely on softer evaluation signals (hypothesis resolution, logical consistency, rigor). This is why Horizon 3 (multi-model feedback) matters — cross-model verification partially compensates for the lack of an objective metric by adding independent perspectives, analogous to peer review in human research.

### Why a Skill, Not Python

| Concern | Python wrapper | Skill |
|---------|---------------|-------|
| PDF reading | Need PyMuPDF/pdfplumber | Claude reads PDFs natively |
| Web search | API client code | WebSearch tool built-in |
| Code execution | Sandbox complexity | Bash tool works |
| Literature search | API wrappers | MCP servers handle it |
| Reasoning | Prompt engineering in code | Claude reasons natively |
| State management | Database/files + glue code | Just files in workspace/ |
| Multi-model | API clients per provider | MCP servers per provider |
| Parallelism | Threading/async code | Subagents |

The AI *is* the research agent. No wrapper needed.

### Why a Pipeline of Skills

A monolithic "do research" skill is hard to test, hard to improve, and hard to reuse partially. By decomposing into `analyze-paper`, `review-literature`, `formalize-problem`, `investigate`, `cross-verify`, and `synthesize`, each skill:
- Can be tested and iterated independently
- Can be used standalone (e.g., just analyze a paper without running the full pipeline)
- Has a clear input/output contract via workspace files
- Can be parallelized (independent skills run as concurrent subagents)

### Why Multi-Model Feedback

No single model is best at everything. Claude is strong at structured reasoning and long-context analysis. Other models may catch different classes of errors, suggest alternative approaches, or have different training data. The cross-verify step treats other models as peer reviewers — the same role human collaborators play in real research. This is especially important because, unlike autoresearch's val_bpb, theoretical research lacks an objective evaluation oracle.

### Why File-Based State

Context windows compress. A long research session will inevitably hit context limits. By writing all intermediate results to `workspace/`, skills can re-read their own notes after compression and continue. This also:
- Enables handoff between different skills in the pipeline
- Provides a full audit trail for the user
- Allows parallel subagents to write to the same workspace without coordination beyond the filesystem
- Mirrors autoresearch's `results.tsv` + git history as the source of truth
