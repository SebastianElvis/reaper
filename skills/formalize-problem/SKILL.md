---
name: formalize-problem
description: "This skill defines a research question as testable hypotheses. You use it to specify model assumptions, properties, and success or failure conditions."
user-invocable: true
argument-hint: "<research-goal>"
license: Apache-2.0
---

# Formalize Problem

You apply the [language rules](../reaper/references/language.md) and [research-state.md](../reaper/references/research-state.md).
You convert the clarified goal into precise claims. You preserve its scope.

## Inputs

You read `reaper-workspace/notes/clarified-goal.md` and the relevant source evidence.
You use `paper-summary.md` or `literature.md` when available. Neither file is mandatory when supplied definitions and evidence suffice.
If the goal lacks a required definition or assumption, you invoke `clarify-goal` before continuing.

## Define the Problem

You state the exact question and success criteria.
You specify each applicable model parameter and property. For cryptography or distributed systems, you use `../reaper/references/model.md` and `../reaper/references/definitional-standards.md`.
You identify assumptions that the user supplied separately from assumptions that you propose.
You do not invent missing assumptions to fill a template.
You use `../reaper/references/impossibility-results.md` only when a relevant result may constrain the claim.
A verified impossibility can answer the original question negatively. You preserve that answer. You label a weaker property or changed assumption as a separate hypothesis.

## Write the Formulation

You write `notes/problem-statement.md` with its formulation version and these sections:

- Research Goal states the exact question.
- Model Assumptions specifies applicable parameters and trust requirements.
- Properties Under Investigation gives definitions or precise source references.
- Performance Metrics states applicable costs and comparison conditions.

Before changing an existing formulation, you preserve the old version under the shared contract. You mark affected claims and dependent claims stale.
You create or update `notes/ideas.md` with the shared hypothesis fields. You create only the hypotheses needed to answer the goal.
You rank them by the effect of resolving them. One hypothesis can suffice.
The `brainstorm` skill develops further ideas only when the investigation needs them.
