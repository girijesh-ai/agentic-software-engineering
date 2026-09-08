#!/usr/bin/env python3
"""Verifier for B0's locate-a-named-behaviour tasks.

Checks ANSWER.md (written by the agent) contains every required term,
case-insensitive. Each argument is one required term; pipe-separate
alternatives within a term for "any of these counts" (e.g. "separate|2184"
passes if either substring appears). Standard library only, matching
tools/ used elsewhere in this course.

    python3 check_answer.py ANSWER.md "alembic" "migration"
    python3 check_answer.py ANSWER.md "DATABASE_URL" "separate|2184"
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: check_answer.py ANSWER.md <required term> [more...]", file=sys.stderr)
        return 2

    answer_path = Path(sys.argv[1])
    required = sys.argv[2:]

    if not answer_path.exists():
        print(f"FAIL: {answer_path} does not exist - no answer was written")
        return 1

    text = answer_path.read_text(encoding="utf-8", errors="replace").lower()
    missing = [
        term for term in required
        if not any(alt.lower() in text for alt in term.split("|"))
    ]

    if missing:
        print(f"FAIL: {answer_path} is missing required terms: {missing}")
        return 1

    print(f"PASS: {answer_path} contains all required terms: {required}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
