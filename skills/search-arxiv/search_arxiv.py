#!/usr/bin/env python3
"""Search arXiv for academic papers.

Usage:
    python search_arxiv.py search "query" [--max-results N] [--categories cat1,cat2]
    python search_arxiv.py download ARXIV_ID [--output-dir DIR]
    python search_arxiv.py citations ARXIV_ID [--max-results N]

Requires: pip install arxiv requests
"""

import argparse
import json
import sys
from pathlib import Path


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


def cmd_citations(args):
    """Get forward/backward citations via Semantic Scholar API."""
    import requests

    base = "https://api.semanticscholar.org/graph/v1/paper"
    arxiv_key = f"ARXIV:{args.arxiv_id}"

    result = {"arxiv_id": args.arxiv_id, "references": [], "citations": []}

    # Backward citations (references)
    try:
        resp = requests.get(
            f"{base}/{arxiv_key}/references",
            params={"fields": "title,authors,year,externalIds,url", "limit": args.max_results},
            timeout=15,
        )
        if resp.status_code == 200:
            for ref in resp.json().get("data", []):
                cited = ref.get("citedPaper", {})
                if cited.get("title"):
                    result["references"].append({
                        "title": cited["title"],
                        "authors": [a["name"] for a in (cited.get("authors") or [])],
                        "year": cited.get("year"),
                        "arxiv_id": (cited.get("externalIds") or {}).get("ArXiv"),
                        "url": cited.get("url"),
                    })
    except requests.RequestException:
        pass

    # Forward citations (who cites this)
    try:
        resp = requests.get(
            f"{base}/{arxiv_key}/citations",
            params={"fields": "title,authors,year,externalIds,url", "limit": args.max_results},
            timeout=15,
        )
        if resp.status_code == 200:
            for cit in resp.json().get("data", []):
                citing = cit.get("citingPaper", {})
                if citing.get("title"):
                    result["citations"].append({
                        "title": citing["title"],
                        "authors": [a["name"] for a in (citing.get("authors") or [])],
                        "year": citing.get("year"),
                        "arxiv_id": (citing.get("externalIds") or {}).get("ArXiv"),
                        "url": citing.get("url"),
                    })
    except requests.RequestException:
        pass

    json.dump(result, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description="Search arXiv for academic papers")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search papers by query")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max-results", type=int, default=10)
    p_search.add_argument("--categories", help="Comma-separated arXiv categories (e.g. cs.CR,cs.DC)")

    p_download = sub.add_parser("download", help="Download paper PDF")
    p_download.add_argument("arxiv_id", help="arXiv paper ID (e.g. 2305.12345)")
    p_download.add_argument("--output-dir", default=".")

    p_cite = sub.add_parser("citations", help="Get forward/backward citations")
    p_cite.add_argument("arxiv_id", help="arXiv paper ID")
    p_cite.add_argument("--max-results", type=int, default=20)

    args = parser.parse_args()
    {"search": cmd_search, "download": cmd_download, "citations": cmd_citations}[args.command](args)


if __name__ == "__main__":
    main()
