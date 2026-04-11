---
name: review-literature
description: "Search for related academic work and produce a structured literature survey. Use when asked to find prior art, related papers, competing approaches, or known results for a crypto/distributed systems research topic."
user-invocable: true
argument-hint: "<research-goal>"
---

# Review Literature

Search for related academic work and produce a structured literature survey.

## Usage

```
/reaper:review-literature "post-quantum threshold signatures"
```

## Instructions

### 1. Gather Context

Read `reaper-workspace/notes/paper-summary.md` if it exists. Extract:
- Key technical terms and concepts
- Author names (to find their other work)
- Cited works mentioned in the introduction
- The specific problem domain

Combine with the research goal to formulate search queries.

### 2. Search — Structured Sources (Primary)

Use the search scripts via Bash to query arXiv and IACR ePrint. Generate multiple diverse queries per source.

**arXiv** (broad CS/math — use for distributed systems, complexity, general crypto):

```bash
python skills/search-arxiv/search_arxiv.py search "<query>" --max-results 10 --categories cs.CR,cs.DC
```

**IACR ePrint** (cryptography-specific — use for all crypto topics):

```bash
python skills/search-iacr/search_iacr.py search "<query>" --max-results 10
```

**Query types** (generate at least one query per type, per source):

- **Direct**: the exact problem (e.g., "BFT consensus communication complexity lower bound")
- **Author-based**: key authors in the area (e.g., "Yin Malkhi Abraham consensus")
- **Technique-based**: the proof/construction technique (e.g., "simulation-based security threshold signatures")
- **Problem variants**: related problems (e.g., "asynchronous Byzantine agreement", "partial synchrony consensus")
- **Attacks/impossibilities**: known negative results (e.g., "FLP impossibility", "DLS lower bound")
- **Surveys**: SoK papers, systematization of knowledge (e.g., "SoK blockchain consensus")

**Spawn parallel subagents** (using the Agent tool) for concurrent search:
- **Subagent 1**: arXiv searches (multiple queries with different categories)
- **Subagent 2**: IACR ePrint searches (multiple queries)
- **Subagent 3**: WebSearch fallback (see step 3)

Each subagent runs its searches and returns structured JSON results.

### 3. Search — WebSearch (Fallback)

Use WebSearch for results that structured APIs may miss:
- Conference proceedings not on arXiv/ePrint (PODC, DISC, STOC, FOCS)
- Blog posts, talks, and informal results
- Author homepages with preprints

This runs as a parallel subagent alongside the structured searches.

### 4. Citation Graph Traversal

For the **seed paper** (from `paper-summary.md`) and the **top 3 most relevant results**, trace citations:

```bash
python skills/search-arxiv/search_arxiv.py citations <arxiv_id> --max-results 20
```

This returns both:
- **References** (backward): what this paper builds on — find foundational results
- **Citations** (forward): who cites this paper — find follow-up improvements, attacks, corrections

Deduplicate results across all search sources.

**Note**: Citation graph requires an arXiv ID. For ePrint-only papers, use WebSearch to find citing works.

### 5. Recent Papers Check

For fast-moving areas, check for very recent publications:

```bash
python skills/search-iacr/search_iacr.py recent --max-results 10
```

Scan titles/abstracts for relevance to the research goal. Include any relevant recent papers that the main search may have missed.

### 6. Filter and Prioritize

For each result found, assess relevance to the research goal:
- **High**: directly addresses the same problem or proves a result we need
- **Medium**: related technique, adjacent problem, or useful building block
- **Low**: tangentially related, different domain but similar approach

Keep high and medium relevance results. Discard low unless it's a seminal work.

Prioritize results from: IACR ePrint, arXiv (cs.CR, cs.DC), CRYPTO, EUROCRYPT, ASIACRYPT, CCS, S&P, NDSS, PODC, DISC, STOC, FOCS.

### 7. Write Output

Write to `reaper-workspace/notes/literature.md`:

```markdown
# Literature Review

## Landscape Summary

[2-3 paragraphs summarizing the state of the art. What approaches exist? What's been proven? What's open? How does the paper under analysis fit into this landscape?]

## Related Works

| # | Title | Authors | Year | Venue | Key Contribution | Relevance |
|---|-------|---------|------|-------|-----------------|-----------|
| 1 | ... | ... | ... | ... | [1-sentence] | [1-sentence explaining why this matters for our goal] |
| 2 | ... | ... | ... | ... | ... | ... |

## Citation Graph

[Summary of citation graph traversal findings. What are the foundational works this area builds on? What are the most active follow-up directions?]

## Key Prior Results

[Bullet list of the most important known results that constrain or inform our investigation. E.g., impossibility results, lower bounds, existing attacks.]

## Gaps Identified

[What hasn't been done? What combinations of assumptions/properties/techniques are unexplored? This feeds into formalize-problem.]
```

### Graceful Degradation

If the Python search scripts fail (missing dependencies, network errors):
1. Log the failure to `reaper-workspace/log.md` with a timestamp and error message.
2. Fall back to WebSearch for all queries.
3. Note in `literature.md` that structured search was unavailable: `> **Note**: arXiv/ePrint API search was unavailable for this review. Results are from web search only.`

The literature review must still meet quality criteria even in fallback mode.

### Quality Criteria

- At least 10 relevant works found (unless the area is very narrow)
- Results include papers from both arXiv and IACR ePrint (when the topic is crypto-related)
- Citation graph section shows forward and backward citations for key papers
- Landscape summary gives a reader unfamiliar with the area a useful mental map
- Each related work has a specific relevance statement (not just "related to our topic")
- Gaps section identifies concrete unexplored directions, not vague "more work needed"
- No hallucinated papers — every entry must come from a real search result
