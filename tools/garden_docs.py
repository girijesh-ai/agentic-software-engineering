#!/usr/bin/env python3
"""garden_docs - a computational sensor for doc staleness (C2).

A link checker (tools/audit.sh check 4) proves a doc points somewhere real.
It cannot prove the doc still describes what's there. This checks two
things a link checker structurally can't:

  STALE001  a doc says something "doesn't exist yet" / "is a placeholder",
            naming a path that now exists for real - the doc is describing
            a repo state that's gone.
  STALE002  a doc states a build/unit sequence ("B0 -> B1 -> ... -> C6")
            and a later-in-sequence unit has real (non-dry-run) results
            while an earlier-in-sequence one doesn't exist yet - the plan
            the doc describes was not the order things actually happened in.

Usage:
    python3 tools/garden_docs.py
    python3 tools/garden_docs.py --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXISTENCE_MARKERS = [
    r"doesn'?t exist",
    r"does not exist",
    r"is currently a placeholder",
    r"will fail immediately",
    r"not yet written",
    r"not yet built",
    r"every number in it is a placeholder",
]
EXISTENCE_RE = re.compile("|".join(EXISTENCE_MARKERS), re.IGNORECASE)
PATH_RE = re.compile(r"`([\w./-]+\.[\w]+|tools/[\w./-]+|units/[\w./-]+)`")

SEQUENCE_TOKEN_RE = re.compile(r"\b([ABCD]\d)\b")
UNIT_SLUG_RE = re.compile(r"^([abcd]\d)-")


@dataclass
class Finding:
    check: str
    doc: str
    line: int
    detail: str
    fix: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)


def _doc_files() -> list[Path]:
    out = []
    for md in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in md.parts):
            continue
        if "node_modules" in md.parts:
            continue
        out.append(md)
    return sorted(out)


def _is_real_and_nonempty(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_dir():
        return any(path.iterdir())
    return path.stat().st_size > 0


def check_existence_claims() -> list[Finding]:
    findings = []
    for doc in _doc_files():
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not EXISTENCE_RE.search(line):
                continue
            for m in PATH_RE.finditer(line):
                candidate = m.group(1)
                resolved = ROOT / candidate
                if _is_real_and_nonempty(resolved):
                    findings.append(
                        Finding(
                            check="STALE001",
                            doc=str(doc.relative_to(ROOT)),
                            line=lineno,
                            detail=(
                                f"line says '{line.strip()}', naming "
                                f"'{candidate}', which exists and is non-empty now."
                            ),
                            fix=(
                                f"Update or remove this line - '{candidate}' is "
                                "real, this doc is describing a repo state that "
                                "no longer holds."
                            ),
                        )
                    )
    return findings


def _shipped_units() -> set[str]:
    shipped = set()
    units_dir = ROOT / "units"
    if not units_dir.is_dir():
        return shipped
    for unit_dir in units_dir.iterdir():
        results = unit_dir / "results" / "authors-run.json"
        if not results.exists():
            continue
        try:
            data = json.loads(results.read_text())
        except Exception:
            continue
        if data.get("dry_run") is False:
            shipped.add(unit_dir.name)
    return shipped


def _slug_for_token(token: str) -> str:
    return token.lower()


def check_sequence_violations() -> list[Finding]:
    findings = []
    shipped = _shipped_units()
    shipped_prefixes = {UNIT_SLUG_RE.match(u).group(1) for u in shipped if UNIT_SLUG_RE.match(u)}

    for doc in _doc_files():
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"(?:[ABCD]\d\s*(?:→|->)\s*){2,}[ABCD]\d", text):
            chain_text = m.group(0)
            tokens = [t.lower() for t in SEQUENCE_TOKEN_RE.findall(chain_text)]
            lineno = text.count("\n", 0, m.start()) + 1
            for i in range(len(tokens) - 1):
                earlier, later = tokens[i], tokens[i + 1]
                if later in shipped_prefixes and earlier not in shipped_prefixes:
                    findings.append(
                        Finding(
                            check="STALE002",
                            doc=str(doc.relative_to(ROOT)),
                            line=lineno,
                            detail=(
                                f"states the order '{earlier} -> {later}', but "
                                f"'{later}' has real shipped results and "
                                f"'{earlier}' does not exist yet - the actual "
                                "build order diverged from this plan."
                            ),
                            fix=(
                                f"Note the actual order next to this chain, or "
                                f"mark this section historical - '{earlier}' "
                                f"was skipped ahead of, not before, '{later}'."
                            ),
                        )
                    )
    return findings


def run() -> Report:
    report = Report()
    report.findings.extend(check_existence_claims())
    report.findings.extend(check_sequence_violations())
    return report


def _print_text(report: Report) -> None:
    if not report.findings:
        print("garden_docs: no stale docs found.")
        return
    print(f"garden_docs: {len(report.findings)} finding(s).")
    print()
    for f in report.findings:
        print(f"  {f.check}  {f.doc}:{f.line}")
        print(f"    {f.detail}")
        print(f"    Fix: {f.fix}")
        print()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    report = run()

    if args.format == "json":
        print(json.dumps([f.__dict__ for f in report.findings], indent=2))
    else:
        _print_text(report)

    return 1 if report.findings else 0


if __name__ == "__main__":
    sys.exit(main())
