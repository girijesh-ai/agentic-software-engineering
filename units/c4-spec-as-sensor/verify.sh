#!/usr/bin/env bash
# Gate for C4, traced to SC-2/SC-4/SC-5 (docs/COURSE-SPEC.md). Run from this
# directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=()
fail() { failures+=("$1"); }

HOOK="$HERE/../../tools/pre-commit-spec-lint"
if [ ! -s "$HOOK" ]; then
    fail "tools/pre-commit-spec-lint is missing or empty."
elif [ ! -x "$HOOK" ]; then
    fail "tools/pre-commit-spec-lint is not executable."
fi

for f in bad-spec.md fixed-spec.md transcript.txt; do
    path="$HERE/results/lab-materials/pre-commit-hook-demo/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/pre-commit-hook-demo/$f is missing or empty."
    fi
done

# The hook itself must actually block the bad spec and pass the fixed one -
# not just exist. Run it for real against both fixtures.
bad_check=$(cd "$HERE/../.." && python3 tools/spec_lint.py "$HERE/results/lab-materials/pre-commit-hook-demo/bad-spec.md" >/dev/null 2>&1; echo $?)
if [ "$bad_check" = "0" ]; then
    fail "bad-spec.md passes spec_lint.py - it should fail (that's the point of the demo)."
fi

fixed_check=$(cd "$HERE/../.." && python3 tools/spec_lint.py "$HERE/results/lab-materials/pre-commit-hook-demo/fixed-spec.md" >/dev/null 2>&1; echo $?)
if [ "$fixed_check" != "0" ]; then
    fail "fixed-spec.md fails spec_lint.py - it should pass."
fi

for f in test_c4_task1_list_my_teams.py test_c4_task2_leave_team.py \
         test_c4_task3_get_single_member.py \
         test_c4_task4_validate_member_user_exists.py \
         test_c4_task5_paginate_members.py \
         CLAUDE.setup-first.md CLAUDE.assume-ready.md init.sh; do
    path="$HERE/results/lab-materials/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/$f is missing or empty."
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
if arms != {'setup-first', 'assume-ready'}:
    print('wrong-arms:' + str(sorted(arms)))
    raise SystemExit
tasks = {r['task'] for r in runs}
if len(tasks) < 5:
    print('too-few-tasks:' + str(len(tasks)))
    raise SystemExit
for arm in arms:
    n = sum(1 for r in runs if r['arm'] == arm)
    if n < 15:
        print(f'too-few-repeats:{arm}={n}')
        raise SystemExit
print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        bad-schema) fail "$results has an unexpected schema_version." ;;
        wrong-arms:*) fail "$results does not have exactly the 'setup-first' and 'assume-ready' arms: ${check#wrong-arms:}" ;;
        too-few-tasks:*) fail "$results covers fewer than 5 tasks: ${check#too-few-tasks:}" ;;
        too-few-repeats:*) fail "$results has fewer than 15 runs for arm ${check#too-few-repeats:}" ;;
    esac
fi

# SC-5's own eval: this unit's ablation must pass the generic validator
# directly, unlike B4/B5/C3's disclosed single-task exceptions - this is
# the standard N>=5 tasks x K>=3 repeats shape the validator was built for.
if [ -f "$results" ]; then
    if ! python3 "$HERE/../../tools/ablation.py" validate "$results" >/dev/null 2>&1; then
        fail "$results does not pass 'tools/ablation.py validate' (SC-5 requires this)."
    fi
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
