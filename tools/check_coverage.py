#!/usr/bin/env python3
"""check_coverage - the superset gate.

"This course is a superset of CS146S" is a claim. Claims rot. This makes it a
check that fails.

    python3 tools/check_coverage.py
    python3 tools/check_coverage.py --allow-planned    # during the build-out

Conditions:

  COV001  error    a topic has status 'omitted'      - a superset has no holes
  COV002  error    a topic has status 'unverified'   - can't claim coverage of
                                                       something you haven't read
  COV003  error    a topic maps to no unit at all
  COV004  error    a topic maps to a unit that does not exist and is not planned
  COV005  warning  a topic is 'planned' (not written yet)
  COV006  warning  evidence_quality is 'secondary'   - the map rests on a
                                                       third-party writeup
  COV007  warning  the map is more than 12 months old

By design this currently FAILS on our own repo: CS146S week 2 is unverified.
That is the tool working. Do not silence it by guessing at the week's content -
a superset claim resting on a guess is exactly the kind of unfalsifiable
assertion spec_lint rejects in specs.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STALE_DAYS = 365


def existing_units(units_dir: Path) -> set[str]:
    if not units_dir.is_dir():
        return set()
    return {d.name.split("-")[0] for d in units_dir.iterdir() if d.is_dir()}


def planned_units(curriculum: Path) -> set[str]:
    """Unit ids that appear as headings in the curriculum but aren't written yet."""
    if not curriculum.exists():
        return set()
    text = curriculum.read_text(encoding="utf-8").lower()
    found = set()
    for token in ("a", "b", "c", "d"):
        for n in range(0, 10):
            if f"### {token}{n} " in text or f"### {token}{n} ·" in text:
                found.add(f"{token}{n}")
    if "## capstone" in text:
        found.add("capstone")
    return found


def check(cmap: dict, written: set[str], planned: set[str],
          allow_planned: bool) -> list[dict]:
    findings: list[dict] = []
    known = written | planned | {t for t in cmap.get("extra_targets", [])}

    for topic in cmap["topics"]:
        tid, status = topic["id"], topic["status"]
        targets = topic.get("covered_by", [])

        if status == "omitted":
            findings.append({
                "code": "COV001", "severity": "error", "subject": tid,
                "message": f"'{topic['title']}' is marked omitted. A superset has no "
                           "deliberate holes.",
                "fix": [
                    "Either add a unit (or a dated appendix) that covers it, and change "
                    "status to 'planned',",
                    "or drop the superset claim in cs146s.map.json and say 'overlaps "
                    "with' instead. Both are honest; claiming superset while skipping "
                    "is not.",
                ],
            })
            continue

        if status == "unverified":
            findings.append({
                "code": "COV002", "severity": "error", "subject": tid,
                "message": f"'{topic['title']}' — content not established. Cannot claim "
                           "coverage of material nobody has read.",
                "fix": [
                    "Read the primary syllabus for this week and record what it "
                    "actually contains.",
                    "Then map it to a unit, or add one.",
                    "Do NOT guess the content from surrounding weeks and mark it "
                    "covered. That converts a known unknown into a false claim.",
                ],
            })
            continue

        if not targets:
            findings.append({
                "code": "COV003", "severity": "error", "subject": tid,
                "message": f"'{topic['title']}' maps to no unit.",
                "fix": ["Add a `covered_by` entry, or set status to 'omitted' and "
                        "accept that the superset claim fails."],
            })
            continue

        for target in targets:
            if target in known or target.startswith("appendix-"):
                continue
            findings.append({
                "code": "COV004", "severity": "error", "subject": f"{tid} -> {target}",
                "message": f"Topic maps to '{target}', which is neither a written unit "
                           f"nor a heading in the curriculum.",
                "fix": [
                    f"Check the unit id. Written units: {sorted(written) or 'none'}.",
                    "If the unit is planned, add its heading to docs/CURRICULUM.md "
                    "first - the curriculum is the source of truth for what exists.",
                ],
            })

        if status == "planned":
            findings.append({
                "code": "COV005",
                "severity": "warning" if allow_planned else "error",
                "subject": tid,
                "message": f"'{topic['title']}' is planned, not written "
                           f"({', '.join(targets)}).",
                "fix": ["Write it, or run with --allow-planned while building out."],
            })

    if cmap.get("evidence_quality") == "secondary":
        findings.append({
            "code": "COV006", "severity": "warning", "subject": "evidence",
            "message": "The map is built from secondary sources, so every 'covered' "
                       "verdict inherits that uncertainty.",
            "fix": ["Verify against the official syllabus, then set evidence_quality "
                    "to 'primary'.",
                    "A superset claim is only as good as the map it is checked against."],
        })

    verified = cmap.get("verified_on")
    if verified:
        age = (date.today() - date.fromisoformat(verified)).days
        if age > STALE_DAYS:
            findings.append({
                "code": "COV007", "severity": "warning", "subject": "freshness",
                "message": f"Map last verified {age} days ago. Their syllabus moves; "
                           "ours doesn't notice.",
                "fix": ["Re-audit against the current CS146S materials and bump "
                        "verified_on."],
            })

    return findings


def render(cmap: dict, findings: list[dict]) -> str:
    topics = cmap["topics"]
    by_status: dict[str, int] = {}
    for t in topics:
        by_status[t["status"]] = by_status.get(t["status"], 0) + 1

    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warning"]

    out = [
        ("SUPERSET CLAIM: FAILS" if errors else "SUPERSET CLAIM: HOLDS")
        + f" — {len(topics)} topics, {len(errors)} error(s), {len(warns)} warning(s).",
        "",
        "  " + "  ".join(f"{k}={v}" for k, v in sorted(by_status.items())),
        "",
    ]
    if not errors:
        deeper = by_status.get("deeper", 0)
        out.append(f"  Every CS146S topic maps to a unit; {deeper} go deeper than the "
                   "original.")
        out.append("")

    for f in errors + warns:
        out.append(f"  {f['severity'].upper():<7} {f['code']}  {f['subject']}")
        out.append(f"    {f['message']}")
        if f.get("fix"):
            out.append("    Fix:")
            out.extend(f"      - {x}" for x in f["fix"])
        out.append("")

    if errors:
        out += [
            "  A superset claim with an error above is marketing, not a claim.",
            "  Fix the map or weaken the wording in docs/CS146S-COVERAGE.md.",
        ]
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--map", default=str(REPO / "cs146s.map.json"))
    p.add_argument("--units", default=str(REPO / "units"))
    p.add_argument("--curriculum", default=str(REPO / "docs" / "CURRICULUM.md"))
    p.add_argument("--allow-planned", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    cmap = json.loads(Path(args.map).read_text(encoding="utf-8"))
    written = existing_units(Path(args.units))
    planned = planned_units(Path(args.curriculum))
    findings = check(cmap, written, planned, args.allow_planned)

    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        print(render(cmap, findings))

    return 1 if any(f["severity"] == "error" for f in findings) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.stderr.close()
        raise SystemExit(0)
