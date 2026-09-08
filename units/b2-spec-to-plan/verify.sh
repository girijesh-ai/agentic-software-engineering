#!/usr/bin/env bash
# Gate for B2, traced to SC-3 (docs/COURSE-SPEC.md). Run from this directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

failures=()
fail() { failures+=("$1"); }

SPEC="$HERE/results/lab-materials/spec-team-sharing.md"
PLAN="$HERE/results/lab-materials/plan-team-sharing.md"

if [ ! -s "$SPEC" ]; then
    fail "spec-team-sharing.md is missing or empty."
elif ! lint_output=$(python3 "$ROOT/tools/spec_lint.py" "$SPEC" 2>&1); then
    fail "spec_lint failed on spec-team-sharing.md:"$'\n'"$lint_output"
fi

if [ ! -s "$PLAN" ]; then
    fail "plan-team-sharing.md is missing or empty."
elif [ -s "$SPEC" ]; then
    if ! trace_output=$(python3 "$HERE/results/lab-materials/check_plan_traceability.py" "$PLAN" "$SPEC" 2>&1); then
        fail "plan traceability failed:"$'\n'"$trace_output"
    fi
fi

results="$HERE/results/authors-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist."
else
    if ! python3 "$ROOT/tools/ablation.py" validate "$results" >/tmp/b2-validate.$$ 2>&1; then
        fail "ablation.py validate failed:"$'\n'"$(cat /tmp/b2-validate.$$)"
    fi
    rm -f /tmp/b2-validate.$$
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
