#!/usr/bin/env python3
"""Custom sensor: no route handler may decide permissions inline.

The invariant it enforces (decided in B2's plan, built in B3): item
permission is decided by exactly one place, app/api/deps.py's
get_item_with_permission dependency. A route handler that references
`owner_id` or `is_superuser` in its own body has regressed to the
pre-refactor pattern of a per-handler inline check - the exact thing
B0's map flagged as the load-bearing risk in adding roles at all.

AST-based, standard library only. Two output modes:

    python3 check_permission_pattern.py <routes_file.py>              # bare
    python3 check_permission_pattern.py <routes_file.py> --remediate  # C3's lab

The --remediate mode is the unit's actual subject: failure output
carrying what's wrong, what must not be touched, ranked likely causes,
and a reproduce command - written for the agent reading it, not for a
human skimming a CI log.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FLAGGED_NAMES = {"owner_id", "is_superuser"}
ROUTE_DECORATOR_PREFIX = "router."


def _is_route_handler(node: ast.FunctionDef) -> bool:
    for dec in node.decorator_list:
        call = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(call, ast.Attribute) and call.attr in (
            "get", "post", "put", "delete", "patch"
        ):
            if isinstance(call.value, ast.Name) and call.value.id == "router":
                return True
    return False


def _is_single_item_route(node: ast.FunctionDef) -> bool:
    """Only single-item-by-id routes (read/update/delete one item) are covered
    by the get_item_with_permission refactor. List, count, and create operate
    over a query or a not-yet-existing item and legitimately reference
    owner_id/is_superuser themselves - that was never the invariant. A
    single-item route is identified by its path containing "{id}", the
    convention this repo already uses (GET/PUT/DELETE /items/{id})."""
    for dec in node.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        for arg in dec.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "{id}" in arg.value:
                return True
    return False


def _references_flagged_name(node: ast.AST) -> list[tuple[int, str]]:
    hits = []
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in FLAGGED_NAMES:
            hits.append((child.lineno, child.id))
        if isinstance(child, ast.Attribute) and child.attr in FLAGGED_NAMES:
            hits.append((child.lineno, child.attr))
    return hits


def find_violations(source: str, filename: str) -> list[dict]:
    tree = ast.parse(source, filename=filename)
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and _is_route_handler(node) and _is_single_item_route(node):
            hits = _references_flagged_name(node)
            if hits:
                violations.append({
                    "function": node.name,
                    "def_line": node.lineno,
                    "hits": hits,
                })
    return violations


def render_bare(filename: str, violations: list[dict]) -> str:
    lines = [f"FAIL: {len(violations)} violation(s) in {filename}"]
    for v in violations:
        for lineno, name in v["hits"]:
            lines.append(f"  {filename}:{lineno}: inline reference to `{name}` in {v['function']}()")
    return "\n".join(lines)


def render_remediation(filename: str, violations: list[dict]) -> str:
    out = [f"FAIL: {len(violations)} violation(s) in {filename}", ""]
    for v in violations:
        names = sorted({name for _, name in v["hits"]})
        lines_str = ", ".join(f"{filename}:{ln}" for ln, _ in v["hits"])
        out += [
            f"  What's wrong: `{v['function']}()` references {', '.join(f'`{n}`' for n in names)} "
            f"directly (at {lines_str}). Permission is supposed to be decided in exactly one "
            "place: app/api/deps.py's get_item_with_permission dependency, not inline in a "
            "route handler.",
            "",
            "  What must not be touched: app/api/deps.py's get_item_with_permission, "
            "_effective_role, and the Role enum are already correct - do not change their "
            "logic or ranking to make this pass.",
            "",
            "  Ranked likely causes:",
            f"    1. `{v['function']}()` was written or reverted to check permissions inline "
            "instead of depending on ViewableItem/EditableItem/OwnedItem "
            "(app/api/routes/items.py's Annotated aliases).",
            "    2. A new route handler was added without one of those three dependency "
            "aliases in its signature.",
            "",
            f"  Reproduce: python3 check_permission_pattern.py {filename} --remediate",
            "",
            f"  Fix: change `{v['function']}()`'s parameter to use ViewableItem, EditableItem, "
            "or OwnedItem (whichever role this handler actually requires), remove the inline "
            f"check, and take `item` as an already-authorized parameter instead of loading and "
            "checking it by hand.",
            "",
        ]
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_permission_pattern.py <file.py> [--remediate]", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    remediate = "--remediate" in sys.argv[2:]
    source = path.read_text(encoding="utf-8")
    violations = find_violations(source, str(path))

    if not violations:
        print(f"PASS: no inline permission checks in {path}")
        return 0

    print(render_remediation(str(path), violations) if remediate else render_bare(str(path), violations))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
