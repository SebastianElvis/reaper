"""This runner grades saved examples or fresh agent outputs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
import shlex
import sys
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

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
    kind: str
    target_layer: str | None
    structural: list[StructuralReport] = field(default_factory=list)
    judge: list[dict] = field(default_factory=list)

    @property
    def structural_passed(self) -> bool:
        return all(r.passed for r in self.structural)

    @property
    def judge_passed(self) -> bool:
        return bool(self.judge) and all(v["passed"] for v in self.judge)

def list_fixtures(skill_filter: str | None = None, fresh: bool = False) -> list[Path]:
    fixtures_root = ROOT / "fixtures"
    specs = sorted(fixtures_root.glob("*/*/spec.yaml"))
    if skill_filter:
        specs = [s for s in specs if s.parent.parent.name == skill_filter]
    return [s for s in specs if ("expectations" if fresh else "reference") in load_spec(s)]

def load_spec(spec_path: Path) -> dict:
    return yaml.safe_load(spec_path.read_text())

def variants_for(spec: dict) -> list[dict]:
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
    spec_dir = spec_path.parent
    spec = load_spec(spec_path)
    skill = spec["skill"]
    case_id = spec["case_id"]

    trial_dir = run_dir / skill / case_id / variant["id"]
    trial_dir.mkdir(parents=True, exist_ok=False)

    inputs_src = spec_dir / "inputs"
    if inputs_src.is_dir():
        for f in inputs_src.iterdir():
            shutil.copy2(f, trial_dir / f.name)

    artifact_src = spec_dir / variant["artifact"]
    if not artifact_src.is_file():
        raise FileNotFoundError(f"variant artifact not found: {artifact_src}")
    shutil.copy2(artifact_src, trial_dir / artifact_src.name)

    return trial_dir

def generate_trial(spec_path: Path, run_dir: Path, command: str, timeout: int) -> Path:
    spec = load_spec(spec_path)
    trial = run_dir / spec["skill"] / spec["case_id"] / "fresh"
    trial.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="reaper-eval-") as directory:
        work = Path(directory)
        shutil.copytree(spec_path.parent / "inputs", work, dirs_exist_ok=True)
        shutil.copytree(REPO_ROOT / "skills", work / "skills")
        prompt = f"Use skills/{spec['skill']}/SKILL.md. Work only in this directory. " + spec["goal"]
        (trial / "prompt.txt").write_text(prompt)
        proc = subprocess.run(shlex.split(command), input=prompt, cwd=work, text=True,
                              capture_output=True, timeout=timeout, check=False)
        (trial / "stdout.txt").write_text(proc.stdout)
        (trial / "stderr.txt").write_text(proc.stderr)
        if proc.returncode:
            raise ValueError(f"The candidate exited with status {proc.returncode}.")
        if not proc.stdout.strip():
            raise ValueError("The candidate returned no answer.")
        parts = ["# Evidence", "## Response", proc.stdout]
        for source in sorted((spec_path.parent / "inputs").rglob("*")):
            if source.is_file():
                parts.extend([f"## Original input: {source.relative_to(spec_path.parent)}", source.read_text(errors="replace")])
        for source in sorted(work.rglob("*")):
            relative = source.relative_to(work)
            if source.is_file() and not source.is_symlink() and relative.parts[0] != "skills" and source.suffix in {".md", ".txt", ".json", ".tex"}:
                destination = trial / "artifacts" / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                parts.extend([f"## {relative}", source.read_text(errors="replace")])
        (trial / "evidence.md").write_text("\n\n".join(parts))
    (trial / "expectations.md").write_text(spec["expectations"])
    shutil.copytree(spec_path.parent / "inputs", trial / "inputs")
    return trial


SKILL_STRUCTURAL_RULES = {
    "reaper": {"artifact": "evidence.md", "required_sections": ["Response"], "min_chars": 100},
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
        return [StructuralReport("coverage", False, "This skill has no structural rules.")]
    artifact = trial_dir / rules["artifact"]
    results = [
        structural.has_sections(artifact, rules["required_sections"]),
        structural.min_length_chars(artifact, rules["min_chars"]),
    ]
    if skill != "reaper":
        results.append(structural.no_broken_local_links(artifact, trial_dir))
    return [StructuralReport(r.name, r.passed, r.detail) for r in results]

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

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--layer", choices=["structural", "judge", "all"], default="structural")
    p.add_argument("--skill")
    p.add_argument("--variant")
    p.add_argument("--model")
    p.add_argument("--run-id")
    p.add_argument("--fresh", action="store_true")
    p.add_argument("--candidate-command", help="The runner splits this command without a shell.")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args(argv)
    if args.fresh and (not args.candidate_command or args.variant):
        p.error("Fresh runs require --candidate-command and exclude --variant.")
    if args.timeout <= 0:
        p.error("The timeout must be positive.")
    run_id = args.run_id or f"{dt.datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    if Path(run_id).name != run_id or run_id in {".", ".."}:
        p.error("The run ID must be a single directory name.")
    specs = list_fixtures(args.skill, args.fresh)
    if not specs:
        p.error("No cases match the requested skill.")
    run_dir = ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    reports = []
    any_failure = False
    for spec_path in specs:
        spec = load_spec(spec_path)
        variants = [{"id": "fresh", "kind": "fresh", "target_layer": None}] if args.fresh else variants_for(spec)
        for variant in variants:
            if args.variant and variant["id"] != args.variant:
                continue
            report = CaseReport(spec["skill"], spec["case_id"], variant["id"], variant["kind"], variant["target_layer"])
            print(f"==> {report.skill}/{report.case_id}/{report.variant}", flush=True)
            try:
                trial_dir = generate_trial(spec_path, run_dir, args.candidate_command, args.timeout) if args.fresh else stage_variant(spec_path, variant, run_dir)
                if args.layer in ("structural", "all"):
                    report.structural = run_structural(report.skill, trial_dir)
                if args.layer in ("judge", "all"):
                    report.judge = run_judge(report.skill, trial_dir, args.model, trial_id=f"{run_id}/{report.case_id}/{report.variant}")
                if report.kind == "negative":
                    passed = report.structural_passed if report.target_layer == "structural" else report.judge_passed
                    any_failure |= passed and args.layer in (report.target_layer, "all")
                else:
                    any_failure |= args.layer in ("structural", "all") and not report.structural_passed
                    any_failure |= args.layer in ("judge", "all") and not report.judge_passed
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                report.structural.append(StructuralReport("execution", False, str(error)))
                any_failure = True
            reports.append(report)
    if not reports:
        p.error("No variants match the requested filter.")
    env = {"cli_version": claude_cli_version() if args.layer != "structural" else None,
           "judge_model": args.model, "candidate_command": args.candidate_command,
           "mode": "fresh" if args.fresh else "calibration", "timeout": args.timeout}
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / f"{run_id}.md").write_text(render_markdown(reports, run_id, env))
    (reports_dir / f"{run_id}.json").write_text(json.dumps({"run_id": run_id, "env": env, "cases": [asdict(r) for r in reports]}, indent=2))
    print(f"Report: {reports_dir / run_id}.json")
    return int(any_failure)


if __name__ == "__main__":
    sys.exit(main())
