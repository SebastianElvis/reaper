---
name: clarify-goal
description: "This skill asks questions to define a research goal. You use it when the scope, assumptions, or success criteria are unclear."
user-invocable: true
argument-hint: "\"<research-goal>\" [paper-path]"
license: Apache-2.0
---

# Clarify Goal

You must read and apply the [language rules](../reaper/references/language.md) before you write any output.

## Usage

You invoke this skill by name with a quoted goal and an optional paper path. Slash-command hosts use `/clarify-goal "<goal>"`.

```
clarify-goal "explore the feasibility of post-quantum threshold signatures"
clarify-goal "is this protocol secure?" path/to/paper.pdf
```

The quoted research goal is required. An additional path to an existing file identifies the paper.

## Instructions

### 1. Read the Paper

If the user supplies a paper, you scan it for this information:

- The paper's topic, system, and protocol.
- The paper's main theorems, security properties, and performance results.
- The sections that contain each result.

You leave full analysis to the `analyze-paper` skill. If the user supplies no paper, you use the goal and research domain.

### 2. Identify Unclear Requirements

You check the goal against the paper or research domain.

- **Scope:** You determine which papers, sections, theorems, or protocols the goal covers.
- **Definitions:** You identify terms with multiple meanings, such as security under different adversary models.
- **Success criteria:** You determine whether the user needs a counterexample, proof gap, or performance bound.
- **Assumptions:** You identify assumptions that the user can change, such as synchrony or adversary type.
- **Comparison:** You identify the metric and baseline for each comparison.

### 3. Ask Questions

You ask 3-5 questions that address the paper and goal. Each question offers concrete options where possible. Each question has a default answer. You use a numbered list. You state the defaults for questions that the user does not answer.

### 4. Use the Answers

After the user responds, you combine their answers with defaults for unanswered questions. You write `reaper-workspace/notes/clarified-goal.md` with title `# Clarified Research Goal` and these level-two sections:

| Section | Content |
|---|---|
| Original Goal | You copy the user's goal exactly. |
| Clarifying Q&A | You record each question and exact answer. You label unanswered items `(default)` and state the default. |
| Refined Goal | You state the precise goal with the user's answers. |
| Scope | You identify the parts of the paper or topic that the research covers. |
| Key Assumptions | You state investigation assumptions. |
| Success Criteria | You state the evidence that answers the goal. |

### 5. Report

You state the refined goal. You ask the user to confirm it before the pipeline continues.

## Quality Criteria

- The refined goal gives `formalize-problem` enough information to proceed.
- If the PDF is unreadable, you report the error. You do not invent context.

## Exceptions

- If the goal is unclear, you ask questions and request confirmation. Without a paper, you ask about the domain, terms, and expected output.
- If the goal is precise, you can omit questions and confirmation. You write `clarified-goal.md`, state that the goal is clear, and continue.
