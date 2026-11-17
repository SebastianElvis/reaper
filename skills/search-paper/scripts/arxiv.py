#!/usr/bin/env python3
"""arXiv platform driver: search papers, list recent submissions, download PDFs, read journal_ref field.

Usage:
    python3 arxiv.py search "<query>" [--max-results N] [--categories cat1,cat2]
    python3 arxiv.py recent ["<query>"] [--max-results N] [--categories cat1,cat2]
    python3 arxiv.py download <arxiv_id> [--output-dir DIR]
    python3 arxiv.py journal-ref <arxiv_id>

Requires: pip install arxiv
"""

import argparse
import json
import os
import sys
from pathlib import Path

# This file is named `arxiv.py` to match the platform convention used by the
# other drivers in this skill. When run as a script, Python prepends our own
# directory to sys.path, which would shadow the third-party `arxiv` PyPI
# package. Strip that entry so `import arxiv` resolves to the package.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p or ".") != _here]


def cmd_search(args):
    """Search arXiv papers by query."""
    import arxiv

    search = arxiv.Search(
        query=args.query,
        max_results=args.max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    if args.categories:
        cats = [c.strip() for c in args.categories.split(",")]
        cat_query = " OR ".join(f"cat:{c}" for c in cats)
        search.query = f"({args.query}) AND ({cat_query})"

    results = []
    client = arxiv.Client()
    for paper in client.results(search):
        results.append({
            "arxiv_id": paper.entry_id.split("/abs/")[-1],
            "title": paper.title.replace("\n", " "),
            "authors": [a.name for a in paper.authors],
            "year": paper.published.year,
            "abstract": paper.summary.replace("\n", " "),
            "categories": paper.categories,
            "pdf_url": paper.pdf_url,
            "published": paper.published.strftime("%Y-%m-%d"),
            "journal_ref": paper.journal_ref,
        })

    json.dump(results, sys.stdout, indent=2)
    print()


def cmd_recent(args):
    """Return the most recently submitted arXiv papers matching the query/categories.

    At least one of `query` or `--categories` must be supplied — the arXiv API
    does not accept an empty search expression.
    """
    import arxiv

    cat_query = None
    if args.categories:
        cats = [c.strip() for c in args.categories.split(",")]
        cat_query = " OR ".join(f"cat:{c}" for c in cats)

    if args.query and cat_query:
        query = f"({args.query}) AND ({cat_query})"
    elif args.query:
        query = args.query
    elif cat_query:
        query = cat_query
    else:
        print(json.dumps({"error": "recent requires a query or --categories"}))
        sys.exit(2)

    search = arxiv.Search(
        query=query,
        max_results=args.max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    results = []
    client = arxiv.Client()
    for paper in client.results(search):
        results.append({
            "arxiv_id": paper.entry_id.split("/abs/")[-1],
            "title": paper.title.replace("\n", " "),
            "authors": [a.name for a in paper.authors],
            "year": paper.published.year,
            "abstract": paper.summary.replace("\n", " "),
            "categories": paper.categories,
            "pdf_url": paper.pdf_url,
            "published": paper.published.strftime("%Y-%m-%d"),
            "journal_ref": paper.journal_ref,
        })

    json.dump(results, sys.stdout, indent=2)
    print()


def cmd_download(args):
    """Download a paper PDF by arXiv ID."""
    import arxiv

    search = arxiv.Search(id_list=[args.arxiv_id])
    client = arxiv.Client()
    paper = next(client.results(search), None)
    if not paper:
        print(json.dumps({"error": f"Paper {args.arxiv_id} not found"}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = paper.download_pdf(dirpath=str(output_dir))
    print(json.dumps({"path": str(path), "title": paper.title}))


def cmd_journal_ref(args):
    """Return the author-supplied journal_ref field for an arXiv paper.

    arXiv lets authors set this when their preprint has been accepted somewhere.
    Sparse but authoritative when present.
    """
    import arxiv

    search = arxiv.Search(id_list=[args.arxiv_id])
    client = arxiv.Client()
    paper = next(client.results(search), None)
    if not paper:
        print(json.dumps({"error": f"Paper {args.arxiv_id} not found"}))
        sys.exit(1)

    json.dump({
        "arxiv_id": args.arxiv_id,
        "journal_ref": paper.journal_ref,
        "title": paper.title.replace("\n", " "),
        "authors": [a.name for a in paper.authors],
        "year": paper.published.year if paper.published else None,
    }, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description="arXiv platform driver")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search papers by query")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max-results", type=int, default=10)
    p_search.add_argument("--categories", help="Comma-separated arXiv categories (e.g. cs.CR,cs.DC)")

    p_recent = sub.add_parser("recent", help="Get recently submitted papers (by date)")
    p_recent.add_argument("query", nargs="?", default=None, help="Optional query to scope the recent feed")
    p_recent.add_argument("--max-results", type=int, default=10)
    p_recent.add_argument("--categories", help="Comma-separated arXiv categories (e.g. cs.CR,cs.DC)")

    p_download = sub.add_parser("download", help="Download paper PDF")
    p_download.add_argument("arxiv_id", help="arXiv paper ID (e.g. 2305.12345)")
    p_download.add_argument("--output-dir", default=".")

    p_jref = sub.add_parser("journal-ref", help="Read arXiv journal_ref field (author-supplied venue)")
    p_jref.add_argument("arxiv_id", help="arXiv paper ID")

    args = parser.parse_args()
    {
        "search": cmd_search,
        "recent": cmd_recent,
        "download": cmd_download,
        "journal-ref": cmd_journal_ref,
    }[args.command](args)


if __name__ == "__main__":
    main()
