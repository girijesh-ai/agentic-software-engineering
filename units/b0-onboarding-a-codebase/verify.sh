#!/usr/bin/env bash
# Gate for B0, traced to SC-5 (docs/COURSE-SPEC.md). Run from this directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

failures=()
fail() { failures+=("$1"); }

for f in results/lab-materials/repo-map.md results/lab-materials/load-bearing.md; do
    path="$HERE/$f"
    if [ ! -s "$path" ]; then
        fail "$f is missing or empty."
    fi
done

results="$HERE/results/authors-run.json"
if [ ! -f "$results" ]; then
    fail "$results does not exist."
else
    if ! python3 "$ROOT/tools/ablation.py" validate "$results" >/tmp/b0-validate.$$ 2>&1; then
        fail "ablation.py validate failed:"$'\n'"$(cat /tmp/b0-validate.$$)"
    fi
    rm -f /tmp/b0-validate.$$

    check=$(python3 -c "
import json
data = json.load(open('$results'))
if data.get('dry_run'):
    print('dry-run')
    raise SystemExit
per_arm = data.get('summary', {}).get('per_arm', {})
arms = list(per_arm)
if len(arms) < 2:
    print('missing-arm')
    raise SystemExit
with_map = None
for name in arms:
    if 'map' in name.lower() and 'no' not in name.lower():
        with_map = name
if with_map is None:
    with_map = arms[-1]
per_task = per_arm[with_map].get('per_task_pass_rate', {})
if len(per_task) < 5:
    print('fewer-than-5-tasks:' + str(len(per_task)))
    raise SystemExit
below = {t: r for t, r in per_task.items() if r < 0.75}
if below:
    print('below-threshold:' + json.dumps(below))
else:
    print('ok')
")
    case "$check" in
        ok) ;;
        dry-run) fail "$results is a dry run, not admissible." ;;
        missing-arm) fail "$results has fewer than 2 arms." ;;
        fewer-than-5-tasks:*) fail "$results covers fewer than 5 tasks (${check#fewer-than-5-tasks:})." ;;
        below-threshold:*) fail "with-map arm scored below 3/4 (0.75) on: ${check#below-threshold:}" ;;
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
