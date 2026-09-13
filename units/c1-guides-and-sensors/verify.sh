#!/usr/bin/env bash
# Gate for C1. Run from this directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

failures=()
fail() { failures+=("$1"); }

for f in results/lab-materials/coverage-map.md results/lab-materials/top-three-gaps.md; do
    path="$HERE/$f"
    if [ ! -s "$path" ]; then
        fail "$f is missing or empty."
    fi
done

results="$HERE/results/authors-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist."
else
    if ! python3 "$ROOT/tools/ablation.py" validate "$results" >/tmp/c1-validate.$$ 2>&1; then
        fail "ablation.py validate failed:"$'\n'"$(cat /tmp/c1-validate.$$)"
    fi
    rm -f /tmp/c1-validate.$$

    check=$(python3 -c "
import json
data = json.load(open('$results'))
if data.get('dry_run'):
    print('dry-run')
    raise SystemExit
units = {r.get('original_unit') for r in data.get('runs', [])}
expected = {'b1', 'b2', 'b3'}
if not expected.issubset(units):
    print('missing-source-units:' + str(sorted(expected - units)))
    raise SystemExit
for u, dirname in (('b1', 'b1-idea-to-spec'), ('b2', 'b2-spec-to-plan'), ('b3', 'b3-plan-to-code')):
    src = '$ROOT/units/' + dirname + '/results/authors-run.json'
    try:
        src_data = json.load(open(src))
    except FileNotFoundError:
        print('source-missing:' + src)
        raise SystemExit
    if src_data.get('dry_run'):
        print('source-is-dry-run:' + src)
        raise SystemExit
print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        missing-source-units:*) fail "regrouped runs are missing source unit(s): ${check#missing-source-units:}" ;;
        source-missing:*) fail "source file does not exist: ${check#source-missing:}" ;;
        source-is-dry-run:*) fail "source file is a dry run: ${check#source-is-dry-run:}" ;;
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
