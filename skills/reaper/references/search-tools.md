# Search Tools Reference

You invoke `search-paper` to execute its bundled scripts for supported searches, downloads, citations, and venue metadata. You require a command result or a specific execution limitation.
Its `SKILL.md` owns command syntax and output fields. You do not maintain a second command catalogue here.

## Available Scripts

| Script | Role |
|---|---|
| `arxiv.py` | The script searches arXiv, lists recent papers, downloads PDFs, and reads archive metadata. |
| `iacr.py` | The script searches IACR ePrint, downloads PDFs, and reads publication metadata. |
| `semantic_scholar.py` | The script retrieves citations and venue candidates. |
| `dblp.py` | The script retrieves computer science venue candidates by title. |
| `openalex.py` | The script provides another source of venue candidates. |

## Decision Tree

You select archives and categories that cover the topic.
For cryptography, you consider arXiv and IACR ePrint. You use web search when the archives miss relevant sources.
For citation tracing, you supply the seed identifier to `search-paper`. You follow only citations that address the goal.
For recent work, you request recent results with a suitable query or category.
During an investigation, you search the exact unresolved question. You return source findings to the main agent for integration into shared notes.
You respect host concurrency limits and service rate-limit responses. You do not repeat failed requests without a useful change.

## Venue Resolution Protocol

You use the protocol in the `search-paper` skill. You cache the paper identity, version, metadata source, and result in workspace notes.
A lookup failure leaves venue status unknown. It does not establish preprint status.
You resolve conflicting metadata against the exact work and version. Query order does not decide correctness.

## Graceful Degradation

If a script fails, you report the error and use another available source.
If web search also fails, you continue only from available evidence and state the coverage limit.
You check current provider documentation when authentication, rate limits, or API behavior blocks a search. You do not assume a fixed public quota.
