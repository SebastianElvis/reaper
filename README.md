# Reaper

**Reaper (REAd PapER)** — an AI-native scientific research pipeline. A [Claude Code plugin](https://code.claude.com/docs/en/discover-plugins) that takes a research paper and a research goal, then autonomously conducts rigorous, multi-step academic research.

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blue)](https://code.claude.com/docs/en/discover-plugins)

## What Reaper Does

Give Reaper a PDF and a question. It reads the paper, searches for related work, formalizes hypotheses, investigates them in parallel, critiques its own findings, and delivers a structured research report — all without manual prompting between steps.

```
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony"
```

**Key capabilities:**

- **Autonomous multi-stage pipeline** — goal clarification, paper analysis, literature review, hypothesis formalization, parallel investigation, critique, and synthesis all chain automatically
- **Parallel investigation with keep-or-discard discipline** — multiple hypotheses are investigated concurrently; only genuine progress advances the working state, while dead ends stay logged
- **Built-in academic search** — arXiv and IACR ePrint search with PDF download and citation graph tracing
- **Domain-agnostic design** — ships with cryptography and distributed systems references, but swap the reference files to adapt to any research domain
- **Optional AI consultation** — enable Codex MCP for a second opinion at every pipeline stage
- **Composable skills** — each pipeline stage is an independent skill you can run standalone

## How It Works

Reaper executes a multi-stage pipeline where investigation runs in parallel batches and critique provides feedback from multiple sources:

```
                      ┌─ /analyze-paper ─────────┐
/clarify-goal ──────> │                          ├─> /formalize-problem
                      └─ /review-literature ─────┘          │
                            (parallel)                      v
                                       ┌──────────────> /brainstorm
                                       │                    │
                                       │    ┌─ /investigate ─────────────────┐
                                       │    │  plan batch                    │
                                       │    │    ├──> agent H1 ─┐            │
                                       │    │    ├──> agent H2 ─┼──> merge   │
                                       │    │    └──> agent H3 ─┘     │      │
                                       │    │          next batch or done     │
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

Each skill can be used independently or composed by the orchestrator:

| Skill | What it does |
|-------|-------------|
| `/reaper` | Full pipeline: clarify → analyze → literature → formalize → brainstorm → investigate ↔ critique → synthesize |
| `/reaper:clarify-goal` | Ask targeted clarifying questions to sharpen a vague research goal |
| `/reaper:analyze-paper` | Extract structured information from a research paper |
| `/reaper:review-literature` | Search and summarize related academic work |
| `/reaper:formalize-problem` | Produce precise, testable hypotheses from a research question |
| `/reaper:brainstorm` | Generate, prioritize, and refine research ideas based on current state |
| `/reaper:investigate` | Run investigation cycles with keep-or-discard discipline |
| `/reaper:critique` | Provide critique via human feedback, Codex consultation, or self-review (can trigger more investigation) |
| `/reaper:synthesize` | Generate a structured research report from investigation results |
| `/reaper:search-arxiv` | Search arXiv papers, download PDFs, and trace citation graphs |
| `/reaper:search-iacr` | Search IACR ePrint archive for cryptography papers |

## Installation

### Prerequisites

The search skills require Python packages:

```bash
pip install arxiv requests beautifulsoup4
```

### From the marketplace

Add the marketplace and install the plugin:

```
/plugin marketplace add SebastianElvis/reaper
/plugin install reaper@SebastianElvis-reaper
```

### Manual installation via Git

Clone the repository and add it as a local marketplace:

```bash
git clone https://github.com/SebastianElvis/reaper.git
/plugin marketplace add ./reaper
/plugin install reaper@reaper
```

Or manually copy skills into your Claude configuration:

```bash
# Clone the repository
git clone https://github.com/SebastianElvis/reaper.git

# Global installation (available in all projects)
cp -r reaper/skills/* ~/.claude/skills/

# Or project-level installation (available in current project only)
cp -r reaper/skills/* ./.claude/skills/
```

See the [Claude Code plugin docs](https://code.claude.com/docs/en/discover-plugins) for more details on installing plugins.

### Optional: Codex MCP for AI consultation

Pass `--codex` to enable pipeline-wide Codex consultation — every skill gains a checkpoint where it can consult OpenAI Codex for a second opinion. The orchestrator controls when consultations happen (see `skills/reaper/references/codex-consultation.md` for the full protocol). To enable, register the [codex-mcp-server](https://github.com/tuannvm/codex-mcp-server):

```bash
claude mcp add codex-cli -- npx -y codex-mcp-server
```

If not configured, Codex consultation is silently skipped and the pipeline continues normally.

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

- **Horizon 1 (The Pipeline)**: Core skills, orchestrator, and eval framework — *complete*
- **Horizon 2 (The Library)**: arXiv/ePrint search via Python scripts + citation graph — *complete*
- **Horizon 3 (The Committee)**: Codex MCP critique via `/reaper:critique --codex` — *complete (optional dependency)*
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

## License

This project is open source. Licensed under the [Apache License 2.0](LICENSE).
