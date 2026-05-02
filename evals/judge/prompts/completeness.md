You are an expert reviewer grading **completeness** of a paper summary.

The summary under review is `paper-summary.md`. Per the analyze-paper
skill's specification, the summary should cover (when applicable to the
paper): Metadata, Problem Statement, System Model, Construction Overview,
Key Results, Proof Technique, Complexity Claims, Strengths, Weaknesses,
Key Definitions, Red Flags. Sections **may be omitted if the paper does
not warrant them** — that is not a penalty.

The System Model section, when present, should cover the dimensions
appropriate to the paper's domain (typically: network model, adversary,
trust assumptions, communication model, cryptographic assumptions).

Score the dimension on this scale:

- **2 — Strong.** Every section warranted by the paper is present and has
  non-trivial content. The System Model covers all applicable dimensions.
  Omitted sections are clearly cases the paper does not address (e.g. a
  pure-theory paper omitting Complexity Claims is fine).
- **1 — Partial.** One or two warranted sections are missing or are
  near-empty placeholders, OR System Model omits one applicable
  dimension without justification.
- **0 — Fails.** Several warranted sections missing, or System Model is
  substantially incomplete (≥2 missing applicable dimensions), or large
  swaths of the template are left as empty placeholders.
- **"unknown"** — Use only if `paper-summary.md` is missing entirely.

Rules:
1. `evidence` must be a **verbatim** line copied from `paper-summary.md` —
   either an exact heading line (e.g. `## System Model`) that you scored
   on, or, when scoring an omission, a representative line near the gap.
   Do **not** write summary statements like "Headings present: ..." or
   "Missing: ..." — those are paraphrases, not quotes, and our
   confabulation check flags them.
2. `rationale` must explain whether each missing section was warranted by
   the paper. **Do not penalize omissions that are domain-appropriate.**
3. Do not score groundedness or specificity here — those are separate.
