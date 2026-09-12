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

You run scripts through the shell with paths relative to this skill directory.
All scripts write JSON to stdout.

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
python3 arxiv.py search "BFT consensus communication complexity" --max-results 10 --categories cs.CR,cs.DC
python3 arxiv.py recent "threshold signatures" --max-results 10 --categories cs.CR
python3 arxiv.py download 2305.12345 --output-dir reaper-workspace/papers/
python3 iacr.py search "threshold signatures" --max-results 10
python3 iacr.py recent --max-results 10
python3 iacr.py download 2024/1234 --output-dir reaper-workspace/papers/
python3 iacr.py url 2024/1234
python3 semantic_scholar.py citations 2305.12345 --max-results 20
```

The arXiv `recent` command requires a query or `--categories`.
The venue protocol below gives the other command forms.

## Instructions

1. You read the query and flags.
2. You select the requested operation. Citation requests use `semantic_scholar.py citations <arxiv_id>`. Venue requests use the Venue Resolution Protocol.
3. For paper discovery, you use `iacr.py search` and `arxiv.py search --categories cs.CR` for cryptography or security.
4. For other computer science discovery, you use `arxiv.py search` with suitable categories.
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
python3 semantic_scholar.py venue --arxiv <arxiv_id>
python3 semantic_scholar.py venue --title "<exact title>"
```

You use title search for papers without an arXiv ID. If `found: true` and `venue` contains a value, you record `source = "semantic_scholar"`.

### Layer 2: Archive Metadata

```bash
python3 arxiv.py journal-ref <arxiv_id>
python3 iacr.py pubinfo <eprint_id>
```

You use the script for the paper's archive. If `journal_ref` or `publication_info` contains a value, you record the result. You set `source = "arxiv_journal_ref"` or `source = "iacr_pubinfo"`.

### Layer 3: DBLP

```bash
python3 dblp.py venue "<title>" --author "<first author surname>"
```

If `found: true`, you record `source = "dblp"`.

### Layer 4: OpenAlex

```bash
python3 openalex.py venue "<title>"
```

If `found: true`, you record `source = "openalex"`.

### Layer 5: Preprint Label

If all four layers fail, you label the entry `(preprint)`. You do not infer a venue from the topic or author's institution.

### Saved Results

You save venue results in workspace notes to avoid repeated searches. If sources disagree, you prefer the higher-ranked source in this protocol. You prefer a full venue name, such as `publicationVenue.name`, to an acronym. You record both results if confidence is low.

## Quality Criteria

- If an API or script fails, you report the error and continue with other sources or layers.

## Dependencies

```bash
pip install arxiv requests beautifulsoup4
```
