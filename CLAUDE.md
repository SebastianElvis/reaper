# Reaper

AI-native scientific research pipeline distributed as a Claude Code plugin. Takes a research paper + research goal and autonomously runs a multi-step research loop. Ships with reference files for cryptography and distributed systems, but the skills themselves are domain-agnostic — swap the reference files to adapt to other research domains.

## Project structure

- `skills/` — 11 composable Claude skills (each has a `SKILL.md` defining its behavior)
  - `reaper/` — Main orchestrator that chains all other skills
  - `clarify-goal/` — Interactive goal clarification (asks user targeted questions before pipeline runs)
  - `analyze-paper/`, `review-literature/`, `formalize-problem/`, `brainstorm/`, `investigate/`, `critique/`, `synthesize/` — Pipeline stages
  - `search-arxiv/`, `search-iacr/` — Academic search via Python scripts
- `tests/` — Python tests for skill structure and search scripts
- `evals/` — Test cases with quality criteria (`evals.json`)
- `dev/` — Development docs including `ROADMAP.md` (full methodology and design)
- `.claude-plugin/plugin.json` — Plugin metadata

## Commands

```bash
# Run tests
pytest tests/

# Python dependencies for search skills
pip install arxiv requests beautifulsoup4
```

## Key conventions

- Skills are the unit of composition. Each skill directory contains a `SKILL.md` with frontmatter.
- The orchestrator (`/reaper`) runs the full pipeline: clarify → analyze → literature → formalize → brainstorm → investigate ↔ critique → synthesize. After delivery, users can iterate via `/reaper:critique "feedback"`.
- Runtime state goes in `reaper-workspace/` (gitignored). Never commit workspace artifacts.
- The six methodology principles (separation of concerns, fixed evaluation signal, structured results log, keep-or-discard loop, never stop, clarity and simplicity) govern how skills behave.
- Domain-specific content (impossibility results, trust model checklists, venue tiers, definitional standards) lives in `skills/reaper/references/`, not inline in skills. Skills reference these files but remain domain-agnostic — the reference files can be swapped for a different research domain.
- Python scripts live alongside the skill that uses them (e.g., `skills/search-arxiv/search_arxiv.py`).
- No JavaScript/TypeScript in this project — it's Claude skills + Python only.
- When adding, removing, or renaming a skill, update `.claude-plugin/marketplace.json` to keep the `skills` array in sync. Also keep `version` in both `plugin.json` and `marketplace.json` consistent with the current release.
- The license is Apache-2.0. If `plugin.json` references a license field, it must say `"Apache-2.0"`.
- When cutting a release tag: (1) bump version in `plugin.json` and `marketplace.json`, (2) commit and merge the version bump PR to `main` first, (3) then create the annotated tag pointing at the merged commit on `main`. The tag must always point to a commit on `main`, never a feature branch. The tag message should summarize changes since the last tag (use `git log <last-tag>..HEAD`).
- Always use squash merge for PRs.
- Before finishing a task, check if important docs (README.md, CLAUDE.md, dev/ROADMAP.md) need to be updated to reflect your changes.
