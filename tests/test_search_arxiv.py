"""Tests for search_arxiv.py — validates CLI interface and output format.

Uses real API calls (integration tests). Requires network access.
"""

import json
import subprocess
import sys

SCRIPT = "skills/search-arxiv/search_arxiv.py"
PYTHON = sys.executable


def run(args):
    result = subprocess.run(
        [PYTHON, SCRIPT] + args,
        capture_output=True, text=True, timeout=30,
    )
    return result


def test_search_returns_json_array():
    r = run(["search", "Byzantine fault tolerance", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data) <= 3


def test_search_result_fields():
    r = run(["search", "threshold signatures", "--max-results", "1"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    paper = data[0]
    for field in ["arxiv_id", "title", "authors", "year", "abstract", "pdf_url"]:
        assert field in paper, f"Missing field: {field}"
    assert isinstance(paper["authors"], list)
    assert isinstance(paper["year"], int)
    assert paper["title"]  # non-empty


def test_search_with_categories():
    r = run(["search", "consensus protocol", "--max-results", "2", "--categories", "cs.CR,cs.DC"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert len(data) > 0


def test_citations_returns_refs_and_cites():
    """Test citation graph for a well-known paper (HotStuff)."""
    r = run(["citations", "1803.05069", "--max-results", "5"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert "references" in data
    assert "citations" in data
    assert isinstance(data["references"], list)
    assert isinstance(data["citations"], list)
    # HotStuff is well-cited, should have both
    assert len(data["references"]) > 0 or len(data["citations"]) > 0


def test_search_empty_query_returns_results():
    """Even a broad query should return something."""
    r = run(["search", "cryptography", "--max-results", "2"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert len(data) > 0


def test_cli_help():
    r = run(["--help"])
    assert r.returncode == 0
    assert "search" in r.stdout.lower()
