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

## Grading protocol - not yet run

§6's *wrong-problem failures* column needs two independent human graders reading
each run's diff against the ticket's actual intent, with the disagreement rate
published here. That hasn't happened; it's tracked in `AGENTS.md` § Known gaps.
Do not fill in that column with a self-graded or single-grader number when this
does get done - the whole point of a second grader is that intent-matching is not a
question either automation or one reader's judgement should be trusted to settle
alone, which is this unit's own thesis applied to itself.

The runs are all in `authors-run.json` (`agent_tail` per run has the model's own
account of what it built); the diffs themselves are not preserved, since the target
clone is a scratch checkout of an external repo. A grading pass would need to
re-run `agent_command` against each `(arm, task, repeat)` and keep the diff, or grade
directly from `agent_tail`'s description with that caveat noted.
