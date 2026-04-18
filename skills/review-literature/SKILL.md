---
name: review-literature
description: "Search for related academic work, download and read key papers, and produce a structured literature survey. Use when asked to find prior art, related papers, competing approaches, or known results for a research topic."
user-invocable: true
argument-hint: "<research-goal>"
---

# Review Literature

Search for related academic work, download and deeply read the most important papers, and produce a structured literature survey organized by relationship to the research goal.

## Usage

Invoke this skill by name with the research topic as a quoted string. On slash-command hosts, prefix with `/` (e.g. `/review-literature "<topic>"`).

```
review-literature "post-quantum threshold signatures"
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

Delegate all paper search to the `/search-paper` skill. It decides which archives to hit (arXiv, IACR ePrint, …), which categories or filters apply for the topic, and returns structured results the caller can merge. The caller's job is to supply good queries, not pick archives.

**Query types** (generate at least one query per type):

- **Direct**: the exact problem (e.g., "BFT consensus communication complexity lower bound")
- **Author-based**: key authors in the area (e.g., "Yin Malkhi Abraham consensus")
- **Technique-based**: the proof/construction technique (e.g., "simulation-based security threshold signatures")
- **Problem variants**: related problems (e.g., "asynchronous Byzantine agreement", "partial synchrony consensus")
- **Attacks/impossibilities**: known negative results (e.g., "FLP impossibility", "DLS lower bound")
- **Surveys**: SoK papers, systematization of knowledge (e.g., "SoK blockchain consensus")

**Spawn parallel subagents** (using your host's parallel-spawn primitive — e.g. Claude Code's `Agent` tool — or run sequentially if unavailable) for concurrent search — one subagent per query type, each invoking `/search-paper`. Run the WebSearch fallback (step 3) as an additional parallel subagent.

**Context efficiency**: Do NOT pass the full `paper-summary.md` to each search subagent. Instead, extract the key search terms (topic, author names, 3-5 key concepts) and pass those as a brief JSON object (~100 words). Each subagent only needs the terms to formulate queries, not the full paper analysis.

Each subagent runs its searches and returns structured JSON results.

### 3. Search — WebSearch (Fallback)

Use WebSearch for results that structured APIs may miss:
- Conference proceedings not on arXiv/ePrint (PODC, DISC, STOC, FOCS)
- Blog posts, talks, and informal results
- Author homepages with preprints

This runs as a parallel subagent alongside the structured searches.

### 4. Citation Graph Traversal

For the **seed paper** (from `paper-summary.md`) and the **top 3 most relevant results**, invoke the `/search-paper` skill to traverse the citation graph (pass the arXiv ID and request up to 20 citations in each direction — forward and backward).

This returns both:
- **References** (backward): what this paper builds on — find foundational results
- **Citations** (forward): who cites this paper — find follow-up improvements, attacks, corrections

Deduplicate results across all search sources.

**Note**: Citation graph requires an arXiv ID. For ePrint-only papers, use WebSearch to find citing works.

### 5. Recent Papers Check

For fast-moving areas, invoke the `/search-paper` skill to pull the most-recently-posted papers in the area (e.g. top 10). Scan titles/abstracts for relevance to the research goal and include any relevant recent papers that the main search may have missed.

### 6. Filter and Prioritize

For each result found, assess relevance to the research goal. Classify each paper into one of two categories:

- **Same Goal**: work that shares the same or a similar research goal (same problem, competing solutions, prior attempts)
- **Same Approach**: work that applies a similar technique/approach to achieve a different goal (methodological relatives)

#### Venue and Author Weighting

Weight results heavily toward top venues. A peer-reviewed top-conference paper is far more trustworthy than an unreviewed preprint. Consult the `/reaper` skill's `references/venue-tiers.md` for the domain-appropriate venue tier table and author weighting criteria.

When two papers make competing claims, prefer the one from the higher-tier venue by authors with more domain-specific expertise. When a preprint contradicts a published top-venue result, flag it but do not treat the preprint as authoritative without independent verification.

#### Relevance Assessment

Within each category (same-goal / same-approach), assess relevance:
- **High**: directly addresses the same problem or proves a result we need / uses the exact technique in a way that informs our approach
- **Medium**: related technique, adjacent problem, or useful building block
- **Low**: tangentially related

Keep high and medium relevance results. Discard low unless it's a seminal work or by a tier-1 venue / leading author in the area.

### 7. Resolve Publication Venues

For every kept paper, resolve the actual publication venue (CRYPTO, S&P, PODC, …) — an arXiv or ePrint ID is not a venue. **Invoke the `/search-paper` skill's Venue Resolution Protocol** with the best identifier available — arXiv ID preferred, else ePrint ID, else title plus first-author surname. `/search-paper` walks the layered Semantic Scholar → author-supplied field → DBLP → OpenAlex ladder and returns either a resolved venue or the explicit `(preprint)` label.

Record the resolved venue inline in your scratch notes so downstream steps and re-runs don't repeat the work. Never guess a venue from topic or affiliation — if `/search-paper` returns `(preprint)`, use that label verbatim.

**Spawn parallel subagents** (one per kept paper, using your host's parallel-spawn primitive) to resolve venues concurrently — each lookup is independent.

### 8. Download and Analyze Key Papers

For all **high-relevance** papers (and medium-relevance papers that seem particularly important), invoke the `/search-paper` skill to download each PDF into `reaper-workspace/papers/` (pass the arXiv ID or ePrint ID).

After downloading, **delegate paper reading to `/analyze-paper`**. For each downloaded paper, invoke the `/analyze-paper` skill with:

```
reaper-workspace/papers/<filename>.pdf --goal "<research-goal>" --output reaper-workspace/papers/<id>-notes.md
```

(On Claude Code: `/analyze-paper <args>`. On other agents: invoke by skill name with the same arguments.)

**Spawn parallel subagents** (using your host's parallel-spawn primitive — e.g. Claude Code's `Agent` tool — or run sequentially if unavailable) to analyze multiple papers concurrently — each paper is independent.

The `/analyze-paper` skill handles the multi-pass reading (calibrating depth by relevance to the goal) and writes per-paper notes to `reaper-workspace/papers/<id>-notes.md`. Passing `--goal` ensures the output includes a relevance assessment.

These notes serve as a durable reference for the investigate step. They are evolving files — update inline if revisited during mid-investigation search.

### 9. Cross-Reference Verification

Using the per-paper notes produced by `/analyze-paper` in the previous step, check whether the paper under analysis correctly cites and uses each high-relevance work:

- **Accuracy**: Does the paper under analysis state the prior result accurately? Compare the claim in the paper against the actual theorem statement in the cited work.
- **Model compatibility**: Are the assumptions of the cited result compatible with the current paper's model? A result proven under synchrony cannot be invoked in an asynchronous protocol without justification.
- **Comparison fairness**: If the paper claims to "extend," "improve," or "generalize" a prior result, is the comparison apples-to-apples? (Same model, same properties, same adversary class.)
- **Version drift**: Is the paper citing the latest version of a result, or has the cited work been updated/corrected since?

Document any discrepancies in the per-paper notes (`<id>-notes.md`) under a `### Discrepancies with Paper Under Analysis` heading. Summarize all discrepancies in the `## Gaps Identified` section of the output file — these are high-priority inputs for the formalize-problem step.

### 10. Write Output

Write to `reaper-workspace/notes/literature.md`:

```markdown
# Literature Review

## Landscape Summary

[2-3 paragraphs summarizing the state of the art. What approaches exist? What's been proven? What's open? How does the paper under analysis fit into this landscape?]

## Same-Goal Works

Papers that address the same or a closely related research goal.

| # | Title | Authors | Year | Venue | Key Contribution | Relation to Our Goal | Link | Local Path |
|---|-------|---------|------|-------|-----------------|---------------------|------|------------|
| 1 | ... | ... | ... | CRYPTO 2023 *or* `(preprint)` | [1-sentence] | [how this relates to our specific goal] | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) or [ePrint](https://eprint.iacr.org/YYYY/NNNN) | `papers/<filename>` |

The `Venue` column holds the resolved publication venue from Step 7 — never the archive ID. Use `(preprint)` only when `/search-paper` returned no venue.

## Same-Approach Works

Papers that apply similar techniques or approaches to different problems.

| # | Title | Authors | Year | Venue | Key Contribution | Shared Technique | Link | Local Path |
|---|-------|---------|------|-------|-----------------|-----------------|------|------------|
| 1 | ... | ... | ... | CRYPTO 2023 *or* `(preprint)` | [1-sentence] | [what technique/approach we share and how they use it] | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) or [ePrint](https://eprint.iacr.org/YYYY/NNNN) | `papers/<filename>` |

## Citation Graph

[Summary of citation graph traversal findings. What are the foundational works this area builds on? What are the most active follow-up directions?]

## Key Prior Results

[Bullet list of the most important known results that constrain or inform our investigation. E.g., impossibility results, lower bounds, existing attacks. Include precise theorem statements where possible, referencing the per-paper notes.]

## Gaps Identified

[What hasn't been done? What combinations of assumptions/properties/techniques are unexplored? This feeds into formalize-problem.]

## Paper Index

Summary of all downloaded papers and their local paths for quick reference during investigation.

| Paper | Link | Local PDF | Notes |
|-------|------|----------|-------|
| [Short title] | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) or [ePrint](https://eprint.iacr.org/YYYY/NNNN) | `papers/<filename>.pdf` | `papers/<id>-notes.md` |
```

### Graceful Degradation

`/search-paper` can fail at any step independently (search, citation graph, venue resolution, download). Apply the right fallback per step:

- **Search fails entirely** (all queries error out): fall back to WebSearch for all queries and add a top-of-file note to `literature.md`: `> **Note**: structured paper search via /search-paper was unavailable for this review (error: ...). Results are from web search only.`
- **Citation graph fails** (step 4): skip the Citation Graph section or populate it from WebSearch; annotate each affected paper's row: "citation graph unavailable".
- **Venue resolution fails** for a specific paper (step 7): label that paper `(preprint)` in the `Venue` column rather than blocking the review.
- **Download fails** for a specific paper (step 8): leave `Local Path` as "unavailable" and proceed with abstract-level understanding for that paper.

In every case, the review still proceeds. Only the quality criteria that depend on the failed step are relaxed (see Quality Criteria below).

### Quality Criteria

**Content criteria (always required):**
- At least 10 relevant works found (unless the area is very narrow)
- Papers are split into same-goal and same-approach categories — both categories should have entries
- High-relevance papers are downloaded (when `/search-paper` download succeeds) and analyzed via `analyze-paper --goal`, with per-paper notes in `reaper-workspace/papers/`
- Per-paper notes (produced by `/analyze-paper`) contain structured analysis with key results, strengths/weaknesses, and relevance assessment — not just abstract-level summaries
- **Every entry in the Venue column is a real publication venue (e.g., CRYPTO 2023, S&P 2024) or the explicit `(preprint)` label** — never just an arXiv/ePrint ID
- Landscape summary gives a reader unfamiliar with the area a useful mental map
- Each related work has a specific relevance statement (not just "related to our topic")
- Gaps section identifies concrete unexplored directions, not vague "more work needed"
- No hallucinated papers — every entry must come from a real search result

**Normal-mode criteria (required unless explicitly degraded):**
- Results draw from multiple structured sources via `/search-paper` (not WebSearch alone) — waived when the `/search-paper` availability note is present
- Citation graph section shows forward and backward citations for key papers — waived when step 4 is marked unavailable
