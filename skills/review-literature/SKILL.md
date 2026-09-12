---
name: review-literature
description: "This skill searches and reads related academic work. You use it to find prior results, related papers, or competing approaches."
user-invocable: true
argument-hint: "<research-goal>"
license: Apache-2.0
compatibility: "This skill requires the search-paper skill and internet access. The host should support PDF reading."
---

# Review Literature

You must read and apply `references/language.md` from the installed `reaper` skill before you write any output.

## Usage

You invoke this skill by name with a quoted topic. Slash-command hosts use `/review-literature "<topic>"`.

```
review-literature "post-quantum threshold signatures"
```

## Instructions

### 1. Gather Context

You read `reaper-workspace/notes/paper-summary.md` if it exists. You extract technical terms, authors, cited works, and the research domain. You combine these details with the research goal to create queries.

### 2. Search Structured Sources

You invoke the `search-paper` skill for all paper searches. The `/search-paper` skill selects archives, categories, and filters. You supply at least one query for each primary search target. You assign each query to one target:

- **Direct:** The query names the exact problem without an author, technique, negative-result, or survey filter.
- **Author:** The query names key authors and the topic.
- **Technique:** The query names the proof or construction technique.
- **Variants:** The query changes the direct query to a related problem or different assumption.
- **Negative results:** The query names attacks, impossibility results, or lower bounds.
- **Surveys:** The query requests surveys or systematization of knowledge papers.

You start one parallel subagent per query type if the host supports subagents. Each subagent invokes the `search-paper` skill and returns structured JSON. You start the web search in Step 3 as another parallel subagent.
If the host cannot run subagents, you run the searches in sequence.

You give each subagent a small JSON object of about 100 words. The object contains the topic, authors, and 3-5 key concepts. You do not send the full paper summary.

### 3. Search the Web as a Fallback

You use web search for results that structured APIs can miss:

- Conference proceedings outside arXiv and ePrint.
- Blog posts and talks that do not duplicate a paper entry.
- Preprints on author websites that do not duplicate a proceedings entry.

### 4. Trace Citations

You invoke the `search-paper` skill for the seed paper and the three most relevant results. You supply each arXiv ID and request up to 20 citations in each direction. Backward citations identify earlier results that the paper uses.
Forward citations identify later improvements, attacks, or corrections. You remove duplicate results across sources. For papers without an arXiv ID, you use web search to find citing works.

### 5. Check Recent Papers

For an area with rapid changes, you invoke the `search-paper` skill for the ten newest papers. You check titles and abstracts. You include relevant recent results that the earlier searches missed.

### 6. Filter and Rank Results

You put each paper in one of two categories:

- **Same Goal:** The paper addresses the same or a similar problem.
- **Same Approach:** The paper uses a similar technique for another problem.

You use `references/venue-tiers.md` from the `reaper` skill for venue and author criteria. For conflicting claims, you prefer reviewed papers from leading venues and authors with domain experience. You flag conflicting preprints and verify them independently.

You assign relevance within each category:

- **High:** The paper addresses the target problem or supplies a result or technique that the research needs.
- **Medium:** The paper supplies related context or a useful component but does not meet High criteria.
- **Low:** The paper has an indirect relation that meets neither High nor Medium criteria.

You keep high and medium relevance papers. You keep low relevance papers only for a foundational result, a tier-1 venue, or a leading author.

### 7. Resolve Publication Venues

You invoke the `search-paper` skill's Venue Resolution Protocol for each kept paper. You prefer an arXiv ID, then an ePrint ID, then a title with the first author's surname. You save the returned venue or `(preprint)` in workspace notes.
You do not infer a venue from a topic or institution. You use one parallel subagent per paper if the host supports it.

### 8. Download and Analyze Papers

You invoke the `search-paper` skill to download papers with high relevance to `reaper-workspace/papers/`. You also download important papers with medium relevance. You supply an arXiv or ePrint ID. For each downloaded PDF, you invoke the `analyze-paper` skill with these arguments:

```
reaper-workspace/papers/<filename>.pdf --goal "<research-goal>" --output reaper-workspace/papers/<id>-notes.md
```

Slash-command hosts can use `/analyze-paper <args>`. You use parallel subagents for independent papers if the host supports them. Otherwise, you analyze papers in sequence.

The `--goal` flag controls reading depth and requires a relevance assessment. Later cycles can update these notes in place.

### 9. Verify Citations

You use the paper notes to check how the source paper uses each result with high relevance.

- **Accuracy:** You compare the cited claim with the original theorem.
- **Model compatibility:** You check that the result's assumptions hold in the source paper's model.
- **Fair comparison:** You check claimed improvements only after model compatibility passes. You compare the same target property and metric.
- **Version changes:** You check whether later versions correct or replace the cited result.

You record differences under `### Discrepancies with Paper Under Analysis` in each `<id>-notes.md`. You summarize these differences in `## Gaps Identified` for the formalization stage.

### 10. Write Output

You write `reaper-workspace/notes/literature.md` with title `# Literature Review` and these level-two sections:

| Section | Content |
|---|---|
| Landscape Summary | You explain approaches, proven results, and open questions in 2-3 short paragraphs. You relate the source paper if available. |
| Same-Goal Works | You tabulate papers with the same or similar goal. |
| Same-Approach Works | You tabulate papers that use similar techniques for different goals. |
| Citation Graph | You identify foundational works and later research directions. |
| Key Prior Results | You list results that constrain or inform the investigation. You include exact theorems where possible and cite paper notes. |
| Gaps Identified | You specify gaps in assumptions, properties, or techniques. |
| Paper Index | You tabulate Paper, Link, Local PDF, and Notes. |

Both literature tables use columns `#`, `Title`, `Authors`, `Year`, `Venue`, `Key Contribution`, `Link`, and `Local Path`.
Same-Goal Works also uses `Relation to Our Goal`. Same-Approach Works uses `Shared Technique`.
The Venue column contains a resolved venue or `(preprint)`.
Paper Index paths use `papers/<filename>.pdf` and `papers/<id>-notes.md`.

## Fallback

Each search operation can fail independently. You continue the review with the available evidence.

- If all structured searches fail, you use web search for all queries. You add the exact error at the start of `literature.md`. The note states `Structured paper search was unavailable. This review uses web search only.`
- If citation search fails, you omit Citation Graph or use web results. You mark each affected row `citation graph unavailable`.
- If venue lookup fails, you use `(preprint)` in the Venue column.
- If a download fails, you mark Local Path `unavailable`. You state that the paper assessment uses only its abstract.

## Quality Criteria

- You find at least ten relevant works unless the area is very narrow.
- Both literature categories contain relevant papers.
- Each paper note contains results, strengths, weaknesses, and a specific relation to the goal.
- The summary explains the area without prior knowledge. Each gap specifies a research direction.
- Every paper comes from an actual search result.
- You use multiple structured sources unless you record a structured-search failure.
- You include forward and backward citations unless you mark citation search unavailable.
