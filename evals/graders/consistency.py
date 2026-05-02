"""Methodology-invariant grader: keep-or-discard cycle consistency.

The Reaper methodology requires that `current-understanding.md` is updated
*only* on cycles whose decision in `results.md` is "keep". Discard cycles
must not advance the working understanding.

This grader inspects a sequence of snapshots — typically captured by the
investigate skill at the end of each cycle — and verifies the invariant.

A "snapshot" is a directory containing both `results.md` and
`current-understanding.md` from one cycle. The grader walks an ordered
list of snapshots and compares consecutive pairs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CycleConsistencyResult:
    passed: bool
    violations: list[str]

    def __bool__(self) -> bool:
        return self.passed


_DECISION_TOKENS = {"keep", "discard"}


def _last_decision(results_md: str) -> str | None:
    """Return the decision from the *last* row of the cycle table.

    Anchored implementation: parses the markdown table whose header row
    contains a "decision" column, then reads the decision cell of the
    final data row. Looser matches (any `| keep |` cell anywhere) would
    misclassify cycles when keep/discard appear in prose or in unrelated
    tables.
    """
    in_table = False
    decision_col: int | None = None
    saw_separator = False
    last_row_decision: str | None = None
    for raw in results_md.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            in_table = False
            decision_col = None
            saw_separator = False
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not in_table:
            in_table = True
            saw_separator = False
            try:
                decision_col = next(
                    i for i, c in enumerate(cells)
                    if c.lower() == "decision"
                )
            except StopIteration:
                decision_col = None
            continue
        if not saw_separator and re.match(r"^[\s:|-]+$", "".join(cells)):
            saw_separator = True
            continue
        if not saw_separator or decision_col is None:
            continue
        if decision_col >= len(cells):
            continue
        cell = cells[decision_col].lower()
        if cell in _DECISION_TOKENS:
            last_row_decision = cell
    return last_row_decision


def check_cycle_consistency(snapshots: list[Path]) -> CycleConsistencyResult:
    """Verify keep-or-discard invariant across an ordered list of snapshots.

    For each consecutive pair (prev, curr):
      - If curr's last decision is "discard", current-understanding.md must
        be byte-identical to prev's.
      - If curr's last decision is "keep", current-understanding.md *may*
        change (a no-op keep is allowed but flagged in detail).
    """
    violations: list[str] = []
    if len(snapshots) < 2:
        return CycleConsistencyResult(True, violations)

    for prev, curr in zip(snapshots, snapshots[1:]):
        results_path = curr / "results.md"
        cur_understanding = curr / "current-understanding.md"
        prev_understanding = prev / "current-understanding.md"
        if not (results_path.is_file() and cur_understanding.is_file()
                and prev_understanding.is_file()):
            violations.append(
                f"missing files in {prev.name} or {curr.name}; cannot verify"
            )
            continue
        decision = _last_decision(results_path.read_text())
        if decision is None:
            violations.append(f"{curr.name}/results.md has no decision row")
            continue
        if decision == "discard":
            if cur_understanding.read_text() != prev_understanding.read_text():
                violations.append(
                    f"{curr.name}: discard cycle modified current-understanding.md"
                )
    return CycleConsistencyResult(not violations, violations)
