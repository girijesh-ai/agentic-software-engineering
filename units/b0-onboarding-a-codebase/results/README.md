# B0 results

`authors-run.json` is the real ablation: 40 runs (2 arms x 5 tasks x 4 repeats),
`claude-haiku-4-5`, against a fresh clone of
[`tiangolo/full-stack-fastapi-template`](https://github.com/tiangolo/full-stack-fastapi-template)
reset between every run. Verified 2026-09-08. See `units/b0-onboarding-a-codebase/README.md`
§6 for the numbers and what they mean.

`lab-materials/` is what was actually used:

- `repo-map.md`, `load-bearing.md` - the two documents that make up "the map." Placed
  into the repo root for the `with-map` arm only.
- `CLAUDE.with-map.md` - the pointer file that told the `with-map` arm to read them.
- `check_answer.py` - the verifier: checks an agent's `ANSWER.md` contains the required
  terms for its task (pipe-separated alternatives count as "any one of these").

## A quoting bug, for the next person

`check_answer.py`'s pipe-separated OR syntax (`"separate|2184|migrat"`) needs to reach
the script as one shell argument. Passing it unquoted in an `ablation.py` task's
`verifier` string lets the shell treat `|` as a real pipe between commands, so the
checker never runs and everything scores as a failure regardless of the actual answer.
Always quote a term containing `|` in the verifier command string. This produced a
real fake 0% in an early pass of this ablation (see README §6); the fix is already
applied in `authors-run.json`'s `config.verifiers`, and worth grepping for if this
pattern gets reused in a future unit's ablation.
