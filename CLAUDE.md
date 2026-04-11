# Reaper

AI-native scientific research pipeline distributed as a Claude Code plugin. Takes a research paper + research goal and autonomously runs a multi-step research loop.

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
- Python scripts live alongside the skill that uses them (e.g., `skills/search-arxiv/search_arxiv.py`).
- No JavaScript/TypeScript in this project — it's Claude skills + Python only.
- When adding, removing, or renaming a skill, update `.claude-plugin/marketplace.json` to keep the `skills` array in sync. Also keep `version` in both `plugin.json` and `marketplace.json` consistent with the current release.
- The license is Apache-2.0. If `plugin.json` references a license field, it must say `"Apache-2.0"`.
- When cutting a release tag, the tag message should summarize changes since the last tag (use `git log <last-tag>..HEAD`).
- Before finishing a task, check if important docs (README.md, CLAUDE.md, dev/ROADMAP.md) need to be updated to reflect your changes.
