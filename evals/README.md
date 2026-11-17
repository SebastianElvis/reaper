# Reaper evals

Layered evaluation for the Reaper skills, following [*Demystifying Evals
for AI Agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
The model-based judge is the local `claude` CLI — no API key required.

## Evaluation modes

The default mode grades saved examples. This mode checks grader calibration.
The fresh mode runs a candidate agent before grading its new response and workspace.
The fresh cases cover false claims, conflicting evidence, interrupted runs, and budget exhaustion.
Structural checks verify artifact shape. Judge checks assess behavior. A structural pass alone does not establish research correctness.

## Layout

```
evals/
  fixtures/<skill>/<case>/   # one directory per fixture
    spec.yaml                # variant declarations + expected layer outcomes
    inputs/                  # what the skill consumes (paper text, etc.)
    reference/               # This optional directory stores a calibration output.
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

You run calibration without an agent:

```bash
python3 -m evals.run_evals --layer structural
```

You run fresh tasks with a candidate command that reads the task from stdin:

```bash
python3 -m evals.run_evals --fresh --skill reaper --layer all --timeout 180 \
  --candidate-command 'claude -p --no-session-persistence --permission-mode acceptEdits --tools Read,Write,Edit,Glob,Grep --allowedTools Read,Write,Edit,Glob,Grep --strict-mcp-config --disable-slash-commands'
```

The runner executes the command without a shell. Each task uses a new temporary directory outside the repository. The directory contains only task inputs and the current skills. The runner withholds expected answers from the candidate prompt and workspace.
The directory provides test isolation, not an operating-system sandbox. The command must use appropriate host permissions.
The runner saves the response, original inputs, and generated text artifacts before it removes the temporary directory. The judge receives those records and the private expectations.
A failed command, timeout, or empty response fails the case. The runner never replaces an existing run directory.
The reports record the candidate command and judge model. You can pin the candidate model in its command.
You use `--layer structural` for a transport check without a judge. You do not treat that result as a behavior evaluation.

## Adding a case

You create `evals/fixtures/<skill>/<case>/spec.yaml` with `skill`, `case_id`, and `goal` fields.
You put source files and any prior workspace in `inputs/`.
You add `expectations` for a fresh case. The runner withholds these expectations from the candidate.
You add `reference` and `negatives` for calibration. Each negative names its target layer and expected failures.
A case can support both modes. The runner selects cases by these fields. Reference outputs remain optional for fresh cases.
You add structural rules and a skill rubric when the skill has no graders.
The tests check case discovery, metadata, graders, isolation, and failure reporting in `tests/test_skill_outputs.py`.

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

## Research checks

The research judge checks proof gaps, fair protocol comparisons, security claims, literature support, and requested publication outputs when these checks apply.
The source selection guidance remains in `dev/test-papers/README.md`. These suggested papers do not count as executed cases until a fixture supplies their inputs and expectations.
Search API tests remain in `tests/test_search_paper.py`. Cycle consistency checks remain in `graders/consistency.py`.
