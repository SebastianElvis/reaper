---
name: critique
description: "This skill reviews research findings with user feedback, Codex, or self-review. You use it to check results or direct more investigation."
user-invocable: true
argument-hint: "\"<feedback>\" | --codex | --self"
license: Apache-2.0
compatibility: "Codex mode requires an MCP host with the codex-cli server. Other modes need no additional tools."
---

# Critique

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

## Usage

You invoke this skill by name with quoted feedback, `--codex`, or `--self`. Slash-command hosts use `/critique <args>`.

```
critique "dig deeper into the liveness proof gap under partial synchrony"
critique --codex
critique --self
```

## Inputs

You always read these sources:

- `reaper-workspace/notes/current-understanding.md`
- `reaper-workspace/notes/results.md`
- `reaper-workspace/notes/problem-statement.md`
- `reaper-workspace/notes/ideas.md`
- `reaper-workspace/feedbacks/`

You read these sources only when a specific question needs them:

- `reaper-workspace/notes/paper-summary.md`, if it exists.
- `reaper-workspace/notes/literature.md`
- `reaper-workspace/papers/`

## Human Feedback

Quoted feedback selects this mode.

### 1. Set the Round Number

You check `reaper-workspace/feedbacks/round-*.md`. N is one greater than the highest existing round, or 1 for the first round.

### 2. Classify and Save Feedback

You split mixed feedback into distinct requests. You assign one category to each request.
You write `reaper-workspace/feedbacks/round-N.md`:

```markdown
# Feedback Round N

**User request**: [You copy the user's feedback exactly.]

**Category**: [scope | deepen | explore | rewrite]

**Action plan**: [You state the required actions.]
```

| Category | Required change |
|---|---|
| `scope` | The feedback changes assumptions, the threat model, or the research question. |
| `deepen` | The feedback requests more evidence for a specific claim or proof step. |
| `explore` | The feedback requests research on a topic that the report does not cover. |
| `rewrite` | The feedback changes only clarity, structure, or presentation. |

### 3. Act on Feedback

- **scope:** You return to the orchestrator with a request to run `formalize-problem` again. You do not run investigation cycles yet.
- **deepen:** You invoke the `brainstorm` skill with the feedback context. You then invoke the `investigate` skill with `5`.
- **explore:** You search for additional literature if necessary. You update `literature.md`, invoke `brainstorm` with the feedback context, then invoke `investigate` with `5`.
- **rewrite:** You return to the orchestrator with a request to run `synthesize` again.

After deepen or explore cycles, the orchestrator invokes `synthesize` for an updated report.

## Codex Consultation (`--codex`)

You use Codex through MCP for a separate review. You follow `../reaper/references/codex-consultation.md` for setup, fallback, context size, and session continuity.

### Select a Role

You count existing `codex-consultation-*.md` files in `reaper-workspace/feedbacks/`. The next consultation number N follows that count.

For odd N, you ask Codex to challenge the findings. You send these inputs:

- The last five findings from `current-understanding.md`, in about 500 words.
- A summary of recent results, including keep and discard counts and patterns.
- A review request that names exact claims, concerns, and reasons, including weak evidence, hidden assumptions, or alternative explanations.

For even N, you ask Codex for alternative approaches. You send these inputs:

- The last five findings, in about 500 words.
- Only unresolved hypotheses from `ideas.md`.
- A request for alternative proof methods, techniques from other fields, and new hypotheses.

You limit context to about 800 words without full workspace files.

### Process Feedback

1. You save the response to `reaper-workspace/feedbacks/codex-consultation-N.md`.
2. You add a hypothesis for each supported gap or useful alternative technique.
3. You continue H numbers from the highest number in `ideas.md`.
4. You tag new hypotheses `[Codex-N]` in the Source field.
5. You record a short explanation for feedback that previous work covers or evidence rejects.
6. If the MCP call fails or times out, you log the failure and return.

You use one Codex session ID for the full investigation run. You pass it through `sessionId`, with a value such as `"reaper-critique-<timestamp>"`.

## Self-Review (`--self`)

You check your own findings for these issues:

- **Conflicts:** You identify incompatible claims within `current-understanding.md` or between that file and `results.md`.
- **Evidence gaps:** You identify unchecked assumptions or weak claims without an identified conflict.
- **New questions:** You identify questions outside the existing claims and assumptions.

For each issue that needs action, you add a hypothesis with the next H number. You tag it `[Self-N]` in the Source field. N is one greater than the number of previous self-review rounds. If you add hypotheses, you invoke the `investigate` skill with `3`.
You record self-review findings in cycle logs under `reaper-workspace/logs/`. You do not create a separate self-review file.

## Quality Criteria

- Each investigation and critique loop creates a cycle log. You never change an existing log.
- New hypotheses include source tags: `[Round N]`, `[Codex-N]`, or `[Self-N]`.
- Additional cycles use the normal investigation process.
