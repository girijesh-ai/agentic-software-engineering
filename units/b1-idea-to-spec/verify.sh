#!/usr/bin/env bash
# Learner gate for B1, traced to SC-2 and SC-3 (docs/COURSE-SPEC.md). Run from
# this directory after completing the lab in README.md section 4.
#
# spec_lint.py already enforces "every criterion names an eval" (SPEC002) and
# "at least one criterion covers failure behaviour" (SPEC004), so a clean
# spec_lint run is both checks, not one of several.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

failures=()
fail() { failures+=("$1"); }

specs=("$HERE"/specs/*.md)
if [ ! -e "${specs[0]}" ]; then
    fail "no spec found under specs/*.md. Run spec-from-idea (README.md §4 step 4) first."
else
    for spec in "${specs[@]}"; do
        if ! lint_output=$(python3 "$ROOT/tools/spec_lint.py" "$spec" 2>&1); then
            fail "spec_lint failed on $spec:"$'\n'"$lint_output"
        fi
    done
fi

results="$HERE/results/learner-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist. Run README.md §4 step 7 (tools/ablation.py) first."
else
    check=$(python3 -c "
import json, sys
try:
    data = json.load(open('$results'))
except Exception as e:
    print('invalid-json:' + str(e))
    sys.exit()
if data.get('dry_run'):
    print('dry-run')
    sys.exit()
arms = {r.get('arm') for r in data.get('runs', [])}
if len(arms) < 2:
    print('missing-arm:' + ','.join(sorted(a for a in arms if a)))
else:
    print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible as a learner result." ;;
        missing-arm:*)
            fail "$results has only these arms: ${check#missing-arm:}. Need both the baseline and the spec-guided arm." ;;
        invalid-json:*)
            fail "$results is not valid JSON: ${check#invalid-json:}" ;;
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
