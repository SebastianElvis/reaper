# Reaper

**Reaper (REAd PapER)** — an AI-native scientific research pipeline. A composable set of [AI agent skills](https://github.com/vercel-labs/skills) that takes a research goal — optionally with a research paper — and autonomously conducts rigorous, multi-step academic research. Runs on any agent that supports the `SKILL.md` convention (Cursor, Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, Claude Code, and 40+ more).

[![Skills](https://img.shields.io/badge/skills-SKILL.md-brightgreen)](https://github.com/vercel-labs/skills)

## What Reaper Does

Give Reaper a research question — with or without a PDF. It reads the paper (if provided), searches for related work, formalizes hypotheses, investigates them in parallel, critiques its own findings, and delivers a structured research report — all without manual prompting between steps.

```
# Without a paper — pure goal-driven research
/reaper "explore the feasibility of post-quantum threshold signatures"

# With a paper
/reaper "determine if the security proof in Section 4 holds under asynchrony" path/to/paper.pdf
```

How you invoke a skill depends on the host agent. The `/<skill>` form above is the canonical display convention used throughout these docs — it works directly on slash-command hosts (e.g. Claude Code), and on auto-discovery hosts (Cursor, Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, …) you simply ask the agent to "run the `/reaper` skill on …" by its bare name.

**Key capabilities:**

- **Autonomous multi-stage pipeline** — goal clarification, paper analysis, literature review, hypothesis formalization, parallel investigation, critique, and synthesis all chain automatically
- **Parallel investigation with keep-or-discard discipline** — multiple hypotheses are investigated concurrently; only genuine progress advances the working state, while dead ends stay logged
- **Built-in academic search** — paper search, PDF download, citation graph tracing, and venue resolution across arXiv, IACR ePrint, Semantic Scholar, DBLP, and OpenAlex
- **Domain-agnostic design** — ships with cryptography and distributed systems references, but swap the reference files to adapt to any research domain
- **External review** — Reaper can request Codex feedback during critique. Other model backends remain planned.
- **Output language** — Reaper follows the shared [language rules](skills/reaper/references/language.md).
- **Composable skills** — each pipeline stage is an independent skill you can run standalone
- **Host-agnostic** — distributed as plain `SKILL.md` folders that work across 45+ AI coding agents

Reaper selects stages from the requested scope. A summary uses paper analysis. A narrow claim check uses only the evidence and checks it needs. Reaper creates a LaTeX paper only when the user requests publication output.

Reaper defaults to 3 investigation cycles for a narrow claim and 10 cycles for an open research goal. A user limit overrides these defaults. Interrupted cycles consume budget. Resume preserves existing work and claim evidence.

## How It Works

Reaper executes a multi-stage pipeline where investigation runs in parallel batches and critique provides feedback from multiple sources:

```
                     ┌── /analyze-paper (if paper) ──┐
/clarify-goal ─────> │                               ├─> /formalize-problem
                     └── /review-literature ─────────┘          │
                           │ (parallel)                         v
                           │                    ┌──────────> /brainstorm
                           └── calls            │                │
                               /analyze-paper   │                │
                               per downloaded   │    ┌─ /investigate ─────────────────┐
                               paper            │    │  plan batch                    │
                                                │    │    ├──> agent H1 ─┐            │
                                                │    │    ├──> agent H2 ─┼──> merge   │
                                                │    │    └──> agent H3 ─┘     │      │
                                                │    │          next batch or done    │
                                                │    └────────────────────────────────┘
                                                │                    │
                                                │    ┌─ /critique ────────────────────┐
                                                │    │  --self  --codex  "feedback"   │
                                                │    └────┬───────────────────┬───────┘
                                                │         │                   │
                                                │   deepen/explore    rewrite/done ──> /write-paper ──> report/main.tex
                                                └─────────┘
```

## Skills

Each skill can be used independently or composed by the orchestrator. Invoke by skill `name` using your host's native skill-loading mechanism.

| Skill | What it does |
|-------|-------------|
| `/reaper` | Full pipeline: clarify → analyze → literature → formalize → brainstorm → investigate ↔ critique → write-paper |
| `/clarify-goal` | Ask targeted clarifying questions to sharpen a vague research goal |
| `/analyze-paper` | Extract structured information from a research paper |
| `/review-literature` | Search and summarize related academic work |
| `/formalize-problem` | Produce precise, testable hypotheses from a research question |
| `/brainstorm` | Generate, prioritize, and refine research ideas based on current state |
| `/investigate` | Run investigation cycles with keep-or-discard discipline |
| `/critique` | Provide critique via human feedback, Codex consultation, or self-review (can trigger more investigation) |
| `/write-paper` | This skill writes a LaTeX research paper that meets the bar of the target venue. The paper separates supported results from conjectures and limitations. |
| `/search-paper` | Find papers, download PDFs, trace citation graphs, and resolve publication venues across arXiv, IACR ePrint, Semantic Scholar, DBLP, and OpenAlex |

> The `/<skill>` form is the canonical display convention used throughout these docs. Slash-command hosts (Claude Code) invoke them directly that way (e.g. `/clarify-goal`). Auto-discovery hosts (Cursor, Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, …) invoke them by the bare skill name — drop the leading `/` when asking the agent to run a skill.

## Installation

### Prerequisites

The search skills require Python packages:

```bash
pip install arxiv requests beautifulsoup4
```

> **Note**: `npx skills` only copies `SKILL.md` files, Python scripts, and reference files into your agent's skills folder. It does **not** install Python dependencies, register MCP servers, or create the `reaper-workspace/` directory. Install Python deps yourself with the command above; register the Codex MCP server separately if you want `--codex` (see [Optional: Multi-model AI consultation](#optional-multi-model-ai-consultation) below); the workspace directory is created automatically the first time the pipeline runs.

### Install via `npx skills` (recommended — works on 45+ agents)

Reaper is distributed as standard `SKILL.md` folders. The cross-agent installer [`vercel-labs/skills`](https://github.com/vercel-labs/skills) shallow-clones this repository and copies all 10 skill directories — including Python scripts and reference files — into your agent's conventional skills folder.

```bash
# Latest from the default branch
npx skills add SebastianElvis/reaper

# Pinned to a specific release (recommended for reproducibility)
npx skills add SebastianElvis/reaper#v0.4.0

# Install into a specific agent (defaults to all detected)
npx skills add SebastianElvis/reaper --agent cursor
```

Supported targets include Cursor, OpenAI Codex CLI, Cline, Continue, Gemini CLI, GitHub Copilot, Windsurf, OpenCode, Warp, Goose, Replit, Claude Code, and a `universal` target at `.agents/skills/`. See `npx skills list-agents` for the full list.

> **Reminder**: `npx skills add` copies files only. Python deps and MCP server registration are separate steps — see Prerequisites above and [Optional: Multi-model AI consultation](#optional-multi-model-ai-consultation) below.

### Install on Claude Code (as a plugin)

Claude Code can also consume Reaper via its native plugin marketplace mechanism, which bundles the same skills with slash-command routing:

```
/plugin marketplace add SebastianElvis/reaper
/plugin install reaper@SebastianElvis-reaper
```

Or clone and add as a local marketplace:

```bash
git clone https://github.com/SebastianElvis/reaper.git
/plugin marketplace add ./reaper
/plugin install reaper@reaper
```

See the [Claude Code plugin docs](https://code.claude.com/docs/en/discover-plugins) for more details.

### Invocation across hosts

- **Slash-command hosts** (Claude Code): `/reaper "<goal>"`, `/analyze-paper <path>`, etc. Each skill is available as a top-level slash command.
- **Auto-discovery hosts** (Cursor, Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, …): the agent loads `SKILL.md` files from its skills folder and invokes them by name when the task matches the skill's `description`. Ask the agent to run the skill, e.g. *"use the reaper skill to research X"*.
- **Manual invocation**: any host can be pointed at a specific `SKILL.md` if its native discovery doesn't pick it up.

A few skill features are host-specific:

- The `--codex` flag enables external-model consultation via MCP. It currently requires a host with MCP support (Claude Code, OpenCode, etc.) and reports unavailable external review and uses self-review elsewhere.
- Frontmatter keys `user-invocable`, `argument-hint`, hooks, and `context: fork` are Claude-Code-specific. They are preserved in the SKILL.md files but no-op on other hosts.

### Optional: Multi-model AI consultation

The `--codex` flag requests external review during critique. The orchestrator schedules any resulting research within the shared budget. The [review protocol](skills/reaper/references/codex-consultation.md) defines evidence, logging, and fallback.

**Supported backends:**

| Model | Setup | Strength |
|-------|-------|----------|
| OpenAI Codex/o3 | Register `codex-mcp-server` in your host's MCP config | Adversarial review, stress-testing arguments |
| Google Gemini | *(coming soon)* | Long-context review across full paper corpora |
| DeepSeek R1 | *(coming soon)* | Proof checking, formal reasoning |
| Local models | *(coming soon — via ollama)* | Offline/private use, cost control |

Example registration on Claude Code:

```bash
claude mcp add codex-cli -- npx -y codex-mcp-server
```

Other MCP-capable hosts use their own equivalent registration. If no model backends are configured, Reaper reports unavailable external review and continues with self-review.

## Workspace

When Reaper runs, it creates a `reaper-workspace/` directory:

```
reaper-workspace/
├── .gitignore                      # Git ignores generated build files.
├── papers/                         # Downloaded PDFs and <id>-notes.md files
├── notes/                          # Evolving — edited inline to reflect latest state
│   ├── research-state.md           # The run records its budget and cycle reservations.
│   ├── clarified-goal.md           # Refined goal, scope, assumptions, Q&A
│   ├── paper-summary.md            # Structured paper extraction
│   ├── literature.md               # Related work survey
│   ├── problem-statement.md        # Formalized problem (model, properties, metrics)
│   ├── ideas.md                    # Research ideas/hypotheses (edited inline on revisit)
│   ├── current-understanding.md    # "Branch tip" — advances only on keep
│   ├── results.md                  # One row per hypothesis, updated inline on revisit
│   ├── venue-bar.md                # Target venue rules, exemplar papers, bar checklist
│   ├── bar-audit.md                # PASS/PARTIAL/FAIL per bar checklist item
│   └── figure-plans.md             # One plan per figure: sources, layout, elements
├── investigations/                 # Evolving — reuse directory on revisit, edit inline
│   └── NNN-<name>/                 # One directory per hypothesis
│       ├── analysis.md             # Reasoning, attempts, dead ends, insights
│       └── proof.md                # Formal proofs (theorems, lemmas, corollaries)
├── feedbacks/                      # Append-only — one file per event, never modified
│   ├── round-N.md                  # The record contains human feedback or self-review.
│   └── codex-consultation-N.md     # The record contains an external review and its limitations.
├── logs/                           # Append-only — one file per cycle, never modified
│   └── cycle-NNN-<slug>.md         # One log per investigation cycle (snapshot at cycle end)
└── report/
    ├── main.tex                    # The paper source uses LaTeX.
    ├── sections/NN-<name>.tex      # Each section has its own file. main.tex inputs them in order.
    ├── figures/<name>.tex          # Each figure has its own file. A section file inputs it.
    ├── tables/<name>.tex           # Each table has its own file. A section file inputs it.
    ├── references.bib              # The bibliography stores citation metadata.
    ├── Makefile                    # The default target builds the PDF. `make clean` removes build files.
    ├── .gitignore                  # Git ignores LaTeX build files.
    └── main.pdf                    # A successful build creates this file.
```

You can build the paper with `make -C reaper-workspace/report`. The build requires `latexmk` and a LaTeX distribution.

The workspace contract is host-agnostic — any agent that can read and write files in the working directory produces the same workspace structure.

## Evaluation

Skills ship with a layered evaluation system following Anthropic's [*Demystifying Evals for AI Agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) methodology. The judge is the local `claude` CLI — no API key, just your existing subscription.

| Layer | Grader | Cadence | Scope |
|---|---|---|---|
| L1 Structural | Code (`evals/graders/`) | Every PR (CI) | Required sections, lengths, broken refs, keep-or-discard cycle invariant |
| L2 Skill rubric | `claude -p` with structured-output JSON schema (`evals/judge/`) | Locally / nightly | Per-skill quality dimensions: groundedness, specificity, completeness |
| L3 End-to-end | Both | Pre-release | Full `/reaper` pipeline against canonical cases |

```bash
# L1 only (no LLM) — same thing CI runs
python3 -m evals.run_evals --layer structural

# L1 + L2 (uses your local claude CLI)
python3 -m evals.run_evals --layer all --skill analyze-paper
```

Calibration fixtures pair reference outputs with planted failures. Fresh cases run the skill on new tasks and grade its output. These modes share `evals/fixtures/`. See [`evals/README.md`](evals/README.md) for the full design and how to add a fixture.

## Methodology

Reaper's research loop follows six principles:

1. **Separation of Concerns** — AI writes to workspace, human provides the goal, skill definitions are fixed
2. **Fixed Evaluation Signal** — Clarify the goal, establish baseline via paper analysis and literature review, then formalize into precise hypotheses with trust assumptions, security properties, and impossibility screening
3. **Structured Results Log** — Every hypothesis gets one row in `notes/results.md` with action, outcome, confidence, and keep/discard status; revisits update the row inline rather than appending duplicates
4. **Keep-or-Discard Loop** — `current-understanding.md` only advances on genuine progress; dead ends stay logged but don't pollute working state
5. **Shared Budget** — Reaper uses one cycle limit across investigation, critique, and reformulation. It stops when the goal resolves, the budget ends, or no distinct useful method remains. It reports unresolved claims.
6. **Clarity and Simplicity** — One "ping" per finding, refutable claims, fewer assumptions = better; write early to crystallize understanding, not just to report it

See [`dev/ROADMAP.md`](dev/ROADMAP.md) for the full methodology and development roadmap.

## Development Status

See [`dev/ROADMAP.md`](dev/ROADMAP.md) for the full roadmap.

- **Horizon 1 (The Pipeline)**: Core skills, orchestrator, and layered eval system (L1 structural graders + L2 Claude-CLI judges with rubrics, calibrated against planted negatives) — *complete; LaTeX report output and broader rubric coverage across all skills planned*
- **Horizon 2 (The Library)**: arXiv/ePrint search via Python scripts + citation graph + venue resolution (Semantic Scholar / DBLP / OpenAlex) — *complete*
- **Horizon 3 (The Committee)**: Multi-model critique via the `/critique` skill's `--codex` mode — *Codex complete, Gemini/DeepSeek/local planned*
- **Horizon 3.5 (The Polyglot)**: Cross-agent distribution via `npx skills` and host-agnostic skill prose — *complete; per-host orchestration polish ongoing*
- **Horizon 4 (The Academy)**: Broader topic search (Scholar/DBLP), author-centric and venue-centric search — *planned*
- **Horizon 5 (The Apprentice)**: Evidence quality taxonomy, evidence-aware critique — *planned*
- **Horizon 6 (The Examiner)**: Proactive reformulation trigger, claim provenance, formal verification — *planned*

## Acknowledgements

These sources inform Reaper's methods. They do not validate its research conclusions. Reaper adapts their advice to the user's scope and evidence.

- [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) supplies an example of experiment logging and keep-or-discard decisions. Its training loop uses a measured validation score. Reaper instead checks claim evidence and uses a finite shared budget. It does not adopt the indefinite-loop instruction.
- [Richard Hamming's “You and Your Research”](https://www.cs.virginia.edu/~robins/YouAndYourResearch.html) encourages researchers to explain why a problem matters. Reaper uses this question to rank work within the user's goal.
- [Zhiyun Qian's research advice](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f) suggests design-space exploration, reusable techniques, and small starting cases. These methods generate candidates. They do not establish novelty.
- [Simon Peyton Jones's writing advice](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf) supports early drafts, explicit contributions, examples, and links from claims to evidence. Reaper drafts arguments in investigation notes before preparing a requested paper.
- [S. Keshav's reading method](https://cs.uwaterloo.ca/~brecht/courses/Perf-Eval-Shared/readings/keshav-paper-reading.pdf) uses up to three passes. Reaper selects reading depth for the task and records what remains unchecked.
- [Mathew Stiller-Reeve's peer-review article](https://www.nature.com/articles/d41586-018-06991-0) provides review guidance. Reaper's severity labels and output format are local conventions, not requirements attributed to that article.
- [`vercel-labs/skills`](https://github.com/vercel-labs/skills) provides the installer used by this repository.

## License

This project is open source. Licensed under the [Apache License 2.0](LICENSE).
