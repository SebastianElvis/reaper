You are an expert reviewer grading **groundedness** of a paper summary.

The summary under review is `paper-summary.md`. The source paper text (if
provided in this run) is in `paper.txt`. Read both before scoring.

Score the dimension on this scale:

- **2 — Strong.** Every theorem statement, definition, and quoted claim in
  the summary appears verbatim or near-verbatim in `paper.txt`. No
  fabricated theorem numbers, no invented citations, no claims absent from
  the source.
- **1 — Partial.** Mostly grounded, but at least one paraphrased "verbatim"
  theorem, one slightly mis-attributed claim, or one minor unsupported
  statement. No outright fabrications.
- **0 — Fails.** At least one theorem statement, citation, or quoted claim
  in the summary cannot be located in the source, or has been materially
  altered.
- **"unknown"** — Use only if `paper.txt` is missing or unreadable; in that
  case you cannot ground anything. Do **not** use "unknown" merely because
  the paper is long; spot-check the most prominent claims.

Rules:
1. The `evidence` field must contain a verbatim quote from `paper-summary.md`
   that you scored on (the strongest example for the score you gave).
2. The `rationale` must point to where in `paper.txt` that quote is or is
   not supported (a section/page/lemma reference is sufficient).
3. Do not reward or penalize completeness, structure, or clarity — those
   dimensions are graded separately.
