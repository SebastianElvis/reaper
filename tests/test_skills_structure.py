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


# ---------------------------------------------------------------------------
# Path-portability regression tests (host-agnostic skills package)
# ---------------------------------------------------------------------------

# Skill files that ship inter-skill or intra-skill path references. Each is
# checked for both: (a) no relative `python skills/...` invocations have crept
# back in, and (b) every {{*_SKILL_DIR}} placeholder used in the file is also
# defined somewhere in the file.
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
    "skills/search-arxiv/SKILL.md",
    "skills/search-iacr/SKILL.md",
]


def test_no_relative_python_skills_invocations():
    """Regression: skills must never invoke `python skills/<name>/...` directly.

    Such relative paths only resolve if the user happens to be running the
    agent from the repo root. After `npx skills add`, the scripts live under
    a per-host install dir (e.g. ~/.agents/skills/, ~/.cursor/skills/), so
    skills must use the {{SEARCH_*_SKILL_DIR}} placeholders that the agent
    substitutes at execution time.
    """
    pattern = re.compile(r"python\s+skills/")
    offenders = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        content = p.read_text()
        for m in pattern.finditer(content):
            # Find the offending line
            line_no = content[: m.start()].count("\n") + 1
            offenders.append(f"{path}:{line_no}")
    assert not offenders, (
        "Found relative `python skills/...` invocations — these break under "
        "npx skills install (scripts live in per-host install dirs, not "
        "under skills/). Use the {{SEARCH_ARXIV_SKILL_DIR}} / "
        "{{SEARCH_IACR_SKILL_DIR}} placeholders instead. Offenders: "
        + ", ".join(offenders)
    )


def test_skill_dir_placeholders_are_defined():
    """Every {{*SKILL_DIR}} placeholder used in a skill must also be defined
    in that same file (so the agent has the substitution rules co-located
    with the references that need substituting). A 'definition' is any
    mention of the placeholder inside a Path-Resolution-style block — we
    detect this by requiring the placeholder appears in a paragraph that
    also contains the word 'install' or 'substitute' or 'resolve' (the
    standardized preamble vocabulary).

    Matches both the multi-skill form ({{REAPER_SKILL_DIR}},
    {{SEARCH_ARXIV_SKILL_DIR}}, {{SEARCH_IACR_SKILL_DIR}}) and the
    own-directory form ({{SKILL_DIR}}) used by leaf skills like
    search-arxiv and search-iacr.
    """
    placeholder_pattern = re.compile(r"\{\{([A-Z_]*SKILL_DIR)\}\}")
    # Words that appear in a definition paragraph (per the standardized
    # Path Resolution Protocol preamble).
    definition_keywords = ("install", "substitute", "resolve", "denote", "absolute")

    failures = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        content = p.read_text()
        used = set(placeholder_pattern.findall(content))
        if not used:
            continue
        # Split into paragraphs and find which paragraphs define a placeholder
        paragraphs = re.split(r"\n\s*\n", content)
        defined = set()
        for para in paragraphs:
            if not any(kw in para.lower() for kw in definition_keywords):
                continue
            for ph in placeholder_pattern.findall(para):
                defined.add(ph)
        missing = used - defined
        if missing:
            failures.append(f"{path}: uses {sorted(missing)} but never defines them")
    assert not failures, (
        "Some skills reference {{*_SKILL_DIR}} placeholders without a local "
        "definition paragraph. Each skill that uses a placeholder must "
        "include a Path Resolution Protocol section that lists install "
        "locations and tells the agent to substitute it. Failures:\n  "
        + "\n  ".join(failures)
    )


def test_path_resolution_protocol_section_present():
    """Skills that use {{*SKILL_DIR}} placeholders must declare a
    'Path Resolution Protocol' section so the convention is visually
    obvious to readers and downstream auditors. Matches both the
    multi-skill placeholders (e.g. {{REAPER_SKILL_DIR}}) and the leaf
    own-directory form ({{SKILL_DIR}})."""
    placeholder_pattern = re.compile(r"\{\{[A-Z_]*SKILL_DIR\}\}")
    failures = []
    for path in PATH_AWARE_SKILLS:
        p = Path(path)
        if not p.exists():
            continue
        content = p.read_text()
        if not placeholder_pattern.search(content):
            continue
        if "Path Resolution Protocol" not in content:
            failures.append(path)
    assert not failures, (
        "Skills that use path placeholders must declare a 'Path Resolution "
        "Protocol' section. Missing in: " + ", ".join(failures)
    )
