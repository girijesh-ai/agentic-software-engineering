# Working in this repo

A custom check has failed. Its output is in `LINT_OUTPUT.md` in the repo root.
Read it and fix the codebase so it passes again, without breaking existing
behavior. You can re-run the check yourself with:

    python3 check_permission_pattern.py backend/app/api/routes/items.py

Existing tests live under `backend/tests/`; run them to confirm you haven't
broken anything.
