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

### 2. Search

Use WebSearch to find related work. Generate multiple diverse queries:

- **Direct**: the exact problem (e.g., "BFT consensus communication complexity lower bound")
- **Author-based**: key authors in the area (e.g., "Yin Malkhi Abraham consensus")
- **Technique-based**: the proof/construction technique (e.g., "simulation-based security threshold signatures")
- **Problem variants**: related problems (e.g., "asynchronous Byzantine agreement", "partial synchrony consensus")
- **Attacks/impossibilities**: known negative results (e.g., "FLP impossibility", "DLS lower bound")
- **Surveys**: SoK papers, systematization of knowledge (e.g., "SoK blockchain consensus")

**Spawn parallel subagents** (using the Agent tool) for different search queries to maximize coverage. Each subagent runs a few searches and returns structured results.

### 3. Filter and Prioritize

For each result found, assess relevance to the research goal:
- **High**: directly addresses the same problem or proves a result we need
- **Medium**: related technique, adjacent problem, or useful building block
- **Low**: tangentially related, different domain but similar approach

Keep high and medium relevance results. Discard low unless it's a seminal work.

Prioritize results from: IACR ePrint, arXiv (cs.CR, cs.DC), CRYPTO, EUROCRYPT, ASIACRYPT, CCS, S&P, NDSS, PODC, DISC, STOC, FOCS.

### 4. Write Output

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

## Key Prior Results

[Bullet list of the most important known results that constrain or inform our investigation. E.g., impossibility results, lower bounds, existing attacks.]

## Gaps Identified

[What hasn't been done? What combinations of assumptions/properties/techniques are unexplored? This feeds into formalize-problem.]
```

### Quality Criteria

- At least 10 relevant works found (unless the area is very narrow)
- Landscape summary gives a reader unfamiliar with the area a useful mental map
- Each related work has a specific relevance statement (not just "related to our topic")
- Gaps section identifies concrete unexplored directions, not vague "more work needed"
- No hallucinated papers — every entry must come from a real search result
