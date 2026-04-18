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
- **Multi-model AI consultation** — optionally consult Codex, Gemini, DeepSeek, or local models for a second opinion at every pipeline stage
- **Composable skills** — each pipeline stage is an independent skill you can run standalone
- **Host-agnostic** — distributed as plain `SKILL.md` folders that work across 45+ AI coding agents

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
                                                │   deepen/explore    rewrite/done ──> /synthesize ──> report.md
                                                └─────────┘
```

## Skills

Each skill can be used independently or composed by the orchestrator. Invoke by skill `name` using your host's native skill-loading mechanism.

| Skill | What it does |
|-------|-------------|
| `/reaper` | Full pipeline: clarify → analyze → literature → formalize → brainstorm → investigate ↔ critique → synthesize |
| `/clarify-goal` | Ask targeted clarifying questions to sharpen a vague research goal |
| `/analyze-paper` | Extract structured information from a research paper |
| `/review-literature` | Search and summarize related academic work |
| `/formalize-problem` | Produce precise, testable hypotheses from a research question |
| `/brainstorm` | Generate, prioritize, and refine research ideas based on current state |
| `/investigate` | Run investigation cycles with keep-or-discard discipline |
| `/critique` | Provide critique via human feedback, Codex consultation, or self-review (can trigger more investigation) |
| `/synthesize` | Generate a structured research report from investigation results |
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
npx skills add SebastianElvis/reaper#v0.3.9

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

- The `--codex` flag enables external-model consultation via MCP. It currently requires a host with MCP support (Claude Code, OpenCode, etc.) and silently falls back to self-review elsewhere.
- Frontmatter keys `user-invocable`, `argument-hint`, hooks, and `context: fork` are Claude-Code-specific. They are preserved in the SKILL.md files but no-op on other hosts.

### Optional: Multi-model AI consultation

Pass `--codex` to enable pipeline-wide AI consultation — every skill gains a checkpoint where it can consult an external model for a second opinion. The orchestrator controls when consultations happen and routes to the best-suited model (see `skills/reaper/references/codex-consultation.md` for the protocol).

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

Other MCP-capable hosts use their own equivalent registration. If no model backends are configured, AI consultation is silently skipped and the pipeline continues with self-review only.

## Workspace

When Reaper runs, it creates a `reaper-workspace/` directory:

```
reaper-workspace/
├── notes/                          # Evolving — edited inline to reflect latest state
│   ├── clarified-goal.md           # Refined goal, scope, assumptions, Q&A
│   ├── paper-summary.md            # Structured paper extraction
│   ├── literature.md               # Related work survey
│   ├── problem-statement.md        # Formalized problem (model, properties, metrics)
│   ├── ideas.md                    # Research ideas/hypotheses (edited inline on revisit)
│   ├── current-understanding.md    # "Branch tip" — advances only on keep
│   └── results.md                  # One row per hypothesis, updated inline on revisit
├── investigations/                 # Evolving — reuse directory on revisit, edit inline
│   └── NNN-<name>/                 # One directory per hypothesis
│       ├── analysis.md             # Reasoning, attempts, dead ends, insights
│       └── proof.md                # Formal proofs (theorems, lemmas, corollaries)
├── feedbacks/                      # Append-only — one file per event, never modified
│   ├── round-N.md                  # Human feedback classified by type
│   └── codex-consultation-N.md     # Codex critique (alternates devil's advocate / inspiration)
├── logs/                           # Append-only — one file per cycle, never modified
│   └── cycle-NNN-<slug>.md         # One log per investigation cycle (snapshot at cycle end)
└── report.md                       # Final synthesized output
```

The workspace contract is host-agnostic — any agent that can read and write files in the working directory produces the same workspace structure.

## Methodology

Reaper's research loop follows six principles:

1. **Separation of Concerns** — AI writes to workspace, human provides the goal, skill definitions are fixed
2. **Fixed Evaluation Signal** — Clarify the goal, establish baseline via paper analysis and literature review, then formalize into precise hypotheses with trust assumptions, security properties, and impossibility screening
3. **Structured Results Log** — Every hypothesis gets one row in `notes/results.md` with action, outcome, confidence, and keep/discard status; revisits update the row inline rather than appending duplicates
4. **Keep-or-Discard Loop** — `current-understanding.md` only advances on genuine progress; dead ends stay logged but don't pollute working state
5. **Never Stop** — Run all cycles without asking permission to continue; if stuck, re-read the paper, question assumptions, combine discarded results, search for more related work, or try a radically different approach
6. **Clarity and Simplicity** — One "ping" per finding, refutable claims, fewer assumptions = better; write early to crystallize understanding, not just to report it

See [`dev/ROADMAP.md`](dev/ROADMAP.md) for the full methodology and development roadmap.

## Development Status

See [`dev/ROADMAP.md`](dev/ROADMAP.md) for the full roadmap.

- **Horizon 1 (The Pipeline)**: Core skills, orchestrator, and eval framework — *complete; LaTeX report output planned*
- **Horizon 2 (The Library)**: arXiv/ePrint search via Python scripts + citation graph + venue resolution (Semantic Scholar / DBLP / OpenAlex) — *complete*
- **Horizon 3 (The Committee)**: Multi-model critique via the `/critique` skill's `--codex` mode — *Codex complete, Gemini/DeepSeek/local planned*
- **Horizon 3.5 (The Polyglot)**: Cross-agent distribution via `npx skills` and host-agnostic skill prose — *complete; per-host orchestration polish ongoing*
- **Horizon 4 (The Academy)**: Broader topic search (Scholar/DBLP), author-centric and venue-centric search — *planned*
- **Horizon 5 (The Apprentice)**: Evidence quality taxonomy, evidence-aware critique — *planned*
- **Horizon 6 (The Examiner)**: Proactive reformulation trigger, claim provenance, formal verification — *planned*

## Acknowledgements

Reaper's methodology draws from the following sources:

- **[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** — Loop discipline: constrain the loop so the AI can iterate autonomously with a clear signal of progress. The structured results log, keep-or-discard mechanism, and never-stop policy are direct adaptations.
- **[Richard Hamming, "You and Your Research"](https://d37ugbyn3rpeym.cloudfront.net/stripe-press/TAODSAE_zine_press.pdf)** — The importance filter ("Why are you not working on the important problems?") and the technique of inverting blockages into insights.
- **[Zhiyun Qian, "How to Look for Ideas in Computer Science Research"](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f)** — Systematic idea generation patterns (fill-in-the-blank, start-small-then-generalize, build-a-hammer) for formulating research ideas.
- **[Simon Peyton Jones, "How to Write a Great Research Paper"](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf)** — Writing as a primary mechanism for doing research, not just reporting it. Shapes the report structure: one clear "ping," explicit refutable contributions, examples before generality.
- **[S. Keshav, "How to Read a Paper" (ACM SIGCOMM CCR, 2007)](http://ccr.sigcomm.org/online/files/p83-keshavA.pdf)** — The three-pass method for reading papers: first pass for the big picture, second pass to grasp content without details, third pass to virtually re-derive the work and challenge every assumption. Structures how the literature review skill reads downloaded papers at increasing depth.
- **[Mathew Stiller-Reeve, "How to Write a Thorough Peer Review" (Nature, 2018)](https://www.nature.com/articles/d41586-018-06991-0)** — Three-reading review method (aims → scientific substance → presentation) and the mirror technique. Structures the per-paper notes in the literature review skill: mirror the paper's claims, classify issues as major/minor/fatal, evaluate whether conclusions answer the introduction's questions.
- **[`vercel-labs/skills`](https://github.com/vercel-labs/skills)** — The cross-agent skills convention and CLI installer that makes Reaper portable across 45+ AI coding agents.

## License

This project is open source. Licensed under the [Apache License 2.0](LICENSE).
