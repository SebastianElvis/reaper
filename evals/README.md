# Reaper evals

Layered evaluation for the Reaper skills, following [*Demystifying Evals
for AI Agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
The model-based judge is the local `claude` CLI — no API key required.

## Three layers

| Layer | Grader | Cost | Cadence | What it covers |
|---|---|---|---|---|
| **L1 Structural** | Code (`evals/graders/`) | Free | Every PR (CI) | Required sections present, min lengths, no broken refs, keep-or-discard cycle invariant |
| **L2 Skill rubric** | `claude -p` (`evals/judge/`) | Subscription tokens | Locally / nightly | Per-skill quality dimensions (groundedness, specificity, completeness) |
| **L3 End-to-end** | Both | Subscription tokens | Pre-release | Full `/reaper` pipeline against the 3 cases in `evals/evals.json` |

## Layout

```
evals/
  evals.json                 # case registry (kept for human reference)
  fixtures/<skill>/<case>/   # one directory per fixture
    spec.yaml                # variant declarations + expected layer outcomes
    inputs/                  # what the skill consumes (paper text, etc.)
    reference/               # gold-standard output (must pass every layer)
    negative-structural/     # planted L1 violation (drops a section, etc.)
    negative-quality/        # planted L2 violation (fabricated claim, etc.)
  rubrics/<skill>.yaml       # which dimensions apply, and their pass thresholds
  judge/
    judge.py                 # claude CLI wrapper, JSON-schema enforced
    schemas/rubric.json      # per-dimension structured-output shape
    prompts/<dimension>.md   # one judge persona per rubric dimension
  graders/
    structural.py            # L1 assertion helpers (pure Python)
    consistency.py           # cycle invariant verifier
  run_evals.py               # orchestrator
  runs/                      # per-trial workspaces (gitignored)
  reports/                   # md + json reports (gitignored)
```

## Running

```bash
# L1 only — same thing CI runs (no claude CLI required)
python3 -m evals.run_evals --layer structural

# L2 only — judges every variant of every fixture (uses claude CLI)
python3 -m evals.run_evals --layer judge --skill analyze-paper

# Full run (L1 + L2)
python3 -m evals.run_evals --layer all --skill analyze-paper

# One variant of one case
python3 -m evals.run_evals --layer all --skill analyze-paper --variant reference
```

The orchestrator stages each variant into a fresh `evals/runs/<run-id>/`
directory before grading — per the eval guide's "isolated environments"
recommendation. Reports land in `evals/reports/<run-id>.{md,json}`.

The pytest entry point that CI uses lives at `tests/test_skill_outputs.py`
and exercises the same L1 graders.

## Adding a fixture

1. Create `evals/fixtures/<skill>/<case>/`.
2. Put what the skill consumes under `inputs/` (paper text, prior notes, etc.).
3. Hand-write a gold-standard output under `reference/`.
4. Write at least one **structural negative** (drops a required section, etc.)
   under `negative-structural/` and one **quality negative** (fabricated
   claim, generic content) under `negative-quality/`. One-sided evals create
   one-sided optimization; both directions matter.
5. Declare the variants in `spec.yaml` (see the existing
   `cryptography-sample` fixture). Each negative carries a `target_layer`
   so the orchestrator knows which grader is supposed to fail.
6. If this is a new skill, add an entry to `SKILL_STRUCTURAL_RULES` in
   `evals/run_evals.py` and a rubric file under `evals/rubrics/`.

`tests/test_skill_outputs.py::test_every_fixture_skill_has_rules` will fail
if you add a fixture without graders — coverage without graders is invisible.

## Adding a judge dimension

1. Drop a per-dimension prompt at `evals/judge/prompts/<dim>.md`. Lead with
   the score scale, require a verbatim `evidence` quote, and include the
   `"unknown"` escape hatch (the schema enforces these fields, but the
   prompt has to ask for them clearly).
2. Add the dimension to the skill's rubric YAML, with a `passing_score`.
3. Calibrate before relying on it: hand-grade ~10 transcripts, compare to
   judge verdicts, iterate the prompt until ≥80% agreement. Keep the
   calibration corpus under `evals/golden/`.

## Calibration

To check whether a judge prompt agrees with expert opinion, run it against
the gold reference and the planted negative for a fixture:

```bash
python3 -m evals.run_evals --layer judge --skill analyze-paper --variant reference
python3 -m evals.run_evals --layer judge --skill analyze-paper --variant quality
```

Expected: reference passes every dimension; the quality negative fails the
dimensions it's planted to violate (see `expected_failures.judge` in
`spec.yaml`). When they don't, fix the prompt, not the fixture.

## Why `claude -p` and not the API?

- No API key in CI or in maintainer envs — uses each maintainer's local
  `claude` CLI auth (subscription or `claude setup-token`).
- `--allowedTools ""` makes the judge a pure grader (no tool calls).
- `--json-schema` pins the output shape — prompt drift can't reshape the
  result.
- `--no-session-persistence` + per-trial `--add-dir` keep trials isolated.
- `--model claude-opus-4-7` is pinned, so judge drift is detectable when
  the model is bumped.
