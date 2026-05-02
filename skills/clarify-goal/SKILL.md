---
name: clarify-goal
description: "Ask the user targeted clarifying questions about their research goal before the pipeline runs. Use when the research goal is vague, ambiguous, or missing key context (e.g., which sections to focus on, threat model assumptions, what 'broken' means). Works with or without a paper."
user-invocable: true
argument-hint: "\"<research-goal>\" [paper-path]"
license: Apache-2.0
---

# Clarify Goal

Ask the user targeted questions to sharpen a vague research goal into something the pipeline can act on precisely.

## Usage

Invoke this skill by name with the research goal (and optional paper path). On slash-command hosts, prefix with `/` (e.g. `/clarify-goal "<goal>"`).

```
# Without a paper — goal-driven research
clarify-goal "explore the feasibility of post-quantum threshold signatures"

# With a paper
clarify-goal "is this protocol secure?" path/to/paper.pdf
```

**Argument parsing:** The research goal (quoted string) is required. If a path to an existing file is also provided, treat it as the paper.

## Instructions

### 1. Read the Paper (quick scan) — if provided

**If a paper path was provided:** Read the paper at the given path. Do a fast scan — you are not producing a full analysis, just enough to understand:
- What the paper is about (topic, system, protocol)
- What it claims (main theorems, security properties, performance results)
- Its structure (which sections cover what)

**If no paper was provided:** Skip this step. You will clarify the goal based on the research prompt alone, using your knowledge of the research domain.

### 2. Identify Ambiguities

Compare the user's research goal against what the paper contains (if provided) or against the research domain in general. Look for:

- **Scope ambiguity**: Does the goal apply to a whole paper/field or specific sections/theorems/protocols?
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
<which parts of the paper/topic are in scope>

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
- The refined goal in `clarified-goal.md` is precise enough for `/formalize-problem` to act on without further clarification
- If the paper PDF is unreadable, report the error — do not proceed with fabricated context

## Important Notes

- This skill is interactive — it requires user input. Do not skip the question-asking step.
- Keep the quick scan fast. Don't spend time on deep analysis — that's what `/analyze-paper` is for.
- If the research goal is already precise and unambiguous (e.g., "Does Theorem 4.2 hold when the adversary controls >1/3 of stake?"), you may skip questions and go straight to writing `clarified-goal.md`. Tell the user the goal is clear and proceed.
- When no paper is provided, focus questions on scoping the research domain, defining key terms, and establishing what kind of output the user expects (survey, feasibility analysis, novel construction, etc.).
