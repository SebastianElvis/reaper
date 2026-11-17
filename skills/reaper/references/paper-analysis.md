# Paper Reading Guide

You use up to three passes, following [Keshav's reading method](https://cs.uwaterloo.ca/~brecht/courses/Perf-Eval-Shared/readings/keshav-paper-reading.pdf).
You stop when the reading supports the requested task. Relevance alone does not require full proof verification.

## Reading Depth

1. You read the title, abstract, introduction, headings, and conclusion. You identify the question and main claims.
2. You inspect the methods, figures, evaluation, and argument structure. You identify definitions and references needed for the task.
3. You reconstruct the relevant arguments and inspect their assumptions, detailed proofs, and appendices when the task requires verification.

You record the reading depth and unchecked sections. You describe a source claim as a source claim until you check its evidence.
A summary does not certify a proof. A failed verification attempt does not establish that the theorem is false.

## Evidence Checks

You inspect the claims, model, definitions, and evidence relevant to the goal.
You use the [analysis output fields](../../analyze-paper/SKILL.md); this reference does not define a second output format.
You preserve exact mathematical statements when needed. You distinguish exact quotations from paraphrases and provide source locations.
You check whether the conclusion answers the question posed in the introduction.

## Warning Signs

These observations prompt a check. They do not prove an error:

- A proof omits a necessary step, adversary behavior, or abort case.
- A claimed appendix or supporting artifact is missing.
- The proof uses stronger timing or trust assumptions than the statement allows.
- A safety argument supplies no evidence for a claimed liveness property.
- A reduction omits runtime, loss, or query limits.
- An adaptive-security claim has only a static-corruption argument.
- A comparison changes the model or metric without explaining the effect.
- An experiment omits uncertainty, baselines, or configuration details needed to interpret the result.
- A result depends on an idealized setup or oracle without stating its limits.

You name the exact location and consequence of each supported issue. You also record evidence that resolves a suspected issue.
