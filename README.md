# Reaper

**Reaper (REAd PapER)** — an AI-native scientific research pipeline. A [Claude Code plugin](https://code.claude.com/docs/en/discover-plugins) that takes a research paper and a research goal, then autonomously conducts rigorous, multi-step academic research.

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blue)](https://code.claude.com/docs/en/discover-plugins)

## Installation

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

## Quick Start

```
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony"
```

## How It Works

Reaper executes a five-stage pipeline with an optional human feedback loop:

```
                        ┌──────────────────┐
                        │ /reaper:         │───┐
┌──────────────────┐    │  analyze-paper   │   │    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ /reaper:         │───▶└──────────────────┘   ├───▶│ /reaper:     │───▶│ /reaper:     │───▶│ /reaper:     │
│  clarify-goal    │    ┌──────────────────┐   │    │  formalize   │    │  investigate │    │  synthesize  │
└──────────────────┘    │ /reaper:         │───┘    │  -problem    │    │              │    │              │
                        │  review-literature│       └──────────────┘    └───────────┬──┘    └──────────────┘
                        └──────────────────┘                                 ▲    │              ▶ report.md
                            (parallel)                                       │keep│                   │
                                                                             └────┘                   │
                                                                                  ▲  human feedback   │
                                                                                  └───────────────────┘
```

## Skills

Each skill can be used independently or composed by the orchestrator:

| Skill | What it does |
|-------|-------------|
| `/reaper` | Full pipeline: clarify → analyze → literature → formalize → investigate → synthesize |
| `/reaper:clarify-goal` | Ask targeted clarifying questions to sharpen a vague research goal |
| `/reaper:analyze-paper` | Extract structured information from a research paper |
| `/reaper:review-literature` | Search and summarize related academic work |
| `/reaper:formalize-problem` | Produce precise, testable hypotheses from a research question |
| `/reaper:investigate` | Run investigation cycles with keep-or-discard discipline (also accepts quoted feedback for iteration) |
| `/reaper:synthesize` | Generate a structured research report from investigation results |
| `/reaper:search-arxiv` | Search arXiv papers, download PDFs, and trace citation graphs |
| `/reaper:search-iacr` | Search IACR ePrint archive for cryptography papers |

## Prerequisites

The search skills require Python packages:

```bash
pip install arxiv requests beautifulsoup4
```

## Workspace

When Reaper runs, it creates a `reaper-workspace/` directory:

```
reaper-workspace/
├── notes/
│   ├── clarified-goal.md           # Refined goal, scope, assumptions, Q&A
│   ├── paper-summary.md            # Structured paper extraction
│   ├── literature.md               # Related work survey
│   ├── hypotheses.md               # Formalized problem + testable claims
│   ├── current-understanding.md    # "Branch tip" — advances only on keep
│   └── scratchpad.md               # Free-form reasoning
├── experiments/
│   └── NNN-<name>/                 # One directory per investigation cycle
├── feedback/                       # Human iteration feedback (round-N.md per round)
├── results.md                      # Cycle-by-cycle log with keep/discard
├── log.md                          # Timestamped narrative
└── report.md                       # Final synthesized output
```

## Methodology

Reaper's research loop follows six principles:

1. **Separation of Concerns** — AI writes to workspace, human provides the goal, skill definitions are fixed
2. **Fixed Evaluation Signal** — Precise hypotheses with explicit success/failure conditions
3. **Structured Results Log** — Every cycle gets a row in results.md
4. **Keep-or-Discard Loop** — current-understanding.md only advances on genuine progress
5. **Never Stop** — Run all cycles without asking permission to continue
6. **Clarity and Simplicity** — One "ping" per finding, refutable claims, fewer assumptions = better

See `dev/ROADMAP.md` for the full methodology and development roadmap.

## Development Status

- **Horizon 1 (The Pipeline)**: Core skills, orchestrator, and eval framework — *complete, pending end-to-end testing*
- **Horizon 2 (The Library)**: arXiv/ePrint search via Python scripts + citation graph — *complete*
- **Horizon 3 (The Committee)**: Multi-model adversarial review — planned
- **Horizon 4 (The Lab)**: Multi-paper, computation, LaTeX — planned

## Acknowledgements

Reaper's methodology draws from four sources:

- **[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** — Loop discipline: constrain the loop so the AI can iterate autonomously with a clear signal of progress. The structured results log, keep-or-discard mechanism, and never-stop policy are direct adaptations.
- **[Richard Hamming, "You and Your Research"](https://d37ugbyn3rpeym.cloudfront.net/stripe-press/TAODSAE_zine_press.pdf)** — The importance filter ("Why are you not working on the important problems?") and the technique of inverting blockages into insights.
- **[Zhiyun Qian, "How to Look for Ideas in Computer Science Research"](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f)** — Systematic idea generation patterns (fill-in-the-blank, start-small-then-generalize, build-a-hammer) for formulating testable claims.
- **[Simon Peyton Jones, "How to Write a Great Research Paper"](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf)** — Writing as a primary mechanism for doing research, not just reporting it. Shapes the report structure: one clear "ping," explicit refutable contributions, examples before generality.

## License

This project is open source. Licensed under the [Apache License 2.0](LICENSE).
