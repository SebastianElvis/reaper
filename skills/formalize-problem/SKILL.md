---
name: formalize-problem
description: "This skill defines a research question as testable hypotheses. You use it to specify model assumptions, properties, and success or failure conditions."
user-invocable: true
argument-hint: "<research-goal>"
license: Apache-2.0
---

# Formalize Problem

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

## Usage

You invoke this skill by name with a quoted research goal. Slash-command hosts use `/formalize-problem "<goal>"`.

```
formalize-problem "determine if the security proof in Section 4 holds under asynchrony"
```

## Instructions

### 1. Read Inputs

You read these inputs:

- `reaper-workspace/notes/clarified-goal.md` supplies the goal, scope, assumptions, and success criteria.
- `reaper-workspace/notes/paper-summary.md` supplies the paper's claims, if this file exists.
- The argument supplies the initial goal. You prefer the refined goal in `clarified-goal.md`.

You read Key Prior Results and Gaps Identified in `reaper-workspace/notes/literature.md`. You read individual paper entries when hypothesis checks need them. Without a paper summary, you use the literature review as the main technical input. You read it in more detail in this case.

### 2. Define the Core Question

You state the exact claim with its property and adversary model.

### 3. Specify Model Assumptions

You use the model dimensions in `../reaper/references/model.md`. You give a concrete answer for each applicable dimension before you create hypotheses. You do not leave fields as `TBD`. Each hypothesis specifies all model parameters that its claim needs.
You reject a hypothesis that omits a relevant dimension.

### 4. Set Priorities

You rank questions by the effect of their answers. You state who needs the answer and why. You use the domain examples in `../reaper/references/model.md`.

### 5. Find Research Gaps

You map existing work across the dimensions in `../reaper/references/model.md`. You use empty combinations as candidate hypotheses.

### 6. Check Impossibility Results

You check each hypothesis against `../reaper/references/impossibility-results.md`. If a known impossibility or lower bound rules out the claim, you take these actions:

1. You identify the conflict in the hypothesis.
2. You change the question to specify additional assumptions or a weaker property.
3. You remove the impossible positive claim from the investigation queue.

### 7. Define Properties

You use the definition forms in `../reaper/references/definitional-standards.md`. You give each core property a precise definition. If the paper uses an informal definition, you provide a formal definition. You state that you made this definition.

### 8. Write Output

You write `reaper-workspace/notes/problem-statement.md` with title `# Problem Statement` and these level-two sections:

- **Research Goal:** You state the precise goal.
- **Model Assumptions:** You give concrete answers for all applicable model dimensions.
- **Security Properties Under Investigation:** You give each property a formal definition or citation.
- **Performance Metrics:** You state applicable communication, round, and other targets.

You write `reaper-workspace/notes/ideas.md` with title `# Ideas` and section `## Initial Ideas`.
Each hypothesis uses `### H1: [Short title]`, with consecutive H numbers.
Each entry has these fields:

- **Statement:** You state a precise claim that evidence can refute.
- **Success condition:** You state the evidence that confirms the claim.
- **Failure condition:** You state the evidence that refutes the claim.
- **Priority:** You use High, Medium, or Low.
- **Rationale:** You explain the effect of resolving the claim.

## Relationship to Brainstorm

This skill defines the initial problem. The `brainstorm` skill revises ideas during investigation. The orchestrator can repeat formalization when the problem changes.

## Quality Criteria

- The hypotheses together answer the research goal.
- You limit the initial set to 5-7 hypotheses. You combine or remove less important ideas if necessary.
- If `clarified-goal.md` is missing, you return an error.
- If `paper-summary.md` is missing, you use `literature.md` and `clarified-goal.md`.
