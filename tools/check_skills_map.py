#!/usr/bin/env python3
"""check_skills_map - a drift sensor for the course/plugin boundary.

The course depends on a plugin that is still growing. This checks that the
dependency is still accurate, and - the part that matters - tells you when the
plugin has grown past the course.

    python3 tools/check_skills_map.py
    python3 tools/check_skills_map.py --plugin-dir ../spec-driven-engineering
    python3 tools/check_skills_map.py --plugin-dir ../spec-driven-engineering --strict

Four conditions, deliberately different severities (docs/PLUGIN-CONTRACT.md section 2):

  MAP001  error    unit declares a capability the lock file does not bind
  MAP002  error    lock file binds a skill the plugin does not have
  MAP003  info     plugin has a skill the lock file does not know about
  MAP004  warning  pinned version differs from the plugin's actual version
  MAP005  warning  a deprecated binding is past its removal date

MAP003 is the point of the tool. A new skill is not a failure - it is the course
falling behind its own tooling, which is silent otherwise. Without this check the
gap analysis in docs/SKILLS-MAP.md would quietly become fiction.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

CAPABILITY_DECL = re.compile(r"<!--\s*capabilities:\s*([^>]*?)\s*-->", re.I)
REPO = Path(__file__).resolve().parent.parent


def unit_capabilities(units_dir: Path) -> dict[str, set[str]]:
    """Scan unit READMEs for their machine-readable capability declarations."""
    found: dict[str, set[str]] = {}
    for readme in sorted(units_dir.glob("*/README.md")):
        unit_id = readme.parent.name.split("-")[0]
        text = readme.read_text(encoding="utf-8")
        caps: set[str] = set()
        for m in CAPABILITY_DECL.finditer(text):
            caps |= {c.strip() for c in m.group(1).split(",") if c.strip()}
        found[unit_id] = caps
    return found


def plugin_skills(plugin_dir: Path) -> set[str]:
    """Skill names from a plugin checkout. The loader scans skills/*/ one level deep."""
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"no skills/ directory under {plugin_dir}")
    return {
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    }


def plugin_version(plugin_dir: Path) -> str | None:
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return None
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("version")
    except json.JSONDecodeError:
        return None


def check(lock: dict, units: dict[str, set[str]],
          checkouts: dict[str, Path]) -> list[dict]:
    findings: list[dict] = []
    caps = lock.get("capabilities", {})
    gaps = set(lock.get("expected_gaps", {})) | {"$comment"}

    # MAP001 - a unit teaches something nothing provides.
    for unit_id, declared in sorted(units.items()):
        for cap in sorted(declared):
            if cap in caps or cap in gaps:
                continue
            findings.append({
                "code": "MAP001", "severity": "error", "subject": f"{unit_id}:{cap}",
                "message": f"Unit {unit_id} declares capability '{cap}', which is not "
                           f"bound in skills.lock.json and is not a known gap.",
                "fix": [
                    f"If the plugin provides it, add '{cap}' to `capabilities` with "
                    "its skill name.",
                    f"If it does not yet, add '{cap}' to `expected_gaps` and to the "
                    "gap analysis in docs/SKILLS-MAP.md.",
                    "If the unit should not depend on it, remove it from the unit's "
                    "<!-- capabilities: ... --> comment.",
                ],
            })

    # Capabilities bound but taught nowhere - dead weight in the lock file.
    taught = {c for cs in units.values() for c in cs}
    for cap, spec in sorted(caps.items()):
        listed = set(spec.get("units", []))
        if listed and not (listed & set(units)):
            continue  # units not written yet; not a finding
        if listed and not (taught & {cap}):
            findings.append({
                "code": "MAP001", "severity": "warning", "subject": cap,
                "message": f"Capability '{cap}' claims units {sorted(listed)} but no "
                           f"unit README declares it.",
                "fix": [f"Add `<!-- capabilities: {cap} -->` to the unit README, "
                        "or drop the units list from the lock entry."],
            })

    declared = lock.get("plugins", {})
    for name, meta in sorted(declared.items()):
        if name in checkouts:
            continue
        required = meta.get("required", True)
        findings.append({
            "code": "MAP002", "severity": "warning" if not required else "warning",
            "subject": name,
            "message": f"No checkout given for plugin '{name}' "
                       f"({'required' if required else 'optional'}). Its bindings were "
                       "not verified against the real thing.",
            "fix": [f"Re-run with --plugin-dir {name}=<path to checkout>"],
        })
    if not checkouts:
        return findings

    # skill name -> owning plugin, for every checkout we were given
    present: dict[str, str] = {}
    for name, path in checkouts.items():
        for skill in plugin_skills(path):
            present[skill] = name

    bound: set[str] = set()
    today = date.today().isoformat()

    for cap, spec in sorted(caps.items()):
        owner = spec.get("plugin", "spec-driven-engineering")
        if owner not in checkouts:
            continue  # already reported above; don't cascade
        for skill in spec.get("skills", []):
            bound.add(skill)
            if skill not in present:
                findings.append({
                    "code": "MAP002", "severity": "error", "subject": f"{cap}:{skill}",
                    "message": f"Capability '{cap}' binds skill '{skill}', which the "
                               f"plugin does not have. Renamed, removed, or stale pin.",
                    "fix": [
                        "Check the plugin's changelog for a rename.",
                        f"Update the binding, and record the old name under "
                        f"`deprecated_skills` for two release cycles "
                        "(docs/PLUGIN-CONTRACT.md section 4).",
                        "Do NOT delete the capability. Units depend on it; the "
                        "capability is the stable name and the skill is the binding.",
                    ],
                })
        for skill in spec.get("deprecated_skills", []):
            bound.add(skill)
            until = spec.get("deprecated_until")
            if until and until < today:
                findings.append({
                    "code": "MAP005", "severity": "warning", "subject": f"{cap}:{skill}",
                    "message": f"Deprecated binding '{skill}' passed its removal date "
                               f"({until}).",
                    "fix": [f"Remove '{skill}' from deprecated_skills for '{cap}'."],
                })

    # MAP003 - the plugin grew. Info, not error. This is the row the tool exists for.
    for skill in sorted(set(present) - bound):
        findings.append({
            "code": "MAP003", "severity": "info", "subject": skill,
            "message": f"Plugin '{present[skill]}' has skill '{skill}' that no "
                       f"capability binds. The plugin has grown past the course.",
            "fix": [
                "Run the intake process: docs/PLUGIN-CONTRACT.md section 3.",
                "Is this a new capability, or a better implementation of one we teach?",
                "A better implementation is a lock-file edit and one sentence of prose.",
                "A new capability defaults to a lab step in an existing unit. It earns "
                "a new unit only if you can write its 'The failure' section without "
                "straining.",
                "If it fills an entry in `expected_gaps`, move it into `capabilities` "
                "and update docs/SKILLS-MAP.md - that gap analysis is a claim with a "
                "shelf life.",
            ],
        })

    for name, path in sorted(checkouts.items()):
        pinned = declared.get(name, {}).get("tested_against")
        actual = plugin_version(path)
        if not (actual and pinned and actual != pinned):
            continue
        findings.append({
            "code": "MAP004", "severity": "warning", "subject": f"{name} version",
            "message": f"'{name}' pinned to {pinned}; checkout is {actual}. The units "
                       f"were verified against {pinned}, so any 'Our numbers' section "
                       f"is evidence about a version nobody is running.",
            "fix": [
                "Re-run the affected units' ablations, then bump `tested_against`.",
                "Do NOT bump the pin as a courtesy. The pin is a claim that someone "
                "ran the units.",
            ],
        })

    return findings


def render(findings: list[dict]) -> str:
    if not findings:
        return "PASS: skills.lock.json is consistent with the units and the plugin."

    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]

    out = [
        ("FAIL" if errors else "PASS (with notes)")
        + f": {len(errors)} error(s), {len(warns)} warning(s), {len(infos)} info.",
        "",
        "The course teaches capabilities; skills.lock.json binds them to plugin skills.",
        "Fix bindings in the lock file, not in unit prose - prose is documentation,",
        "the lock file is the contract.",
        "",
    ]
    for f in errors + warns + infos:
        out.append(f"  {f['severity'].upper():<7} {f['code']}  {f['subject']}")
        out.append(f"    {f['message']}")
        if f.get("fix"):
            out.append("    Fix:")
            out.extend(f"      - {x}" for x in f["fix"])
        out.append("")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lock", default=str(REPO / "skills.lock.json"))
    p.add_argument("--units", default=str(REPO / "units"))
    p.add_argument("--plugin-dir", action="append", default=[],
                   metavar="NAME=PATH",
                   help="repeatable, e.g. --plugin-dir spec-driven-engineering=../sde "
                        "--plugin-dir ponytail=../ponytail")
    p.add_argument("--strict", action="store_true",
                   help="warnings and info become blocking")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    units = unit_capabilities(Path(args.units))

    checkouts: dict[str, Path] = {}
    for spec in args.plugin_dir:
        if "=" not in spec:
            print(f"--plugin-dir needs NAME=PATH, got {spec!r}", file=sys.stderr)
            return 2
        name, path = spec.split("=", 1)
        checkouts[name] = Path(path)

    findings = check(lock, units, checkouts)

    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        print(render(findings))

    blocking = [
        f for f in findings
        if f["severity"] == "error" or (args.strict and f["severity"] != "info")
    ]
    return 1 if blocking else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.stderr.close()
        raise SystemExit(0)
