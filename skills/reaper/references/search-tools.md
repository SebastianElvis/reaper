# Search Tools Reference

Reaper uses Python scripts to search academic paper archives. This document catalogs the available tools, when to use each, and common workflow patterns.

## Tools

### search_arxiv.py

**Location**: `skills/search-arxiv/search_arxiv.py`
**Dependencies**: `pip install arxiv requests`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `search "<query>"` | Find papers by topic | `--max-results N`, `--categories cs.CR,cs.DC` |
| `download <arxiv_id>` | Download paper PDF | `--output-dir DIR` |
| `citations <arxiv_id>` | Forward + backward citations via Semantic Scholar | `--max-results N` |

**When to use**: Broad CS topics (distributed systems, complexity theory, algorithms), papers that appear on arXiv. Also use `citations` for any paper with an arXiv ID regardless of primary venue.

**Output**: JSON to stdout. Search returns array of `{arxiv_id, title, authors, year, abstract, categories, pdf_url, published}`. Citations returns `{references: [...], citations: [...]}`.

**Categories for crypto/distributed systems**:
- `cs.CR` — Cryptography and Security
- `cs.DC` — Distributed, Parallel, and Cluster Computing
- `cs.DS` — Data Structures and Algorithms
- `cs.CC` — Computational Complexity

### search_iacr.py

**Location**: `skills/search-iacr/search_iacr.py`
**Dependencies**: `pip install requests beautifulsoup4`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `search "<query>"` | Find papers by topic | `--max-results N` |
| `recent` | Get latest ePrint papers | `--max-results N` |
| `download <eprint_id>` | Download paper PDF | `--output-dir DIR` |
| `url <eprint_id>` | Get paper URL | — |

**When to use**: Cryptography and security topics. IACR ePrint is the primary preprint server for cryptography — use this for all crypto-related searches. Top 5 search results are automatically enriched with metadata (title, authors, abstract) from the paper page.

**Output**: JSON to stdout. Search returns array of `{eprint_id, title, authors, year, abstract, pdf_url, url}`. ePrint IDs are in `YYYY/NNNN` format.

### WebSearch (built-in)

**When to use as fallback**:
- Conference proceedings not on arXiv/ePrint (PODC, DISC, STOC, FOCS proceedings)
- Blog posts, talks, informal write-ups
- Author homepages with preprints
- When Python scripts fail (missing deps, network issues)

## Decision Tree

```
Is the topic cryptography/security?
├── Yes → Search BOTH arXiv (cs.CR) AND ePrint
│         Use ePrint for crypto-specific terms
│         Use arXiv for cross-domain terms
└── No  → Search arXiv only
          Use cs.DC for distributed systems
          Use cs.DS/cs.CC for algorithms/complexity

Always supplement with WebSearch for non-academic sources.

Need citation context?
├── Have arXiv ID → use search_arxiv.py citations
└── No arXiv ID  → use WebSearch for "cited by" / "references"

Need very recent papers?
└── Use search_iacr.py recent + arXiv search sorted by date
```

## Common Workflow Patterns

### Full Literature Review

1. **Parallel search**: Spawn 3 subagents
   - Subagent 1: `search_arxiv.py search` with 3-4 diverse queries
   - Subagent 2: `search_iacr.py search` with 3-4 diverse queries
   - Subagent 3: WebSearch for non-academic sources
2. **Merge and deduplicate** results across all sources
3. **Citation graph**: For seed paper + top 3 results, run `search_arxiv.py citations`
4. **Recent check**: `search_iacr.py recent` to catch very new papers
5. **Filter and prioritize** by relevance

### Mid-Investigation Literature Search

1. Run a focused query on the specific question that arose:
   ```bash
   python skills/search-iacr/search_iacr.py search "exact technical question" --max-results 5
   python skills/search-arxiv/search_arxiv.py search "exact technical question" --max-results 5
   ```
2. If a highly relevant paper is found, download and read it:
   ```bash
   python skills/search-arxiv/search_arxiv.py download <id> --output-dir reaper-workspace/papers/
   ```
3. Append findings to `literature.md` under `## Mid-Investigation Additions`

### Citation Chasing

1. Start with a known paper's arXiv ID
2. Get references (backward) and citations (forward):
   ```bash
   python skills/search-arxiv/search_arxiv.py citations 2305.12345 --max-results 20
   ```
3. For each highly relevant citation, recursively chase (1-2 hops max)

## Rate Limits and Reliability

- **arXiv API**: No authentication needed. Recommended: ≤1 request/second. The `arxiv` Python package handles rate limiting.
- **IACR ePrint**: No documented rate limits. Scrapes HTML search results, so may break if the site redesigns. Top 5 results fetch individual paper pages (5 additional requests).
- **Semantic Scholar** (used by `citations`): Free tier allows 100 requests/5 minutes without API key. Sufficient for citation graph traversal.
- **Graceful degradation**: All skills that use these tools must fall back to WebSearch if scripts fail.
