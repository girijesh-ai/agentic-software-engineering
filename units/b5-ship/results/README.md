# B5 results

`authors-run.json` is the real ablation: 24 runs (2 arms x 1 task x 12
repeats), `claude-haiku-4-5`, against a fixed mid-feature-interruption
baseline reset between every run. Verified 2026-09-15. See
`units/b5-ship/README.md` § 6 for the numbers - structured handoff finished
less often than unstructured (67% vs 100%), traced to a specific permission-
seeking mechanism, not either of the two failure modes the curriculum
predicted.

`lab-materials/` is what was actually used:

- `test_b5_features.py` - the 7 tests that define F1/F2/F3 as done. Run
  against `baseline-state/` before any agent touches it: F1 2/2, F2 1/2
  (fails on the persistence check), F3 0/3.
- `features.json`, `PROGRESS.md`, `init.sh` - the structured arm's handoff
  artifacts, copied into the target repo only for that arm.
- `CLAUDE.structured.md` - the arm-specific pointer file. Its first
  instruction ("run `init.sh`") is the mechanism identified in the unit
  README § 6.
- `baseline-state/teams.py`, `baseline-state/models.py` - the exact
  mid-feature files both arms reset to: F1 correct, F2's endpoint present
  but missing `session.commit()`, F3 absent entirely.

## Why this unit's ablation has 1 task, not >=5

`tools/ablation.py validate` hard-requires 5 distinct tasks - a shape built
for B0-C1's multi-ticket ablations. B5's actual lab (`docs/CURRICULUM.md`) is
one fixed mid-feature kill, ablated on handoff condition, by design - the
gate is literally "kill a session mid-feature," singular. This unit's own
`verify.sh` checks the invariants that actually apply (2 arms, non-dry-run,
>=10 repeats each) instead of calling the generic validator - see that
script's header comment for the full reasoning, and
`units/c3-enforcing-architecture/verify.sh` for the same disclosed pattern
used first. `tools/audit.sh`, the repo-wide gate, only checks `dry_run` and
`module_id`, so this doesn't affect the standard gates.

## The baseline commit

Both arms reset to a dedicated commit in the target clone
(`~/Documents/ai-swe-course-scratch/fsft`, commit message "B5 mid-feature
interruption state: F1 done, F2 has an unverified bug, F3 not started"),
built on top of C3's baseline. `baseline-state/` in this directory is a
durable copy of the two files that commit changed in `backend/app/`, so the
scenario survives even if the scratch clone doesn't.
