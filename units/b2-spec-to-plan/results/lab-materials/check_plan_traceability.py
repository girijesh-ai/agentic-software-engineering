#!/usr/bin/env python3
"""B2's own gate: every plan step traces to a spec Success Criterion ID.

An orphan step - one naming no SC and not explicitly flagged as a
deliberate exception - fails the lab. A step may legitimately serve none
(resolving an open question the spec left unresolved, say) but must say
so explicitly with the literal phrase "Serves: none directly" - silence
is not an exception, it's the bug this check exists to catch.

    python3 check_plan_traceability.py plan.md spec.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STEP_HEADER = re.compile(r"^\*\*Step \d+ — .+\*\*$", re.MULTILINE)
SERVES_LINE = re.compile(r"^Serves:\s*(.+)$", re.MULTILINE)
SC_ID = re.compile(r"\bSC-\d+\b")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_plan_traceability.py <plan.md> <spec.md>", file=sys.stderr)
        return 2

    plan_path, spec_path = Path(sys.argv[1]), Path(sys.argv[2])
    plan_text = plan_path.read_text(encoding="utf-8")
    spec_text = spec_path.read_text(encoding="utf-8")

    known_sc_ids = set(SC_ID.findall(spec_text))
    if not known_sc_ids:
        print(f"FAIL: no SC-n criteria found in {spec_path}")
        return 1

    headers = list(STEP_HEADER.finditer(plan_text))
    if not headers:
        print(f"FAIL: no '**Step N — ...**' headers found in {plan_path}")
        return 1

    problems: list[str] = []
    referenced: set[str] = set()

    for i, header in enumerate(headers):
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(plan_text)
        block = plan_text[start:end]
        step_name = header.group(0)

        serves_match = SERVES_LINE.search(block)
        if not serves_match:
            problems.append(f"{step_name}: no 'Serves:' line at all - orphan step.")
            continue

        serves_text = serves_match.group(1)
        sc_ids = set(SC_ID.findall(serves_text))

        if not sc_ids:
            if "none directly" not in serves_text.lower():
                problems.append(
                    f"{step_name}: 'Serves:' names no SC-n and isn't explicitly "
                    f"flagged 'none directly' - orphan step. Got: {serves_text!r}"
                )
            continue

        unknown = sc_ids - known_sc_ids
        if unknown:
            problems.append(
                f"{step_name}: references {sorted(unknown)}, not in {spec_path}'s "
                f"known criteria {sorted(known_sc_ids)}."
            )
        referenced |= sc_ids

    uncovered = known_sc_ids - referenced
    if uncovered:
        problems.append(
            f"Criteria with no plan step at all: {sorted(uncovered)}."
        )

    if problems:
        print(f"FAIL: {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(
        f"PASS: {len(headers)} step(s), {len(known_sc_ids)} criteria, "
        f"all traced, no orphans."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
