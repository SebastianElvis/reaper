# Search Tools Reference

Reaper uses the `/search-paper` skill for all academic paper search, citation graph traversal, and publication-venue resolution. The skill ships five Python scripts under one directory; this document catalogs them and shows the common workflows.


## Scripts

### `arxiv.py` — arXiv preprint server

**Location**: `../../search-paper/arxiv.py`
**Dependencies**: `pip install arxiv`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `search "<query>"` | Find papers by topic (sorted by relevance) | `--max-results N`, `--categories cs.CR,cs.DC` |
| `recent ["<query>"]` | Get recently submitted papers (sorted by date) | `--max-results N`, `--categories cs.CR` |
| `download <arxiv_id>` | Download paper PDF | `--output-dir DIR` |
| `journal-ref <arxiv_id>` | Read author-supplied venue field | — |

**When to use**: Broad CS topics (distributed systems, complexity theory, algorithms), papers that appear on arXiv.

**Output**: JSON to stdout. Search returns array of `{arxiv_id, title, authors, year, abstract, categories, pdf_url, published, journal_ref}`.

**Categories for crypto/distributed systems**:
- `cs.CR` — Cryptography and Security
- `cs.DC` — Distributed, Parallel, and Cluster Computing
- `cs.DS` — Data Structures and Algorithms
- `cs.CC` — Computational Complexity

### `iacr.py` — IACR ePrint archive

**Location**: `../../search-paper/iacr.py`
**Dependencies**: `pip install requests beautifulsoup4`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `search "<query>"` | Find papers by topic | `--max-results N` |
| `recent` | Get latest ePrint papers | `--max-results N` |
| `download <eprint_id>` | Download paper PDF | `--output-dir DIR` |
| `url <eprint_id>` | Get paper URL | — |
| `pubinfo <eprint_id>` | Read "Publication info" line (venue) | — |

**When to use**: Cryptography and security topics. IACR ePrint is the primary preprint server for cryptography. Top 5 search results are automatically enriched with metadata (title, authors, abstract, publication_info) from the paper page.

**Output**: JSON to stdout. Search returns array of `{eprint_id, title, authors, year, abstract, publication_info, venue, pdf_url, url}`. ePrint IDs are in `YYYY/NNNN` format.

### `semantic_scholar.py` — Semantic Scholar metadata

**Location**: `../../search-paper/semantic_scholar.py`
**Dependencies**: `pip install requests`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `venue --arxiv <id>` | Look up venue by arXiv ID | — |
| `venue --title "<title>"` | Look up venue by title | `--author "<surname>"` |
| `citations <arxiv_id>` | Forward + backward citations | `--max-results N` |

**When to use**: Citation graph traversal (any paper with an arXiv ID). Primary venue resolver — Semantic Scholar covers the most papers.

**Output**: JSON to stdout. `venue` returns `{found, venue, venue_full, venue_type, year, title, authors}`. `citations` returns `{arxiv_id, references, citations}` with each entry including `venue` when known.

### `dblp.py` — DBLP metadata

**Location**: `../../search-paper/dblp.py`
**Dependencies**: `pip install requests`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `venue "<title>"` | Look up venue by title | `--author "<surname>"` |

**When to use**: Authoritative for CS conference and journal venues. Use as the title-based fallback when Semantic Scholar fails.

### `openalex.py` — OpenAlex metadata

**Location**: `../../search-paper/openalex.py`
**Dependencies**: `pip install requests`

| Command | Purpose | Key Parameters |
|---------|---------|---------------|
| `venue "<title>"` | Look up venue by title | — |

**When to use**: Broad coverage beyond CS (non-CS journals, niche workshops, books). Final fallback before labeling a paper as preprint-only.

### WebSearch (built-in)

**When to use as fallback**:
- Conference proceedings not on arXiv/ePrint (some PODC/DISC/STOC/FOCS proceedings)
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
├── Have arXiv ID → use semantic_scholar.py citations
└── No arXiv ID  → use WebSearch for "cited by" / "references"

Need very recent papers?
└── Use iacr.py recent + arxiv.py recent (both sort by submission date)

Need to resolve a paper's publication venue?
└── Follow the layered Venue Resolution Protocol below.
```

## Venue Resolution Protocol

Every paper that appears in `notes/literature.md` or the `## References` section of `report.md` must have a real publication venue (CRYPTO, S&P, PODC, …) — not just an archive ID.

The authoritative layered protocol lives in the `/search-paper` skill's own `SKILL.md` ("Venue Resolution Protocol" section). At a glance, it walks Semantic Scholar → author-supplied field (arXiv `journal-ref` / ePrint `pubinfo`) → DBLP → OpenAlex, stopping at the first success, and labels the paper `(preprint)` if all layers fail. Callers should invoke `/search-paper` rather than orchestrating the layers themselves, and cache the resolved venue in their workspace notes to avoid re-resolving across cycles.

## Common Workflow Patterns

### Full Literature Review

1. **Parallel search**: Spawn 3 subagents
   - Subagent 1: `arxiv.py search` with 3-4 diverse queries
   - Subagent 2: `iacr.py search` with 3-4 diverse queries
   - Subagent 3: WebSearch for non-academic sources
2. **Merge and deduplicate** results across all sources
3. **Citation graph**: For seed paper + top 3 results, run `semantic_scholar.py citations`
4. **Recent check**: `iacr.py recent` to catch very new papers
5. **Filter and prioritize** by relevance
6. **Resolve venue** for every kept paper using the layered protocol above

### Mid-Investigation Literature Search

1. Run a focused query on the specific question that arose:
   ```bash
   python3 ../../search-paper/iacr.py search "exact technical question" --max-results 5
   python3 ../../search-paper/arxiv.py search "exact technical question" --max-results 5
   ```
2. If a highly relevant paper is found, download and read it:
   ```bash
   python3 ../../search-paper/arxiv.py download <id> --output-dir reaper-workspace/papers/
   ```
3. Resolve its venue via the layered protocol; integrate findings into `literature.md` inline (add to appropriate existing sections)

### Citation Chasing

1. Start with a known paper's arXiv ID
2. Get references (backward) and citations (forward):
   ```bash
   python3 ../../search-paper/semantic_scholar.py citations 2305.12345 --max-results 20
   ```
3. For each highly relevant citation, recursively chase (1-2 hops max)

## Rate Limits and Reliability

- **arXiv API**: No authentication needed. Recommended: ≤1 request/second. The `arxiv` Python package handles rate limiting.
- **IACR ePrint**: No documented rate limits. Scrapes HTML, may break if the site redesigns. Top 5 search results fetch individual paper pages (5 additional requests per search).
- **Semantic Scholar**: Free tier allows 100 requests / 5 minutes without API key. Sufficient for citation graph traversal and the bulk of venue lookups.
- **DBLP**: No documented hard limits, but be polite — at most a few requests per second.
- **OpenAlex**: Free, no auth needed. Consider passing `mailto=<your-email>` as a parameter to enter the polite pool with higher limits.
- **Graceful degradation**: All skills that use these tools must fall back to WebSearch if scripts fail.
