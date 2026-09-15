#!/usr/bin/env bash
# Gate for B5, traced to SC-4/SC-5 (docs/COURSE-SPEC.md). Run from this directory.
#
# Does NOT call `tools/ablation.py validate` directly: that check hard-requires
# >=5 distinct tasks, a shape built for B0-C1's multi-ticket ablations. B5's
# lab (docs/CURRICULUM.md) is one fixed mid-feature-interruption scenario -
# F1 done, F2 done-but-subtly-buggy, F3 not started - ablated on whether the
# resuming session gets structured handoff artifacts (features.json,
# PROGRESS.md, init.sh) or nothing. Inventing 5 unrelated tasks to satisfy a
# schema built for a different kind of lab would not buy real coverage; see
# units/c3-enforcing-architecture/verify.sh for the same disclosed pattern
# used once already in this course. This script checks the invariants that
# actually apply here instead.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=()
fail() { failures+=("$1"); }

for f in test_b5_features.py features.json PROGRESS.md init.sh CLAUDE.structured.md; do
    path="$HERE/results/lab-materials/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/$f is missing or empty."
    fi
done

for f in teams.py models.py; do
    path="$HERE/results/lab-materials/baseline-state/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/baseline-state/$f is missing or empty."
    fi
done

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
if arms != {'structured', 'unstructured'}:
    print('wrong-arms:' + str(sorted(arms)))
    raise SystemExit
for arm in arms:
    n = sum(1 for r in runs if r['arm'] == arm)
    if n < 10:
        print(f'too-few-repeats:{arm}={n}')
        raise SystemExit
print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        bad-schema) fail "$results has an unexpected schema_version." ;;
        wrong-arms:*) fail "$results does not have exactly the 'structured' and 'unstructured' arms: ${check#wrong-arms:}" ;;
        too-few-repeats:*) fail "$results has fewer than 10 repeats for arm ${check#too-few-repeats:}" ;;
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
