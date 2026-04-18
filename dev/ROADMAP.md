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

- **AI writes to `workspace/`** — notes, investigations, results, reports. This is the AI's exclusive working space. Files in `notes/`, `investigations/`, and `papers/` are **evolving documents** edited inline to reflect the latest understanding. Files in `feedbacks/` and `logs/` are **append-only snapshots** — each is created once and never modified.
- **Human writes the research goal prompt** — the paper to analyze and what to investigate. This is the sole steering mechanism.
- **SKILL.md files and workspace file contracts are fixed** — they define the pipeline, evaluation criteria, and interfaces between skills. Neither the AI nor the human modifies them during a run.

| Role | What |
|------|------|
| AI modifies | `workspace/` (notes, investigations, report) |
| Human provides | Research goal prompt (paper + what to investigate) |
| Fixed harness | SKILL.md files + workspace file contracts |

### Principle 2: Fixed Evaluation Signal

Before investigation begins, the problem must be precisely defined with concrete evaluation criteria. This happens in two stages:

**Stage 0: Clarify the goal.** Before any analysis begins, `/clarify-goal` quick-scans the paper and asks the user 3-5 targeted clarifying questions about scope, assumptions, and success criteria. This produces `notes/clarified-goal.md` which grounds all downstream skills. If the goal is already precise, this step proceeds without questions.

**Stage 1: Establish baseline.** Before formalizing the problem, `/analyze-paper` and `/review-literature` establish what is already known — the paper's claims, existing approaches, and the state of the art. This grounds the investigation in reality rather than starting from a vacuum.

**Stage 2: Formalize the problem.** `/formalize-problem` then produces a problem statement in `notes/problem-statement.md` containing:

- **Trust assumptions**: Every dimension pinned down unambiguously — communication, timing, PKI/setup, corruption (timing, power, bound), computation, composition, cryptographic hardness, protocol-specific assumptions. A hypothesis without fully specified trust assumptions is rejected.
- **Security properties**: What must hold, stated as formal predicates, game-based definitions, simulation-based definitions, or precise references to existing definitions. Informal descriptions like "safety" or "liveness" without formal definitions are not acceptable.
- **Performance metrics/goals**: What are the concrete targets? (e.g., "O(n) communication complexity per decision, finality in 3 rounds")
- **Impossibility screening**: Each hypothesis is checked against known impossibility results (FLP, DLS, Dolev-Reischuk, etc.). Hypotheses that contradict known impossibilities are flagged and reformulated, not left for the investigate skill to waste cycles on.
- **Ideas** (written to a separate `notes/ideas.md`): Derived from the above — specific hypotheses with explicit success/failure conditions

Not all hypotheses are equally worth investigating. Among the ideas, prioritize those whose resolution would be most consequential — a security proof gap that invalidates a deployed protocol matters more than a tighter constant in a complexity bound (Hamming: "If you do not work on important problems, how can you expect to do important work?"). Use Qian's "fill in the blank" pattern to find gaps: map the dimensions of existing work (threat models × protocol families × security properties) and identify unexplored combinations.

Every investigation cycle is then evaluated against these fixed criteria — did the cycle make progress toward confirming or refuting a specific claim?

Progress is tracked in `notes/results.md` (see Principle 3).

### Principle 3: Structured Results Log

`workspace/notes/results.md` tracks every hypothesis in a structured table — **one row per hypothesis, updated inline on revisit**:

```markdown
| Cycle | Hypothesis | Action | Outcome | Confidence | Status | Description |
|-------|-----------|--------|---------|------------|--------|-------------|
| 003 | H1 | Alternative proof | Confirmed | Medium | keep | Constructed fix for Lemma 3.2 using rewinding |
| 002 | H2 | Counterexample search | Inconclusive | Low | discard | Tried 2-party case, no counterexample found, approach too narrow |
```

When a hypothesis is revisited (e.g., H1 initially refuted in cycle 001, then confirmed via alternative proof in cycle 003), the existing row is **updated inline** — cycle number, outcome, confidence, and description all reflect the latest result. The full history of prior attempts is preserved in the `investigations/` directories.

- **keep**: The cycle produced a meaningful advance in understanding. Findings propagate to `notes/current-understanding.md`.
- **discard**: The cycle was a dead end. It stays logged in `notes/results.md` and its investigation directory, but does not update the running state.

This is the ground-truth scoreboard. Every hypothesis gets exactly one row reflecting its current state.

### Principle 4: Keep-or-Discard Loop

`notes/current-understanding.md` is the "branch tip." It represents the best current understanding of the research question. After each investigation cycle:

- If the cycle produced genuine progress (new finding, resolved hypothesis, corrected error) → **keep**: edit `current-understanding.md` inline to integrate the new insight — revise existing sections, not just append.
- If the cycle was unproductive (dead end, inconclusive without useful narrowing, redundant with prior work) → **discard**: log it in `notes/results.md`, leave the investigation directory for the audit trail, but do not touch `current-understanding.md`.

The AI always works from the best-known state. This prevents accumulation of noise in the working state while preserving the full history for audit.

### Principle 5: Never Stop

Run all N cycles without asking "should I continue?" The only valid early stop is genuine convergence — all hypotheses resolved with high confidence. If stuck:

1. Re-read the paper. Look at sections you skimmed earlier.
2. Re-read `notes/current-understanding.md`. What assumptions haven't been questioned?
3. Re-read `notes/results.md`. Can two "discard" results be combined into something useful?
4. Search for related work you haven't found yet.
5. Try a radically different approach to the same hypothesis.
6. If all execution-level tactics are exhausted, log the cycle as inconclusive and continue. The orchestrator will call `/brainstorm` after the batch to generate new ideas (applying Hamming inversion, Qian's patterns, gap-finding) based on the pattern of failures.

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
│   ├── clarify-goal/SKILL.md               # Stage 0: clarify the goal
│   ├── analyze-paper/SKILL.md              # Stage 1a: paper analysis
│   ├── review-literature/SKILL.md          # Stage 1b: literature review
│   ├── formalize-problem/SKILL.md          # Stage 2: formalize the problem
│   ├── brainstorm/SKILL.md                 # Stage 2.5: recurring ideation
│   ├── investigate/SKILL.md                # Stage 3: investigate (proof/analysis cycles)
│   ├── critique/SKILL.md                   # Stage 3 sub-step: human / external-model / self review
│   ├── synthesize/SKILL.md                 # Stage 4: synthesize (report generation)
│   ├── search-arxiv/                       # Crypto/CS topic search via arXiv
│   │   ├── SKILL.md
│   │   └── search_arxiv.py                 # arXiv API + Semantic Scholar citations
│   └── search-iacr/                        # Crypto-specific IACR ePrint search
│       ├── SKILL.md
│       └── search_iacr.py                  # IACR ePrint scraper
├── tests/                                  # Python tests
├── dev/
│   ├── ROADMAP.md                          # This file
│   └── test-papers/                        # Papers for testing
├── evals/
│   └── evals.json                          # Test cases for skill evaluation
├── .claude-plugin/                         # Claude-Code-specific plugin manifest (other hosts ignore)
│   ├── plugin.json
│   └── marketplace.json
├── .github/workflows/                      # CI: pytest + npx-skills discovery check
└── README.md
```

Skills are distributed primarily via [`vercel-labs/skills`](https://github.com/vercel-labs/skills) (`npx skills add SebastianElvis/reaper`) and run on any host that supports the `SKILL.md` convention.

### User's Workspace (generated at runtime)

When a user invokes the `/reaper` skill (by name on auto-discovery hosts, as `/reaper` on slash-command hosts), this structure is created in their working directory:

```
reaper-workspace/
├── notes/                              # Evolving — edited inline to reflect latest state
│   ├── clarified-goal.md              # Refined goal, scope, assumptions, Q&A
│   ├── paper-summary.md                # Structured extraction from the paper
│   ├── literature.md                   # Related work found during search
│   ├── problem-statement.md                   # Problem statement (model, properties, metrics)
│   ├── ideas.md                               # Research ideas/hypotheses (edited inline on revisit)
│   ├── current-understanding.md        # "Branch tip" — only advances on keep
│   └── results.md                      # One row per hypothesis, updated inline on revisit
├── investigations/                     # Evolving — reuse directory on revisit, edit inline
│   └── NNN-<name>/                     # One directory per hypothesis
├── feedbacks/                          # Append-only — one file per event, never modified
├── logs/                               # Append-only — one file per event, never modified
└── report.md                           # Final synthesized output (Markdown report) — written by `/synthesize`. A future horizon may add a compilable LaTeX project (see ROADMAP horizons for that direction).
```

---

## Horizons

Each horizon enriches a specific stage of the methodology pipeline. H1 builds the decomposed pipeline from day one. H2 adds crypto-specific search. H3 strengthens the evaluation signal with multi-model feedback. H3.5 makes Reaper portable across AI agent platforms. H4 expands to the broader CS academic network. H5 makes the system honest about evidence quality. H6 adds proactive reformulation and claim provenance.

```
Methodology stage:     Clarify → Baseline → Formalize → Brainstorm → Investigate ↔ Critique → Synthesize
                         │         │           │            │              │              │          │
H1 The Pipeline:         ✓       paper + web  ✓            ✓              ✓              ✓          ✓
H2 The Library:                    + arXiv/ePrint                           + mid-loop search
H3 The Committee:                                                           + multi-model review (Codex, Gemini, DeepSeek, local)
H3.5 The Polyglot:       ◇         ◇           ◇            ◇              ◇              ◇          ◇  (all stages portable)
H4 The Academy:                    + Scholar/DBLP/venues + author search     + mid-loop author/venue
H5 The Apprentice:                                                          + evidence taxonomy        + proven vs conjecture
H6 The Examiner:                                           + reformulation  + (stretch: Z3/Tamarin)    + claim provenance
```

### Horizon 1: The Pipeline

**Methodology stage:** All four stages, decomposed into independent skills from day one.

**Goal:** Build the full research pipeline as composable sub-skills that each map 1:1 to a methodology stage. Each skill is independently useful, has a clear file contract, and can be composed by the orchestrator with subagent parallelism. Literature search uses WebSearch initially (MCP servers come in H2).

**What success looks like:** invoking the `/reaper` skill with `"check if the security proof in Section 4 holds under asynchrony" paper.pdf` produces a workspace with:
- `notes/problem-statement.md` containing a precise problem statement (trust assumptions, security properties, performance goals)
- `notes/ideas.md` containing the research ideas/hypotheses and their resolution status
- `notes/results.md` showing cycle-by-cycle progression with keep/discard decisions
- `notes/current-understanding.md` with the accumulated findings
- `report.md` containing a synthesized Markdown report that a researcher could review (a compilable LaTeX project is a future horizon, not H1)

And each skill works standalone: invoke `analyze-paper paper.pdf` for just a structured summary, `/formalize-problem` for just a problem statement, etc.

#### Skills and File Contracts

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/clarify-goal` | Stage 0: Clarify | Input paper, goal prompt | `notes/clarified-goal.md` (refined goal, scope, assumptions, Q&A) |
| `/analyze-paper` | Stage 1a: Baseline (paper) | Input paper | `notes/paper-summary.md` |
| `/review-literature` | Stage 1b: Baseline (literature) | `notes/clarified-goal.md`, `notes/paper-summary.md` | `notes/literature.md` |
| `/formalize-problem` | Stage 2: Formalize | `notes/clarified-goal.md`, `notes/paper-summary.md`, `notes/literature.md`, goal prompt | `notes/problem-statement.md` (trust assumptions, security properties, performance goals), `notes/ideas.md` (initial ideas) |
| `/brainstorm` | Stage 2.5: Recurring ideation | `notes/problem-statement.md`, `notes/ideas.md`, `notes/current-understanding.md`, `notes/results.md`, `notes/literature.md`, `notes/paper-summary.md` | Updates `notes/ideas.md` (adds new, edits existing inline) |
| `/investigate` | Stage 3: Investigate (one cycle) | `notes/problem-statement.md`, `notes/ideas.md`, `notes/current-understanding.md` | `investigations/NNN-<name>/` (reuses on revisit), updates `notes/results.md` inline, edits `current-understanding.md` on keep |
| `/critique` | Stage 3 sub-step: review | `investigations/`, `notes/current-understanding.md`, `notes/ideas.md` | `feedbacks/`, `logs/`, may add hypotheses to `notes/ideas.md` |
| `/synthesize` | Stage 4: Synthesize | All `notes/`, `investigations/`, `notes/results.md` | `report.md` (synthesized Markdown report; a future horizon may add a compilable LaTeX project) |
| `/reaper` | Orchestrator | Paper + goal prompt | Full workspace |

**`/synthesize` report structure** (following Peyton Jones):
- **One "ping"**: The report must have one clear, central finding stated upfront. If the research yielded multiple findings, the report must still identify the single most important one.
- **Explicit, refutable contributions**: A bulleted list of specific claims, each concrete enough that a reader could disagree. Not "we analyze protocol X" but "we show that claim Y fails because Z."
- **Examples before generality**: Introduce findings with a concrete example (a specific execution trace, a specific adversary strategy) before presenting the general argument.
- **Narrative flow**: Problem → why it matters → what we found → evidence → how it compares to prior understanding. Not a chronological diary of the investigation.

#### Subagent Parallelism

- **Orchestrator**: Run `/analyze-paper` and `/review-literature` as parallel subagents (Stage 1a and 1b are independent)
- **`/review-literature`**: Spawn parallel subagents to search different sources simultaneously, then merge results
- **`/investigate`**: When multiple independent hypotheses exist, spawn parallel subagents to explore them concurrently

#### Tasks

- [x] Write `references/methodology.md` (proof verification, security analysis, protocol extension, comparison, counterexample patterns)
- [x] Write `references/paper-analysis.md` (extraction guide for crypto/distributed systems/blockchain papers)
- [x] Define the workspace file contract between skills (the table above, formalized)
- [x] Build `/analyze-paper` skill; test independently
- [x] Build `/review-literature` skill (WebSearch only for now); test independently
- [x] Build `/formalize-problem` skill; test that it produces trust assumptions + security properties + performance goals
- [x] Build `/investigate` skill with full loop discipline:
  - `notes/results.md` structured log with keep/discard per cycle (Principle 3)
  - `current-understanding.md` that only advances on keep (Principle 4)
  - Never-stop and when-stuck guidance (Principle 5)
  - Simplicity criterion for evaluating cycles (Principle 6)
- [x] Build `/synthesize` skill; test independently
- [x] Build the `/reaper` orchestrator that composes them with subagent parallelism
- [x] Create eval framework (`evals/evals.json`) with test cases and quality criteria
- [x] Create test paper specifications (`dev/test-papers/README.md`)
- [x] Tune skill descriptions for reliable triggering (added action verbs, specific outputs, broader trigger phrases)
- [ ] Upgrade `/synthesize` to produce a compilable LaTeX project instead of markdown:
  - [ ] Change output from `report.md` to `report/` directory (`main.tex`, `references.bib`, `Makefile`)
  - [ ] Use `article` class by default; support venue-specific document classes (`llncs`, `acmart`, `IEEEtran`) selectable via clarified goal or user argument
  - [ ] Map existing paper structure to LaTeX: `\begin{definition}`, `\begin{lemma}`, `\begin{theorem}`, `\begin{proof}` via `amsthm`; `\begin{conjecture}` for unproven claims
  - [ ] Generate `references.bib` from `notes/literature.md` entries with `\cite{}` references in the body
  - [ ] Include a `Makefile` that runs `latexmk -pdf main.tex` so `make` produces a PDF
  - [ ] Update the `/synthesize` SKILL.md template: replace the markdown template with LaTeX equivalents
  - [ ] Ensure the orchestrator and other skills that reference `report.md` (e.g., critique reading the report) are updated to read `report/main.tex`
  - [ ] Test: does `make` in `report/` produce a valid PDF without manual fixes?
- [ ] Test full pipeline end-to-end with 3 real papers:
  - A cryptographic construction with a known proof gap
  - A consensus protocol paper (e.g., compare HotStuff variants)
  - A blockchain paper with questionable security claims
- [ ] Iterate on skills based on test results (using eval framework)

### Horizon 2: The Library

**Methodology stage:** Enriches Stage 1b (establish baseline from literature) with real academic paper servers.

**Goal:** Upgrade `/review-literature` from generic web search to structured academic search — arXiv, IACR ePrint, citation graph traversal — using lightweight Python scripts (no MCP dependency). Also enable `/investigate` to pull in new references mid-loop when a cycle reveals a gap in context.

**What success looks like:** invoking the `/review-literature` skill with `"post-quantum threshold signatures"` automatically searches arXiv and IACR ePrint, traces forward/backward citations via Semantic Scholar, and produces a structured literature survey with precise references.

#### Search Tools

| Script | Location | Capabilities | Dependencies |
|--------|----------|--------------|-------------|
| `search_arxiv.py` | `skills/search-arxiv/` | `search`, `download`, `citations` (via Semantic Scholar) | `pip install arxiv requests` |
| `search_iacr.py` | `skills/search-iacr/` | `search`, `recent`, `download`, `url` | `pip install requests beautifulsoup4` |

#### Tasks

- [x] Build `/search-arxiv` skill with Python script (arXiv API + Semantic Scholar citations)
- [x] Build `/search-iacr` skill with Python script (IACR ePrint scraper)
- [x] Write `references/search-tools.md` — catalog of search tools with usage patterns and decision tree
- [x] Update `/review-literature` skill: structured search as primary, WebSearch as fallback, citation graph, recent papers
- [x] Update `/investigate` skill: mid-cycle literature search via search scripts
- [x] Handle graceful degradation when search scripts are unavailable
- [x] Document Python prerequisites in README
- [ ] Test: given a seed paper, can Reaper find and summarize the 10 most relevant related works?

### Horizon 3: The Committee

**Methodology stage:** Strengthens the evaluation signal in Stage 3 (investigate) by adding multi-model adversarial review.

**Goal:** After investigation cycles, get external critique via human feedback, multi-model consultation, or self-review — finding flaws, suggesting alternative approaches, sanity-checking conclusions. This compensates for the lack of an objective numeric metric by adding independent perspectives, analogous to peer review in human research. Different models catch different classes of errors: formal reasoning models (DeepSeek R1) excel at proof checking, long-context models (Gemini) can review entire paper corpora, and adversarial reasoners (o3) stress-test arguments.

**What success looks like:** Reaper sends its proof that "protocol X is insecure under asynchrony" to multiple models as devil's advocates. DeepSeek R1 catches a gap in the formal reduction. Gemini, having ingested the full paper corpus, points out a related construction the literature review missed. The critique triggers additional investigation cycles, the flaws are addressed, and the final report includes the corrections. Human users can also inject feedback at any point by invoking the `/critique` skill with `"your analysis misses the abort case"`. When no API keys are configured, the pipeline degrades gracefully to self-review only.

#### Architecture

```
investigate ──> critique
                     │
         ┌───────────┼───────────────────────┐
         ▼           ▼                       ▼
    human feedback  model consultation      self-review
    "your proof     (routed by task type)    "re-examine
     misses X"           │                   assumptions"
         │     ┌─────────┼──────────┐        │
         │     ▼         ▼          ▼        │
         │   Codex/o3  Gemini    DeepSeek    │
         │   (adversar- (breadth/ (formal/   │
         │    ial)      context)  math)      │
         │     │         │          │        │
         │     ▼         ▼          ▼        │
         │   optional: local models (Llama,  │
         │   Qwen, Mistral via ollama)       │
         │     │         │          │        │
         └─────┴─────────┴──────────┴────────┘
               ▼
     workspace/feedbacks/
     ├── round-N.md
     └── <model>-consultation-N.md
               │
               ▼
     keep-or-discard + may trigger
     more investigation cycles
```

#### Implemented Skill

| Skill | Methodology Stage | Reads | Writes |
|-------|------------------|-------|--------|
| `/critique` | Stage 3 sub-step: adversarial review | `investigations/`, `notes/current-understanding.md` | `feedbacks/*.md`, `logs/*.md`, may add hypotheses |

The original `cross-verify` concept was implemented as the more general `/critique` skill, which supports three modes: human feedback, external-model MCP consultation (devil's advocate / inspiration), and self-review.

#### Model Backends

Different models have different strengths. The critique skill should route consultations based on task type:

| Model | Access Method | Strength | Best For |
|-------|--------------|----------|----------|
| **OpenAI Codex/o3** | MCP (`codex-mcp-server`) | Adversarial reasoning, code analysis | Devil's advocate review, stress-testing arguments |
| **Google Gemini** | MCP or API | 1M+ token context, multimodal | Reviewing full paper corpora, catching missed related work |
| **DeepSeek R1** | API (`api.deepseek.com`) | Math & formal reasoning | Proof checking, formal reductions, algebraic claims |
| **Grok** | xAI API | Broad training data | Alternative perspectives, sanity checks |
| **Mistral Large** | API (`api.mistral.ai`) | Multilingual, European research | Non-English papers, EU venue coverage |
| **Qwen 2.5** | API or local (ollama) | Math/CS, CJK languages | Chinese crypto/systems papers, formal reasoning |
| **Llama 4** | Local (ollama) | Fully offline, no API costs | Privacy-sensitive research, offline use, cost control |

**Routing heuristic** (implemented in critique skill):
- **Proof checking / formal claims** → DeepSeek R1 (strongest at mathematical reasoning)
- **Adversarial review / stress testing** → o3 (strongest at finding flaws in arguments)
- **Breadth / missed references** → Gemini (longest context, can ingest full literature)
- **General sanity check** → any available model; prefer local models to reduce cost
- **Fallback** → self-review if no external models configured

#### MCP Servers

| Server | Repository | Purpose |
|--------|-----------|---------|
| codex-mcp-server | https://github.com/tuannvm/codex-mcp-server | Route queries to OpenAI Codex/o3 for adversarial review |
| (Gemini TBD) | | Google Gemini for long-context review |
| (DeepSeek TBD) | | DeepSeek R1 for formal reasoning |
| (ollama TBD) | | Local models (Llama, Qwen, Mistral) via ollama |

**Design notes:**
- MCP is the preferred integration path (keeps skills platform-agnostic). For models without an MCP server, a thin Python wrapper script (like the search scripts in H2) can bridge the gap.
- All model backends are optional. The critique skill must degrade gracefully: try configured models in priority order, fall back to self-review.
- Model consultation follows the same protocol as Codex today: compressed context (~800 words), structured prompt (devil's advocate or inspiration), response integrated into `feedbacks/`.

#### Tasks

- [x] Build `/critique` skill (replaces planned `cross-verify`):
  - Human feedback mode: user provides critique text
  - External-model consultation mode: alternates devil's advocate / inspiration via MCP
  - Self-review mode: self-critique of current findings
  - Can trigger additional investigation cycles
- [x] Define feedback prompt templates (devil's advocate, alternative approach)
- [x] Integrate critique into the orchestrator (investigate ↔ critique loop)
- [x] Apply keep-or-discard to external feedback
- [x] Document MCP-server setup in README (Codex MCP server as the first integrated backend)
- [ ] Generalize critique skill's Codex-specific protocol to a model-agnostic consultation protocol (model name as parameter, not hardcoded)
- [ ] Add Gemini backend (MCP or API wrapper) for long-context review
- [ ] Add DeepSeek R1 backend (API wrapper) for formal reasoning / proof checking
- [ ] Add local model support via ollama (Llama, Qwen, Mistral) for offline/private use
- [ ] Add Grok backend (xAI API) for alternative perspectives
- [ ] Implement routing heuristic: match consultation task type to best-suited model
- [ ] Update `references/codex-consultation.md` → `references/model-consultation.md` (generalize per-skill checkpoints to be model-agnostic)
- [ ] Update README: document multi-model setup (API keys, ollama install, MCP registration)
- [ ] Test: does multi-model feedback catch errors that single-model analysis misses?
- [ ] Test: does routing (proof→DeepSeek, adversarial→o3, breadth→Gemini) outperform uniform model selection?

### Horizon 3.5: The Polyglot (Cross-Agent Distribution)

**Methodology stage:** All stages — makes the entire pipeline portable across AI agent platforms.

**Current state:** Reaper ships as standard `SKILL.md` folders compatible with the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) convention. A single `npx skills add SebastianElvis/reaper` shallow-clones the repo and copies all 11 skill directories into the host agent's conventional skills folder, supporting 45+ targets including Cursor, OpenAI Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, OpenCode, Warp, Goose, Replit, and Claude Code. The orchestrator and inter-skill triggers use host-agnostic phrasing ("invoke the `<name>` skill") so that auto-discovery agents and slash-command agents both route correctly.

**Goal:** Make Reaper a first-class skills package — authored once, runnable on any host that consumes `SKILL.md` files. Achieved by converging on the `SKILL.md` convention rather than building per-host adapters.

**What success looks like:** A researcher on any supported host (Cursor, Codex CLI, Gemini CLI, Cline, Continue, Copilot, Windsurf, OpenCode, Warp, Goose, Claude Code, …) can install Reaper with one command and run the same pipeline against the same workspace contract — the only thing that varies between hosts is the surface invocation form. No per-host translation layer required.

#### Distribution Mechanism

| Component | Mechanism | Status |
|-----------|-----------|--------|
| **Skill format** | `SKILL.md` with `name` + `description` frontmatter (vercel-labs/skills spec) | ✓ |
| **Cross-agent installer** | `npx skills add SebastianElvis/reaper` | ✓ |
| **Pin syntax** | `npx skills add SebastianElvis/reaper#v0.3.9` (git tags) | ✓ |
| **Inter-skill calls** | Host-agnostic prose ("invoke the `<name>` skill") | ✓ |
| **Python script bundling** | Whole-directory copy includes `search_arxiv.py`, `search_iacr.py`, `references/` | ✓ |
| **Frontmatter compatibility** | Claude-only keys (`user-invocable`, `argument-hint`, hooks) preserved as opaque YAML, no-op on other hosts | ✓ |
| **CI validation** | Frontmatter regex check + strict `npx skills add` discovery test (verifies every expected skill, Python script, and reference file is present after install; fails the build if any asset is missing) | ✓ |
| **Claude Code plugin path** | `.claude-plugin/marketplace.json` for slash-command routing | ✓ |

#### Host Compatibility

| Host | Skills folder | Discovery model | Notes |
|------|--------------|-----------------|-------|
| Claude Code | `.claude/skills/` | Slash commands (`/reaper:<sub>`) + Skill tool | Native plugin path also available via `.claude-plugin/marketplace.json` |
| Cursor | `.agents/skills/` (universal) | Auto-route by `description` match | |
| OpenAI Codex CLI | `.agents/skills/` (universal) | Auto-route by `description` match | |
| Cline | `.agents/skills/` (universal) | Auto-route by `description` match | |
| Continue | `.continue/skills/` | Auto-route by `description` match | |
| Gemini CLI | `.agents/skills/` (universal) | Auto-route by `description` match | |
| GitHub Copilot | `.agents/skills/` (universal) | Auto-route by `description` match | |
| Windsurf | `.windsurf/skills/` | Auto-route by `description` match | |
| OpenCode | `.agents/skills/` (universal) | Auto-route by `description` match | MCP support enables `--codex` mode |
| Warp | `.agents/skills/` (universal) | Auto-route by `description` match | |
| Goose | `.goose/skills/` | Auto-route by `description` match | |
| Replit | `.agents/skills/` (universal) | Auto-route by `description` match | |
| Universal target | `.agents/skills/` | Manual invocation | Fallback for hosts without auto-discovery |

#### Known Caveats

- The `--codex` flag depends on a host with MCP support and a registered Codex MCP server. Non-MCP hosts silently fall back to self-review.
- Auto-discovery quality varies by host. Reliable routing depends on the skill's `description` matching the user's request — Reaper's descriptions are tuned for action-verb match (e.g. "Run the full Reaper research pipeline…") to improve auto-routing.
- Python dependencies (`arxiv`, `requests`, `beautifulsoup4`) are not installed by `npx skills` — users must `pip install` separately. The skill prose tells the agent to do this if missing.
- Sub-skill `Usage` blocks now lead with the bare-name form and show `/reaper:<sub>` as a slash-command-host example only.

#### Tasks

- [x] Adopt `vercel-labs/skills` `SKILL.md` convention as the canonical distribution format
- [x] Audit all skill frontmatter for `npx skills` parser compliance (`name` regex, `name` matches directory)
- [x] Rewrite orchestrator + critique inter-skill triggers to host-agnostic phrasing
- [x] Update sub-skill `Usage` blocks to lead with skill-name invocation, mark `/reaper:` as slash-command-host example
- [x] Document multi-host install in README (`npx skills add` as primary, Claude Code plugin as secondary)
- [x] Add CI: frontmatter validation + `npx skills add` discovery check
- [ ] Per-host smoke test: same research goal on Cursor, Codex CLI, Gemini CLI — compare workspace output quality and routing reliability
- [ ] Document `description` tuning patterns for reliable auto-routing across hosts
- [ ] Investigate listing in the skills.sh registry (used by `npx skills find`) for discoverability
- [ ] If specific hosts can't auto-discover sibling skills the orchestrator triggers, document host-specific install instructions or build a thin Python driver as a fallback orchestration path

### Horizon 4: The Academy

**Methodology stage:** Enriches Stage 1b (literature baseline) and Stage 3 (mid-investigation search) by expanding from crypto-specific sources to the broader CS academic network, and adding author-centric and venue-centric search alongside topic-centric search.

**Current state:** H2 (The Library) added arXiv and IACR ePrint as structured search sources, with Semantic Scholar for citation traversal. This covers cryptography and security well, but Reaper's methodology is domain-agnostic — a consensus protocol paper may need distributed systems literature (PODC, DISC), a blockchain paper may need systems/networking work (NSDI, OSDI), and any paper draws on a broader CS context. The current search tools also only support topic-centric queries ("find papers about X"), not author-centric ("what has this researcher published?") or venue-centric ("what was accepted at CCS 2025?").

**Goal:** Three new search dimensions beyond topic search:

1. **Broader topic search** — Google Scholar and DBLP cover all of CS, not just crypto. Google Scholar also indexes workshop papers, technical reports, and theses that arXiv/ePrint miss. DBLP provides clean bibliographic metadata (venue, year, co-authors) that Semantic Scholar sometimes lacks.
2. **Author-centric search** — Given a name from a paper's references or a related work, find their DBLP profile or Google Scholar page, retrieve their publication list, identify their recent focus areas, and find co-authors who work on similar problems. This is how human researchers navigate literature: "Elaine Shi has been working on this — what else has her group done?"
3. **Venue-centric search** — Given a conference (CCS, CRYPTO, PODC, S&P, EUROCRYPT), find recent proceedings, accepted papers, program committee members, and keynote topics. This surfaces work that topic search misses because the terminology differs across communities (e.g., "Byzantine agreement" vs. "atomic broadcast" vs. "state machine replication").

**What success looks like:** Given a paper on BFT consensus, `/review-literature` automatically:
- Searches arXiv + ePrint (existing) for direct topic matches
- Searches Google Scholar and DBLP for broader CS coverage
- Identifies key authors from initial results, retrieves their recent publications
- Checks proceedings of relevant venues (PODC, DISC, CCS) for recent related work
- Produces a literature survey that a reviewer wouldn't fault for missing obvious related work

#### Search Tools

Following H2's pattern: lightweight Python scripts, JSON output, graceful degradation when unavailable.

| Script | Location | Capabilities | Dependencies |
|--------|----------|--------------|-------------|
| `search_scholar.py` | `skills/search-scholar/` | `search` (topic query), `author` (author profile + publications), `citations` (citing/cited papers) | `pip install scholarly` or scraping with `requests`+`beautifulsoup4` |
| `search_dblp.py` | `skills/search-dblp/` | `search` (topic query), `author` (publication list by author), `venue` (proceedings by venue+year) | `pip install requests` (DBLP has a clean REST API) |
| `search_venue.py` | `skills/search-venue/` | `proceedings` (accepted papers by venue+year), `pc` (program committee), `recent` (last N editions) | `pip install requests beautifulsoup4` (scrapes conference websites) |

**Design notes:**
- Google Scholar aggressively rate-limits and blocks scrapers. The `scholarly` Python library works but is fragile. Consider Google Scholar as best-effort with WebSearch as fallback, not a reliable primary source.
- DBLP has a well-documented, stable REST API (`dblp.org/search/publ/api`). This is the most reliable new integration.
- Conference website scraping is inherently brittle (each conference has a different site structure). Start with a small set of well-structured venues (IACR conferences via iacr.org, ACM conferences via dl.acm.org) and expand incrementally.

#### Search Strategies

The `/review-literature` skill currently does topic-centric search only. With the new tools, it should orchestrate three search strategies in parallel:

| Strategy | When to use | Tools |
|----------|------------|-------|
| **Topic search** | Always — the baseline | arXiv, ePrint, Google Scholar, DBLP |
| **Author search** | When initial results identify recurring authors (≥2 papers by the same group) | DBLP author lookup, Google Scholar profile |
| **Venue search** | When the paper targets a specific venue or subfield (identified from paper metadata or clarified goal) | DBLP venue proceedings, conference website |

The `/investigate` skill's mid-cycle search should also gain access to author and venue search — "this proof technique was introduced by [author], what else have they published on this?" is a common mid-investigation need.

#### Tasks

- [ ] Build `search-dblp` skill with Python script (DBLP REST API: topic search, author publications, venue proceedings)
- [ ] Build `search-scholar` skill with Python script (Google Scholar: topic search, author profiles, citation traversal)
- [ ] Build `search-venue` skill with Python script (conference proceedings scraper, starting with IACR + ACM DL)
- [ ] Update `/review-literature` skill: add author-centric and venue-centric search strategies alongside existing topic search
- [ ] Update `/investigate` skill: mid-cycle author/venue search when a cycle reveals a key researcher or venue
- [ ] Update `references/search-tools.md`: add new tools to the catalog and decision tree
- [ ] Handle graceful degradation: Google Scholar blocking, conference site structure changes
- [ ] Test: given a seed paper, does the expanded search surface find relevant work that arXiv + ePrint missed?
- [ ] Test: does author-centric search surface work that topic search misses due to different terminology?

### Horizon 5: The Apprentice (Evidence Quality)

**Methodology stage:** Strengthens the evaluation signal across all stages by making the system self-aware of its evidence quality.

**Goal:** The `/investigate` skill already tracks confidence (High/Medium/Low) and outcome (confirmed/refuted/inconclusive), but these are vibes — there's no framework distinguishing a formal proof from a plausible argument from a heuristic suspicion. The Apprentice adds an evidence taxonomy so Reaper is honest about *what kind* of evidence backs each claim, and enforces that weak evidence gets elevated or discarded.

**Current state:** The investigate skill has confidence levels with a "default one level lower than instinct" heuristic and outcome tags (confirmed/refuted/partially-confirmed/inconclusive/new-hypothesis/reformulate). The critique skill classifies feedback into scope/deepen/explore/rewrite. Neither reasons about evidence *strength*.

**What success looks like:** When Reaper says "we found a gap in the proof," it classifies the evidence as "formal counterexample" vs. "plausible argument" vs. "heuristic suspicion." A "keep" decision at the heuristic level automatically queues a follow-up cycle to elevate the evidence. The critique skill flags claims where stated confidence exceeds evidence strength. The final report distinguishes proven claims from conjectures.

#### Evidence Taxonomy

Every claim in `notes/results.md` and `current-understanding.md` must be tagged with an evidence level:

| Level | Meaning | Example |
|-------|---------|---------|
| **Formal proof** | Complete, step-by-step argument with no gaps | "Theorem 3.2 fails because step (ii) assumes synchrony (see investigation 003)" |
| **Reduction** | Claim follows from a known result via explicit reduction | "Insecurity follows by reduction to the impossibility of [DLS88]" |
| **Counterexample** | Concrete execution trace or adversary strategy | "Adversary corrupts parties {1,2}, sends conflicting messages in round 3 → safety violation" |
| **Bounded search** | Systematic search found no counterexample in a defined space | "No counterexample exists for n ≤ 6, t ≤ 2 (exhaustive check)" |
| **Plausible argument** | Informal but coherent reasoning | "The simulator likely cannot handle abort because it has no rewinding opportunity" |
| **Heuristic suspicion** | Pattern match or intuition, not yet substantiated | "The proof structure resembles [X] which had a known flaw" |

The `/investigate` skill's keep-or-discard decision should account for evidence level: a "keep" at the "heuristic suspicion" level must be followed by a cycle that attempts to elevate it. The orchestrator's adaptation signals (currently ">50% discard → brainstorm") should also consider evidence distribution — a round where most keeps are heuristic-level warrants deepening, not advancing.

#### Evidence-Aware Critique

The `/critique` skill's self-review mode currently identifies "weak claims" and "untested assumptions" but has no systematic way to evaluate them. With the evidence taxonomy:

- **Self-review** checks each claim's evidence level against its stated confidence. High confidence + heuristic suspicion = flag.
- **Codex consultation** receives evidence levels as context, enabling more targeted devil's advocate ("this claim rests on a plausible argument — can you construct a counterexample?").
- **Human feedback** records whether the human's correction reveals a mis-classified evidence level (e.g., what Reaper called a "formal proof" had a gap).

#### Tasks

- [ ] Define and document the evidence taxonomy (the table above, integrated into `/investigate` and `/critique` skills)
- [ ] Update `notes/results.md` format to include evidence level column alongside existing confidence and outcome
- [ ] Update `/investigate` skill: tag every claim with evidence level, require elevation plan for heuristic-level keeps
- [ ] Update `/critique` skill: self-review checks evidence level vs. confidence, Codex consultation includes evidence context
- [ ] Update `/synthesize` skill: distinguish proven claims from conjectures in the report (leverages LaTeX theorem/conjecture environments from H1)
- [ ] Update orchestrator adaptation signals: factor in evidence distribution, not just keep/discard ratio
- [ ] Test: does evidence tagging change keep/discard decisions compared to current behavior?

### Horizon 6: The Examiner (Verification & Provenance)

**Methodology stage:** Strengthens Stage 3 (investigate) with proactive reformulation and claim provenance, with formal verification as a stretch goal.

**Goal:** Address two structural gaps: (1) the pipeline can reformulate reactively (the investigate skill already emits `outcome: reformulate` which triggers re-formalization), but has no *proactive* trigger when a pattern of failure suggests the problem statement itself is wrong; (2) claims in the final report don't link back to the investigation cycles that support them, making audit difficult.

**Current state:** The investigate skill has `outcome: reformulate` which hands control to the orchestrator to re-run `/formalize-problem`. The orchestrator checks for this after each batch. But this only fires when a single cycle explicitly concludes "reformulate" — it doesn't detect the pattern of 5 consecutive inconclusive results that suggests the formalization is flawed. Separately, `/synthesize` reads investigation directories selectively but doesn't generate provenance links in the report.

**What success looks like:** After 5 consecutive inconclusive/discard cycles where no individual cycle triggered reformulation, the orchestrator proactively escalates — passing the accumulated failure evidence to `/formalize-problem` for re-examination. The final report includes investigation references for every claim, so a reader can trace any finding back to its supporting reasoning.

#### Proactive Reformulation Trigger

The existing reactive mechanism (`outcome: reformulate`) handles cases where a cycle discovers a specific flaw in the formalization. The proactive trigger handles the subtler case: persistent failure without a clear cause.

**Trigger condition:** After N consecutive discard/inconclusive results (default N=5), or when the `/critique` skill flags a systematic pattern of failure, the orchestrator invokes `/formalize-problem` again with:
- The original inputs (paper, goal, literature)
- The accumulated evidence of what doesn't work (from `notes/results.md`)
- An explicit directive: "The current formalization may be flawed. Re-examine the trust assumptions, security property definitions, and hypothesis framing in light of these failed attempts."

The reformulated `problem-statement.md` replaces the old one (old version archived in `investigations/`). Investigation continues from the new formulation. This complements the existing reactive path — both can coexist.

#### Claim Provenance

Every claim in `report.md` should reference the investigation cycle(s) that support it. The `/synthesize` skill already reads investigations selectively; provenance links are a natural extension:

- Each claim references the investigation directory and notes/results.md cycle that produced it
- Evidence level (from H5) is included so readers know the strength of support
- Claims supported by multiple cycles reference all of them

This doesn't require a rigid format — the `/synthesize` skill should produce natural prose with inline references, not a mechanical template.

#### Formal Verification (Stretch)

For specific claim types, mechanical checking could complement informal reasoning. This is a stretch goal because the hard problem is *encoding* — translating informal prose claims into tool-specific languages (Tamarin models, Z3 constraints) is itself a research problem.

| Claim type | Tool | Feasibility |
|-----------|------|-------------|
| Protocol safety/liveness | Tamarin, ProVerif | Medium — symbolic models are well-understood for standard protocols |
| Arithmetic/algebraic claims | Z3, SageMath | High — constraint encoding is relatively straightforward |
| Counterexample search | Z3, model checking | High — bounded search is well-suited to SMT solvers |
| Proof steps | Lean, Coq | Low — requires deep formalization expertise, aspirational only |

The investigate skill already has access to Bash for running external tools. Integration means teaching the skill *when* to attempt mechanical checking and *how* to interpret results (timeouts ≠ confirmation). The evidence taxonomy (H5) classifies tool-backed claims as stronger evidence.

#### Tasks

- [ ] Add proactive reformulation trigger to orchestrator: count consecutive discards/inconclusives, escalate at N=5
- [ ] Update `/formalize-problem` skill: accept "reformulation mode" with prior failure evidence alongside existing initial mode
- [ ] Update `/synthesize` skill: generate investigation references for each claim in the report (uses LaTeX `\label`/`\ref` cross-references and BibTeX `\cite{}` from H1)
- [ ] Add `references/computation.md` — decision tree for when mechanical checking is worth attempting (Z3 for bounded search, Tamarin for protocol models)
- [ ] (Stretch) Build Z3 integration for bounded counterexample search — lowest barrier, highest payoff
- [ ] (Stretch) Build Tamarin integration for protocol security claims
- [ ] Test: does proactive reformulation produce better outcomes than the existing reactive-only path?

---

## Design Decisions

### Intellectual Heritage

Reaper's methodology draws from four sources:

**[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** — The loop discipline. Constrain the loop enough that the AI can iterate autonomously at high speed, with a clear signal of what constitutes progress. The structured results log, keep-or-discard mechanism, never-stop policy, and simplicity criterion are all direct adaptations. The key difference: autoresearch has `val_bpb` as an objective oracle. Reaper must rely on softer evaluation signals (hypothesis resolution, logical consistency, rigor). This is why Horizon 3 (multi-model feedback) matters — cross-model verification partially compensates for the lack of an objective metric.

**[Richard Hamming, "You and Your Research"](https://d37ugbyn3rpeym.cloudfront.net/stripe-press/TAODSAE_zine_press.pdf)** (Stripe Press edition of *The Art of Doing Science and Engineering*) — The importance filter and problem-inversion technique. Hamming's central question — "Why are you not working on the important problems in your field?" — shapes the importance filter in Principle 2: prioritize hypotheses by consequence, not convenience. His technique of inverting blockages into insights (if you can't prove it, try to disprove it) is built into the "when stuck" protocol in Principle 5. Hamming also taught that effort compounds — steady, disciplined investigation cycles accumulate understanding the way compound interest accumulates capital.

**[Zhiyun Qian, "How to Look for Ideas in Computer Science Research"](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f)** — Systematic idea generation patterns. Qian's six patterns (fill-in-the-blank, expansion, build-a-hammer, start-small-then-generalize, reproduce-prior-work, external-sources) are incorporated into Principles 2 and 5, and into the `/formalize-problem` skill's approach to generating ideas. The "fill in the blank" pattern — mapping dimensions of existing research and finding unexplored combinations — is particularly powerful for theoretical research where the design space of threat models, protocol families, and security properties can be systematically enumerated.

**[Simon Peyton Jones, "How to Write a Great Research Paper"](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf)** — Writing as research methodology. Peyton Jones's core insight — that writing is a primary mechanism for doing research, not just for reporting it — is woven into Principle 6 (Clarity and Simplicity). His structural advice (one clear "ping," explicit refutable contributions, examples before generality, narrative flow over chronological recounting) shapes the `/synthesize` skill's report format. Most importantly, the idea that you should write *before* you fully understand forces Reaper to crystallize its understanding in `current-understanding.md` at every cycle, not just at the end.

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

A monolithic "do research" skill is hard to test, hard to improve, and hard to reuse partially. By decomposing into `/analyze-paper`, `/review-literature`, `/formalize-problem`, `/investigate`, `cross-verify`, and `/synthesize`, each skill:
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
