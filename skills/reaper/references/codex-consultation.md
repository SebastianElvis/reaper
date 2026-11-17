# External Review Protocol

The `--codex` option requests external review through the host's registered Codex MCP tools.
You discover the available tool schema. You do not assume a tool name or a `sessionId` parameter.
The `critique` skill owns external review. Other stages return review questions to the orchestrator rather than starting duplicate consultations.

## Evidence and Continuity

You send the goal, exact claim, assumptions, evidence locations, and the proof or test under review.
You summarize unrelated context. You do not impose a word cap that removes evidence needed to check the claim.
You include relevant excerpts when the reviewer cannot read local paths. You label the review incomplete when required evidence remains inaccessible.
You reuse a returned session identifier only when the tool supports it. Otherwise, each review receives the necessary context.

## Logging and Fallback

You save each request, response, limitation, and resulting action to `feedbacks/codex-consultation-N.md`.
N is one greater than the highest existing consultation number. You never overwrite a prior record.
If the tool fails or is unavailable, you record the failure and report it to the user. You then perform the self-review defined in `critique`.
You distinguish external feedback from verified evidence. A reviewer suggestion does not establish a claim.
All resulting research uses the existing shared budget.
