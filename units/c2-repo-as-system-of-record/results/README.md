# C2 results

`authors-run.json` is the real ablation: 30 runs (2 arms x 5 tasks x 3
repeats), `claude-haiku-4-5`, against a fresh clone of this course repo
itself. Verified 2026-09-21. See `units/c2-repo-as-system-of-record/
README.md` § 6 for the numbers - a perfect 100%/100% ceiling on pass rate,
with a real, secondary wall-clock gap (structured 30% slower at the
median) underneath it.

`lab-materials/` is what was actually used:

- `c2-arm-materials/CLAUDE.monolithic.md` - this repo's real `AGENTS.md` plus
  the full text of every doc it points to, concatenated into one file
  (2,456 lines - bigger than the curriculum's own "800-line" example, not
  smaller, and every line of it is this repo's real, current content).
- `c2-arm-materials/CLAUDE.structured.md` - the pointer file for the
  `structured` arm; the real `AGENTS.md` and `docs/` tree are left in place
  and reachable.
- `c2-arm-materials/check_answer.py` - the verifier, reused unchanged from
  B0 (same shape: does `ANSWER.md` contain the required terms).
- `gardener-run-before-fix.txt`, `gardener-run-after-existence-fix.txt` -
  real `tools/garden_docs.py` output against this repo's own history,
  captured before and after fixing the one genuinely stale claim it found
  in `docs/BUILD-ORDER.md`. Not seeded - this was real drift already in the
  repo when the sensor was pointed at it.

## The target

Each run works against a disposable git clone of this course repo
(`~/Documents/ai-swe-course-scratch/course-repo-copy`, cloned from `main` at
commit `f9e6051`), reset with `git checkout . && git clean -fd` between
every run. The `monolithic` arm's setup step moves `AGENTS.md` and `docs/`
aside before dropping in the monolithic `CLAUDE.md`, so the only source of
truth available to that arm is the one big file, not a weaker test where
the agent can route around it.

## Why this unit's tasks are Q&A, not code

Consistent with B0's tasks (same shape, same verifier): the point is
whether the agent can locate a real, specific fact, not whether it can
write code. C2's question is about documentation structure, not
implementation - a coding task would confound "found the right doc" with
"wrote correct code," which B3/C4 already measure elsewhere.
