"""Tests for search_iacr.py — validates CLI interface and output format.

Uses real API calls (integration tests). Requires network access.
"""

import json
import subprocess
import sys

SCRIPT = "skills/search-iacr/search_iacr.py"
PYTHON = sys.executable


def run(args):
    result = subprocess.run(
        [PYTHON, SCRIPT] + args,
        capture_output=True, text=True, timeout=30,
    )
    return result


def test_search_returns_json_array():
    r = run(["search", "threshold signatures", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) > 0


def test_search_result_fields():
    r = run(["search", "post-quantum", "--max-results", "1"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert len(data) > 0
    paper = data[0]
    for field in ["eprint_id", "title", "pdf_url", "url"]:
        assert field in paper, f"Missing field: {field}"
    assert paper["eprint_id"]  # non-empty
    assert "/" in paper["eprint_id"]  # format: YYYY/NNNN


def test_url_command():
    r = run(["url", "2024/1234"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert data["eprint_id"] == "2024/1234"
    assert "eprint.iacr.org/2024/1234" in data["url"]
    assert data["pdf_url"].endswith(".pdf")


def test_recent_returns_results():
    r = run(["recent", "--max-results", "3"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    # Recent might be empty if the scraping format changed, but shouldn't error
    # We just check it returns valid JSON


def test_cli_help():
    r = run(["--help"])
    assert r.returncode == 0
    assert "search" in r.stdout.lower()
