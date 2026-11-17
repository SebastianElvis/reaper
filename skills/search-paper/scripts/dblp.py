#!/usr/bin/env python3
"""DBLP driver: title+author venue lookup. Authoritative for CS venues.

Usage:
    python3 dblp.py venue "<title>" [--author "<surname>"]

Requires: pip install requests
"""

import argparse
import json
import re
import sys


API = "https://dblp.org/search/publ/api"
HTTP_TIMEOUT = 15


def _normalize(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip() or None


def cmd_venue(args):
    """Search DBLP by title (+ optional author) and return the top hit's venue."""
    import requests

    query = args.title
    if args.author:
        query = f"{args.title} {args.author}"

    try:
        resp = requests.get(
            API,
            params={"q": query, "format": "json", "h": 3},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code != 200:
            _emit(args.title, None)
            return
        hits = (resp.json().get("result", {}).get("hits", {}).get("hit", []) or [])
    except (requests.RequestException, ValueError):
        _emit(args.title, None)
        return

    for hit in hits:
        info = hit.get("info") or {}
        venue = _normalize(info.get("venue"))
        if not venue:
            continue
        year = info.get("year")
        venue_with_year = f"{venue} {year}" if year else venue
        json.dump({
            "query": {"title": args.title, "author": args.author},
            "found": True,
            "venue": venue_with_year,
            "venue_full": venue,
            "venue_type": info.get("type"),
            "year": int(year) if (year or "").isdigit() else None,
            "title": _normalize(info.get("title")),
            "url": info.get("url"),
        }, sys.stdout, indent=2)
        print()
        return

    _emit(args.title, None)


def _emit(title, _):
    json.dump({
        "query": {"title": title},
        "found": False,
        "venue": None,
        "venue_full": None,
        "venue_type": None,
        "year": None,
        "title": None,
        "url": None,
    }, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description="DBLP driver")
    sub = parser.add_subparsers(dest="command", required=True)

    p_venue = sub.add_parser("venue", help="Look up venue by title (+ author)")
    p_venue.add_argument("title", help="Paper title")
    p_venue.add_argument("--author", help="Author surname (improves disambiguation)")

    args = parser.parse_args()
    {"venue": cmd_venue}[args.command](args)


if __name__ == "__main__":
    main()
