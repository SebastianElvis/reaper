"""Claude CLI judge wrapper.

Invokes `claude -p` as a model-based grader. The judge receives:
  - a system prompt (per-dimension rubric),
  - the artifact(s) to grade (read from disk via --add-dir),
  - a JSON Schema that pins the output shape.

Design choices follow Anthropic's "Demystifying Evals for AI Agents":
  - --allowedTools "" : the judge has no tools, eliminating any risk of it
    "doing the work" instead of grading it.
  - --json-schema     : structured output enforces (score, evidence, rationale)
    so prompt drift cannot reshape the result.
  - one call per dimension, never holistic — reduces hallucinated scores.
  - --no-session-persistence : every trial is fresh; no shared state.
  - pinned --model    : judge drift is detectable when the model is bumped.

This module never reads ANTHROPIC_API_KEY; it relies entirely on the user's
local `claude` CLI authentication (subscription or `claude setup-token`).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_TIMEOUT_SEC = 180


class JudgeError(RuntimeError):
    """Raised when the judge invocation or its output is unusable."""


@dataclass(frozen=True)
class JudgeVerdict:
    """One dimension's verdict on one artifact set.

    `score` is 0, 1, 2, or the string "unknown" (the escape hatch that lets
    the judge abstain when evidence is insufficient — recommended by the
    eval methodology to reduce hallucinated grades).
    """

    dimension: str
    score: int | str
    evidence: str
    rationale: str
    raw: dict

    def meets(self, passing_score: int) -> bool:
        """Pass/fail against the *rubric's* threshold — not a global default.

        `unknown` always fails: an abstaining judge cannot certify a pass.
        """
        return isinstance(self.score, int) and self.score >= passing_score

    @property
    def is_unknown(self) -> bool:
        return self.score == "unknown"


def _claude_path() -> str:
    path = shutil.which("claude")
    if not path:
        raise JudgeError(
            "`claude` CLI not found on PATH. Install Claude Code "
            "(https://docs.anthropic.com/en/docs/claude-code) and run "
            "`claude auth` or `claude setup-token`."
        )
    return path


def build_user_prompt(
    *,
    dimension: str,
    artifact_name: str,
    artifact_paths: list[Path],
    salt: str | None = None,
) -> str:
    """Assemble the judge's user message with artifact contents inlined.

    Embedding the files (rather than letting the judge read them via tools)
    is deliberate:
      - the judge needs no tools, so we can run it with --tools "" which
        eliminates the multi-turn read/explore loop that otherwise burns
        tokens and makes JSON-schema conformance harder for the model;
      - the artifact set the judge sees is fully reproducible from the
        prompt — calibration is meaningful;
      - cost is bounded and predictable per call.

    `salt` is included in the prompt header so two near-identical variants
    (or repeated trials of the same variant) don't collide on the prompt
    cache — that would make pass^k consistency look fake.

    Reads use `errors="replace"` so a non-UTF-8 byte in an artifact does
    not abort the eval. The judge sees `\\ufffd` and can score "unknown" if
    the corruption made the artifact unreadable.
    """
    parts: list[str] = [
        f"Grade the artifact `{artifact_name}` for the `{dimension}` "
        f"dimension. The artifact and any supporting files are embedded "
        f"below between fenced markers. Return your verdict as JSON "
        f"matching the schema.",
    ]
    if salt:
        parts.append(f"\n[trial-id: {salt}]")
    for p in artifact_paths:
        if not p.is_file():
            parts.append(f"\n=== {p.name} (NOT FOUND) ===\n")
            continue
        parts.append(f"\n=== {p.name} ===\n")
        parts.append(p.read_text(errors="replace"))
        parts.append(f"\n=== end {p.name} ===\n")
    return "".join(parts)


def claude_cli_version() -> str:
    """Capture the local CLI version for the run report.

    Logged alongside results so a silent CLI bump does not invalidate
    historical comparisons (per Anthropic's guide: "monitor for
    distribution drift").
    """
    try:
        proc = subprocess.run(
            [_claude_path(), "--version"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        return proc.stdout.strip() or proc.stderr.strip() or "unknown"
    except (subprocess.TimeoutExpired, JudgeError):
        return "unknown"


def evidence_supported_by(evidence: str, sources: list[str]) -> bool:
    """Cheap defense against judge confabulation.

    True if the evidence quote (after whitespace normalization) appears as
    a substring of at least one source. Quotation marks and ellipses are
    stripped because the judge often wraps quotes. This is a *signal*, not
    a hard guarantee — a clever judge could echo a phrase that happens to
    occur for unrelated reasons. We use it to flag suspicious verdicts.
    """
    if not evidence.strip():
        return False
    cleaned = evidence.strip().strip("\"'`").replace("…", "").replace("...", "")
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return False
    for src in sources:
        normalized = " ".join(src.split())
        if cleaned in normalized:
            return True
    # Also accept any contiguous 8-word window of the evidence — judges
    # sometimes paraphrase across line breaks but quote enough to verify.
    words = cleaned.split()
    if len(words) >= 8:
        for src in sources:
            normalized = " ".join(src.split())
            for i in range(len(words) - 7):
                window = " ".join(words[i : i + 8])
                if window in normalized:
                    return True
    return False


def grade_dimension(
    *,
    dimension: str,
    system_prompt_path: Path,
    user_prompt: str,
    schema_path: Path,
    model: str = DEFAULT_MODEL,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> JudgeVerdict:
    """Run one judge call for one rubric dimension.

    Args:
      dimension: rubric dimension name (e.g. "groundedness"). Recorded on
        the verdict; not sent to the model (the system prompt already
        encodes it).
      system_prompt_path: file with the per-dimension judge persona +
        scoring criteria. Loaded via --append-system-prompt so the default
        system prompt is preserved.
      user_prompt: the dimension-specific user message, with the
        artifact(s) embedded. Build with `build_user_prompt`.
      schema_path: JSON Schema file pinning the output shape.
      model: pinned model id (default claude-opus-4-7). Bumping this
        invalidates calibration; do it intentionally.
      timeout_sec: hard timeout on the CLI call.

    Returns:
      JudgeVerdict.

    Raises:
      JudgeError: if the CLI fails, output is not JSON, or the schema is
        violated despite the CLI's --json-schema enforcement.
    """
    if not system_prompt_path.is_file():
        raise JudgeError(f"system prompt not found: {system_prompt_path}")
    if not schema_path.is_file():
        raise JudgeError(f"schema not found: {schema_path}")

    schema_text = schema_path.read_text()

    # `--tools ""` disables every built-in tool — the judge is a pure grader
    # operating only on the embedded artifact text. This avoids the
    # multi-turn read/explore loop that otherwise burns tokens and makes
    # schema conformance harder for the model. The user prompt is fed via
    # stdin to avoid being swallowed by any other variadic flag.
    cmd = [
        _claude_path(),
        "-p",
        "--model", model,
        "--output-format", "json",
        "--json-schema", schema_text,
        "--tools", "",
        "--no-session-persistence",
        "--append-system-prompt", system_prompt_path.read_text(),
    ]

    try:
        proc = subprocess.run(
            cmd,
            input=user_prompt,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise JudgeError(
            f"judge timed out after {timeout_sec}s on dimension {dimension!r}"
        ) from e

    if proc.returncode != 0:
        raise JudgeError(
            f"claude CLI exited {proc.returncode} on dimension {dimension!r}.\n"
            f"stderr: {proc.stderr.strip()}"
        )

    # `--output-format json` wraps the model's response in an envelope;
    # the judge's structured output (matching --json-schema) lives in the
    # `result` field. We parse defensively because the envelope shape has
    # historically varied across CLI versions.
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise JudgeError(
            f"judge stdout was not JSON on dimension {dimension!r}: {e}\n"
            f"stdout (truncated): {proc.stdout[:500]!r}"
        ) from e

    payload = _extract_structured_payload(envelope)
    return _verdict_from_payload(dimension, payload)


def _extract_structured_payload(envelope: dict | list | str) -> dict:
    """Pull the rubric payload out of the CLI's JSON envelope.

    The CLI envelope has both a free-text `result` and a schema-conforming
    `structured_output` when --json-schema is used; we prefer the latter.
    Older CLI versions only had `result`, sometimes containing the JSON as
    a string.
    """
    if not isinstance(envelope, dict):
        raise JudgeError(f"unexpected envelope type: {type(envelope).__name__}")

    if envelope.get("is_error"):
        raise JudgeError(
            f"CLI reported error: subtype={envelope.get('subtype')!r}, "
            f"errors={envelope.get('errors')!r}"
        )

    # Defensive: --tools "" should mean zero tool calls. If the envelope
    # reports a tool-use stop_reason, the judge is no longer pure (and
    # likely cost much more than expected). Surface as JudgeError so the
    # operator notices, instead of silently trusting a possibly-cheating
    # verdict.
    if envelope.get("stop_reason") == "tool_use":
        raise JudgeError(
            "judge made tool calls despite --tools \"\"; "
            f"num_turns={envelope.get('num_turns')!r} "
            f"subtype={envelope.get('subtype')!r}"
        )

    # Preferred: dedicated structured-output field.
    so = envelope.get("structured_output")
    if isinstance(so, dict):
        return so
    if isinstance(so, str):
        try:
            parsed = json.loads(so)
        except json.JSONDecodeError as e:
            raise JudgeError(
                f"`structured_output` was a string but not JSON: {e}"
            ) from e
        if isinstance(parsed, dict):
            return parsed

    # Fallback: older CLI versions returned the schema payload via `result`.
    result = envelope.get("result")
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError as e:
            raise JudgeError(
                f"no `structured_output`; `result` was a string but not JSON: "
                f"{e!s}; result preview: {result[:200]!r}"
            ) from e
        if isinstance(parsed, dict):
            return parsed

    raise JudgeError(
        f"could not locate rubric payload in envelope; "
        f"keys={list(envelope.keys())}"
    )


def _verdict_from_payload(dimension: str, payload: dict) -> JudgeVerdict:
    for key in ("score", "evidence", "rationale"):
        if key not in payload:
            raise JudgeError(
                f"judge payload missing `{key}` on dimension {dimension!r}: "
                f"{payload!r}"
            )
    raw_score = payload["score"]
    # Schema constrains score to {"0","1","2","unknown"}. Convert numeric
    # strings to ints so callers can compare against `passing_score`
    # numerically; leave "unknown" as-is.
    if raw_score == "unknown":
        score: int | str = "unknown"
    elif isinstance(raw_score, str) and raw_score in {"0", "1", "2"}:
        score = int(raw_score)
    elif isinstance(raw_score, int) and 0 <= raw_score <= 2:
        score = raw_score
    else:
        raise JudgeError(
            f"judge `score` out of range on dimension {dimension!r}: "
            f"{raw_score!r}"
        )
    return JudgeVerdict(
        dimension=dimension,
        score=score,
        evidence=str(payload["evidence"]),
        rationale=str(payload["rationale"]),
        raw=payload,
    )
