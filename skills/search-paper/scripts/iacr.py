#!/usr/bin/env python3
"""IACR ePrint platform driver: search, recent, download, url, pubinfo.

Usage:
    python3 iacr.py search "<query>" [--max-results N]
    python3 iacr.py recent [--max-results N]
    python3 iacr.py download <eprint_id> [--output-dir DIR]
    python3 iacr.py url <eprint_id>
    python3 iacr.py pubinfo <eprint_id>

Requires: pip install requests beautifulsoup4
"""

import argparse
import json
import re
import sys
from pathlib import Path


EPRINT_BASE = "https://eprint.iacr.org"

# Acronyms recognized in ePrint "Publication info" lines.
KNOWN_VENUES = (
    "CRYPTO", "EUROCRYPT", "ASIACRYPT", "TCC", "PKC", "CHES", "FSE",
    "CCS", "S&P", "USENIX Security", "USENIX", "NDSS", "Oakland",
    "FC", "ESORICS", "ACNS", "SCN", "PETS", "AFT",
    "ICALP", "STOC", "FOCS", "PODC", "DISC", "OPODIS", "DSN",
    "JoC", "TIFS", "TDSC", "DCC",
)


def _parse_search_results(html, max_results):
    """Parse ePrint search results HTML into structured data."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

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
            parent = link.find_parent(["div", "li", "dd", "tr", "p"])
            if parent:
                bold = parent.find(["b", "strong"])
                if bold:
                    title = bold.get_text(strip=True)

        authors = []
        parent = link.find_parent(["div", "li", "dd", "tr", "p"])
        if parent:
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


def _extract_publication_info(soup):
    """Extract the 'Publication info' free-form line from a paper page, if any.

    Format varies: 'A minor revision of an IACR publication in CRYPTO 2023',
    'Published elsewhere. SCN 2022', 'Conference: ASIACRYPT 2024', etc.
    Returns the raw line plus best-effort parsed venue/year.
    """
    raw = None

    # Newer template uses <dt>Publication info</dt><dd>...</dd>
    for dt in soup.find_all("dt"):
        if "publication info" in dt.get_text(strip=True).lower():
            dd = dt.find_next_sibling("dd")
            if dd:
                raw = dd.get_text(" ", strip=True)
                break

    # Older template: a <p> or <b> introducing the line
    if not raw:
        for tag in soup.find_all(["b", "strong"]):
            if "publication info" in tag.get_text(strip=True).lower():
                parent = tag.find_parent(["p", "div", "dd"])
                if parent:
                    text = parent.get_text(" ", strip=True)
                    raw = re.sub(r"^.*?publication info[:\s]*", "", text, flags=re.IGNORECASE).strip()
                    break

    # Generic fallback: any element directly containing the literal string
    if not raw:
        match = re.search(r"Publication info[:\s]+([^\n<]+)", soup.get_text("\n"))
        if match:
            raw = match.group(1).strip()

    if not raw:
        return {"raw": None, "venue": None, "year": None}

    venue = None
    for v in KNOWN_VENUES:
        if re.search(rf"\b{re.escape(v)}\b", raw, re.IGNORECASE):
            venue = v
            break

    year = None
    m = re.search(r"\b(19|20)\d{2}\b", raw)
    if m:
        year = int(m.group(0))

    venue_with_year = f"{venue} {year}" if venue and year else venue
    return {"raw": raw, "venue": venue_with_year, "year": year}


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

    title_el = soup.find("h3")
    if title_el:
        title = title_el.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).replace("ePrint Report – ", "")

    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text.startswith("Abstract:") or text.startswith("Abstract."):
            abstract = text.split(":", 1)[-1].strip() if ":" in text else text.split(".", 1)[-1].strip()

    for meta in soup.find_all("meta", {"name": "citation_author"}):
        content = meta.get("content", "")
        if content:
            authors.append(content)

    meta_title = soup.find("meta", {"name": "citation_title"})
    if meta_title and meta_title.get("content"):
        title = meta_title["content"]

    pub = _extract_publication_info(soup)

    return {
        "eprint_id": eprint_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "publication_info": pub["raw"],
        "venue": pub["venue"],
        "venue_year": pub["year"],
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

    enriched = []
    for r in results[:min(5, len(results))]:
        try:
            detail = _fetch_paper_page(r["eprint_id"])
            r.update({k: v for k, v in detail.items() if v})
            enriched.append(r)
        except Exception:
            enriched.append(r)

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


def cmd_pubinfo(args):
    """Fetch the 'Publication info' line from an ePrint paper page.

    ePrint authors mark the venue here (e.g., 'A major revision of CRYPTO 2023').
    Returns raw line + best-effort parsed venue/year.
    """
    detail = _fetch_paper_page(args.eprint_id)
    json.dump({
        "eprint_id": args.eprint_id,
        "title": detail.get("title"),
        "authors": detail.get("authors") or [],
        "publication_info": detail.get("publication_info"),
        "venue": detail.get("venue"),
        "venue_year": detail.get("venue_year"),
    }, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description="IACR ePrint platform driver")
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

    p_pub = sub.add_parser("pubinfo", help="Read ePrint 'Publication info' field (author-supplied venue)")
    p_pub.add_argument("eprint_id", help="ePrint ID")

    args = parser.parse_args()
    {
        "search": cmd_search,
        "recent": cmd_recent,
        "download": cmd_download,
        "url": cmd_url,
        "pubinfo": cmd_pubinfo,
    }[args.command](args)


if __name__ == "__main__":
    main()
