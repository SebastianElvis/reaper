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

**Stage 0: Clarify the goal.** Before any analysis begins, `clarify-goal` quick-scans the paper and asks the user 3-5 targeted clarifying questions about scope, assumptions, and success criteria. This produces `notes/clarified-goal.md` which grounds all downstream skills. If the goal is already precise, this step proceeds without questions.

**Stage 1: Establish baseline.** Before formalizing the problem, `analyze-paper` and `review-literature` establish what is already known — the paper's claims, existing approaches, and the state of the art. This grounds the investigation in reality rather than starting from a vacuum.

**Stage 2: Formalize the problem.** `formalize-problem` then produces a problem statement in `notes/problem-statement.md` containing:

- **Trust assumptions**: Every dimension pinned down unambiguously — communication, timing, PKI/setup, corruption (timing, power, bound), computation, composition, cryptographic hardness, protocol-specific assumptions. A hypothesis without fully specified trust assumptions is rejected.
- **Security properties**: What must hold, stated as formal predicates, game-based definitions, simulation-based definitions, or precise references to existing definitions. Informal descriptions like "safety" or "liveness" without formal definitions are not acceptable.
- **Performance metrics/goals**: What are the concrete targets? (e.g., "O(n) communication complexity per decision, finality in 3 rounds")
- **Impossibility screening**: Each hypothesis is checked against known impossibility results (FLP, DLS, Dolev-Reischuk, etc.). Hypotheses that contradict known impossibilities are flagged and reformulated, not left for the investigate skill to waste cycles on.
- **Ideas**: Derived from the above — specific hypotheses with explicit success/failure conditions

Not all hypotheses are equally worth investigating. Among the ideas, prioritize those whose resolution would be most consequential — a security proof gap that invalidates a deployed protocol matters more than a tighter constant in a complexity bound (Hamming: "If you do not work on important problems, how can you expect to do important work?"). Use Qian's "fill in the blank" pattern to find gaps: map the dimensions of existing work (threat models × protocol families × security properties) and identify unexplored combinations.

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
6. If all execution-level tactics are exhausted, log the cycle as inconclusive and continue. The orchestrator will call `brainstorm` after the batch to generate new ideas (applying Hamming inversion, Qian's patterns, gap-finding) based on the pattern of failures.

Uncertainty about whether the human wants you to continue is *never* a reason to stop. The human will interrupt when they want you to stop.

### Principle 6: Clarity and Simplicity

**Simplicity in reasoning:**
- A proof that achieves the same result with fewer assumptions is better.
- Replacing a 3-page case analysis with a one-paragraph reduction is progress, even if the "result" is unchanged.
- If removing a hypothesis and still reaching the same conclusion, that's a simplification win — keep it.
- Don't accumulate tangential findings that don't serve the research goal. Depth on the core question beats breadth across distractions.

**Clarity in expression** (Peyton Jones: writing is a primary mechanism for doing research, not just for reporting it):
- **Write early, not last.** Each investigation cycle should update `current-understanding.md` not just with results but with *explanations* of those results, as if explaining at a whiteboard. Writing crystallizes understanding.
- **One "ping" per finding.** Each cycle should produce one clear, sharp insight. If a cycle's outcome cannot be stated in a single sentence, it needs to be decomposed further.
- **Contributions must be refutable.** Every claim — whether in `problem-statement.md` or `report.md` — should be specific enough that a reader could disagree with it. "We analyze the security of protocol X" is not a contribution. "We show that protocol X's safety proof fails under asynchrony because the simulator cannot handle abort in round 3" is.

When evaluating whether a cycle produced progress, weight clarity and elegance alongside novelty. A cycle that narrows the search space on an important question is a "keep" even if it didn't resolve the hypothesis.

---

## Project Structure

### Skill Repository (this repo)

```
reaper/
├── skills/
│   ├── reaper/SKILL.md                     # Orchestrator — composes the pipeline
│   ├── clarify-goal/SKILL.md               # /reaper:clarify-goal
│   ├── analyze-paper/SKILL.md              # /reaper:analyze-paper
│   ├── review-literature/SKILL.md          # /reaper:review-literature
│   ├── formalize-problem/SKILL.md          # /reaper:formalize-problem
│   ├── brainstorm/SKILL.md                 # /reaper:brainstorm (recurring ideation)
│   ├── investigate/SKILL.md                # /reaper:investigate (proof/analysis cycles)
│   ├── critique/SKILL.md                   # /reaper:critique (human/Codex/self review)
│   ├── synthesize/SKILL.md                 # /reaper:synthesize (report generation)
│   ├── search-arxiv/                       # /reaper:search-arxiv
│   │   ├── SKILL.md
│   │   └── search_arxiv.py                 # arXiv API + Semantic Scholar citations
│   └── search-iacr/                        # /reaper:search-iacr
│       ├── SKILL.md
│       └── search_iacr.py                  # IACR ePrint scraper
├── tests/                                  # Python tests
├── dev/
│   ├── ROADMAP.md                          # This file
│   └── test-papers/                        # Papers for testing
├── evals/
│   └── evals.json                          # Test cases for skill evaluation
├── .claude-plugin/plugin.json              # Plugin metadata
└── README.md
```

### User's Workspace (generated at runtime)

When a user invokes `/reaper`, this structure is created in their working directory:

```
reaper-workspace/
├── notes/
│   ├── clarified-goal.md              # Refined goal, scope, assumptions, Q&A
│   ├── paper-summary.md                # Structured extraction from the paper
│   ├── literature.md                   # Related work found during search
│   ├── problem-statement.md                   # Problem statement + ideas
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
Methodology stage:     Clarify → Baseline → Formalize → Brainstorm → Investigate ↔ Critique → Synthesize
                         │         │           │            │              │              │          │
H1 The Pipeline:         ✓       paper + web  ✓            ✓              ✓              ✓          ✓
H2 The Library:                    + arXiv/ePrint                           + mid-loop search
H3 The Committee:                                                           + Codex MCP review
H4 The Lab:                        + multi-paper                            + computation          + LaTeX
```

### Horizon 1: The Pipeline

**Methodology stage:** All four stages, decomposed into independent skills from day one.

**Goal:** Build the full research pipeline as composable sub-skills that each map 1:1 to a methodology stage. Each skill is independently useful, has a clear file contract, and can be composed by the orchestrator with subagent parallelism. Literature search uses WebSearch initially (MCP servers come in H2).

**What success looks like:** `/reaper paper.pdf "check if the security proof in Section 4 holds under asynchrony"` produces a workspace with:
- `notes/problem-statement.md` containing a precise problem statement (trust assumptions, security properties, performance goals)
- `results.md` showing cycle-by-cycle progression with keep/discard decisions
- `current-understanding.md` with the accumulated findings
- `report.md` that a researcher would find genuinely useful

And each skill works standalone: `/reaper:analyze-paper paper.pdf` for just a structured summary, `/reaper:formalize-problem` for just a problem statement, etc.

#### Skills and File Contracts

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/reaper:clarify-goal` | Stage 0: Clarify | Input paper, goal prompt | `notes/clarified-goal.md` (refined goal, scope, assumptions, Q&A) |
| `/reaper:analyze-paper` | Stage 1a: Baseline (paper) | Input paper | `notes/paper-summary.md` |
| `/reaper:review-literature` | Stage 1b: Baseline (literature) | `notes/clarified-goal.md`, `notes/paper-summary.md` | `notes/literature.md` |
| `/reaper:formalize-problem` | Stage 2: Formalize | `notes/clarified-goal.md`, `notes/paper-summary.md`, `notes/literature.md`, goal prompt | `notes/problem-statement.md` (trust assumptions, security properties, performance goals, ideas) |
| `/reaper:brainstorm` | Stage 2.5: Recurring ideation | `notes/problem-statement.md`, `notes/current-understanding.md`, `results.md`, `notes/literature.md`, `notes/paper-summary.md` | Appends new ideas to `notes/problem-statement.md` |
| `/reaper:investigate` | Stage 3: Investigate (one cycle) | `notes/problem-statement.md`, `notes/current-understanding.md` | `experiments/NNN-<name>/`, appends to `results.md`, conditionally updates `current-understanding.md` |
| `/reaper:critique` | Stage 3 sub-step: review | `experiments/`, `notes/current-understanding.md` | `feedback/`, may add hypotheses to `notes/problem-statement.md` |
| `/reaper:synthesize` | Stage 4: Synthesize | All `notes/`, `experiments/`, `results.md` | `report.md` |
| `/reaper` | Orchestrator | Paper + goal prompt | Full workspace |

**`synthesize` report structure** (following Peyton Jones):
- **One "ping"**: The report must have one clear, central finding stated upfront. If the research yielded multiple findings, the report must still identify the single most important one.
- **Explicit, refutable contributions**: A bulleted list of specific claims, each concrete enough that a reader could disagree. Not "we analyze protocol X" but "we show that claim Y fails because Z."
- **Examples before generality**: Introduce findings with a concrete example (a specific execution trace, a specific adversary strategy) before presenting the general argument.
- **Narrative flow**: Problem → why it matters → what we found → evidence → how it compares to prior understanding. Not a chronological diary of the investigation.

#### Subagent Parallelism

- **Orchestrator**: Run `analyze-paper` and `review-literature` as parallel subagents (Stage 1a and 1b are independent)
- **`review-literature`**: Spawn parallel subagents to search different sources simultaneously, then merge results
- **`investigate`**: When multiple independent hypotheses exist, spawn parallel subagents to explore them concurrently

#### Tasks

- [x] Write `references/methodology.md` (proof verification, security analysis, protocol extension, comparison, counterexample patterns)
- [x] Write `references/paper-analysis.md` (extraction guide for crypto/distributed systems/blockchain papers)
- [x] Define the workspace file contract between skills (the table above, formalized)
- [x] Build `/reaper:analyze-paper`; test independently
- [x] Build `/reaper:review-literature` (WebSearch only for now); test independently
- [x] Build `/reaper:formalize-problem`; test that it produces trust assumptions + security properties + performance goals
- [x] Build `/reaper:investigate` with full loop discipline:
  - `results.md` structured log with keep/discard per cycle (Principle 3)
  - `current-understanding.md` that only advances on keep (Principle 4)
  - Never-stop and when-stuck guidance (Principle 5)
  - Simplicity criterion for evaluating cycles (Principle 6)
- [x] Build `/reaper:synthesize`; test independently
- [x] Build the `/reaper` orchestrator that composes them with subagent parallelism
- [x] Create eval framework (`evals/evals.json`) with test cases and quality criteria
- [x] Create test paper specifications (`dev/test-papers/README.md`)
- [x] Tune skill descriptions for reliable triggering (added action verbs, specific outputs, broader trigger phrases)
- [ ] Test full pipeline end-to-end with 3 real papers:
  - A cryptographic construction with a known proof gap
  - A consensus protocol paper (e.g., compare HotStuff variants)
  - A blockchain paper with questionable security claims
- [ ] Iterate on skills based on test results (using eval framework)

### Horizon 2: The Library

**Methodology stage:** Enriches Stage 1b (establish baseline from literature) with real academic paper servers.

**Goal:** Upgrade `review-literature` from generic web search to structured academic search — arXiv, IACR ePrint, citation graph traversal — using lightweight Python scripts (no MCP dependency). Also enable `investigate` to pull in new references mid-loop when a cycle reveals a gap in context.

**What success looks like:** `/reaper:review-literature "post-quantum threshold signatures"` automatically searches arXiv and IACR ePrint, traces forward/backward citations via Semantic Scholar, and produces a structured literature survey with precise references.

#### Search Tools

| Script | Location | Capabilities | Dependencies |
|--------|----------|--------------|-------------|
| `search_arxiv.py` | `skills/search-arxiv/` | `search`, `download`, `citations` (via Semantic Scholar) | `pip install arxiv requests` |
| `search_iacr.py` | `skills/search-iacr/` | `search`, `recent`, `download`, `url` | `pip install requests beautifulsoup4` |

#### Tasks

- [x] Build `search-arxiv` skill with Python script (arXiv API + Semantic Scholar citations)
- [x] Build `search-iacr` skill with Python script (IACR ePrint scraper)
- [x] Write `references/search-tools.md` — catalog of search tools with usage patterns and decision tree
- [x] Update `review-literature` skill: structured search as primary, WebSearch as fallback, citation graph, recent papers
- [x] Update `investigate` skill: mid-cycle literature search via search scripts
- [x] Handle graceful degradation when search scripts are unavailable
- [x] Document Python prerequisites in README
- [ ] Test: given a seed paper, can Reaper find and summarize the 10 most relevant related works?

### Horizon 3: The Committee

**Methodology stage:** Strengthens the evaluation signal in Stage 3 (investigate) by adding multi-model adversarial review.

**Goal:** After investigation cycles, get external critique via human feedback, Codex MCP consultation, or self-review — finding flaws, suggesting alternative approaches, sanity-checking conclusions. This compensates for the lack of an objective numeric metric by adding independent perspectives, analogous to peer review in human research.

**What success looks like:** Reaper sends its proof that "protocol X is insecure under asynchrony" to Codex as devil's advocate. Codex catches a flaw in the reduction argument. The critique triggers additional investigation cycles, the flaw is addressed, and the final report includes the correction. Human users can also inject feedback at any point via `/reaper:critique "your analysis misses the abort case"`.

#### Architecture

```
investigate ──> /reaper:critique
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    human feedback  Codex MCP   self-review
    "your proof     "find       "re-examine
     misses X"      flaws"      assumptions"
         │           │           │
         └─────┬─────┘───────────┘
               ▼
     workspace/feedback/
     ├── round-N.md
     └── codex-consultation-N.md
               │
               ▼
     keep-or-discard + may trigger
     more investigation cycles
```

#### Implemented Skill

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/reaper:critique` | Stage 3 sub-step: adversarial review | `experiments/`, `notes/current-understanding.md` | `feedback/*.md`, may add hypotheses |

The original `cross-verify` concept was implemented as the more general `/reaper:critique` skill, which supports three modes: human feedback, Codex MCP consultation (devil's advocate / inspiration), and self-review.

#### MCP Servers

| Server | Repository | Purpose |
|--------|-----------|---------|
| codex-mcp-server | https://github.com/tuannvm/codex-mcp-server | Route queries to OpenAI Codex/o3 for adversarial review |
| (others TBD) | | Gemini, Grok, open-source models |

#### Tasks

- [x] Build `/reaper:critique` skill (replaces planned `cross-verify`):
  - Human feedback mode: user provides critique text
  - Codex consultation mode: alternates devil's advocate / inspiration via MCP
  - Self-review mode: self-critique of current findings
  - Can trigger additional investigation cycles
- [x] Define feedback prompt templates (devil's advocate, alternative approach)
- [x] Integrate critique into the orchestrator (investigate ↔ critique loop)
- [x] Apply keep-or-discard to external feedback
- [x] Document codex-mcp-server setup in README
- [ ] Add more MCP model backends (Gemini, Grok, open-source models)
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

### Intellectual Heritage

Reaper's methodology draws from four sources:

**[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** — The loop discipline. Constrain the loop enough that the AI can iterate autonomously at high speed, with a clear signal of what constitutes progress. The structured results log, keep-or-discard mechanism, never-stop policy, and simplicity criterion are all direct adaptations. The key difference: autoresearch has `val_bpb` as an objective oracle. Reaper must rely on softer evaluation signals (hypothesis resolution, logical consistency, rigor). This is why Horizon 3 (multi-model feedback) matters — cross-model verification partially compensates for the lack of an objective metric.

**[Richard Hamming, "You and Your Research"](https://d37ugbyn3rpeym.cloudfront.net/stripe-press/TAODSAE_zine_press.pdf)** (Stripe Press edition of *The Art of Doing Science and Engineering*) — The importance filter and problem-inversion technique. Hamming's central question — "Why are you not working on the important problems in your field?" — shapes the importance filter in Principle 2: prioritize hypotheses by consequence, not convenience. His technique of inverting blockages into insights (if you can't prove it, try to disprove it) is built into the "when stuck" protocol in Principle 5. Hamming also taught that effort compounds — steady, disciplined investigation cycles accumulate understanding the way compound interest accumulates capital.

**[Zhiyun Qian, "How to Look for Ideas in Computer Science Research"](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f)** — Systematic idea generation patterns. Qian's six patterns (fill-in-the-blank, expansion, build-a-hammer, start-small-then-generalize, reproduce-prior-work, external-sources) are incorporated into Principles 2 and 5, and into the `formalize-problem` skill's approach to generating ideas. The "fill in the blank" pattern — mapping dimensions of existing research and finding unexplored combinations — is particularly powerful for theoretical research where the design space of threat models, protocol families, and security properties can be systematically enumerated.

**[Simon Peyton Jones, "How to Write a Great Research Paper"](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf)** — Writing as research methodology. Peyton Jones's core insight — that writing is a primary mechanism for doing research, not just for reporting it — is woven into Principle 6 (Clarity and Simplicity). His structural advice (one clear "ping," explicit refutable contributions, examples before generality, narrative flow over chronological recounting) shapes the `synthesize` skill's report format. Most importantly, the idea that you should write *before* you fully understand forces Reaper to crystallize its understanding in `current-understanding.md` at every cycle, not just at the end.

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
