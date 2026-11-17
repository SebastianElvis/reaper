#!/usr/bin/env python3
"""Semantic Scholar driver: venue lookup and citation graph.

Usage:
    python3 semantic_scholar.py venue --arxiv <arxiv_id>
    python3 semantic_scholar.py venue --title "<title>" [--author "<surname>"]
    python3 semantic_scholar.py citations <arxiv_id> [--max-results N]

Requires: pip install requests
"""

import argparse
import json
import re
import sys


BASE = "https://api.semanticscholar.org/graph/v1/paper"
HTTP_TIMEOUT = 15


def _normalize(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip() or None


def _emit_venue(query, data):
    """Format a Semantic Scholar paper record into a venue response."""
    if not data:
        json.dump({
            "query": query,
            "found": False,
            "venue": None,
            "venue_full": None,
            "venue_type": None,
            "year": None,
            "title": None,
            "authors": [],
        }, sys.stdout, indent=2)
        print()
        return

    pub_venue = data.get("publicationVenue") or {}
    venue_full = _normalize(pub_venue.get("name"))
    venue_short = _normalize(data.get("venue")) or venue_full

    json.dump({
        "query": query,
        "found": True,
        "venue": venue_short,
        "venue_full": venue_full,
        "venue_type": pub_venue.get("type"),
        "year": data.get("year"),
        "title": _normalize(data.get("title")),
        "authors": [a.get("name") for a in (data.get("authors") or []) if a.get("name")],
    }, sys.stdout, indent=2)
    print()


def cmd_venue(args):
    """Look up venue + paper metadata for an arXiv ID or by title match."""
    import requests

    fields = "title,authors,year,venue,publicationVenue,externalIds"

    if args.arxiv:
        url = f"{BASE}/ARXIV:{args.arxiv}"
        try:
            resp = requests.get(url, params={"fields": fields}, timeout=HTTP_TIMEOUT)
            data = resp.json() if resp.status_code == 200 else None
        except (requests.RequestException, ValueError):
            data = None
        _emit_venue({"arxiv": args.arxiv}, data)
        return

    if args.title:
        url = f"{BASE}/search/match"
        params = {"query": args.title, "fields": fields}
        try:
            resp = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
            payload = resp.json() if resp.status_code == 200 else {}
            matches = payload.get("data") or []
            data = matches[0] if matches else None
        except (requests.RequestException, ValueError):
            data = None
        _emit_venue({"title": args.title}, data)
        return

    print(json.dumps({"error": "venue requires --arxiv or --title"}))
    sys.exit(2)


def cmd_citations(args):
    """Forward + backward citations for an arXiv paper."""
    import requests

    arxiv_key = f"ARXIV:{args.arxiv_id}"
    fields = "title,authors,year,externalIds,url,venue"
    result = {"arxiv_id": args.arxiv_id, "references": [], "citations": []}

    try:
        resp = requests.get(
            f"{BASE}/{arxiv_key}/references",
            params={"fields": fields, "limit": args.max_results},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code == 200:
            for ref in resp.json().get("data", []):
                cited = ref.get("citedPaper", {})
                if cited.get("title"):
                    result["references"].append({
                        "title": cited["title"],
                        "authors": [a["name"] for a in (cited.get("authors") or [])],
                        "year": cited.get("year"),
                        "venue": cited.get("venue"),
                        "arxiv_id": (cited.get("externalIds") or {}).get("ArXiv"),
                        "url": cited.get("url"),
                    })
    except requests.RequestException:
        pass

    try:
        resp = requests.get(
            f"{BASE}/{arxiv_key}/citations",
            params={"fields": fields, "limit": args.max_results},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code == 200:
            for cit in resp.json().get("data", []):
                citing = cit.get("citingPaper", {})
                if citing.get("title"):
                    result["citations"].append({
                        "title": citing["title"],
                        "authors": [a["name"] for a in (citing.get("authors") or [])],
                        "year": citing.get("year"),
                        "venue": citing.get("venue"),
                        "arxiv_id": (citing.get("externalIds") or {}).get("ArXiv"),
                        "url": citing.get("url"),
                    })
    except requests.RequestException:
        pass

    json.dump(result, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description="Semantic Scholar driver")
    sub = parser.add_subparsers(dest="command", required=True)

    p_venue = sub.add_parser("venue", help="Look up venue by arXiv ID or by title")
    p_venue.add_argument("--arxiv", help="arXiv paper ID")
    p_venue.add_argument("--title", help="Paper title (uses /paper/search/match)")
    p_venue.add_argument("--author", help="Optional author surname (currently informational)")

    p_cite = sub.add_parser("citations", help="Get forward/backward citations")
    p_cite.add_argument("arxiv_id", help="arXiv paper ID")
    p_cite.add_argument("--max-results", type=int, default=20)

    args = parser.parse_args()
    {"venue": cmd_venue, "citations": cmd_citations}[args.command](args)


if __name__ == "__main__":
    main()
