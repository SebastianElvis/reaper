"""Eval orchestrator.

Modes:

  L1 only (no LLM, no network — runs in CI on every PR):
      python -m evals.run_evals --layer structural [--skill analyze-paper]

  L1 + L2 (uses `claude` CLI as judge — locally, on demand):
      python -m evals.run_evals --layer all --skill analyze-paper

  Calibration (judge against the gold reference, not a fresh skill output):
      python -m evals.run_evals --layer judge --skill analyze-paper \\
          --variant reference   # expect passes
      python -m evals.run_evals --layer judge --skill analyze-paper \\
          --variant negative    # expect failures

For each fixture, the orchestrator stages artifacts under
`evals/runs/<run-id>/<skill>/<case>/<variant>/` (clean per the eval guide's
"isolated environments" requirement) and runs:

  - structural graders (cheap, deterministic — see graders/structural.py),
  - one judge call per rubric dimension (see judge/judge.py).

Reports go to evals/reports/<run-id>.{md,json}.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

# Make `from evals.judge.judge import ...` work when invoked as a script.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.graders import structural  # noqa: E402
from evals.judge.judge import (  # noqa: E402
    JudgeError,
    JudgeVerdict,
    build_user_prompt,
    claude_cli_version,
    evidence_supported_by,
    grade_dimension,
)

SCHEMA_PATH = ROOT / "judge" / "schemas" / "rubric.json"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class StructuralReport:
    name: str
    passed: bool
    detail: str


@dataclass
class CaseReport:
    skill: str
    case_id: str
    variant: str
    kind: str  # "reference" | "negative"
    target_layer: str | None  # only set on negatives
    structural: list[StructuralReport] = field(default_factory=list)
    judge: list[dict] = field(default_factory=list)

    @property
    def structural_passed(self) -> bool:
        return all(r.passed for r in self.structural)

    @property
    def judge_passed(self) -> bool:
        return bool(self.judge) and all(v["passed"] for v in self.judge)


# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------

def list_fixtures(skill_filter: str | None = None) -> list[Path]:
    """Return spec.yaml paths for every fixture (optionally filtered by skill)."""
    fixtures_root = ROOT / "fixtures"
    specs = sorted(fixtures_root.glob("*/*/spec.yaml"))
    if skill_filter:
        specs = [s for s in specs if s.parent.parent.name == skill_filter]
    return specs


def load_spec(spec_path: Path) -> dict:
    return yaml.safe_load(spec_path.read_text())


# ---------------------------------------------------------------------------
# Trial isolation — copy fixture artifacts into a fresh run dir
# ---------------------------------------------------------------------------

def variants_for(spec: dict) -> list[dict]:
    """Return a list of variant descriptors {id, kind, artifact, target_layer?}.

    `kind` is one of "reference" or "negative". Negatives carry a
    `target_layer` so the orchestrator knows which grader is supposed to
    fail (structural-targeted negatives are L1's problem; judge-targeted
    negatives are L2's).
    """
    out: list[dict] = [{
        "id": "reference",
        "kind": "reference",
        "artifact": spec["reference"]["artifact"],
        "target_layer": None,
    }]
    for neg in spec.get("negatives", []):
        out.append({
            "id": neg["id"],
            "kind": "negative",
            "artifact": neg["artifact"],
            "target_layer": neg.get("target_layer", "judge"),
        })
    return out


def stage_variant(spec_path: Path, variant: dict, run_dir: Path) -> Path:
    """Copy `inputs/` and the variant artifact into a clean trial dir.

    Returns the trial directory. Per the eval methodology: every trial gets
    a fresh, isolated environment. The judge's --add-dir points here.
    """
    spec_dir = spec_path.parent
    spec = load_spec(spec_path)
    skill = spec["skill"]
    case_id = spec["case_id"]

    trial_dir = run_dir / skill / case_id / variant["id"]
    if trial_dir.exists():
        shutil.rmtree(trial_dir)
    trial_dir.mkdir(parents=True)

    inputs_src = spec_dir / "inputs"
    if inputs_src.is_dir():
        for f in inputs_src.iterdir():
            shutil.copy2(f, trial_dir / f.name)

    artifact_src = spec_dir / variant["artifact"]
    if not artifact_src.is_file():
        raise FileNotFoundError(f"variant artifact not found: {artifact_src}")
    shutil.copy2(artifact_src, trial_dir / artifact_src.name)

    return trial_dir


# ---------------------------------------------------------------------------
# Structural (L1)
# ---------------------------------------------------------------------------

# Per-skill structural specs derived from evals.json's skill_unit_tests.
# Keep this small and readable; per-fixture overrides live in spec.yaml
# (we'll layer that in when more skills are wired up).
SKILL_STRUCTURAL_RULES = {
    "analyze-paper": {
        "artifact": "paper-summary.md",
        "required_sections": [
            "Metadata",
            "Problem Statement",
            "Key Results",
            "Strengths",
            "Weaknesses",
            "Red Flags",
        ],
        "min_chars": 400,
    },
}


def run_structural(skill: str, trial_dir: Path) -> list[StructuralReport]:
    rules = SKILL_STRUCTURAL_RULES.get(skill)
    if not rules:
        return []
    artifact = trial_dir / rules["artifact"]
    results = [
        structural.has_sections(artifact, rules["required_sections"]),
        structural.min_length_chars(artifact, rules["min_chars"]),
        structural.no_broken_local_links(artifact, trial_dir),
    ]
    return [StructuralReport(r.name, r.passed, r.detail) for r in results]


# ---------------------------------------------------------------------------
# Judge (L2)
# ---------------------------------------------------------------------------

def load_rubric(skill: str) -> dict:
    rubric_path = ROOT / "rubrics" / f"{skill}.yaml"
    if not rubric_path.is_file():
        raise FileNotFoundError(f"no rubric for skill: {skill} ({rubric_path})")
    return yaml.safe_load(rubric_path.read_text())


def run_judge(
    skill: str,
    trial_dir: Path,
    model: str | None,
    *,
    trial_id: str,
) -> list[dict]:
    rubric = load_rubric(skill)
    verdicts: list[dict] = []
    for dim in rubric["dimensions"]:
        prompt_path = ROOT / "judge" / dim["prompt"]
        artifact_paths = [trial_dir / name for name in dim["applies_to"]]
        user_prompt = build_user_prompt(
            dimension=dim["name"],
            artifact_name=rubric["artifact"],
            artifact_paths=artifact_paths,
            salt=f"{trial_id}/{dim['name']}",
        )
        try:
            verdict: JudgeVerdict = grade_dimension(
                dimension=dim["name"],
                system_prompt_path=prompt_path,
                user_prompt=user_prompt,
                schema_path=SCHEMA_PATH,
                **({"model": model} if model else {}),
            )
            # Post-hoc anti-confabulation check: every quote in `evidence`
            # should be locatable in at least one source artifact. Surface
            # but don't block — the heuristic has false negatives.
            sources = [
                p.read_text(errors="replace")
                for p in artifact_paths
                if p.is_file()
            ]
            grounded = evidence_supported_by(verdict.evidence, sources)
            verdicts.append({
                "dimension": dim["name"],
                "score": verdict.score,
                "passed": verdict.meets(dim["passing_score"]),
                "passing_score": dim["passing_score"],
                "evidence": verdict.evidence,
                "evidence_grounded": grounded,
                "rationale": verdict.rationale,
            })
        except JudgeError as e:
            verdicts.append({
                "dimension": dim["name"],
                "score": "error",
                "passed": False,
                "passing_score": dim["passing_score"],
                "evidence": "",
                "evidence_grounded": False,
                "rationale": f"judge error: {e}",
            })
    return verdicts


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def render_markdown(reports: list[CaseReport], run_id: str, env: dict) -> str:
    lines = [f"# Eval report `{run_id}`", ""]
    lines.append(
        f"_Environment: claude CLI {env.get('cli_version', 'unknown')}, "
        f"judge model {env.get('judge_model', 'default')}._"
    )
    lines.append("")
    for r in reports:
        lines.append(f"## {r.skill} / {r.case_id} / {r.variant}")
        lines.append("")
        if r.structural:
            lines.append("**Structural (L1):**")
            for s in r.structural:
                mark = "PASS" if s.passed else "FAIL"
                detail = f" — {s.detail}" if s.detail else ""
                lines.append(f"- [{mark}] {s.name}{detail}")
            lines.append("")
        if r.judge:
            lines.append("**Judge (L2):**")
            for v in r.judge:
                mark = "PASS" if v["passed"] else "FAIL"
                grounded = "" if v.get("evidence_grounded", True) \
                    else " ⚠ evidence not located in source"
                lines.append(
                    f"- [{mark}] {v['dimension']}: score={v['score']} "
                    f"(needs ≥{v['passing_score']}){grounded}"
                )
                lines.append(f"    - evidence: {v['evidence']!r}")
                lines.append(f"    - rationale: {v['rationale']}")
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--layer", choices=["structural", "judge", "all"], default="structural",
        help="`structural` = L1 only (no LLM); `judge` = L2 only; `all` = both",
    )
    p.add_argument("--skill", default=None, help="Filter to one skill")
    p.add_argument(
        "--variant", default=None,
        help="Filter to one variant id (default: all variants from spec.yaml)",
    )
    p.add_argument("--model", default=None, help="Override judge model")
    p.add_argument("--run-id", default=None, help="Run identifier (default: timestamp+uuid)")
    args = p.parse_args(argv)

    run_id = args.run_id or f"{dt.datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    run_dir = ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    specs = list_fixtures(args.skill)
    if not specs:
        print(f"No fixtures found (skill filter: {args.skill!r})", file=sys.stderr)
        return 2

    reports: list[CaseReport] = []
    any_failure = False
    for spec_path in specs:
        spec = load_spec(spec_path)
        skill = spec["skill"]
        case_id = spec["case_id"]
        for variant in variants_for(spec):
            if args.variant and variant["id"] != args.variant:
                continue
            print(f"==> {skill}/{case_id}/{variant['id']}")
            trial_dir = stage_variant(spec_path, variant, run_dir)
            report = CaseReport(
                skill=skill,
                case_id=case_id,
                variant=variant["id"],
                kind=variant["kind"],
                target_layer=variant["target_layer"],
            )
            if args.layer in ("structural", "all"):
                report.structural = run_structural(skill, trial_dir)
            if args.layer in ("judge", "all"):
                trial_id = f"{run_id}/{skill}/{case_id}/{variant['id']}"
                report.judge = run_judge(
                    skill, trial_dir, args.model, trial_id=trial_id,
                )
            reports.append(report)

            # Expectations:
            #   reference  : every active layer must pass.
            #   negative   : the layer it targets must fail.
            if variant["kind"] == "reference":
                if args.layer in ("structural", "all") and not report.structural_passed:
                    any_failure = True
                if args.layer in ("judge", "all") and not report.judge_passed:
                    any_failure = True
            else:  # negative
                tl = variant["target_layer"]
                if tl == "structural" and args.layer in ("structural", "all"):
                    if report.structural_passed:
                        any_failure = True  # graders too permissive
                if tl == "judge" and args.layer in ("judge", "all"):
                    if report.judge_passed:
                        any_failure = True  # judge missed the planted flaw

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    md_path = reports_dir / f"{run_id}.md"
    json_path = reports_dir / f"{run_id}.json"
    env = {
        "cli_version": claude_cli_version() if args.layer != "structural" else None,
        "judge_model": args.model,
    }
    md_path.write_text(render_markdown(reports, run_id, env))
    json_path.write_text(json.dumps(
        {"run_id": run_id, "env": env, "cases": [asdict(r) for r in reports]},
        indent=2, default=str,
    ))
    print(f"\nReport: {md_path}")
    return 1 if any_failure else 0


if __name__ == "__main__":
    sys.exit(main())
