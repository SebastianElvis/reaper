"""These graders check sections, table rows, and local links in skill outputs."""

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


# ---------------------------------------------------------------------------
# LaTeX project layout (write-paper)
# ---------------------------------------------------------------------------

_INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
_FLOAT_RE = re.compile(r"\\begin\{(figure|table)\*?\}")


def _tex(path: Path) -> str:
    return re.sub(r"(?<!\\)%.*", "", path.read_text())


def latex_project(root: Path) -> list[GraderResult]:
    """The write-paper project must keep sections, figures, and tables in their own files."""
    sections = sorted((root / "sections").glob("[0-9][0-9]-*.tex"))
    missing = [n for n in ("main.tex", "references.bib", "Makefile", ".gitignore") if not (root / n).is_file()]
    if not sections:
        missing.append("sections/NN-<name>.tex")
    if (root / "Makefile").is_file() and "latexmk" not in (root / "Makefile").read_text():
        missing.append("latexmk in Makefile")
    if missing:
        return [GraderResult("latex_required_files", False, f"missing: {missing}")]
    sources = [root / "main.tex", *sections]
    broken = [f"{p.name}: {t}" for p in sources for t in _INPUT_RE.findall(_tex(p))
              if not (root / t).with_suffix(".tex").is_file()]
    inline = [p.name for p in sources if _FLOAT_RE.search(_tex(p)) or (p.name == "main.tex" and "\\section" in _tex(p))]
    for folder, kind in (("figures", "figure"), ("tables", "table")):
        inline += [f"{folder}/{p.name}" for p in (root / folder).glob("*.tex")
                   if not any(m.group(1) == kind for m in _FLOAT_RE.finditer(_tex(p)))]
    return [
        GraderResult("latex_required_files", True),
        GraderResult("latex_inputs_resolve", not broken, f"missing \\input targets: {broken}" if broken else ""),
        GraderResult("latex_floats_in_own_files", not inline, f"misplaced content: {inline}" if inline else ""),
    ]
