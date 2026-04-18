---
name: search-paper
description: "Find papers, download PDFs, traverse citation graphs, and resolve publication venues across arXiv, IACR ePrint, Semantic Scholar, DBLP, and OpenAlex. Use when you need to find papers, trace citations, or determine where a paper was published."
user-invocable: true
argument-hint: "<query> [--source arxiv|iacr] [--max-results N]"
---

# Search Paper

A single skill that wraps five platform drivers — two preprint archives (arXiv, IACR ePrint) and three metadata services (Semantic Scholar, DBLP, OpenAlex). The SKILL.md itself acts as the orchestrator: each script does one thing per platform, and the agent chains them.

## Usage

Invoke this skill by name. On slash-command hosts: `/search-paper "<query>"`.

```
search-paper "post-quantum threshold signatures" --source iacr --max-results 15
```

## Path Resolution Protocol

This skill ships five Python scripts in the **same directory as this `SKILL.md`**. The placeholder **`{{SKILL_DIR}}`** below is a template token — **you MUST substitute it with the absolute install path of this skill before invoking, or the exec will fail.** Common install locations:

- `~/.claude/skills/search-paper/` (Claude Code)
- `~/.cursor/skills/search-paper/` (Cursor)
- `~/.agents/skills/search-paper/` (Codex CLI, Cline, Gemini CLI, Copilot, OpenCode, Warp, Goose, Replit — universal target)
- `~/.continue/skills/search-paper/` (Continue)
- `~/.windsurf/skills/search-paper/` (Windsurf)
- `<repo-root>/skills/search-paper/` (during repo development)

This skill has no sibling-skill dependencies — it ships its own scripts.

## Scripts

Run via Bash. All scripts emit JSON on stdout.

### `arxiv.py` — arXiv preprint server

```bash
python {{SKILL_DIR}}/arxiv.py search "BFT consensus communication complexity" --max-results 10 --categories cs.CR,cs.DC
python {{SKILL_DIR}}/arxiv.py recent "threshold signatures" --max-results 10 --categories cs.CR
python {{SKILL_DIR}}/arxiv.py download 2305.12345 --output-dir reaper-workspace/papers/
python {{SKILL_DIR}}/arxiv.py journal-ref 2305.12345
```

- `search` — array of `{arxiv_id, title, authors, year, abstract, categories, pdf_url, published, journal_ref}` sorted by relevance.
- `recent` — same fields, sorted by submission date (newest first). Requires a query and/or `--categories`.
- `download` — saves PDF, returns `{path, title}`.
- `journal-ref` — author-supplied venue (sparse but authoritative when present).

### `iacr.py` — IACR ePrint archive

```bash
python {{SKILL_DIR}}/iacr.py search "threshold signatures" --max-results 10
python {{SKILL_DIR}}/iacr.py recent --max-results 10
python {{SKILL_DIR}}/iacr.py download 2024/1234 --output-dir reaper-workspace/papers/
python {{SKILL_DIR}}/iacr.py url 2024/1234
python {{SKILL_DIR}}/iacr.py pubinfo 2024/1234
```

- `search` — array of `{eprint_id, title, authors, year, abstract, publication_info, venue, pdf_url, url}`. Top 5 results are enriched with metadata from the paper page (including `publication_info`).
- `recent` — most-recently-posted ePrint papers.
- `download` / `url` — PDF download and URL resolution.
- `pubinfo` — scrapes the "Publication info" line from the paper page (e.g. *"A major revision of CRYPTO 2023"*) and best-effort parses out the venue acronym + year.

### `semantic_scholar.py` — Semantic Scholar metadata

```bash
python {{SKILL_DIR}}/semantic_scholar.py venue --arxiv 2305.12345
python {{SKILL_DIR}}/semantic_scholar.py venue --title "HotStuff: BFT Consensus in the Lens of Blockchain"
python {{SKILL_DIR}}/semantic_scholar.py citations 2305.12345 --max-results 20
```

- `venue` — looks up the publication venue by arXiv ID (preferred when available — exact match) or by title (fuzzy match via `/paper/search/match`). Returns `{found, venue, venue_full, venue_type, year, title, authors}`.
- `citations` — forward (who cites this) + backward (what this builds on) citations. Each entry includes `venue` when known.

### `dblp.py` — DBLP (CS-focused)

```bash
python {{SKILL_DIR}}/dblp.py venue "HotStuff: BFT Consensus" --author "Yin"
```

- `venue` — title (+ optional author surname) lookup. DBLP is authoritative for CS conference and journal venues.

### `openalex.py` — OpenAlex (broad coverage)

```bash
python {{SKILL_DIR}}/openalex.py venue "HotStuff: BFT Consensus in the Lens of Blockchain"
```

- `venue` — title-based lookup. Use when DBLP doesn't cover the venue (non-CS, niche workshops, books).

## Role

- **Standalone**: Invoked directly by the user to search for papers, trace citations, or resolve a venue.
- **Building block**: Called by `/review-literature` and `/investigate` for structured paper search and venue resolution.

## Instructions

When invoked directly:

1. Parse the user's query and any flags from the argument.
2. Pick the right script(s):
   - Crypto/security topic → run `iacr.py search` AND `arxiv.py search --categories cs.CR`.
   - General CS topic → run `arxiv.py search` with appropriate categories.
   - Citation context → `semantic_scholar.py citations <arxiv_id>`.
   - Venue resolution → follow the **Venue Resolution Protocol** below.
3. Format paper results as a readable table:

```markdown
| # | Title | Authors | Year | Venue | ID | Link |
|---|-------|---------|------|-------|----|------|
| 1 | ... | ... | ... | ... | arXiv:XXXX.XXXXX | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) |
```

4. For each highly relevant result, show the abstract excerpt.

## Venue Resolution Protocol

A paper's archive ID (arXiv, ePrint) is *not* its publication venue. Resolve the actual venue (CRYPTO, S&P, PODC, …) for every paper that goes into a literature review or report references section. Run the layers in order and **stop at the first success**:

### Layer 1 — Semantic Scholar (cheapest, highest hit-rate)

```bash
# arXiv-known papers
python {{SKILL_DIR}}/semantic_scholar.py venue --arxiv <arxiv_id>

# ePrint-only papers
python {{SKILL_DIR}}/semantic_scholar.py venue --title "<exact title>"
```

If `found: true` and `venue` is non-empty → done. Record `source = "semantic_scholar"`.

### Layer 2 — Author-supplied field on the source archive

Authors sometimes mark the venue on their own preprint:

```bash
# arXiv: the journal_ref field
python {{SKILL_DIR}}/arxiv.py journal-ref <arxiv_id>

# ePrint: the "Publication info" line
python {{SKILL_DIR}}/iacr.py pubinfo <eprint_id>
```

If a non-empty `journal_ref` / `publication_info` is returned → done. Record `source = "arxiv_journal_ref"` or `"iacr_pubinfo"`.

### Layer 3 — DBLP (CS-authoritative title+author search)

```bash
python {{SKILL_DIR}}/dblp.py venue "<title>" --author "<first author surname>"
```

If `found: true` → done. Record `source = "dblp"`.

### Layer 4 — OpenAlex (broad coverage)

```bash
python {{SKILL_DIR}}/openalex.py venue "<title>"
```

If `found: true` → done. Record `source = "openalex"`.

### Layer 5 — Preprint-only label

If all four layers fail, label the entry `(preprint)` rather than silently omitting. Do **not** guess a venue from the topic or author affiliation — an unverified guess is worse than an honest "preprint only".

### Notes

- Layers 1 + 2 cover ~80% of papers at near-zero cost. Add layers 3 + 4 only when needed.
- Cache results in your workspace notes — don't re-resolve the same paper across cycles.
- When two sources disagree, prefer the higher-tier source name (Semantic Scholar's `publicationVenue.name` over DBLP's terse acronym, etc.). Record both if confidence is low.

## Quality Criteria

- Search returns results (graceful error message if API is down or script fails)
- Results are formatted as a readable table with abstract excerpts for top hits
- For literature reviews and synthesized reports, every cited paper has a resolved venue or an explicit `(preprint)` label — no entry shows only an arXiv/ePrint ID where a venue is expected
- If a script fails (missing deps, network error), report the error to the caller and continue with other layers

## Dependencies

```bash
pip install arxiv requests beautifulsoup4
```
