---
name: search-iacr
description: "Search IACR ePrint archive for cryptography papers, get recent papers, and download PDFs. Use when you need to find cryptography/security papers on ePrint, check recent publications, or download a specific ePrint paper."
user-invocable: true
argument-hint: "<query> [--max-results N]"
---

# Search IACR ePrint

Search the IACR Cryptology ePrint Archive for cryptography and security papers.

## Usage

```
/search-iacr "threshold signatures" --max-results 15
```

## Commands

This skill wraps `skills/search-iacr/search_iacr.py`. Run commands via Bash.

### Search

```bash
python skills/search-iacr/search_iacr.py search "post-quantum threshold signatures" --max-results 10
```

Returns JSON array of papers: `eprint_id`, `title`, `authors`, `year`, `abstract` (for top 5), `pdf_url`, `url`. Top 5 results are enriched with metadata from the paper page.

### Recent Papers

```bash
python skills/search-iacr/search_iacr.py recent --max-results 10
```

Returns the most recently published ePrint papers.

### Download

```bash
python skills/search-iacr/search_iacr.py download 2024/1234 --output-dir reaper-workspace/papers/
```

Downloads the paper PDF. Returns JSON with `path` and `eprint_id`.

### Get URL

```bash
python skills/search-iacr/search_iacr.py url 2024/1234
```

Returns JSON with `url` and `pdf_url` for the paper.

## Role

- **Standalone**: Invoked directly by the user to search for papers.
- **Building block**: Called by `review-literature` and `investigate` via the underlying Python script.

## Instructions

When invoked directly:

1. Parse the user's query and any flags from the argument.
2. Run the search command via Bash.
3. Format the results as a readable table:

```markdown
| # | Title | Authors | Year | ePrint ID |
|---|-------|---------|------|-----------|
| 1 | ... | ... | ... | ... |
```

4. For enriched results (top 5), show the abstract excerpt.

## Quality Criteria

- Search returns results (graceful error message if API is down or script fails)
- Results are formatted as a readable table with abstract excerpts for enriched hits
- If the script fails (missing deps, network error), report the error to the caller

## Dependencies

Requires `requests` and `beautifulsoup4` Python packages:

```bash
pip install requests beautifulsoup4
```
