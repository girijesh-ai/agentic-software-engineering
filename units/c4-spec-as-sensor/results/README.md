# C4 results

`authors-run.json` is the real ablation: 30 runs (2 arms x 5 tasks x 3
repeats), `claude-haiku-4-5`, against 5 independent, real single-endpoint
tasks on top of C3/B5's baseline. Verified 2026-09-15. See
`units/c4-spec-as-sensor/README.md` § 6 for the numbers - a dead-even null
(93% vs 93%) that does not reproduce B5's finding, plus an unplanned,
confirmed-by-reproduction FastAPI routing bug both arms hit at the same
rate.

`lab-materials/` is what was actually used:

- `test_c4_task1_list_my_teams.py` through `test_c4_task5_paginate_members.py`
  - the 5 tasks' verifier tests, each independent (list a user's teams, leave
    a team, view a single member, reject a nonexistent user_id, paginate the
    roster). Run against `reference-fix-teams.py` (a hand-written correct
    solution to all 5) before use: 14/14 pass. Run against the unmodified
    baseline: 12/14 fail cleanly with 405s (routes don't exist yet) or the
    unfixed behaviour - see the unit README § 4 for the exact split.
- `CLAUDE.setup-first.md`, `CLAUDE.assume-ready.md`, `init.sh` - the two
  arm-specific pointer files and the setup script `setup-first` tells the
  agent to run. This is B5's exact mechanism (§7 of that unit's README),
  generalized past its one fixed scenario to 5 fresh, independent tasks.
- `reference-fix-teams.py` - the hand-written correct implementation of all
  5 tasks, used only to validate the tests before running the real ablation.
  Not given to any agent.
- `pre-commit-hook-demo/` - `bad-spec.md`, `fixed-spec.md`, and
  `transcript.txt`, the seeded-violation demo for `tools/pre-commit-spec-lint`
  (SC-2's mechanical enforcement, this unit's other half).

## The baseline commit

Both arms reset to a dedicated commit in the target clone
(`~/Documents/ai-swe-course-scratch/fsft`, commit message "C4 baseline: 5
independent team-endpoint tasks, verifier tests only"), built directly on
top of B5's baseline. Only the 5 test files are added; none of the 5
features exist yet.
