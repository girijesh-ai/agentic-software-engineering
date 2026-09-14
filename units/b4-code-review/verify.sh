#!/usr/bin/env bash
# Gate for B4. Run from this directory.
#
# Does NOT call `tools/ablation.py validate` directly: that check requires
# >=3 repeats per (arm, task). This unit's lab is 5 hand-constructed PRs with
# documented ground truth, each reviewed once per condition (spec-provided,
# spec-withheld) by an independent agent - repeating a deterministic-ish
# reasoning task against a fixed, known-answer PR doesn't buy statistical
# power the way repeating a stochastic coding task does, and tripling the
# review-agent cost for that would not be a good trade. See
# results/README.md for the full reasoning, and units/c3-enforcing-architecture
# for the same disclosed pattern used once already in this course.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=()
fail() { failures+=("$1"); }

GROUND_TRUTH="$HERE/results/lab-materials/prs/ground-truth.md"
if [ ! -s "$GROUND_TRUTH" ]; then
    fail "ground-truth.md is missing or empty."
fi

for i in 1 2 3 4 5; do
    diff_file="$HERE/results/lab-materials/prs/pr${i}.diff"
    if [ ! -s "$diff_file" ]; then
        fail "pr${i}.diff is missing or empty."
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
if arms != {'spec-provided', 'spec-withheld'}:
    print('wrong-arms:' + str(sorted(arms)))
    raise SystemExit
tasks = {r['task'] for r in runs}
if len(tasks) < 5:
    print('too-few-prs:' + str(len(tasks)))
    raise SystemExit
for arm in arms:
    n = sum(1 for r in runs if r['arm'] == arm)
    if n < 5:
        print(f'too-few-reviews:{arm}={n}')
        raise SystemExit
print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        bad-schema) fail "$results has an unexpected schema_version." ;;
        wrong-arms:*) fail "$results does not have exactly the 'spec-provided' and 'spec-withheld' arms: ${check#wrong-arms:}" ;;
        too-few-prs:*) fail "$results covers fewer than 5 PRs: ${check#too-few-prs:}" ;;
        too-few-reviews:*) fail "$results has fewer than 5 reviews for arm ${check#too-few-reviews:}" ;;
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
