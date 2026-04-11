#!/usr/bin/env python3
"""Search IACR ePrint archive for cryptography papers.

Usage:
    python search_iacr.py search "query" [--max-results N]
    python search_iacr.py recent [--max-results N]
    python search_iacr.py download EPRINT_ID [--output-dir DIR]
    python search_iacr.py url EPRINT_ID

Requires: pip install requests beautifulsoup4
"""

import argparse
import json
import re
import sys
from pathlib import Path


EPRINT_BASE = "https://eprint.iacr.org"


def _parse_search_results(html, max_results):
    """Parse ePrint search results HTML into structured data."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # ePrint search results are in <dl> with <dt> containing the ID and <dd> containing details
    # Try the newer format first: papers are in divs or list items
    # The search page returns results as a list of papers

    # Pattern: look for links to /YEAR/NNN
    paper_links = soup.find_all("a", href=re.compile(r"^/\d{4}/\d+$"))
    seen = set()

    for link in paper_links:
        if len(results) >= max_results:
            break

        href = link.get("href", "")
        eprint_id = href.lstrip("/")
        if eprint_id in seen:
            continue
        seen.add(eprint_id)

        title = link.get_text(strip=True)
        if not title or title == eprint_id:
            # Try to find title in surrounding context
            parent = link.find_parent(["div", "li", "dd", "tr", "p"])
            if parent:
                # Look for bold or strong text as title
                bold = parent.find(["b", "strong"])
                if bold:
                    title = bold.get_text(strip=True)

        # Try to extract authors from surrounding context
        authors = []
        parent = link.find_parent(["div", "li", "dd", "tr", "p"])
        if parent:
            # Authors often appear in <em> or <i> tags, or after "by"
            em = parent.find(["em", "i"])
            if em:
                authors_text = em.get_text(strip=True)
                authors = [a.strip() for a in authors_text.split(",") if a.strip()]

        year = eprint_id.split("/")[0] if "/" in eprint_id else None

        results.append({
            "eprint_id": eprint_id,
            "title": title if title else f"ePrint {eprint_id}",
            "authors": authors,
            "year": int(year) if year else None,
            "pdf_url": f"{EPRINT_BASE}/{eprint_id}.pdf",
            "url": f"{EPRINT_BASE}/{eprint_id}",
        })

    return results


def _fetch_paper_page(eprint_id):
    """Fetch and parse a single ePrint paper page for metadata."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(f"{EPRINT_BASE}/{eprint_id}", timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = ""
    authors = []
    abstract = ""

    # Title is typically in <h3> or page title
    title_el = soup.find("h3")
    if title_el:
        title = title_el.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).replace("ePrint Report – ", "")

    # Look for metadata in <div class="paper-..."> or <p> tags
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text.startswith("Abstract:") or text.startswith("Abstract."):
            abstract = text.split(":", 1)[-1].strip() if ":" in text else text.split(".", 1)[-1].strip()

    # Authors from meta tags
    for meta in soup.find_all("meta", {"name": "citation_author"}):
        content = meta.get("content", "")
        if content:
            authors.append(content)

    # Title from meta tag
    meta_title = soup.find("meta", {"name": "citation_title"})
    if meta_title and meta_title.get("content"):
        title = meta_title["content"]

    return {
        "eprint_id": eprint_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "pdf_url": f"{EPRINT_BASE}/{eprint_id}.pdf",
        "url": f"{EPRINT_BASE}/{eprint_id}",
    }


def cmd_search(args):
    """Search ePrint papers by query."""
    import requests

    resp = requests.get(
        f"{EPRINT_BASE}/search",
        params={"q": args.query},
        timeout=15,
    )
    resp.raise_for_status()
    results = _parse_search_results(resp.text, args.max_results)

    # Enrich top results with metadata from individual pages
    enriched = []
    for r in results[:min(5, len(results))]:
        try:
            detail = _fetch_paper_page(r["eprint_id"])
            r.update({k: v for k, v in detail.items() if v})
            enriched.append(r)
        except Exception:
            enriched.append(r)

    # Add remaining without enrichment
    enriched.extend(results[5:])
    json.dump(enriched, sys.stdout, indent=2)
    print()


def cmd_recent(args):
    """Get recent ePrint papers."""
    import requests

    resp = requests.get(f"{EPRINT_BASE}/search", params={"q": "*", "sort": "date"}, timeout=15)
    resp.raise_for_status()
    results = _parse_search_results(resp.text, args.max_results)

    json.dump(results, sys.stdout, indent=2)
    print()


def cmd_download(args):
    """Download a paper PDF by ePrint ID."""
    import requests

    pdf_url = f"{EPRINT_BASE}/{args.eprint_id}.pdf"
    resp = requests.get(pdf_url, timeout=30)
    resp.raise_for_status()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{args.eprint_id.replace('/', '_')}.pdf"
    path = output_dir / filename
    path.write_bytes(resp.content)

    print(json.dumps({"path": str(path), "eprint_id": args.eprint_id}))


def cmd_url(args):
    """Get the URL of a paper."""
    print(json.dumps({
        "eprint_id": args.eprint_id,
        "url": f"{EPRINT_BASE}/{args.eprint_id}",
        "pdf_url": f"{EPRINT_BASE}/{args.eprint_id}.pdf",
    }))


def main():
    parser = argparse.ArgumentParser(description="Search IACR ePrint archive")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search papers by query")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max-results", type=int, default=10)

    p_recent = sub.add_parser("recent", help="Get recent papers")
    p_recent.add_argument("--max-results", type=int, default=10)

    p_download = sub.add_parser("download", help="Download paper PDF")
    p_download.add_argument("eprint_id", help="ePrint ID (e.g. 2024/1234)")
    p_download.add_argument("--output-dir", default=".")

    p_url = sub.add_parser("url", help="Get paper URL")
    p_url.add_argument("eprint_id", help="ePrint ID")

    args = parser.parse_args()
    {"search": cmd_search, "recent": cmd_recent, "download": cmd_download, "url": cmd_url}[args.command](args)


if __name__ == "__main__":
    main()
