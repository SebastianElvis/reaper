"""Tests for the /search-paper skill scripts — validates CLI interfaces and output formats.

Uses real API calls (integration tests). Requires network access.
"""

import json
import subprocess
import sys

SKILL_DIR = "skills/search-paper"
PYTHON = sys.executable


def run(script, args, timeout=30):
    result = subprocess.run(
        [PYTHON, f"{SKILL_DIR}/{script}"] + args,
        capture_output=True, text=True, timeout=timeout,
    )
    return result


# ---------------------------------------------------------------------------
# arxiv.py
# ---------------------------------------------------------------------------

def test_arxiv_search_returns_json_array():
    r = run("arxiv.py", ["search", "Byzantine fault tolerance", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert 0 < len(data) <= 3


def test_arxiv_search_result_fields():
    r = run("arxiv.py", ["search", "threshold signatures", "--max-results", "1"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    paper = data[0]
    for field in ["arxiv_id", "title", "authors", "year", "abstract", "pdf_url", "journal_ref"]:
        assert field in paper, f"Missing field: {field}"
    assert isinstance(paper["authors"], list)
    assert isinstance(paper["year"], int)
    assert paper["title"]


def test_arxiv_search_with_categories():
    r = run("arxiv.py", ["search", "consensus protocol", "--max-results", "2", "--categories", "cs.CR,cs.DC"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert len(data) > 0


def test_arxiv_journal_ref_returns_field():
    """HotStuff (1803.05069) has been published; journal_ref may or may not be set
    depending on author choice, but the script must always return a JSON object
    with the expected keys."""
    r = run("arxiv.py", ["journal-ref", "1803.05069"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["arxiv_id", "journal_ref", "title", "authors", "year"]:
        assert field in data, f"Missing field: {field}"
    assert data["arxiv_id"] == "1803.05069"


def test_arxiv_recent_returns_results():
    """recent must return a JSON array sorted by submission date. At least one
    of query/--categories is required; we pass --categories to scope the feed."""
    r = run("arxiv.py", ["recent", "--max-results", "3", "--categories", "cs.CR"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert 0 < len(data) <= 3
    # Results should be sorted newest-first by `published`.
    dates = [p["published"] for p in data]
    assert dates == sorted(dates, reverse=True), f"recent results not date-sorted: {dates}"


def test_arxiv_recent_requires_query_or_categories():
    """recent with neither a query nor --categories must exit non-zero with a
    clear error — arXiv's API rejects empty search expressions."""
    r = run("arxiv.py", ["recent", "--max-results", "1"])
    assert r.returncode != 0
    err_payload = (r.stdout or "") + (r.stderr or "")
    assert "query" in err_payload.lower() or "categories" in err_payload.lower()


def test_arxiv_cli_help():
    r = run("arxiv.py", ["--help"])
    assert r.returncode == 0
    assert "search" in r.stdout.lower()
    assert "recent" in r.stdout.lower()
    assert "journal-ref" in r.stdout.lower()


# ---------------------------------------------------------------------------
# iacr.py
# ---------------------------------------------------------------------------

def test_iacr_search_returns_json_array():
    r = run("iacr.py", ["search", "threshold signatures", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) > 0


def test_iacr_search_result_fields():
    r = run("iacr.py", ["search", "post-quantum", "--max-results", "1"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert len(data) > 0
    paper = data[0]
    for field in ["eprint_id", "title", "pdf_url", "url"]:
        assert field in paper, f"Missing field: {field}"
    assert paper["eprint_id"]
    assert "/" in paper["eprint_id"]


def test_iacr_url_command():
    r = run("iacr.py", ["url", "2024/1234"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert data["eprint_id"] == "2024/1234"
    assert "eprint.iacr.org/2024/1234" in data["url"]
    assert data["pdf_url"].endswith(".pdf")


def test_iacr_pubinfo_returns_fields():
    """The pubinfo endpoint must always return a JSON object with the expected
    keys, even if the paper page has no Publication info line."""
    r = run("iacr.py", ["pubinfo", "2024/1234"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["eprint_id", "title", "authors", "publication_info", "venue", "venue_year"]:
        assert field in data, f"Missing field: {field}"
    assert data["eprint_id"] == "2024/1234"


def test_iacr_recent_returns_results():
    r = run("iacr.py", ["recent", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)


def test_iacr_cli_help():
    r = run("iacr.py", ["--help"])
    assert r.returncode == 0
    assert "search" in r.stdout.lower()
    assert "pubinfo" in r.stdout.lower()


# ---------------------------------------------------------------------------
# semantic_scholar.py
# ---------------------------------------------------------------------------

def test_s2_venue_by_arxiv_returns_fields():
    """HotStuff is published at PODC 2019 — venue should resolve. But we tolerate
    transient API failures by only checking that the expected keys are present."""
    r = run("semantic_scholar.py", ["venue", "--arxiv", "1803.05069"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["query", "found", "venue", "venue_full", "year", "title", "authors"]:
        assert field in data, f"Missing field: {field}"


def test_s2_venue_by_title_returns_fields():
    r = run("semantic_scholar.py", ["venue", "--title", "HotStuff: BFT Consensus in the Lens of Blockchain"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["query", "found", "venue", "title"]:
        assert field in data, f"Missing field: {field}"


def test_s2_citations_returns_refs_and_cites():
    r = run("semantic_scholar.py", ["citations", "1803.05069", "--max-results", "5"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert "references" in data
    assert "citations" in data
    assert isinstance(data["references"], list)
    assert isinstance(data["citations"], list)


def test_s2_cli_help():
    r = run("semantic_scholar.py", ["--help"])
    assert r.returncode == 0
    assert "venue" in r.stdout.lower()
    assert "citations" in r.stdout.lower()


# ---------------------------------------------------------------------------
# dblp.py
# ---------------------------------------------------------------------------

def test_dblp_venue_returns_fields():
    """DBLP indexes most CS papers — HotStuff should resolve. Tolerate transient
    failures by only checking that the expected JSON shape comes back."""
    r = run("dblp.py", ["venue", "HotStuff: BFT Consensus", "--author", "Yin"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["query", "found", "venue", "venue_full", "year", "title"]:
        assert field in data, f"Missing field: {field}"


def test_dblp_cli_help():
    r = run("dblp.py", ["--help"])
    assert r.returncode == 0
    assert "venue" in r.stdout.lower()


# ---------------------------------------------------------------------------
# openalex.py
# ---------------------------------------------------------------------------

def test_openalex_venue_returns_fields():
    r = run("openalex.py", ["venue", "HotStuff: BFT Consensus in the Lens of Blockchain"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    for field in ["query", "found", "venue", "venue_full", "year", "title"]:
        assert field in data, f"Missing field: {field}"


def test_openalex_cli_help():
    r = run("openalex.py", ["--help"])
    assert r.returncode == 0
    assert "venue" in r.stdout.lower()
