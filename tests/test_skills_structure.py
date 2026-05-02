"""Tests for H1/H2 skill structure — validates all SKILL.md files exist,
have correct frontmatter, and reference the right files.

These are offline tests (no network needed).
"""

import re
from pathlib import Path

SKILLS_DIR = Path("skills")

EXPECTED_SKILLS = {
    # H1
    "reaper": "skills/reaper/SKILL.md",
    "clarify-goal": "skills/clarify-goal/SKILL.md",
    "analyze-paper": "skills/analyze-paper/SKILL.md",
    "review-literature": "skills/review-literature/SKILL.md",
    "formalize-problem": "skills/formalize-problem/SKILL.md",
    "brainstorm": "skills/brainstorm/SKILL.md",
    "investigate": "skills/investigate/SKILL.md",
    "critique": "skills/critique/SKILL.md",
    "synthesize": "skills/synthesize/SKILL.md",
    # H2
    "search-paper": "skills/search-paper/SKILL.md",
}

EXPECTED_REFERENCES = [
    "skills/reaper/references/methodology.md",
    "skills/reaper/references/paper-analysis.md",
    "skills/reaper/references/search-tools.md",
]

EXPECTED_SCRIPTS = [
    "skills/search-paper/arxiv.py",
    "skills/search-paper/iacr.py",
    "skills/search-paper/semantic_scholar.py",
    "skills/search-paper/dblp.py",
    "skills/search-paper/openalex.py",
]


def test_all_skill_files_exist():
    for name, path in EXPECTED_SKILLS.items():
        assert Path(path).exists(), f"Missing skill: {name} at {path}"


def test_all_reference_files_exist():
    for path in EXPECTED_REFERENCES:
        assert Path(path).exists(), f"Missing reference: {path}"


def test_all_scripts_exist():
    for path in EXPECTED_SCRIPTS:
        assert Path(path).exists(), f"Missing script: {path}"


def test_skill_frontmatter_format():
    """Every SKILL.md must satisfy the vercel-labs/skills parser:
    - name matches [a-z][a-z0-9-]* and equals the directory name
    - description is non-empty
    Also asserts the Claude-Code-specific user-invocable key is present.
    """
    name_pattern = re.compile(r"^[a-z][a-z0-9-]*$")
    for name, path in EXPECTED_SKILLS.items():
        content = Path(path).read_text()
        assert content.startswith("---"), f"{path}: missing frontmatter"
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"{path}: malformed frontmatter"
        fm = parts[1]

        name_match = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
        assert name_match, f"{path}: missing 'name' in frontmatter"
        parsed_name = name_match.group(1).strip("\"'")
        assert name_pattern.match(parsed_name), (
            f"{path}: name '{parsed_name}' must match [a-z][a-z0-9-]* "
            f"(npx skills requirement)"
        )
        assert parsed_name == name, (
            f"{path}: frontmatter name '{parsed_name}' must equal directory "
            f"name '{name}' (npx skills resolves skills by directory)"
        )

        desc_match = re.search(r"^description:\s*(.+)", fm, re.MULTILINE)
        assert desc_match, f"{path}: missing 'description' in frontmatter"
        desc = desc_match.group(1).strip().strip("\"'")
        assert desc, f"{path}: empty description"

        assert "user-invocable:" in fm, f"{path}: missing 'user-invocable' in frontmatter"


def test_marketplace_json_lists_all_skills():
    """marketplace.json's skills array must list every directory under skills/."""
    import json
    marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())
    listed = set()
    for plugin in marketplace.get("plugins", []):
        for skill_path in plugin.get("skills", []):
            listed.add(Path(skill_path).name)
    expected = set(EXPECTED_SKILLS.keys())
    missing = expected - listed
    extra = listed - expected
    assert not missing, f"marketplace.json missing skills: {missing}"
    assert not extra, f"marketplace.json lists unknown skills: {extra}"


def test_review_literature_delegates_to_search_paper():
    """review-literature must delegate paper search, download, citation graph,
    and venue resolution to the /search-paper skill rather than invoking its
    scripts directly, and must stay fully path-agnostic."""
    content = Path("skills/review-literature/SKILL.md").read_text()
    assert "/search-paper" in content, "review-literature doesn't reference the /search-paper skill"
    # Must not reach into any platform driver by name — those are /search-paper's concern.
    for script in ("arxiv.py", "iacr.py", "semantic_scholar.py", "dblp.py", "openalex.py"):
        assert script not in content, (
            f"review-literature references {script} directly; delegate to /search-paper instead"
        )
    # Must remain fully path-agnostic — the review-literature skill never
    # reaches into another skill's filesystem directly.
    assert "../search-paper" not in content and "../reaper" not in content, (
        "review-literature should not include sibling-skill paths; it "
        "delegates by skill name only."
    )


def test_investigate_references_search_scripts():
    """H2: investigate should reference the search scripts for mid-cycle search."""
    content = Path("skills/investigate/SKILL.md").read_text()
    assert "iacr.py" in content, "investigate doesn't reference iacr.py"
    assert "arxiv.py" in content, "investigate doesn't reference arxiv.py"


def test_review_literature_has_graceful_degradation():
    """H2: review-literature should handle search script failures."""
    content = Path("skills/review-literature/SKILL.md").read_text()
    assert "graceful degradation" in content.lower() or "fallback" in content.lower() or "Graceful Degradation" in content


def test_review_literature_has_citation_graph():
    """H2: review-literature should include citation graph traversal."""
    content = Path("skills/review-literature/SKILL.md").read_text()
    assert "citation" in content.lower()
    assert "citations" in content  # references the citations command


def test_review_literature_has_recent_papers():
    """H2: review-literature should check recent papers."""
    content = Path("skills/review-literature/SKILL.md").read_text()
    assert "recent" in content.lower()


def test_search_tools_reference_exists_and_complete():
    """The search-tools reference doc should cover all five platform scripts."""
    content = Path("skills/reaper/references/search-tools.md").read_text()
    for script in ("arxiv.py", "iacr.py", "semantic_scholar.py", "dblp.py", "openalex.py"):
        assert script in content, f"search-tools.md missing reference to {script}"
    assert "Decision Tree" in content or "decision tree" in content
    assert "Graceful" in content or "fallback" in content.lower()
    assert "Venue Resolution Protocol" in content, "search-tools.md missing the layered venue protocol"


def test_evals_json_valid():
    """evals.json should be valid JSON with expected structure."""
    import json
    content = Path("evals/evals.json").read_text()
    data = json.loads(content)
    assert "test_cases" in data
    assert "skill_unit_tests" in data
    assert len(data["test_cases"]) >= 3
    assert len(data["skill_unit_tests"]) >= 5


def test_readme_mentions_prerequisites():
    """README should document Python prerequisites."""
    content = Path("README.md").read_text()
    assert "pip install" in content
    assert "arxiv" in content
    assert "beautifulsoup4" in content


def test_readme_lists_search_skills():
    """README should list the unified search-paper skill."""
    content = Path("README.md").read_text()
    assert "search-paper" in content


# ---------------------------------------------------------------------------
# Path-portability regression tests (host-agnostic skills package)
# ---------------------------------------------------------------------------
#
# Per the Agent Skills specification (https://agentskills.io/specification),
# file references inside a skill must use **relative paths from the skill
# root**. Cross-skill references rely on `npx skills add` co-installing all
# skills as siblings under the host's skills directory.

PATH_AWARE_SKILLS = [
    "skills/reaper/SKILL.md",
    "skills/reaper/references/search-tools.md",
    "skills/reaper/references/codex-consultation.md",
    "skills/clarify-goal/SKILL.md",
    "skills/analyze-paper/SKILL.md",
    "skills/review-literature/SKILL.md",
    "skills/formalize-problem/SKILL.md",
    "skills/brainstorm/SKILL.md",
    "skills/investigate/SKILL.md",
    "skills/critique/SKILL.md",
    "skills/synthesize/SKILL.md",
    "skills/search-paper/SKILL.md",
]


def test_no_skill_dir_placeholders():
    """The `{{*SKILL_DIR}}` placeholder convention has been replaced by
    spec-compliant relative paths. Regression: no placeholders should
    reappear in any skill or reference file.
    """
    placeholder_pattern = re.compile(r"\{\{[A-Z_]*SKILL_DIR\}\}")
    offenders = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        if placeholder_pattern.search(p.read_text()):
            offenders.append(path)
    assert not offenders, (
        "Found {{*SKILL_DIR}} placeholders. Use relative paths instead "
        "(e.g. `../reaper/references/methodology.md` for sibling-skill "
        "references, bare filename for same-directory scripts). "
        "Offenders: " + ", ".join(offenders)
    )


def test_no_python2_invocations():
    """Skills should invoke `python3` rather than `python` for portability
    across hosts where `python` may not exist."""
    pattern = re.compile(r"\bpython (?=[a-zA-Z_./])")
    offenders = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        content = p.read_text()
        for m in pattern.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            offenders.append(f"{path}:{line_no}")
    assert not offenders, (
        "Found `python ...` invocations — use `python3 ...` for portability. "
        "Offenders: " + ", ".join(offenders)
    )


def test_no_relative_python_skills_invocations():
    """Skills must never invoke `python3 skills/<name>/...` from inside a
    SKILL.md — such paths only resolve at the repo root, not after install.
    """
    pattern = re.compile(r"python3?\s+skills/")
    offenders = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        content = p.read_text()
        for m in pattern.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            offenders.append(f"{path}:{line_no}")
    assert not offenders, (
        "Found `python skills/...` invocations — use relative paths from "
        "the skill root instead (e.g. `../search-paper/arxiv.py`). "
        "Offenders: " + ", ".join(offenders)
    )
