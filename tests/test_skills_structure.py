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
    "analyze-paper": "skills/analyze-paper/SKILL.md",
    "review-literature": "skills/review-literature/SKILL.md",
    "formalize-problem": "skills/formalize-problem/SKILL.md",
    "investigate": "skills/investigate/SKILL.md",
    "critique": "skills/critique/SKILL.md",
    "synthesize": "skills/synthesize/SKILL.md",
    # H2
    "search-arxiv": "skills/search-arxiv/SKILL.md",
    "search-iacr": "skills/search-iacr/SKILL.md",
}

EXPECTED_REFERENCES = [
    "skills/reaper/references/methodology.md",
    "skills/reaper/references/paper-analysis.md",
    "skills/reaper/references/search-tools.md",
]

EXPECTED_SCRIPTS = [
    "skills/search-arxiv/search_arxiv.py",
    "skills/search-iacr/search_iacr.py",
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
    """Every SKILL.md must have name, description, user-invocable in frontmatter."""
    for name, path in EXPECTED_SKILLS.items():
        content = Path(path).read_text()
        assert content.startswith("---"), f"{path}: missing frontmatter"
        # Extract frontmatter
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"{path}: malformed frontmatter"
        fm = parts[1]
        assert "name:" in fm, f"{path}: missing 'name' in frontmatter"
        assert "description:" in fm, f"{path}: missing 'description' in frontmatter"
        assert "user-invocable:" in fm, f"{path}: missing 'user-invocable' in frontmatter"


def test_review_literature_references_search_scripts():
    """H2: review-literature should reference the search scripts."""
    content = Path("skills/review-literature/SKILL.md").read_text()
    assert "search_arxiv.py" in content, "review-literature doesn't reference search_arxiv.py"
    assert "search_iacr.py" in content, "review-literature doesn't reference search_iacr.py"


def test_investigate_references_search_scripts():
    """H2: investigate should reference the search scripts for mid-cycle search."""
    content = Path("skills/investigate/SKILL.md").read_text()
    assert "search_iacr.py" in content, "investigate doesn't reference search_iacr.py"
    assert "search_arxiv.py" in content, "investigate doesn't reference search_arxiv.py"


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
    """The search-tools reference doc should cover both scripts."""
    content = Path("skills/reaper/references/search-tools.md").read_text()
    assert "search_arxiv.py" in content
    assert "search_iacr.py" in content
    assert "Decision Tree" in content or "decision tree" in content
    assert "Graceful" in content or "fallback" in content.lower()


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
    """README should list the new search skills."""
    content = Path("README.md").read_text()
    assert "search-arxiv" in content
    assert "search-iacr" in content
