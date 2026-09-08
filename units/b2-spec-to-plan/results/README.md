# B2 results

`authors-run.json` is the real ablation: 30 runs (2 arms x 5 tasks x 3 repeats),
`claude-haiku-4-5`, against the same `tiangolo/full-stack-fastapi-template` clone and
five verifier-first tasks B1 used, with B1's final specs held constant across both
arms so only the plan format varies. Verified 2026-09-08. See
`units/b2-spec-to-plan/README.md` §6 for the numbers and why the surprising direction
(untraced plan scored higher) isn't trusted as a real effect.

`lab-materials/` is what was actually used:

- `spec-team-sharing.md`, `plan-team-sharing.md` - the real spec and plan for this
  unit's own running-thread feature (team-based item sharing), which B3 builds from.
  Not part of the ablation - the ablation isolates plan-traceability using B1's
  smaller, already-proven task set instead (see README §4 for why).
- `check_plan_traceability.py` - the mechanical orphan-step / uncovered-criterion
  checker, this unit's own gate logic.
- `plans-traced/`, `plans-untraced/` - the two plan variants per B1 task, identical
  content except for `Serves: SC-n` lines. The ablation's actual independent variable.
