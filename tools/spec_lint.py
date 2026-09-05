#!/usr/bin/env python3
"""spec_lint - a computational sensor for the behaviour harness.

Track C teaches you to build sensors. B1 argues the spec is the only sensor for
wrong-problem failures. This closes the loop: it checks that the spec you are
relying on is worth relying on.

    python3 tools/spec_lint.py specs/rate-limiting.md
    python3 tools/spec_lint.py specs/*.md --strict     # warnings become errors
    python3 tools/spec_lint.py specs/x.md --format json

What it checks, and why each check exists:

  SPEC001  no Success Criteria section        - nothing downstream can trace to it
  SPEC002  criterion has no eval              - a feedforward guide with no sensor
  SPEC003  criterion is unfalsifiable         - the agent gets to define "good"
  SPEC004  no failure-behaviour criterion     - the expensive bugs live here
  SPEC005  no Non-goals section               - scope creep has no boundary to cross
  SPEC006  criterion has no measurable value  - warning; sometimes legitimately binary
  SPEC007  duplicate criterion IDs            - breaks traceability from plan steps

Failure messages are written for the agent that has to fix them, not for a human
reading a build log. That is the technique from C3, applied to this tool itself.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Adjectives that feel like requirements and cannot be wrong. An agent handed one of
# these has been given permission to decide what it means.
UNFALSIFIABLE = [
    "robust", "scalable", "graceful", "gracefully", "seamless", "seamlessly",
    "user-friendly", "user friendly", "intuitive", "efficient", "performant",
    "fast", "quick", "quickly", "slow", "responsive", "lightweight",
    "better", "improved", "improve", "optimal", "optimize", "optimized",
    "appropriate", "appropriately", "reasonable", "reasonably", "sensible",
    "significant", "significantly", "minimal", "modern", "clean", "elegant",
    "best practice", "best practices", "industry standard", "high load",
    "properly", "as needed", "where appropriate", "high quality", "production-ready",
    "easy to use", "maintainable", "flexible", "secure",
]

# A criterion mentioning one of these is describing what happens when things break.
FAILURE_WORDS = [
    "fail", "failure", "error", "invalid", "reject", "rejected", "timeout",
    "unavailable", "down", "outage", "missing", "exceed", "exceeds", "exceeded",
    "corrupt", "retry", "degraded", "unreachable", "crash", "malformed",
    "empty", "null", "denied", "429", "500", "5xx", "4xx", "rollback", "revert",
]

# A number, a percentage, a duration, a size, or a comparison. Anything a test can
# actually assert against.
MEASURABLE = re.compile(
    r"\b\d+(\.\d+)?\s*(%|ms|s\b|sec|seconds?|min|minutes?|hours?|d\b|days?|"
    r"[kmg]b\b|req|rps|qps|x\b|times?)?|"
    r"\b(exactly|at most|at least|no more than|fewer than|greater than|less than|"
    r"within|under|over|between)\b",
    re.I,
)

CRITERION_START = re.compile(
    r"^\s*(?:[-*+]\s*)?(?:#{1,6}\s*)?(?:\*\*)?\s*(SC-\d+)\b", re.I
)
# Real specs write this at least five ways: `Eval:`, `**Eval.**`, `**Evals:**`,
# `Eval —`, `### Eval`. Matching only one of them makes the check punish formatting
# rather than substance, which is the fastest way to get a linter switched off.
EVAL_MARKER = re.compile(
    r"(?:\*\*\s*evals?\s*[.:\-—]?\s*\*\*|\bevals?\s*[:\-—]|^#{1,6}\s*evals?\b)",
    re.I | re.M,
)


@dataclass
class Finding:
    code: str
    severity: str          # "error" | "warning"
    line: int
    subject: str           # criterion id, or the file
    message: str
    remediation: list[str] = field(default_factory=list)
    do_not: str | None = None


@dataclass
class Criterion:
    cid: str
    line: int
    text: str


# --------------------------------------------------------------------------- #
# parsing
# --------------------------------------------------------------------------- #

def _find_section(lines: list[str], pattern: str) -> tuple[int, int] | None:
    """Return (start, end) line indices of a markdown section whose heading matches."""
    rx = re.compile(pattern, re.I)
    start = None
    level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            continue
        if start is None and rx.search(m.group(2)):
            start, level = i, len(m.group(1))
            continue
        if start is not None and len(m.group(1)) <= level:
            return (start, i)
    return (start, len(lines)) if start is not None else None


def parse_criteria(lines: list[str], span: tuple[int, int]) -> list[Criterion]:
    start, end = span
    criteria: list[Criterion] = []
    current: Criterion | None = None
    for i in range(start + 1, end):
        m = CRITERION_START.match(lines[i])
        if m:
            if current:
                criteria.append(current)
            current = Criterion(cid=m.group(1).upper(), line=i + 1, text=lines[i])
        elif current is not None:
            current.text += "\n" + lines[i]
    if current:
        criteria.append(current)
    return criteria


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #

def lint(path: Path) -> list[Finding]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.split("\n")
    findings: list[Finding] = []

    span = _find_section(lines, r"success\s+criteri")
    if span is None:
        return [
            Finding(
                "SPEC001", "error", 1, path.name,
                "No Success Criteria section. Nothing downstream can trace to this spec.",
                remediation=[
                    "Add a `## Success Criteria & Evals` section.",
                    "Write 3-6 criteria, each with an ID (SC-1, SC-2, ...).",
                    "Each criterion needs a falsifiable statement and a named eval.",
                    "At least one must describe behaviour when the feature fails.",
                    "Run `spec-from-idea` if you are starting from an unstructured idea.",
                ],
            )
        ]

    criteria = parse_criteria(lines, span)

    if not criteria:
        findings.append(
            Finding(
                "SPEC001", "error", span[0] + 1, path.name,
                "Success Criteria section exists but contains no criteria with SC-n IDs.",
                remediation=[
                    "Give each criterion an ID of the form `SC-1`, `SC-2`.",
                    "IDs are what plan steps and review findings trace back to; "
                    "without them the traceability chain is broken at the first link.",
                ],
            )
        )
        return findings

    seen: dict[str, int] = {}
    has_failure_criterion = False

    for c in criteria:
        # The criterion's own ID contains a digit. Left in, every criterion looks
        # measurable because of its label, which is the opposite of the check's job.
        body = re.sub(r"\bSC-\d+\b", "", c.text, flags=re.I)
        low = body.lower()

        if c.cid in seen:
            findings.append(
                Finding(
                    "SPEC007", "error", c.line, c.cid,
                    f"Duplicate criterion ID (first seen on line {seen[c.cid]}).",
                    remediation=["Renumber. Plan steps trace by ID; duplicates make "
                                 "traceability ambiguous and silently wrong."],
                )
            )
        else:
            seen[c.cid] = c.line

        if not EVAL_MARKER.search(body):
            findings.append(
                Finding(
                    "SPEC002", "error", c.line, c.cid,
                    "No eval named. This is a feedforward guide with no feedback sensor.",
                    remediation=[
                        "Add an `Eval:` line naming the thing that decides.",
                        "Prefer a real identifier: `tests/test_x.py::test_y`, a script, "
                        "a metric threshold, or a named manual protocol.",
                        "If the eval does not exist yet, name it anyway and mark it "
                        "`(not yet written)`. A criterion whose eval you cannot name "
                        "is a wish, not a criterion.",
                    ],
                    do_not="Do not satisfy this by writing 'Eval: we will test it'. "
                           "That is the same criterion with extra words.",
                )
            )

        hits = [w for w in UNFALSIFIABLE if re.search(rf"\b{re.escape(w)}\b", low)]
        if hits and not MEASURABLE.search(body):
            findings.append(
                Finding(
                    "SPEC003", "error", c.line, c.cid,
                    f"Unfalsifiable: {', '.join(sorted(set(hits))[:4])} — with no value "
                    f"to check against, nobody can say this is not true.",
                    remediation=[
                        "Replace the adjective with the number you would accept.",
                        "  'handles high load'  ->  'sustains 500 rps at p99 < 200ms'",
                        "  'graceful failure'   ->  'returns 429 with Retry-After'",
                        "If you do not know the number, write the range you would "
                        "accept and say why. A stated range is honest; an invented "
                        "precise value looks like evidence and is not.",
                    ],
                    do_not="Do not delete the adjective and leave the vague claim. "
                           "The problem is the missing threshold, not the word.",
                )
            )
        elif not MEASURABLE.search(body):
            findings.append(
                Finding(
                    "SPEC006", "warning", c.line, c.cid,
                    "No measurable value. Fine if the criterion is genuinely binary; "
                    "suspicious otherwise.",
                    remediation=[
                        "Check whether this is binary (a thing exists / does not) or "
                        "whether you skipped deciding a threshold.",
                        "Binary criteria are legitimate. Undecided ones are not.",
                    ],
                )
            )

        if any(re.search(rf"\b{re.escape(w)}\b", low) for w in FAILURE_WORDS):
            has_failure_criterion = True

    if not has_failure_criterion:
        findings.append(
            Finding(
                "SPEC004", "error", span[0] + 1, path.name,
                "No criterion describes behaviour when the feature fails. Success "
                "criteria say what happens when it works; the expensive bugs live in "
                "the unstated behaviour when it does not.",
                remediation=[
                    "Add at least one criterion covering a failure path.",
                    "Useful prompts: What happens when the dependency is down? "
                    "When input is malformed? When the limit is exceeded? "
                    "Does it fail closed or open?",
                    "Run `grill-me` on this spec — finding this class of gap is "
                    "most of what that skill is for.",
                ],
            )
        )

    if _find_section(lines, r"non-?goals?|out of scope") is None:
        findings.append(
            Finding(
                "SPEC005", "warning", 1, path.name,
                "No Non-goals section. Scope creep has no boundary to cross.",
                remediation=[
                    "Add `## Non-goals` listing what this deliberately does not do.",
                    "This is the cheapest guard against the agent building a "
                    "plausible adjacent feature you never asked for.",
                ],
            )
        )

    return findings


# --------------------------------------------------------------------------- #
# output
# --------------------------------------------------------------------------- #

def render(path: Path, findings: list[Finding]) -> str:
    if not findings:
        return f"PASS: {path} — all criteria measurable, evaled, and scoped."

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warning"]
    head = "FAIL" if errors else "PASS (with warnings)"

    out = [
        f"{head}: {path} — {len(errors)} error(s), {len(warns)} warning(s).",
        "",
        "This spec is the behaviour harness. No computational or inferential sensor",
        "catches well-formed code that solves the wrong problem; only this document",
        "does. Findings below are ordered by severity.",
        "",
    ]

    for f in errors + warns:
        out.append(f"  {f.severity.upper()} {f.code}  {f.subject}  (line {f.line})")
        out.append(f"    {f.message}")
        if f.remediation:
            out.append("    Fix:")
            out.extend(f"      - {r}" for r in f.remediation)
        if f.do_not:
            out.append(f"    Do NOT: {f.do_not}")
        out.append("")

    out += [
        "  Re-check with: python3 tools/spec_lint.py " + str(path),
        "",
        "  Do not weaken a criterion to make this pass. Lowering a threshold or",
        "  deleting a criterion is the fastest path to green and the reason this",
        "  check exists. If a criterion is genuinely wrong, change it and say why",
        "  in the spec's revision note.",
    ]
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("paths", nargs="+")
    p.add_argument("--strict", action="store_true", help="warnings become errors")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    failed = False
    payload = []

    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"FAIL: {path} — not found", file=sys.stderr)
            failed = True
            continue

        findings = lint(path)
        blocking = [
            f for f in findings
            if f.severity == "error" or (args.strict and f.severity == "warning")
        ]
        failed = failed or bool(blocking)

        if args.format == "json":
            payload.append({
                "path": str(path),
                "passed": not blocking,
                "findings": [vars(f) for f in findings],
            })
        else:
            print(render(path, findings))

    if args.format == "json":
        print(json.dumps(payload, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Piped into `head`/`less`. Not an error; don't emit a traceback that looks
        # like a lint failure.
        sys.stderr.close()
        raise SystemExit(0)
