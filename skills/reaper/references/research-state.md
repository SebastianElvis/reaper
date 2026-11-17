# Research State

## Shared Budget

You record the goal, output type, cycle limit, consumed cycles, reservations, and stop reason in `notes/research-state.md`.
You use the user's cycle limit. Otherwise, you use 3 cycles for a narrow claim or 10 cycles for open research.
A standalone investigation uses its requested count, or 5 cycles, as its run limit. A standalone critique reports proposed actions without starting research. A new user request can establish a new limit explicitly in the record.
Each cycle tests one hypothesis. Nested proof and counterexample checks share that cycle.
The main agent reserves a cycle before dispatch. A reserved cycle consumes budget even if the worker fails or the run stops.
Only the main agent changes the budget. Workers return results without starting additional cycles.
You reconcile reservations with logs on resume. You never reuse a consumed cycle number.
If an older workspace has no budget record, you count distinct logged cycles and incomplete investigation attempts before setting the remaining budget.
Reformulation, critique, retries, and publication audits never reset the budget.
You stop new research at the limit. You still summarize findings and unresolved claims.

## Claim Evidence

You use stable claim IDs in `notes/current-understanding.md` and investigation files.
Each material claim records these fields:

- The statement gives the exact claim and its formulation version.
- The assumptions give the model and parameter limits.
- The evidence gives the source version and page, section, or theorem location. A local link identifies each proof, counterexample, or test.
- The dependencies identify claims that the argument uses.
- The report locations identify sections and theorem labels that use the claim.
- The status is `verified`, `refuted`, `conjecture`, `unresolved`, or `stale`.
- The limits identify proof gaps, unchecked cases, and conflicting evidence.

You preserve evidence type. A test of finite cases does not establish a general theorem. Model agreement does not replace proof verification.
You check the evidence before assigning `verified` or `refuted`. Confidence alone does not establish either status.
When an assumption or dependency changes, you mark affected claims and their dependent claims `stale`. You remove them from accepted conclusions until revalidation.
You preserve old evidence with its original formulation version. You do not apply it silently to the new model.
The report includes source citations and proof or test references.

## Conflicting Results

You compare the exact statements, assumptions, and evidence of conflicting results.
You replay a counterexample or check its trace. You locate the proof step that excludes or permits it.
You accept an outcome only after that check resolves the conflict. Otherwise, you record `unresolved` and explain the disagreement.
You do not select a result by completion time, model vote, author reputation, or venue.

## Workspace Ownership and Recovery

All paths in this contract are relative to `reaper-workspace/`.
The main agent creates missing notes and preserves existing files on resume.
The main agent owns shared notes during investigation batches. Workers return findings and literature additions without changing shared files.
Each worker has a distinct output path. The main agent merges proof and counterexample work only after checking both results.
The responsible stage writes its output outside active batches. The writer can add report locations to claim records but cannot raise claim confidence.
Cycle logs and feedback records are immutable. Each new file uses an unused number above the highest existing number for its prefix.
You preserve downloaded papers locally. You do not commit files merely because later stages need them.
You ignore generated build files in version control.
You reconstruct progress from reservations, cycle logs, and investigation evidence. A report's existence does not establish completion.

## Hypotheses and Formulations

Each hypothesis in `notes/ideas.md` has a stable H number, Statement, Assumptions or formulation version, Success condition, Failure condition, Priority, Rationale, and Source.
You use High, Medium, or Low priority. You cite the originating goal, finding, or review in Source.
You update priorities and statuses in place. You assign a new H number when the claim or its assumptions change materially.
Before replacing a formulation, you preserve `notes/problem-statement.md` as `notes/problem-statement-v<N>.md` using its old version number.
You never overwrite an existing version file. You increment the active version and mark dependent claims stale.
You preserve the original question and any supported negative answer. A changed model is a separate alternative.

## Results and Review Records

`notes/results.md` uses one current row per hypothesis with columns Cycle, Hypothesis, Action, Outcome, Confidence, Status, and Description.
A revisit updates its existing row. The cycle log preserves the earlier result.
Outcomes are `confirmed`, `refuted`, `partially-confirmed`, `inconclusive`, `new-hypothesis`, or `reformulate`.
`confirmed` requires verified evidence for the stated claim. `partially-confirmed` requires a verified narrower result. A proof gap alone gives `inconclusive`.
Confidence is `high`, `medium`, or `low`. You derive it from evidence and preserve its scope.
Status is `keep` for useful progress and `discard` otherwise. A refutation can be useful progress. Neither status proves a claim.
Each completed cycle creates `logs/cycle-NNN-<slug>.md`. Its title is `# Cycle NNN: <hypothesis title>`. It records Hypothesis, Action, Outcome, Confidence, Verdict, and a Summary with evidence links.
An interrupted reservation still consumes budget. You record the interruption when resuming without inventing completed evidence.
Reviews use `feedbacks/round-N.md` or `feedbacks/codex-consultation-N.md`. They do not create cycle logs unless an actual investigation cycle occurs.
