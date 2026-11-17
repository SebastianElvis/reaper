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

You invoke the `search-paper` skill for supported paper operations. You require its command result or a specific execution limitation before treating the operation as complete. The `/search-paper` skill selects archives, categories, and filters. You select query types that address the goal and evidence gaps. You assign each query to one target:

- **Direct:** The query names the exact problem without an author, technique, negative-result, or survey filter.
- **Author:** The query names key authors and the topic.
- **Technique:** The query names the proof or construction technique.
- **Variants:** The query changes the direct query to a related problem or different assumption.
- **Negative results:** The query names attacks, impossibility results, or lower bounds.
- **Surveys:** The query requests surveys or systematization of knowledge papers.

You run selected independent queries in parallel within the host concurrency limit. Each subagent executes the applicable commands through `search-paper`. It returns parsed results, the command used, and any execution error. You start the web search in Step 3 as another parallel subagent.
If the host cannot run subagents, you run the searches in sequence.

You give each subagent a small JSON object of about 100 words. The object contains the topic, authors, and 3-5 key concepts. You do not send the full paper summary.

### 3. Search the Web as a Fallback

You use web search for results that structured APIs can miss:

- Conference proceedings outside arXiv and ePrint.
- Blog posts and talks that supply relevant evidence and do not duplicate a paper entry.
- Preprints on author websites that do not duplicate a proceedings entry.

You assess supporting evidence under `references/venue-tiers.md` from the `reaper` skill. You label claims that lack verification.

### 4. Trace Citations

You invoke the `search-paper` skill for the seed paper and the three most relevant results. You supply each arXiv ID and request up to 20 citations in each direction. Backward citations identify earlier results that the paper uses.
Forward citations identify later improvements, attacks, or corrections. You remove duplicate results across sources. For papers without an arXiv ID, you use web search to find citing works.

### 5. Check Recent Papers

For an area with rapid changes, you invoke the `search-paper` skill for the ten newest papers. You check titles and abstracts. You include relevant recent results that the earlier searches missed.

### 6. Filter and Rank Results

You put each paper in one of two categories:

- **Same Goal:** The paper addresses the same or a similar problem.
- **Same Approach:** The paper uses a similar technique for another problem.

You use `references/venue-tiers.md` from the `reaper` skill for evidence quality. You compare conflicting claims under the same assumptions. You preserve unresolved conflicts.

You assign relevance within each category:

- **High:** The paper addresses the target problem or supplies a result or technique that the research needs.
- **Medium:** The paper supplies related context or a useful component but does not meet High criteria.
- **Low:** The paper has an indirect relation that meets neither High nor Medium criteria.

You keep high and medium relevance papers. You keep low relevance papers only when their evidence supports a necessary definition or dependency.

### 7. Resolve Publication Venues

You invoke the `search-paper` skill's Venue Resolution Protocol for each kept paper. You prefer an arXiv ID, then an ePrint ID, then a title with the first author's surname. You save the verified venue or explicit publication status in workspace notes.
You do not infer a venue from a topic or institution.
You retain relevant evidence regardless of venue or author reputation. You distinguish unknown publication status from a confirmed preprint.

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

### 10. Set the Venue Bar

You perform this step only for a requested paper or publication output. The venue bar separates mandatory publication rules from optional quality targets inferred from related work. You write it to `reaper-workspace/notes/venue-bar.md`.

1. **Target venue:** You use the target venue in `notes/clarified-goal.md`. If the goal names no venue, you select a venue whose topic and article type match the requested paper.
2. **Venue rules:** You read the current call for papers. If it is not published, you use the most recent call and mark each rule `(proxy: <year>)`. You record the template, page limit, anonymity rules, and mandatory sections, such as ethics or artifact availability.
3. **Exemplar papers:** You select relevant Same-Goal Works from the target venue or comparable venues. If the selected papers do not cover the required comparisons, you invoke the `search-paper` skill to find recent papers from the target venue on a related topic. You download each exemplar to `reaper-workspace/papers/`.
4. **Bar measurement:** You read each exemplar. You record its contributions, its novelty claim against prior work, and its evidence, such as proofs, experiments, baselines, and metrics. You also record its section list, page count, figure and table count, and writing and presentation practices.
5. **Bar checklist:** You write numbered checklist items from the venue rules and the exemplars. Each item names its source, such as the call for papers or exemplar E2. The items cover contributions, novelty, evidence, writing, presentation, and format. For contributions and novelty, each item identifies a specific comparison to assess. Exemplars do not impose a requirement to outperform every prior result.

`venue-bar.md` has title `# Venue Bar` and the level-two sections Venue Rules, Exemplar Papers, and Bar Checklist.

### 11. Write Output

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
The Venue column contains the verified venue, `(preprint)`, or `(unknown)`.
Paper Index paths use `papers/<filename>.pdf` and `papers/<id>-notes.md`.

## Fallback

Each search operation can fail independently. You continue the review with the available evidence.

- If all structured searches fail, you use web search for all queries. You add the exact error at the start of `literature.md`. The note states `Structured paper search was unavailable. This review uses web search only.`
- If citation search fails, you omit Citation Graph or use web results. You mark each affected row `citation graph unavailable`.
- If venue lookup fails, you record `(unknown)` unless the archive confirms preprint status.
- If a download fails, you mark Local Path `unavailable`. You state that the paper assessment uses only its abstract.
- If the call for papers or an exemplar is unavailable, you build the bar from the available sources. You mark each affected checklist item `unverified` in `venue-bar.md`.

## Quality Criteria

- You search until the required evidence is covered or the search limit ends. You report coverage limits.
- You omit a literature category when no relevant work fits it.
- Each paper note contains results, strengths, weaknesses, and a specific relation to the goal.
- The summary explains the area without prior knowledge. Each gap specifies a research direction.
- Every paper comes from an actual search result.
- Each retained paper has relevant evidence or an explicit verification gap.
- You use multiple structured sources unless you record a structured-search failure.
- You include forward and backward citations unless you mark citation search unavailable.
- Each bar checklist item names its source. The contribution and novelty items identify relevant comparisons.
