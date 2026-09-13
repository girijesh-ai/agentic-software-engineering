#!/usr/bin/env bash
# Arm B verifier: restore the hidden reference test to check real
# correctness (this drives ablation.py's pass/fail), then separately
# mutation-test whichever app/*.py files the agent touched against
# whatever test command the agent's own new test files support.
#
# Usage: verify_self_tested.sh <reference_test_path>
set -uo pipefail
REF_TEST="$1"

git checkout -- "$REF_TEST" 2>/dev/null

# Harmless no-op when there's nothing new to migrate; required when the
# agent's change (e.g. items-archive) added a column via its own migration -
# the DB's applied-migration state doesn't reset with the git working tree.
(cd backend && FASTAPI_ENV=development uv run alembic upgrade head) >/dev/null 2>&1

echo "--- correctness (hidden reference test) ---"
(cd backend && FASTAPI_ENV=development uv run pytest "${REF_TEST#backend/}" -q)
CORRECTNESS_RC=$?

echo "--- mutation testing the agent's own implementation + tests ---"
MUTATE=/Users/girijesh/Documents/ai-swe-course-scratch/b3-arm-materials/mutate_and_test.py

CHANGED_APP_FILES=$(git diff --name-only HEAD -- 'backend/app/*.py' 2>/dev/null)
NEW_TEST_FILES=$(git status --porcelain -- 'backend/tests/*.py' 2>/dev/null | awk '{print $2}')

if [ -z "$NEW_TEST_FILES" ]; then
    echo "NO_SELF_TESTS: agent wrote no test files"
elif [ -z "$CHANGED_APP_FILES" ]; then
    echo "NO_APP_CHANGES: nothing to mutate"
else
    TEST_ARGS=$(echo "$NEW_TEST_FILES" | sed 's#^backend/##' | tr '\n' ' ')
    for f in $CHANGED_APP_FILES; do
        echo "mutating: $f"
        python3 "$MUTATE" "$f" -- "cd backend && FASTAPI_ENV=development uv run pytest $TEST_ARGS -q"
    done
fi

exit $CORRECTNESS_RC
