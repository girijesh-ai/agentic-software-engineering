#!/usr/bin/env bash
# All sensors this repo runs on itself. Standard library only: bash + python3 stdlib.
# Every failure is a real gap, not a bug in this script. Do not weaken a check to
# make a run go green; add the gap to AGENTS.md instead.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

failures=()
fail() { failures+=("$1"); }

# 1. AGENTS.md is <= 120 lines.
agents_lines=$(wc -l < AGENTS.md | tr -d ' ')
if [ "$agents_lines" -gt 120 ]; then
    fail "AGENTS.md is $agents_lines lines, over the 120-line cap."
fi

# 2 & 3. Every units/*/README.md has the eight required sections and a
# <!-- capabilities: ... --> declaration.
required_sections=(
    "The question"
    "The failure"
    "The idea"
    "The lab"
    "The gate"
    "Our numbers"
    "What makes this obsolete"
    "Sources"
)

if [ -d units ]; then
    for unit_dir in units/*/; do
        [ -d "$unit_dir" ] || continue
        unit="${unit_dir%/}"
        readme="$unit_dir/README.md"
        if [ ! -f "$readme" ]; then
            fail "$unit has no README.md."
            continue
        fi
        for i in "${!required_sections[@]}"; do
            n=$((i + 1))
            section="${required_sections[$i]}"
            if ! grep -qE "^#{1,2} $n\. $section( |$)" "$readme"; then
                fail "$readme is missing required section $n. $section."
            fi
        done
        if ! grep -qE '<!--[[:space:]]*capabilities:[[:space:]]*[^[:space:]-]' "$readme"; then
            fail "$readme has no non-empty <!-- capabilities: ... --> declaration."
        fi
    done
fi

# 4. Internal markdown links resolve.
while IFS= read -r -d '' md; do
    dir=$(dirname "$md")
    while IFS= read -r link; do
        [ -z "$link" ] && continue
        case "$link" in
            http://*|https://*|mailto:*|\#*) continue ;;
        esac
        target="${link%%#*}"
        [ -z "$target" ] && continue
        if [ ! -e "$dir/$target" ]; then
            fail "$md links to '$link', which does not resolve to a file."
        fi
    done < <(grep -oE '\]\([^)]+\)' "$md" | sed -E 's/^\]\(([^)]+)\)$/\1/')
done < <(find . -mindepth 1 -name '.*' -prune -o -name '*.md' -print0)

# 5. docs/CS146S-COVERAGE.md is under 12 months old.
coverage_doc="docs/CS146S-COVERAGE.md"
if [ ! -f "$coverage_doc" ]; then
    fail "$coverage_doc does not exist."
else
    marker=$(grep -oE '<!--[[:space:]]*last-verified:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*-->' "$coverage_doc" | head -1)
    if [ -z "$marker" ]; then
        fail "$coverage_doc has no <!-- last-verified: YYYY-MM-DD --> marker, so its age cannot be verified."
    else
        verified_date=$(echo "$marker" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
        age_days=$(python3 -c "
import datetime, sys
verified = datetime.date.fromisoformat('$verified_date')
print((datetime.date.today() - verified).days)
")
        if [ "$age_days" -gt 365 ]; then
            fail "$coverage_doc was last verified $verified_date, which is $age_days days ago (over 12 months)."
        fi
    fi
fi

# 6. Every shipped unit has a non-dry-run results/authors-run.json whose
# module_id matches its directory.
if [ -d units ]; then
    for unit_dir in units/*/; do
        [ -d "$unit_dir" ] || continue
        unit="${unit_dir%/}"
        unit_id=$(basename "$unit")
        results_file="$unit_dir/results/authors-run.json"
        if [ ! -f "$results_file" ]; then
            fail "$unit has no results/authors-run.json."
            continue
        fi
        check=$(python3 -c "
import json, sys
try:
    data = json.load(open('$results_file'))
except Exception as e:
    print('invalid-json:' + str(e))
    sys.exit()
if data.get('dry_run'):
    print('dry-run')
elif data.get('module_id') != '$unit_id':
    print('id-mismatch:' + str(data.get('module_id')))
else:
    print('ok')
")
        case "$check" in
            ok) ;;
            dry-run) fail "$results_file is a dry run, not admissible as a real result." ;;
            id-mismatch:*) fail "$results_file has module_id '${check#id-mismatch:}', which does not match unit directory '$unit_id'." ;;
            invalid-json:*) fail "$results_file is not valid JSON: ${check#invalid-json:}" ;;
        esac
    done
fi

# Report.
if [ "${#failures[@]}" -eq 0 ]; then
    echo "audit.sh: all checks passed."
    exit 0
fi

echo "audit.sh: ${#failures[@]} failure(s):"
for f in "${failures[@]}"; do
    echo "  - $f"
done
exit 1
