"""These tests check calibration, fresh generation, and cycle consistency."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals import run_evals as runner
from evals.graders import structural  # noqa: E402
from evals.graders.consistency import check_cycle_consistency  # noqa: E402
from evals.run_evals import (  # noqa: E402
    SKILL_STRUCTURAL_RULES,
    list_fixtures,
    load_spec,
    run_structural,
    stage_variant,
    variants_for,
)


# ---------------------------------------------------------------------------
# Fixture-driven structural tests
# ---------------------------------------------------------------------------

def _reference_params():
    return [
        pytest.param(spec, id=f"{load_spec(spec)['skill']}-{load_spec(spec)['case_id']}")
        for spec in list_fixtures()
    ]


def _structural_negative_params():
    out = []
    for spec_path in list_fixtures():
        spec = load_spec(spec_path)
        for v in variants_for(spec):
            if v["kind"] == "negative" and v["target_layer"] == "structural":
                out.append(pytest.param(
                    spec_path, v,
                    id=f"{spec['skill']}-{spec['case_id']}-{v['id']}",
                ))
    return out


@pytest.fixture
def staging_dir(tmp_path: Path) -> Path:
    return tmp_path / "evals-runs"


@pytest.mark.parametrize("spec_path", _reference_params())
def test_reference_passes_structural(spec_path: Path, staging_dir: Path):
    """The gold-standard artifact must pass every structural rule."""
    spec = load_spec(spec_path)
    reference_variant = next(v for v in variants_for(spec) if v["kind"] == "reference")
    trial_dir = stage_variant(spec_path, reference_variant, staging_dir)
    results = run_structural(spec["skill"], trial_dir)
    assert results, (
        f"no structural rules wired up for skill {spec['skill']!r}; "
        f"add an entry to SKILL_STRUCTURAL_RULES"
    )
    failures = [(r.name, r.detail) for r in results if not r.passed]
    assert not failures, f"reference failed: {failures}"


@pytest.mark.parametrize("spec_path,variant", _structural_negative_params())
def test_structural_negative_trips_a_rule(
    spec_path: Path, variant: dict, staging_dir: Path,
):
    """An L1-targeted negative must trip at least one structural rule.

    If this passes, the graders are too permissive — fix the graders, don't
    weaken the negative fixture. Per the eval guide: one-sided evals create
    one-sided optimization, so we test both directions.
    """
    spec = load_spec(spec_path)
    trial_dir = stage_variant(spec_path, variant, staging_dir)
    results = run_structural(spec["skill"], trial_dir)
    failed = [r.name for r in results if not r.passed]
    expected = variant_expected_structural_failures(spec_path, variant["id"])
    if expected:
        missing = [name for name in expected if name not in failed]
        assert not missing, (
            f"structural negative {variant['id']!r} failed to trip expected "
            f"rules: {missing} (got failures: {failed})"
        )
    else:
        assert failed, (
            f"structural negative {variant['id']!r} passed every rule — "
            f"graders for {spec['skill']!r} are too permissive"
        )


def variant_expected_structural_failures(spec_path: Path, variant_id: str) -> list[str]:
    spec = load_spec(spec_path)
    for neg in spec.get("negatives", []):
        if neg["id"] == variant_id:
            return neg.get("expected_failures", {}).get("structural", [])
    return []


# ---------------------------------------------------------------------------
# Direct grader unit tests
# ---------------------------------------------------------------------------

def test_has_sections_detects_missing(tmp_path: Path):
    f = tmp_path / "x.md"
    f.write_text("# A\n\n## B\n")
    assert structural.has_sections(f, ["A", "B"]).passed
    res = structural.has_sections(f, ["A", "B", "C"])
    assert not res.passed
    assert "C" in res.detail


def test_count_table_rows_basic():
    md = (
        "| col1 | col2 |\n"
        "|------|------|\n"
        "| a    | b    |\n"
        "| c    | d    |\n"
    )
    assert structural.count_table_rows(md) == 2


def test_count_table_rows_skips_separator_and_handles_breaks():
    md = (
        "| h |\n|---|\n| 1 |\n\nplain text\n\n"
        "| h2 |\n|----|\n| x |\n| y |\n"
    )
    # 1 row in first table, 2 rows in second
    assert structural.count_table_rows(md) == 3


def test_no_broken_local_links_skips_external(tmp_path: Path):
    target = tmp_path / "target.md"
    target.write_text("ok")
    src = tmp_path / "src.md"
    src.write_text(
        "[external](https://example.com)\n"
        "[ok](target.md)\n"
    )
    assert structural.no_broken_local_links(src, tmp_path).passed


def test_no_broken_local_links_flags_missing(tmp_path: Path):
    src = tmp_path / "src.md"
    src.write_text("[oops](does-not-exist.md)\n")
    res = structural.no_broken_local_links(src, tmp_path)
    assert not res.passed
    assert "does-not-exist.md" in res.detail


# ---------------------------------------------------------------------------
# Cycle consistency (keep-or-discard invariant)
# ---------------------------------------------------------------------------

def _make_snapshot(d: Path, decision: str, understanding: str):
    d.mkdir(parents=True, exist_ok=True)
    (d / "results.md").write_text(
        f"| cycle | hypothesis | decision |\n"
        f"|-------|------------|----------|\n"
        f"| 001   | h1         | {decision} |\n"
    )
    (d / "current-understanding.md").write_text(understanding)


def test_cycle_consistency_passes_on_keep(tmp_path: Path):
    a, b = tmp_path / "001", tmp_path / "002"
    _make_snapshot(a, "keep", "v1")
    _make_snapshot(b, "keep", "v2")
    assert check_cycle_consistency([a, b]).passed


def test_cycle_consistency_passes_on_discard_with_no_change(tmp_path: Path):
    a, b = tmp_path / "001", tmp_path / "002"
    _make_snapshot(a, "keep", "v1")
    _make_snapshot(b, "discard", "v1")
    assert check_cycle_consistency([a, b]).passed


def test_cycle_consistency_fails_on_discard_that_modifies(tmp_path: Path):
    a, b = tmp_path / "001", tmp_path / "002"
    _make_snapshot(a, "keep", "v1")
    _make_snapshot(b, "discard", "v2-but-shouldnt-have-changed")
    res = check_cycle_consistency([a, b])
    assert not res.passed
    assert any("002" in v for v in res.violations)


def test_cycle_consistency_ignores_unrelated_keep_in_prose(tmp_path: Path):
    """Anchored regex: a "keep" word in prose or an unrelated table must
    not be read as the cycle decision. The actual decision row says
    "discard" and `current-understanding.md` did not change → must pass.
    """
    a, b = tmp_path / "001", tmp_path / "002"
    _make_snapshot(a, "keep", "v1")
    b.mkdir()
    (b / "results.md").write_text(
        "Some prose: we should keep the experiment running.\n\n"
        "| unrelated |\n|---|\n| keep alive |\n\n"
        "| cycle | hypothesis | decision |\n"
        "|-------|------------|----------|\n"
        "| 002   | h2         | discard  |\n"
    )
    (b / "current-understanding.md").write_text("v1")
    assert check_cycle_consistency([a, b]).passed


# ---------------------------------------------------------------------------
# Sanity: every skill referenced by a fixture has structural rules
# ---------------------------------------------------------------------------

def test_every_fixture_skill_has_rules():
    specs = set(list_fixtures() + list_fixtures(fresh=True))
    assert specs == set((runner.ROOT / "fixtures").glob("*/*/spec.yaml"))
    for spec_path in specs:
        spec = load_spec(spec_path)
        assert spec["skill"] == spec_path.parent.parent.name
        assert spec["case_id"] == spec_path.parent.name
        assert spec["skill"] in SKILL_STRUCTURAL_RULES
        assert runner.load_rubric(spec["skill"])["dimensions"]


def command(code):
    return shlex.join([sys.executable, "-c", code])


def test_generation_hides_answers_and_preserves_evidence(tmp_path):
    spec = runner.list_fixtures("reaper", fresh=True)[0]
    trial = runner.generate_trial(spec, tmp_path, command(
        "from pathlib import Path; import sys; "
        "assert 'SKILL.md' in sys.stdin.read(); "
        "assert Path('skills/reaper/SKILL.md').is_file(); "
        "assert not list(Path('.').rglob('spec.yaml')); "
        "assert not Path('expectations.md').exists(); "
        "Path('result.md').write_text('The claim remains unresolved.'); "
        "print('The budget is exhausted.')"
    ), 5)
    assert (trial / "artifacts/result.md").read_text() == "The claim remains unresolved."
    assert "Original input" in (trial / "evidence.md").read_text()
    assert (trial / "expectations.md").is_file()
    with pytest.raises(FileExistsError):
        runner.generate_trial(spec, tmp_path, command("print('overwrite')"), 5)


@pytest.mark.parametrize("code, timeout", [("raise SystemExit(2)", 5), ("pass", 5), ("import time; time.sleep(5)", 0.01)])
def test_generation_failure_fails_the_run(tmp_path, monkeypatch, code, timeout):
    root = tmp_path / "evals"
    task = root / "fixtures/reaper/failure"
    (task / "inputs").mkdir(parents=True)
    (task / "spec.yaml").write_text(yaml.safe_dump({
        "skill": "reaper", "case_id": "failure", "goal": "Check the input.", "expectations": "The answer cites evidence."
    }))
    monkeypatch.setattr(runner, "ROOT", root)
    generate = runner.generate_trial
    monkeypatch.setattr(runner, "generate_trial", lambda spec, run, cmd, _: generate(spec, run, cmd, timeout))
    assert runner.main(["--fresh", "--candidate-command", command(code), "--run-id", "failure"]) == 1
    report = json.loads((root / "reports/failure.json").read_text())
    assert report["cases"][0]["structural"][0]["name"] == "execution"
    assert not report["cases"][0]["structural"][0]["passed"]


def test_fresh_cases_have_private_expectations_and_rubrics():
    specs = runner.list_fixtures("reaper", fresh=True)
    assert len(specs) == 4
    for path in specs:
        spec = runner.load_spec(path)
        assert spec["goal"] and spec["expectations"]
        assert (path.parent / "inputs").is_dir()
        assert runner.load_rubric(spec["skill"])["dimensions"]
