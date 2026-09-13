#!/usr/bin/env bash
# Gate for B3. Run from this directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

failures=()
fail() { failures+=("$1"); }

REF_DIR="$HERE/results/lab-materials/reference-implementation"
for f in models.py deps.py teams.py items.py api_main.py; do
    if [ ! -s "$REF_DIR/$f" ]; then
        fail "reference-implementation/$f is missing or empty."
    fi
done
if ! ls "$REF_DIR"/*add_team*.py >/dev/null 2>&1; then
    fail "reference-implementation has no migration file for team/team_membership."
fi

results="$HERE/results/authors-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist."
else
    if ! python3 "$ROOT/tools/ablation.py" validate "$results" >/tmp/b3-validate.$$ 2>&1; then
        fail "ablation.py validate failed:"$'\n'"$(cat /tmp/b3-validate.$$)"
    fi
    rm -f /tmp/b3-validate.$$
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
