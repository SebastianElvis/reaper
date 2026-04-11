# Definitional Standards

Domain-specific reference for enforcing definitional hygiene and composition awareness. The standards below are for cryptography and distributed systems. For other research domains, adapt this file with the relevant definitional forms and composition considerations for that field.

## Acceptable Definition Forms

Each security property or core claim must be stated as one of:

- A **formal predicate** over executions/views (e.g., "For all executions E, if honest parties p_i and p_j both output, then output(p_i) = output(p_j)")
- A **game-based definition** (e.g., "For all PPT adversaries A, Pr[Game^A = 1] <= negl(lambda)")
- A **simulation-based definition** (e.g., "There exists a PPT simulator S such that REAL ~=_c IDEAL")
- A **reference** to a specific definition in a specific paper (e.g., "Agreement as defined in [CKPS01, Definition 2]")

Informal terms like "safety" or "liveness" without a formal definition are NOT acceptable. Different papers define these differently — pin it down. If the paper under analysis uses informal definitions, formalize them explicitly and note that you are doing so.

## Composition Awareness

When a security property is confirmed, note the composition implications:

- Does the proof use rewinding? If so, it likely doesn't compose (not UC-secure).
- Does the protocol use a CRS? Is the CRS shared with other protocols?
- Is the result in the standalone model, sequential composition, or UC?
- If the paper claims the protocol is "used as a building block" in a larger system, does the proven security level actually support that usage?

Log composition limitations even if the original hypothesis didn't ask about composition — this is critical context for the final report.
