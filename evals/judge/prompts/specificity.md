You are an expert reviewer grading **specificity** of a paper summary.

The summary under review is `paper-summary.md`. Look in particular at the
**Strengths**, **Weaknesses**, and **Red Flags** sections.

Score the dimension on this scale:

- **2 — Strong.** Every strength/weakness/red-flag points to a specific
  artifact in the paper: a named lemma, a section, a proof step, an
  experimental table, an assumption, etc. Severity labels
  (major/minor/fatal for weaknesses) are applied per the skill's
  specification.
- **1 — Partial.** Most items are specific, but one or more are generic
  ("the writing could be clearer", "evaluation is limited") without a
  concrete pointer. Severity labels mostly present.
- **0 — Fails.** Most items are generic, missing pointers to specific
  paper artifacts, or severity labels are absent where required.
- **"unknown"** — Use only if the relevant sections are entirely missing
  (in which case Completeness will catch it).

Rules:
1. `evidence` must quote one bullet from `paper-summary.md` — pick the
   weakest one if the score is 0 or 1, or a representative one if 2.
2. `rationale` explains why that bullet is or is not specific (what
   pointer is missing, or what specific artifact is named).
3. Do not penalize the summary for missing sections — that is the
   completeness dimension. Score only the items that *are* present.
