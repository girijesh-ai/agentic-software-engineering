# C3 results

`authors-run.json` is the real ablation: 30 runs (2 arms x 1 task x 15 repeats),
`claude-haiku-4-5`, against B2/B3's reference implementation with a seeded
permission-check regression reset between every run. Verified 2026-09-14. See
`units/c3-enforcing-architecture/README.md` §6 for the numbers - a near-null
pass-rate comparison that turns out to have a single, precise, shared cause
across both arms, not a message-style effect.

`lab-materials/` is what was actually used:

- `check_permission_pattern.py` - the custom sensor. AST-based, scoped to
  single-item routes only after an early version over-fired on the list/count/
  create handlers (see the unit README §3.1 and this file's own docstring).
  Two output modes: bare verdict, and `--remediate`.
- `seed_violation.py` - reproducibly reintroduces the exact pre-refactor inline
  permission check into `update_item()`.
- `CLAUDE.bare.md`, `CLAUDE.remediation.md` - the two arm-specific pointer files,
  differing only in which flag they tell the agent to re-run the linter with.

## Why this unit's ablation has 1 task, not >=5

`tools/ablation.py validate` hard-requires 5 distinct tasks - a shape built for
B0-C1's multi-ticket ablations. C3's actual lab (`docs/CURRICULUM.md`) is one
linter and one seeded violation, ablated on message style, by design. This
unit's own `verify.sh` checks the invariants that actually apply (2 arms,
non-dry-run, >=3 repeats each) instead of calling the generic validator - see
that script's header comment for the full reasoning. `tools/audit.sh`, the
repo-wide gate, only checks `dry_run` and `module_id`, so this doesn't affect
the standard gates.

## The baseline commit

Unlike B0-B3's ablations (which reset to the bare upstream template), C3's task
resets to a dedicated commit in the target clone with B2/B3's reference
implementation already applied - this lab is specifically about defending an
architecture decision that already exists, not building one from scratch. See
the target clone's own git log (`git log --oneline`, commit "C3 baseline: apply
B2/B3 reference implementation + custom permission linter") for exactly what
that commit contains.
