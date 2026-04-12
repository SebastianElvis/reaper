---
name: review-literature
description: "Search for related academic work, download and read key papers, and produce a structured literature survey. Use when asked to find prior art, related papers, competing approaches, or known results for a research topic."
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

**Context efficiency**: Do NOT pass the full `paper-summary.md` to each search subagent. Instead, extract the key search terms (topic, author names, 3-5 key concepts) and pass those as a brief JSON object (~100 words). Each subagent only needs the terms to formulate queries, not the full paper analysis.

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

#### Venue and Author Weighting

Weight results heavily toward top venues. A peer-reviewed top-conference paper is far more trustworthy than an unreviewed preprint. Consult `references/venue-tiers.md` for the domain-appropriate venue tier table and author weighting criteria.

When two papers make competing claims, prefer the one from the higher-tier venue by authors with more domain-specific expertise. When a preprint contradicts a published top-venue result, flag it but do not treat the preprint as authoritative without independent verification.

#### Relevance Assessment

Within each category (same-goal / same-approach), assess relevance:
- **High**: directly addresses the same problem or proves a result we need / uses the exact technique in a way that informs our approach
- **Medium**: related technique, adjacent problem, or useful building block
- **Low**: tangentially related

Keep high and medium relevance results. Discard low unless it's a seminal work or by a tier-1 venue / leading author in the area.

### 7. Download and Read Key Papers

For all **high-relevance** papers (and medium-relevance papers that seem particularly important), download the PDF to the local workspace:

```bash
# arXiv papers
python skills/search-arxiv/search_arxiv.py download <arxiv_id> --output-dir reaper-workspace/papers

# IACR ePrint papers
python skills/search-iacr/search_iacr.py download <eprint_id> --output-dir reaper-workspace/papers
```

After downloading, **read each paper** using the Read tool (which can read PDFs). Apply [Keshav's three-pass method](http://ccr.sigcomm.org/online/files/p83-keshavA.pdf) combined with [Stiller-Reeve's review structure](https://www.nature.com/articles/d41586-018-06991-0):

1. **First pass** — title, abstract, intro, headings, conclusions. Get the category, context, and claimed contributions. Stop here for low-relevance papers.
2. **Second pass** — grasp arguments, note key figures and theorems, skip proof details. Enough for medium-relevance papers.
3. **Third pass** (high-relevance only) — challenge assumptions, verify proof sketches, re-derive key results.

Write a per-paper summary to `reaper-workspace/papers/<id>-notes.md`:

- **Mirror**: Restate the paper's aims, results, and novelty in your own words (one paragraph).
- **Contribution**: What this paper advances over prior work and how.
- **Key results**: Main theorems, definitions, and techniques (stated precisely).
- **Strengths** (label major/minor): novelty, methodology fit, proof rigor, evaluation quality, clarity.
- **Weaknesses** (label major/minor/fatal): broken methodology, missing proofs, unjustified claims, unfair comparisons, unclear writing, overclaimed results.
- **Relevance to our research** — tag one or more: *problem definition*, *formalization*, *solution technique*, *negative result*, *literature/context*, *writing model*. One sentence per tag explaining how.

These notes serve as a durable reference for the investigate step.

### 8. Cross-Reference Verification

For each high-relevance downloaded paper, check whether the paper under analysis correctly cites and uses it:

- **Accuracy**: Does the paper under analysis state the prior result accurately? Compare the claim in the paper against the actual theorem statement in the cited work.
- **Model compatibility**: Are the assumptions of the cited result compatible with the current paper's model? A result proven under synchrony cannot be invoked in an asynchronous protocol without justification.
- **Comparison fairness**: If the paper claims to "extend," "improve," or "generalize" a prior result, is the comparison apples-to-apples? (Same model, same properties, same adversary class.)
- **Version drift**: Is the paper citing the latest version of a result, or has the cited work been updated/corrected since?

Document any discrepancies in the per-paper notes (`<id>-notes.md`) under a `### Discrepancies with Paper Under Analysis` heading. Summarize all discrepancies in the `## Gaps Identified` section of the output file — these are high-priority inputs for the formalize-problem step.

### 9. Write Output

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
- Per-paper notes contain mirror, contribution, key results, strengths/weaknesses, and relevance tags — not just abstract-level summaries
- Citation graph section shows forward and backward citations for key papers
- Landscape summary gives a reader unfamiliar with the area a useful mental map
- Each related work has a specific relevance statement (not just "related to our topic")
- Gaps section identifies concrete unexplored directions, not vague "more work needed"
- No hallucinated papers — every entry must come from a real search result
