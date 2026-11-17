---
name: search-paper
description: "This skill finds papers, downloads PDFs, traces citations, and identifies publication venues. You use it for academic paper searches and venue checks."
user-invocable: true
argument-hint: "<query> [--source arxiv|iacr] [--max-results N]"
license: Apache-2.0
compatibility: "This skill requires python3, arxiv, requests, beautifulsoup4, and internet access."
---

# Search Paper

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

## Usage

You invoke this skill by name. Slash-command hosts use `/search-paper "<query>"`.

```
search-paper "post-quantum threshold signatures" --source iacr --max-results 15
```

## Scripts

You execute the bundled script for each supported operation. A command example or a recalled result does not complete the operation.
You resolve `search_skill_dir` to the absolute directory containing this installed `SKILL.md`. You resolve `research_workspace` to the user's research workspace, not the skill directory.
You set both shell variables before using the commands below. You quote paths and keep the shell in the user's working directory.
The executable files live in `scripts/`. All scripts write JSON to stdout.
You check the exit status and parse the returned JSON before using a result. You inspect error fields even when the process exits successfully.
You record the command, result source, and any error in the existing research notes or returned result. Workers return this evidence to the main agent.
You can reuse a recorded result when its query, source, and version still answer the request.

| Script | Commands and results |
|---|---|
| `arxiv.py` | `search` returns `{arxiv_id, title, authors, year, abstract, categories, pdf_url, published, journal_ref}` by relevance. `recent` returns these fields by submission date. |
| `arxiv.py` | `download` saves a PDF and returns `{path, title}`. `journal-ref` returns the author's venue field. |
| `iacr.py` | `search` returns `{eprint_id, title, authors, year, abstract, publication_info, venue, pdf_url, url}`. The first five results include paper-page metadata. |
| `iacr.py` | `recent` returns the newest papers. `download` saves the PDF. `url` returns its URL. `pubinfo` extracts publication information and attempts venue parsing. |
| `semantic_scholar.py` | `venue` accepts an arXiv ID or title. It returns `{found, venue, venue_full, venue_type, year, title, authors}`. |
| `semantic_scholar.py` | `citations` returns forward and backward citations with venues when known. Title lookup uses `/paper/search/match` for approximate matches. |
| `dblp.py` | `venue` searches by title and optional author surname for computer science publications. |
| `openalex.py` | `venue` searches by title when DBLP lacks coverage. |

You use these command forms:

```bash
python3 "$search_skill_dir/scripts/arxiv.py" search "BFT consensus communication complexity" --max-results 10 --categories cs.CR,cs.DC
python3 "$search_skill_dir/scripts/arxiv.py" recent "threshold signatures" --max-results 10 --categories cs.CR
python3 "$search_skill_dir/scripts/arxiv.py" download 2305.12345 --output-dir "$research_workspace/papers"
python3 "$search_skill_dir/scripts/iacr.py" search "threshold signatures" --max-results 10
python3 "$search_skill_dir/scripts/iacr.py" recent --max-results 10
python3 "$search_skill_dir/scripts/iacr.py" download 2024/1234 --output-dir "$research_workspace/papers"
python3 "$search_skill_dir/scripts/iacr.py" url 2024/1234
python3 "$search_skill_dir/scripts/semantic_scholar.py" citations 2305.12345 --max-results 20
```

The arXiv `recent` command requires a query or `--categories`.
The venue protocol below gives the other command forms.

## Instructions

1. You read the query and flags.
2. You select the requested operation. Citation requests use `semantic_scholar.py citations <arxiv_id>`. Venue requests use the Venue Resolution Protocol.
3. You honor an explicit `--source`. Otherwise, you use the relevant archive scripts for the topic. Cryptography can use IACR ePrint and arXiv.
4. You execute the selected command with the requested query and result limit. For arXiv, you select categories that match the topic.
5. You present results in this table with quoted abstract excerpts for highly relevant papers.

```markdown
| # | Title | Authors | Year | Venue | ID | Link |
|---|-------|---------|------|-------|----|------|
| 1 | ... | ... | ... | ... | arXiv:XXXX.XXXXX | [arXiv](https://arxiv.org/abs/XXXX.XXXXX) |
```

## Venue Resolution Protocol

An archive ID does not identify a publication venue. You find a venue for every paper in a literature review or report reference list. You run these layers in order. You stop at the first successful result.

### Layer 1: Semantic Scholar

```bash
python3 "$search_skill_dir/scripts/semantic_scholar.py" venue --arxiv <arxiv_id>
python3 "$search_skill_dir/scripts/semantic_scholar.py" venue --title "<exact title>"
```

You use title search for papers without an arXiv ID. If `found: true` and `venue` contains a value, you record `source = "semantic_scholar"`.

### Layer 2: Archive Metadata

```bash
python3 "$search_skill_dir/scripts/arxiv.py" journal-ref <arxiv_id>
python3 "$search_skill_dir/scripts/iacr.py" pubinfo <eprint_id>
```

You use the script for the paper's archive. If `journal_ref` or `publication_info` contains a value, you record the result. You set `source = "arxiv_journal_ref"` or `source = "iacr_pubinfo"`.

### Layer 3: DBLP

```bash
python3 "$search_skill_dir/scripts/dblp.py" venue "<title>" --author "<first author surname>"
```

If `found: true`, you record `source = "dblp"`.

### Layer 4: OpenAlex

```bash
python3 "$search_skill_dir/scripts/openalex.py" venue "<title>"
```

If `found: true`, you record `source = "openalex"`.

### Layer 5: Unresolved Status

If all four layers fail, you record `(unknown)`. You use `(preprint)` only when the source establishes that status. You do not infer a venue from the topic or author's institution.

### Saved Results

You save venue results in workspace notes to avoid repeated searches. If sources disagree, you verify the exact title, authors, version, and publisher record. Query order does not establish correctness. You prefer a full venue name, such as `publicationVenue.name`, to an acronym. You record both results if confidence is low.

## Quality Criteria

- You use web search to supplement unsupported sources or after an observed script failure. A host without shell execution reports that limitation before using a fallback.
- You preserve the actual failure or missing capability in the result. You do not report a fallback search as a successful script run.
- You verify downloaded files at the returned path before reporting completion.

## Dependencies

```bash
pip install arxiv requests beautifulsoup4
```
