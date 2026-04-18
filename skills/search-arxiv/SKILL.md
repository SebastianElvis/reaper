---
name: search-arxiv
description: "Search arXiv for academic papers, download PDFs, and retrieve citation graphs. Use when you need to find papers on arXiv by topic, download a specific paper, or trace forward/backward citations."
user-invocable: true
argument-hint: "<query> [--max-results N] [--categories cs.CR,cs.DC]"
---

# Search arXiv

Search arXiv for academic papers using the `arxiv` Python package, with citation graph support via Semantic Scholar.

## Usage

Invoke this skill by name with the query as a quoted string. On slash-command hosts, prefix with `/` (e.g. `/search-arxiv "<query>"`).

```
search-arxiv "post-quantum threshold signatures" --max-results 15 --categories cs.CR
```

## Path Resolution Protocol

This skill wraps `search_arxiv.py`, which lives in the **same directory as this `SKILL.md`**. **`{{SKILL_DIR}}`** below is a template placeholder — **you MUST substitute it with the absolute install path of this skill before invoking, or the exec will fail.** Common install locations:

- `~/.claude/skills/search-arxiv/` (Claude Code)
- `~/.cursor/skills/search-arxiv/` (Cursor)
- `~/.agents/skills/search-arxiv/` (Codex CLI, Cline, Gemini CLI, Copilot, OpenCode, Warp, Goose, Replit — universal target)
- `~/.continue/skills/search-arxiv/` (Continue)
- `~/.windsurf/skills/search-arxiv/` (Windsurf)
- `<repo-root>/skills/search-arxiv/` (during repo development)

This skill has no sibling-skill dependencies — it ships its own Python script.

## Commands

Run commands via Bash.

### Search

```bash
python {{SKILL_DIR}}/search_arxiv.py search "BFT consensus communication complexity" --max-results 10 --categories cs.CR,cs.DC
```

Returns JSON array of papers: `arxiv_id`, `title`, `authors`, `year`, `abstract`, `categories`, `pdf_url`, `published`.

### Download

```bash
python {{SKILL_DIR}}/search_arxiv.py download 2305.12345 --output-dir reaper-workspace/papers/
```

Downloads the paper PDF. Returns JSON with `path` and `title`.

### Citations

```bash
python {{SKILL_DIR}}/search_arxiv.py citations 2305.12345 --max-results 20
```

Returns JSON with `references` (backward citations — what this paper builds on) and `citations` (forward citations — who cites this paper). Each entry has `title`, `authors`, `year`, `arxiv_id`, `url`.

## Role

- **Standalone**: Invoked directly by the user to search for papers.
- **Building block**: Called by `/review-literature` and `/investigate` via the underlying Python script.

## Instructions

When invoked directly:

1. Parse the user's query and any flags from the argument.
2. Run the search command via Bash.
3. Format the results as a readable table:

```markdown
| # | Title | Authors | Year | arXiv ID | Link | Categories |
|---|-------|---------|------|----------|------|------------|
| 1 | ... | ... | ... | ... | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) | ... |
```

4. For each highly relevant result, show the abstract excerpt.

## Quality Criteria

- Search returns results (graceful error message if API is down or script fails)
- Results are formatted as a readable table with abstract excerpts for top hits
- If the script fails (missing deps, network error), report the error to the caller

## Dependencies

Requires `arxiv` and `requests` Python packages:

```bash
pip install arxiv requests
```
