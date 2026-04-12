---
name: clarify-goal
description: "Ask the user targeted clarifying questions about their research goal before the pipeline runs. Use when the research goal is vague, ambiguous, or missing key context (e.g., which sections to focus on, threat model assumptions, what 'broken' means)."
user-invocable: true
argument-hint: "<paper-path> \"<research-goal>\""
---

# Clarify Goal

Ask the user targeted questions to sharpen a vague research goal into something the pipeline can act on precisely.

## Usage

```
/reaper:clarify-goal path/to/paper.pdf "is this protocol secure?"
```

## Instructions

### 1. Read the Paper (quick scan)

Read the paper at the given path. Do a fast scan — you are not producing a full analysis, just enough to understand:
- What the paper is about (topic, system, protocol)
- What it claims (main theorems, security properties, performance results)
- Its structure (which sections cover what)

### 2. Identify Ambiguities

Compare the user's research goal against what the paper actually contains. Look for:

- **Scope ambiguity**: Does the goal apply to the whole paper or specific sections/theorems/protocols?
- **Definition ambiguity**: Does the goal use terms that could mean multiple things? (e.g., "secure" — against what adversary? under what model?)
- **Success criteria ambiguity**: What would a satisfying answer look like? A counterexample? A proof gap? A performance bound?
- **Assumption ambiguity**: Are there implicit assumptions the user might want to constrain or relax? (e.g., synchrony vs. asynchrony, static vs. adaptive adversary)
- **Comparison ambiguity**: If the goal involves comparison ("is this better than X?"), what metric and what baseline?

### 3. Ask Questions

Ask the user **3-5 targeted questions** (no more). Each question should:
- Be specific to the paper and goal, not generic
- Offer concrete options where possible (e.g., "Do you mean the safety proof in Section 4.2 or the liveness proof in Section 5.1?")
- Have a sensible default so the user can skip questions they don't care about

Format as a numbered list. After the questions, state what you'll assume if they don't answer a particular question (the defaults).

### 4. Incorporate Answers

After the user responds:
- Merge their answers with your defaults for any unanswered questions
- Write the refined research goal and key context to `reaper-workspace/notes/clarified-goal.md`

The file should contain:
```markdown
# Clarified Research Goal

## Original Goal
<what the user initially said>

## Clarifying Q&A
<numbered list of each question you asked and the user's answer, or "(default)" if they didn't answer>

## Refined Goal
<precise, unambiguous version incorporating the user's answers>

## Scope
<which parts of the paper are in scope>

## Key Assumptions
<assumptions that the investigation should operate under>

## Success Criteria
<what a satisfying answer looks like>
```

### 5. Report

Tell the user the refined goal and confirm before the pipeline proceeds.

## Quality Criteria

- Questions are specific to the paper and goal, not generic
- Each question offers concrete options or defaults
- The refined goal in `clarified-goal.md` is precise enough for `formalize-problem` to act on without further clarification
- If the paper PDF is unreadable, report the error — do not proceed with fabricated context

## Important Notes

- This skill is interactive — it requires user input. Do not skip the question-asking step.
- Keep the quick scan fast. Don't spend time on deep analysis — that's what `analyze-paper` is for.
- If the research goal is already precise and unambiguous (e.g., "Does Theorem 4.2 hold when the adversary controls >1/3 of stake?"), you may skip questions and go straight to writing `clarified-goal.md`. Tell the user the goal is clear and proceed.
