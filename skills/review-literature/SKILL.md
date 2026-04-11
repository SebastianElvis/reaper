---
name: review-literature
description: "Search for related academic work, download and read key papers, and produce a structured literature survey. Use when asked to find prior art, related papers, competing approaches, or known results for a crypto/distributed systems research topic."
user-invocable: true
argument-hint: "<research-goal>"
---

# Review Literature

Search for related academic work, download and deeply read the most important papers, and produce a structured literature survey organized by relationship to the research goal.

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

For each result found, assess relevance to the research goal. Classify each paper into one of two categories:

- **Same Goal**: work that shares the same or a similar research goal (same problem, competing solutions, prior attempts)
- **Same Approach**: work that applies a similar technique/approach to achieve a different goal (methodological relatives)

Within each category, assess relevance:
- **High**: directly addresses the same problem or proves a result we need / uses the exact technique in a way that informs our approach
- **Medium**: related technique, adjacent problem, or useful building block
- **Low**: tangentially related

Keep high and medium relevance results. Discard low unless it's a seminal work.

Prioritize results from: IACR ePrint, arXiv (cs.CR, cs.DC), CRYPTO, EUROCRYPT, ASIACRYPT, CCS, S&P, NDSS, PODC, DISC, STOC, FOCS.

### 7. Download and Read Key Papers

For all **high-relevance** papers (and medium-relevance papers that seem particularly important), download the PDF to the local workspace:

```bash
# arXiv papers
python skills/search-arxiv/search_arxiv.py download <arxiv_id> --output-dir reaper-workspace/papers

# IACR ePrint papers
python skills/search-iacr/search_iacr.py download <eprint_id> --output-dir reaper-workspace/papers
```

After downloading, **read each paper** using the Read tool (which can read PDFs). Do not just skim the abstract — understand the paper's internals:

- **Problem formulation**: What exactly is being solved? What are the formal definitions?
- **Techniques**: What proof techniques, constructions, or algorithms are used?
- **Key results**: What are the main theorems, lemmas, and their implications?
- **Assumptions and limitations**: What trust/system model? What doesn't the paper handle?
- **Relation to our goal**: How does this paper's approach or result specifically connect to our research goal?

For long papers, focus on the introduction, main results/theorems, key proofs, and conclusion. Read specific sections in more depth when they are directly relevant to the research goal.

Write a per-paper summary to `reaper-workspace/papers/<id>-notes.md` containing:
- One-paragraph summary of the paper's contribution
- Key definitions and theorems (stated precisely)
- Techniques used and why they work
- Limitations and open questions from the paper
- Specific relevance to our research goal

These notes serve as a durable reference for the investigate step.

### 8. Write Output

Write to `reaper-workspace/notes/literature.md`:

```markdown
# Literature Review

## Landscape Summary

[2-3 paragraphs summarizing the state of the art. What approaches exist? What's been proven? What's open? How does the paper under analysis fit into this landscape?]

## Same-Goal Works

Papers that address the same or a closely related research goal.

| # | Title | Authors | Year | Venue | Key Contribution | Relation to Our Goal | Local Path |
|---|-------|---------|------|-------|-----------------|---------------------|------------|
| 1 | ... | ... | ... | ... | [1-sentence] | [how this relates to our specific goal] | `papers/<filename>` |

## Same-Approach Works

Papers that apply similar techniques or approaches to different problems.

| # | Title | Authors | Year | Venue | Key Contribution | Shared Technique | Local Path |
|---|-------|---------|------|-------|-----------------|-----------------|------------|
| 1 | ... | ... | ... | ... | [1-sentence] | [what technique/approach we share and how they use it] | `papers/<filename>` |

## Citation Graph

[Summary of citation graph traversal findings. What are the foundational works this area builds on? What are the most active follow-up directions?]

## Key Prior Results

[Bullet list of the most important known results that constrain or inform our investigation. E.g., impossibility results, lower bounds, existing attacks. Include precise theorem statements where possible, referencing the per-paper notes.]

## Gaps Identified

[What hasn't been done? What combinations of assumptions/properties/techniques are unexplored? This feeds into formalize-problem.]

## Paper Index

Summary of all downloaded papers and their local paths for quick reference during investigation.

| Paper | Local PDF | Notes |
|-------|----------|-------|
| [Short title] | `papers/<filename>.pdf` | `papers/<id>-notes.md` |
```

### Graceful Degradation

If the Python search scripts fail (missing dependencies, network errors):
1. Log the failure to `reaper-workspace/log.md` with a timestamp and error message.
2. Fall back to WebSearch for all queries.
3. Note in `literature.md` that structured search was unavailable: `> **Note**: arXiv/ePrint API search was unavailable for this review. Results are from web search only.`

If PDF download fails for a paper, note it in the table (leave Local Path as "unavailable") and proceed with abstract-level understanding. The review must still meet quality criteria even in degraded mode.

### Quality Criteria

- At least 10 relevant works found (unless the area is very narrow)
- Results include papers from both arXiv and IACR ePrint (when the topic is crypto-related)
- Papers are split into same-goal and same-approach categories — both categories should have entries
- High-relevance papers are downloaded and read, with per-paper notes in `reaper-workspace/papers/`
- Per-paper notes contain precise theorem statements and technique descriptions, not just abstract-level summaries
- Citation graph section shows forward and backward citations for key papers
- Landscape summary gives a reader unfamiliar with the area a useful mental map
- Each related work has a specific relevance statement (not just "related to our topic")
- Gaps section identifies concrete unexplored directions, not vague "more work needed"
- No hallucinated papers — every entry must come from a real search result
