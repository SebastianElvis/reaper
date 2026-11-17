#!/usr/bin/env python3
"""OpenAlex driver: title-based venue lookup. Broad coverage beyond CS.

Usage:
    python3 openalex.py venue "<title>"

Requires: pip install requests
"""

import argparse
import json
import re
import sys


API = "https://api.openalex.org/works"
HTTP_TIMEOUT = 15


def _normalize(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip() or None


def cmd_venue(args):
    """Search OpenAlex by title and return the top hit's venue."""
    import requests

    try:
        resp = requests.get(
            API,
            params={"search": args.title, "per-page": 1},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code != 200:
            _emit(args.title, None)
            return
        results = resp.json().get("results", [])
    except (requests.RequestException, ValueError):
        _emit(args.title, None)
        return

    if not results:
        _emit(args.title, None)
        return

    work = results[0]
    # Newer schema: primary_location.source.display_name
    # Older schema: host_venue.display_name
    source = (work.get("primary_location") or {}).get("source") or {}
    venue_full = _normalize(source.get("display_name")) or _normalize(
        (work.get("host_venue") or {}).get("display_name")
    )
    venue_type = source.get("type") or (work.get("host_venue") or {}).get("type")
    year = work.get("publication_year")

    if not venue_full:
        _emit(args.title, None)
        return

    venue_with_year = f"{venue_full} {year}" if year else venue_full
    json.dump({
        "query": {"title": args.title},
        "found": True,
        "venue": venue_with_year,
        "venue_full": venue_full,
        "venue_type": venue_type,
        "year": year,
        "title": _normalize(work.get("title") or work.get("display_name")),
        "url": work.get("doi") or work.get("id"),
    }, sys.stdout, indent=2)
    print()


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
    parser = argparse.ArgumentParser(description="OpenAlex driver")
    sub = parser.add_subparsers(dest="command", required=True)

    p_venue = sub.add_parser("venue", help="Look up venue by title")
    p_venue.add_argument("title", help="Paper title")

    args = parser.parse_args()
    {"venue": cmd_venue}[args.command](args)


if __name__ == "__main__":
    main()
