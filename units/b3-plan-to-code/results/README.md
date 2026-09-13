# B3 results

`authors-run.json` is the real ablation: 30 runs (2 arms x 5 tasks x 3 repeats),
`claude-haiku-4-5`, against the same `tiangolo/full-stack-fastapi-template` clone and
five tasks B1/B2 used. Verified 2026-09-13. See `units/b3-plan-to-code/README.md` §6
for the numbers - a real correctness gap (test-first 93% vs self-tested 53%), and a
sharper, unplanned finding that mutation score stayed a perfect 1.00 in the
self-tested arm regardless of whether the implementation was actually correct.

`lab-materials/` is what was actually used:

- `reference-implementation/` - B2's plan, fully built, test-first against the
  pre-written acceptance tests. All nine of B2's Success Criteria pass. This is a
  snapshot of the implementation files, not a runnable checkout - see the file
  headers' originating paths (`backend/app/...`) to place them in a real clone.
- `mutate_and_test.py` - the AST-based mutation tester, self-tested against known
  strong/weak suites before use.
- `hide_reference_tests.sh`, `verify_self_tested.sh` - the self-tested arm's setup
  (physically removes the reference test before the agent's turn) and verifier
  (restores it for grading, then mutation-tests whatever the agent wrote).
- `CLAUDE.test-first.md`, `CLAUDE.self-tested.md` - the two arm-specific pointer
  files.

## A recurring infrastructure note for the next person

This ablation's target-repo clone was corrupted twice by macOS's periodic `/tmp`
cleanup during multi-day gaps between sessions (once losing `.git/HEAD`, once losing
git objects outright, destroying an uncommitted reference implementation in the
process). The clone now lives under `~/Documents/ai-swe-course-scratch/fsft`
instead of `/private/tmp/.../scratchpad`, specifically because scratch space is not
durable across the multi-day gaps this course's own sessions actually have. Commit
anything meant to survive a gap immediately, not at the end of a work session - and
verify a git checkout task's `reset` step won't restore uncommitted, hard-won work
before relying on it.
