# Reaper

AI-native scientific research pipeline distributed as a host-agnostic skills package. Each pipeline stage is a `SKILL.md` folder that runs on any AI coding agent supporting the [skills convention](https://github.com/vercel-labs/skills) — Cursor, OpenAI Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, Claude Code, and 40+ others. Takes a research goal — optionally with a research paper — and autonomously runs a multi-step research loop. Ships with reference files for cryptography and distributed systems, but the skills themselves are domain-agnostic — swap the reference files to adapt to other research domains.

## Project structure

- `skills/` — 11 composable skills (each has a `SKILL.md` defining its behavior; the `/<skill>` form is the canonical display convention used in all user-facing docs)
  - `/reaper` — Main orchestrator that chains all other skills
  - `/clarify-goal` — Interactive goal clarification (asks user targeted questions before pipeline runs)
  - `/analyze-paper`, `/review-literature`, `/formalize-problem`, `/brainstorm`, `/investigate`, `/critique`, `/synthesize` — Pipeline stages
  - `/search-arxiv`, `/search-iacr` — Academic search via Python scripts
- `tests/` — Python tests for skill structure and search scripts
- `evals/` — Test cases with quality criteria (`evals.json`)
- `dev/` — Development docs including `ROADMAP.md` (full methodology and design)
- `.claude-plugin/` — Claude-Code-specific plugin manifest (`plugin.json`, `marketplace.json`); other hosts ignore this directory
- `.github/workflows/` — CI (pytest + strict `npx skills` discovery check that asserts every expected skill, script, and reference file is present after installation)

## Commands

```bash
# Run tests
pytest tests/

# Python dependencies for search skills
pip install arxiv requests beautifulsoup4
```

## Key conventions

- Skills are the unit of composition. Each skill directory contains a `SKILL.md` with YAML frontmatter — `name` (lowercase + hyphens, matches the directory name) and `description` are required by the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) parser; everything else is optional.
- The orchestrator skill (`/reaper`) runs the full pipeline: clarify → analyze → literature → formalize → brainstorm → investigate ↔ critique → synthesize. After delivery, users can iterate by re-invoking the `/critique` skill with feedback.
- Runtime state goes in `reaper-workspace/` (gitignored). Never commit workspace artifacts.
- The six methodology principles (separation of concerns, fixed evaluation signal, structured results log, keep-or-discard loop, never stop, clarity and simplicity) govern how skills behave.
- Domain-specific content (impossibility results, trust model checklists, venue tiers, definitional standards) lives in `skills/reaper/references/`, not inline in skills. Skills reference these files but remain domain-agnostic — the reference files can be swapped for a different research domain.
- Python scripts live alongside the skill that uses them (e.g., `skills/search-arxiv/search_arxiv.py`).
- No JavaScript/TypeScript in this project — it's `SKILL.md` files + Python only.
- The license is Apache-2.0. Any plugin manifest that references a license field must say `"Apache-2.0"`.
- When cutting a release tag, the tag message should summarize changes since the last tag (use `git log <last-tag>..HEAD`).
- Always use squash merge for PRs.
- Before finishing a task, check if important docs (README.md, CLAUDE.md, dev/ROADMAP.md) need to be updated to reflect your changes.

## Distribution

Primary distribution: [`vercel-labs/skills`](https://github.com/vercel-labs/skills) — `npx skills add SebastianElvis/reaper` shallow-clones the repo and copies all skill directories into the host agent's conventional skills folder. Targets 45+ agents including Cursor, OpenAI Codex CLI, Cline, Continue, Gemini CLI, Copilot, Windsurf, OpenCode, Warp, Goose, Replit, and Claude Code.

- Pin syntax: `npx skills add SebastianElvis/reaper#v0.3.9`. Tagged releases are the pin contract.
- The installer copies the entire skill directory (including Python scripts and `references/`); only `metadata.json`, `.git`, `__pycache__`, `__pypackages__` are excluded.
- All `SKILL.md` files must use host-agnostic phrasing ("invoke the `<name>` skill") for inter-skill calls. Sub-skill `Usage` blocks may show host-specific invocation forms (e.g. `/<sub>` on slash-command hosts like Claude Code) as examples, clearly labeled as such.

Secondary distribution: Claude Code plugin via `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. When adding, removing, or renaming a skill, keep the `skills` array in `marketplace.json` in sync. Keep `version` in both `plugin.json` and `marketplace.json` consistent with the current release tag — note that `marketplace.json.version` is ignored by `npx skills` (which uses git tags), so it serves only the Claude Code plugin path.

Claude-Code-specific frontmatter keys (`user-invocable`, `argument-hint`, hooks, `context: fork`) are preserved in `SKILL.md` files but no-op on other hosts. The `--codex` flag depends on a host with MCP support; non-MCP hosts silently fall back to self-review.
