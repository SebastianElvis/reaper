"""Code-based (L1) graders.

These are deterministic, cheap, and run on every PR. They test that skill
outputs satisfy structural invariants from `evals/evals.json` (sections
present, table row counts, JSON shape, no broken file references).

L1 catches regressions; subjective quality is left to L2 LLM-judge graders.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GraderResult:
    name: str
    passed: bool
    detail: str = ""

    def __bool__(self) -> bool:
        return self.passed


# ---------------------------------------------------------------------------
# Markdown structure
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def markdown_headings(text: str) -> list[str]:
    """Return all heading titles in document order (level-agnostic)."""
    return [m.group(2).strip() for m in _HEADING_RE.finditer(text)]


def has_sections(path: Path, required: list[str]) -> GraderResult:
    """Every name in `required` must appear as a markdown heading."""
    if not path.is_file():
        return GraderResult("has_sections", False, f"missing file: {path}")
    headings = set(markdown_headings(path.read_text()))
    missing = [s for s in required if s not in headings]
    return GraderResult(
        name="has_sections",
        passed=not missing,
        detail=f"missing sections: {missing}" if missing else "",
    )


# ---------------------------------------------------------------------------
# Markdown tables (results.md, literature.md)
# ---------------------------------------------------------------------------

def count_table_rows(text: str) -> int:
    """Count GitHub-flavored markdown table data rows.

    Skips header and the `|---|---|` separator. Counts only lines that look
    like `| ... |` after that separator, across every table in the document.
    """
    total = 0
    in_table = False
    saw_separator = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                saw_separator = False
                continue  # header row
            if not saw_separator and re.match(r"^\|[\s:|-]+\|$", stripped):
                saw_separator = True
                continue
            if saw_separator:
                total += 1
        else:
            in_table = False
            saw_separator = False
    return total


def min_table_rows(path: Path, minimum: int) -> GraderResult:
    if not path.is_file():
        return GraderResult("min_table_rows", False, f"missing file: {path}")
    n = count_table_rows(path.read_text())
    return GraderResult(
        name="min_table_rows",
        passed=n >= minimum,
        detail=f"found {n} rows (need ≥{minimum})",
    )


# ---------------------------------------------------------------------------
# Reference integrity
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[[^\]]+\]\((?P<href>[^)]+)\)")


def no_broken_local_links(path: Path, root: Path) -> GraderResult:
    """All relative-path links in `path` must resolve under `root`.

    Skips http(s):, mailto:, fragment-only, and absolute paths — those are
    out of scope for structural grading.
    """
    if not path.is_file():
        return GraderResult("no_broken_local_links", False, f"missing file: {path}")
    text = path.read_text()
    broken: list[str] = []
    for m in _LINK_RE.finditer(text):
        href = m.group("href").split("#", 1)[0].split(" ", 1)[0]
        if not href:
            continue
        if href.startswith(("http://", "https://", "mailto:", "/")):
            continue
        target = (path.parent / href).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            broken.append(href)
            continue
        if not target.exists():
            broken.append(href)
    return GraderResult(
        name="no_broken_local_links",
        passed=not broken,
        detail=f"broken links: {broken}" if broken else "",
    )


# ---------------------------------------------------------------------------
# Plain-text invariants
# ---------------------------------------------------------------------------

def contains(path: Path, needle: str, *, case_insensitive: bool = False) -> GraderResult:
    if not path.is_file():
        return GraderResult("contains", False, f"missing file: {path}")
    haystack = path.read_text()
    if case_insensitive:
        ok = needle.lower() in haystack.lower()
    else:
        ok = needle in haystack
    return GraderResult(
        name="contains",
        passed=ok,
        detail="" if ok else f"missing substring: {needle!r}",
    )


def min_length_chars(path: Path, minimum: int) -> GraderResult:
    if not path.is_file():
        return GraderResult("min_length_chars", False, f"missing file: {path}")
    n = len(path.read_text().strip())
    return GraderResult(
        name="min_length_chars",
        passed=n >= minimum,
        detail=f"length {n} chars (need ≥{minimum})",
    )
