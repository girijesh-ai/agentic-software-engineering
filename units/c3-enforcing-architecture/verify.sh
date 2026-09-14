#!/usr/bin/env bash
# Gate for C3, traced to SC-4/SC-5 (docs/COURSE-SPEC.md). Run from this directory.
#
# Does NOT call `tools/ablation.py validate` directly: that check hard-requires
# >=5 distinct tasks, a shape built for B0-C1's multi-ticket ablations. C3's lab
# is legitimately one linter, one seeded violation, ablated on message style
# (docs/CURRICULUM.md's own C3 lab description: "the same linter emitting a
# bare verdict") - forcing 5 unrelated task IDs onto a single-scenario lab
# would be inventing task diversity to satisfy a schema, not real coverage.
# This script checks the invariants that actually apply here instead.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=()
fail() { failures+=("$1"); }

LINTER="$HERE/results/lab-materials/check_permission_pattern.py"
if [ ! -s "$LINTER" ]; then
    fail "check_permission_pattern.py is missing or empty."
fi

results="$HERE/results/authors-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist."
else
    check=$(python3 -c "
import json
data = json.load(open('$results'))
if data.get('dry_run'):
    print('dry-run')
    raise SystemExit
if data.get('schema_version') != 1:
    print('bad-schema')
    raise SystemExit
runs = data.get('runs', [])
arms = {r['arm'] for r in runs}
if arms != {'bare', 'remediation'}:
    print('wrong-arms:' + str(sorted(arms)))
    raise SystemExit
for arm in arms:
    n = sum(1 for r in runs if r['arm'] == arm)
    if n < 3:
        print(f'too-few-repeats:{arm}={n}')
        raise SystemExit
print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        bad-schema) fail "$results has an unexpected schema_version." ;;
        wrong-arms:*) fail "$results does not have exactly the 'bare' and 'remediation' arms: ${check#wrong-arms:}" ;;
        too-few-repeats:*) fail "$results has fewer than 3 repeats for arm ${check#too-few-repeats:}" ;;
    esac
fi

if [ "${#failures[@]}" -eq 0 ]; then
    echo "verify.sh: passed."
    exit 0
fi

echo "verify.sh: ${#failures[@]} failure(s):"
for f in "${failures[@]}"; do
    echo "  - $f"
done
exit 1
