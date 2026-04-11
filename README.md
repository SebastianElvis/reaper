# Reaper

**AI-native scientific research pipeline.** Takes a research paper and a research goal, and autonomously conducts rigorous, multi-step academic research.

## Installation

Install as a Claude Code plugin:

```
/plugin install reaper@SebastianElvis
```

Or clone and install locally:

```bash
git clone https://github.com/SebastianElvis/reaper.git
cd reaper
/plugin install .
```

## Quick Start

```
/reaper path/to/paper.pdf "determine if the security proof in Section 4 holds under asynchrony"
```

## Skills

Each skill can be used independently or composed by the orchestrator:

| Skill | What it does |
|-------|-------------|
| `/reaper:reaper` | Full pipeline: analyze → literature → formalize → investigate → synthesize |
| `/reaper:analyze-paper` | Extract structured information from a research paper |
| `/reaper:review-literature` | Search and summarize related academic work |
| `/reaper:formalize-problem` | Produce precise, testable hypotheses from a research question |
| `/reaper:investigate` | Run investigation cycles with keep-or-discard discipline |
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
│   ├── paper-summary.md            # Structured paper extraction
│   ├── literature.md               # Related work survey
│   ├── hypotheses.md               # Formalized problem + testable claims
│   ├── current-understanding.md    # "Branch tip" — advances only on keep
│   └── scratchpad.md               # Free-form reasoning
├── experiments/
│   └── NNN-<name>/                 # One directory per investigation cycle
├── feedback/                       # Cross-model reviews (Horizon 3)
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
