#!/usr/bin/env bash
# Gate for C2, traced to SC-7 (docs/COURSE-SPEC.md). Run from this directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."

failures=()
fail() { failures+=("$1"); }

# 1. Entry point under 120 lines - the repo's own AGENTS.md, checked directly
# rather than re-implemented, since this unit's claim is about THIS repo.
agents_lines=$(wc -l < "$ROOT/AGENTS.md" | tr -d ' ')
if [ "$agents_lines" -gt 120 ]; then
    fail "AGENTS.md is $agents_lines lines, over the 120-line cap this unit's §3 claims."
fi

# 2. Link checker green - tools/audit.sh check 4 already does this repo-wide;
# this unit doesn't reimplement it, it cites it. Run it here as evidence.
if ! (cd "$ROOT" && ./tools/audit.sh >/dev/null 2>&1); then
    fail "tools/audit.sh does not pass - the link checker (and other repo-wide gates) failed."
fi

# 3. The gardener exists and is a real, working sensor: it must currently
# report clean on this repo (the one stale doc it found for real, §6, is
# fixed) - a gardener that always reports findings forever isn't a sensor,
# it's noise.
GARDENER="$ROOT/tools/garden_docs.py"
if [ ! -s "$GARDENER" ]; then
    fail "tools/garden_docs.py is missing or empty."
else
    if ! python3 "$GARDENER" >/dev/null 2>&1; then
        fail "tools/garden_docs.py currently reports findings - fix them or confirm they're expected before shipping."
    fi
fi

for f in gardener-run-before-fix.txt gardener-run-after-existence-fix.txt; do
    path="$HERE/results/lab-materials/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/$f is missing or empty."
    fi
done

for f in CLAUDE.monolithic.md CLAUDE.structured.md check_answer.py; do
    path="$HERE/results/lab-materials/c2-arm-materials/$f"
    if [ ! -s "$path" ]; then
        fail "lab-materials/c2-arm-materials/$f is missing or empty."
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
if arms != {'structured', 'monolithic'}:
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
        wrong-arms:*) fail "$results does not have exactly the 'structured' and 'monolithic' arms: ${check#wrong-arms:}" ;;
        too-few-tasks:*) fail "$results covers fewer than 5 tasks: ${check#too-few-tasks:}" ;;
        too-few-repeats:*) fail "$results has fewer than 15 runs for arm ${check#too-few-repeats:}" ;;
    esac
fi

if [ -f "$results" ]; then
    if ! python3 "$ROOT/tools/ablation.py" validate "$results" >/dev/null 2>&1; then
        fail "$results does not pass 'tools/ablation.py validate'."
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
