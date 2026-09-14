# B1 results

`authors-run.json` is the real ablation: 60 runs (4 arms x 5 tasks x 3 repeats),
`claude-haiku-4-5`, `--permission-mode acceptEdits`, against a fresh clone of
[`tiangolo/full-stack-fastapi-template`](https://github.com/tiangolo/full-stack-fastapi-template)
reset between every run. Verified 2026-09-07. See `units/b1-idea-to-spec/README.md`
§6 for the numbers and what they mean.

`lab-materials/` is what was actually run, so the claim in §6 is checkable rather than
taken on faith:

- `specs-unlinted/` - the first-draft spec per task, before `spec_lint`/`grill-me`.
- `specs-final/` - the same specs after fixing what `spec_lint` flagged and adding a
  failure-behaviour criterion, the "linted + grilled" arm's input.
- `verifiers/` - the pytest files that decided pass/fail, written and confirmed to
  fail against the unmodified template before any arm ran.
- `CLAUDE.prompt-only.md`, `CLAUDE.spec-pointer.md` - the two `CLAUDE.md` variants
  used by the `prompt-only` and both spec arms respectively.

## Grading protocol - run 2026-09-14, with a disclosed substitution

§6's *wrong-problem failures* column is now filled from a real grading pass over all
11 of B1's failed runs (there were no failures in the two spec arms to grade). Full
protocol, rubric, per-case data, and results:
[`lab-materials/grading/`](lab-materials/grading/) —
[`rubric.md`](lab-materials/grading/rubric.md),
[`failed-runs-packet.json`](lab-materials/grading/failed-runs-packet.json),
[`grading-results.md`](lab-materials/grading/grading-results.md).

**The graders were two independent, context-isolated AI agents, not the two human
graders this protocol originally specified.** That substitution is disclosed, not
hidden, and `grading-results.md` explains why it matters rather than treating it as
a formality: this course's own thesis is that inferential sensors (which is what an
AI grader is) are exactly the kind of check that can miss a wrong-problem failure.
Two AI graders agreeing unanimously that none occurred is real data, not proof.
If a genuine human grading pass ever runs against this same packet, compare its
verdicts against `grading-results.md` and publish the three-way disagreement rate
rather than quietly overwriting the AI graders' numbers.

Diffs were never captured (`tools/ablation.py` never recorded them, and the target
clone is a scratch checkout with no durable history per run) - both graders worked
from `agent_tail`'s self-reported closing summary plus the verifier's failure output,
not the actual code change. `grading-results.md` § "Why this doesn't settle the
question either" names this and two other real limitations explicitly.
