# C4 · Making the spec computational

**Prerequisites.** B1 (the spec as the only sensor for wrong-problem
failures), C3 (agent-directed remediation, the pattern this unit's hook
reuses), B5 (the trace-analysis finding this unit's ablation generalizes).
**Time.** ~4 hours. **Cost.** Under $10 in agent tokens.

<!-- capabilities: spec-linting, change-measurement -->
**Serves.** SC-2, SC-5, via the hook demo in §4.1 and the ablation in §6.

---

## 1. The question

Your specs are the behaviour harness. What checks the specs?

## 2. The failure

B1 found that the spec is the only instrument that catches wrong-problem
failures - a well-formed, well-tested implementation of the wrong thing
passes every other check. That makes spec quality a load-bearing property,
and this course had been treating it as a discipline: write a good spec,
hope the next person does too. `tools/spec_lint.py` already exists and
already runs in this repo's own CI (`.github/workflows/gates.yml`) - but
nothing stopped a bad spec from being *written* in the first place, only
from being merged after the fact. §4.1 closes that half cleanly.

The other half is the harder failure, and it's the more useful one. B5's
trace analysis found a specific mechanism - a handoff file's first
instruction reading as a Bash call needing approval that headless execution
can't grant - and this unit set out to measure whether fixing that
instruction's wording generalizes past the one scenario it was found in.
**It doesn't reproduce at all on 5 fresh, unrelated tasks: 93% vs 93%, a
dead-even null (§6).** That's not the fix failing. It's evidence that B5's
ablation varied two things at once - the literal instruction text *and* an
explicit "someone else was interrupted here" narrative (`PROGRESS.md`, a
half-done feature) - and this unit's cleaner test, which kept the former
and dropped the latter, suggests the narrative was doing the work, not the
wording. A real methodological lesson, not a clean replication.

## 3. The idea

### 3.1 A sensor at the earliest possible point

C3 taught agent-directed remediation: a check's failure output should carry
what's wrong, what not to touch, ranked causes, and a reproduce command.
`spec_lint.py` already does this (see any `SPEC0NN` finding's `Fix:` block).
The gap wasn't the sensor, it was where it ran. A CI gate catches a bad spec
after a PR exists; a pre-commit hook catches it before a bad spec's Success
Criteria ever get read by `plan-from-spec` or `review-code`. `tools/
pre-commit-spec-lint` (§4.1) closes that gap: same tool, same rules, run one
step earlier, non-`--strict` so warnings never block a commit - only the
errors SC-2 actually cares about (no eval, unfalsifiable, no failure-path
criterion, no Non-goals, duplicate IDs).

### 3.2 Trace analysis as the improvement loop, not intuition

The curriculum's second half is evals: what to measure when an agent has
many trajectories to the same outcome, and ablation methodology as the
discipline of publishing what actually happened. B5 gave this unit a real,
already-analyzed trace: reading every failing run's `agent_tail` and
wall-clock time showed that a handoff file's literal first instruction
("run `init.sh`") reads as a Bash call needing approval that headless
execution can never grant, so the agent stops before writing any code. That
finding came from one fixed scenario, repeated 12 times per arm, where the
handoff file also told the agent it was resuming someone else's interrupted
work. The question this unit's ablation asks is whether the mechanism is a
fact about the instruction wording or a fact about that surrounding
narrative - and the way to find out is to keep the wording, drop the
narrative, and run the same two-arm design against 5 fresh tasks that carry
no interruption story at all.

Trace analysis doesn't stop at picking the hypothesis. Reading every
`leave-team` failure's `verifier_tail` (§6) found a second, unplanned
result: a real FastAPI routing bug both arms hit at the same rate,
unrelated to either arm's instructions. Finding it required the same
discipline C3 and B5 both used - read the actual failing transcripts,
don't stop at the aggregate number.

### 3.3 The closing question

If `spec_lint.py` has run in this repo's CI since before this unit existed
and has never once blocked a merge with an ERROR, is that because the specs
here are unusually good, or because the checks aren't strict enough to
catch what's actually wrong with them? §4.1's demo answers this for the
*hook* mechanically (it does fire, on a real seeded violation) but not for
this repo's own specs, which is the more important and less comfortable
version of the question. `docs/COURSE-SPEC.md`'s own lint run has 0 errors
and 5 SPEC006 warnings (unmeasurable-but-possibly-binary criteria) every
time it's been checked in this course - worth treating as an open question
in this repo's own `AGENTS.md`, not a clean bill of health.

## 4. The lab

### 4.1 Part one - the pre-commit hook

`tools/pre-commit-spec-lint` wraps `spec_lint.py`: finds every staged
Markdown file with a `## Success Criteria` section, lints just those,
non-`--strict`. Install with:

```bash
ln -sf ../../tools/pre-commit-spec-lint .git/hooks/pre-commit
```

Demonstrated against a throwaway repo in
`results/lab-materials/pre-commit-hook-demo/`: `bad-spec.md` (no eval, no
failure-path criterion, no Non-goals) blocks the commit with the exact same
`SPEC002`/`SPEC004`/`SPEC005` findings the CLI reports directly; replacing
its content with `fixed-spec.md`'s (named evals, a fail-closed criterion, a
Non-goals section) lets the commit through. `transcript.txt` has the full
exchange.

### 4.2 Part two - the ablation

**Step 1 - Five independent tasks, verified against a correct reference
before use.** Each a small, real addition to the team-sharing API from
B0-B5: list the current user's teams, leave a team (409 for a sole owner),
view a single member's role, reject a nonexistent `user_id` on add, and
paginate the member list to match `items.py`'s existing convention.
`reference-fix-teams.py` implements all 5 correctly; running the 5 test
files against it: 14/14 pass. Running them against the unfixed baseline:
12/14 fail, cleanly (405s for routes that don't exist yet, or the
unpatched behaviour for the two tasks that modify an existing route).

**Step 2 - Ablate B5's fix, generalized.** Two arms, identical to B5's
mechanism: `setup-first` copies `init.sh` and tells the agent to run it
before starting (`CLAUDE.setup-first.md`); `assume-ready` tells the agent
the environment is already running and gives the same two setup commands
only as a fallback if something's actually down (`CLAUDE.assume-ready.md`).
Same prompt content otherwise - only the environment framing differs. 5
tasks x 2 arms x 3 repeats = 30 runs, `claude-haiku-4-5`, `claude -p ...
--permission-mode acceptEdits`, reset to the C4 baseline commit between
every run.

**Step 3 - Verify externally.** Each task's own pytest file, run after the
agent's session ends, independent of what the agent itself claimed.

## 5. The gate

```bash
./verify.sh
```

Passes when: `tools/pre-commit-spec-lint` exists and is executable; the
hook demo's three files exist and the hook actually blocks `bad-spec.md`
and passes `fixed-spec.md` when run for real; all 5 task test files and the
2 arm pointer files exist; `results/authors-run.json` is a real (non-dry-run)
run with exactly the `setup-first` and `assume-ready` arms, >=5 tasks, >=15
runs per arm, **and passes `tools/ablation.py validate` directly** - unlike
B4/B5/C3's disclosed single-task exceptions, SC-5's own eval requires this
unit's ablation to fit the standard N>=5-tasks x K>=3-repeats shape, and it
does by construction.

## 6. Our numbers

Real run: `results/authors-run.json`, 30 runs (2 arms x 5 tasks x 3
repeats), `claude-haiku-4-5`, against the 5-task baseline in § 4.2. Verified
2026-09-15. This is the standard N>=5-tasks x K>=3-repeats shape SC-5's own
eval requires - `tools/ablation.py validate` passes directly, no disclosed
exception needed, unlike B4/B5/C3.

| Arm | n | Pass rate | Median agent wall (s) |
|---|---|---|---|
| setup-first | 15 | 93% | 50.6 |
| assume-ready | 15 | 93% | 48.6 |

`assume-ready` vs `setup-first`: **+0.0%** (95% CI -20.0 to +20.0) -
inconclusive, interval crosses zero. Per task, the two arms are identical
to the run:

| Task | setup-first | assume-ready |
|---|---|---|
| list-my-teams | 100% | 100% |
| leave-team | 67% | 67% |
| get-single-member | 100% | 100% |
| validate-member-user-exists | 100% | 100% |
| paginate-members | 100% | 100% |

**The mechanism B5 found never fired here at all.** B5's structured
failures were unmistakable in wall-clock time: three of four exited clean
in 15-23 seconds, having asked for permission before writing a line of
code. Sorting this run's 30 wall times finds nothing like it - the fastest
`setup-first` run took 32.8 seconds, and every failure took exactly as long
as a normal successful run (75.6s and 130.1s, both well inside the range of
passing runs in either arm). Reading the `setup-first` agent transcripts
directly confirms it: every one goes straight to reading files and writing
code, with no permission request anywhere in the visible tail. The
front-loaded stall B5 documented is specific to something this ablation
didn't reproduce.

**Both arms' identical `leave-team` failures trace to one FastAPI routing
bug, confirmed by direct reproduction.** All 6 failures (3 setup-first, 3
assume-ready) fail the same way: 3/3 tests fail in ~0.55-0.59 seconds,
versus 1-2 seconds for a real request cycle. Reproducing it directly -
adding the exact same endpoint *after* the pre-existing `remove_member`
route (`DELETE /{team_id}/members/{user_id}`) instead of before it -
reproduces the identical failure: `assert 422 == 200`. FastAPI matches
routes in registration order for the same HTTP method; `.../members/me`
registered after `.../members/{user_id}` gets shadowed, because `"me"`
fails to parse as the `uuid.UUID` the earlier route expects, so every
request 422s before `leave_team`'s own code ever runs. This is a specific,
well-known FastAPI pitfall (a literal path segment placed after a
parameterized one of the same method), not a corner either arm's
instructions relate to - and it fired at exactly the same rate (1/3) in
both arms, which is why the per-task numbers are identical rather than
merely close.

**Why the null doesn't refute B5, and the more precise thing it actually
shows:** B5's ablation varied more than the instruction wording between
its two arms. The `structured` arm's handoff artifacts didn't just say "run
`init.sh` first" - they said it inside a `PROGRESS.md` narrating a
previous session's interruption and a `features.json` with one feature
already flagged unverified. This unit's `setup-first` arm kept the literal
"run `init.sh` first" instruction and dropped everything else: no
interruption story, no partially-done feature, a clean fresh-task prompt.
The effect disappeared completely. The most defensible reading isn't
"structured handoff is fine after all" - it's that B5's own design
conflated two variables (instruction wording and interruption narrative)
that this unit's design deliberately separated, and the separation points
at the narrative, not the wording, as the more likely load-bearing one.
That's a real answer, and it's a materially different claim than the one
B5's README stated as the natural next step (§7 there proposed rewording
the instruction; this result says rewording alone may not be the lever).

**Limitations, stated plainly:**

1. **This ablates one candidate fix, not the narrative hypothesis
   directly.** The natural next unit is not "does rewording help" (this
   unit's null already answers that: not by itself) but "does restoring
   the interruption narrative, with this unit's identical instruction
   wording, bring the effect back." That's a third, not-yet-run ablation,
   named explicitly rather than left implicit.
2. **n=3 per (arm, task) cell.** Bootstrap CIs on 15-run arms are wide
   (-20pp to +20pp here); a true small effect in either direction could be
   hiding inside that interval. The dead-even 93%/93% and identical
   per-task breakdown are more informative than the CI width alone - a
   coincidence this exact would be a strange way for a real, moderate
   effect to hide.
3. **`leave-team`'s routing bug is now a known trap, not a live one for
   future runs of this exact task pool** - anyone re-running this ablation
   with an agent that has seen this README will likely route around it,
   which is worth disclosing so a future re-run's improved leave-team pass
   rate isn't mistaken for a harness change instead of a spoiled fixture.

## 7. What makes this obsolete

The direct next step is named in §6's limitations: ablate the interruption
narrative itself (restore `PROGRESS.md` and a partially-done feature, keep
this unit's identical instruction wording) rather than the wording alone.
If that reproduces B5's effect, the fix worth teaching is "don't hand a
resuming session a story about being interrupted," not "reword the setup
instruction" - a different, more specific claim than either unit has
established on its own. Separately: if Claude Code's permission model adds
a declared-safe marker for routine setup scripts, both this unit's and
B5's `setup-first`/`structured` arms stop being able to trigger the
mechanism at all, and whatever *new* framing produces the next front-loaded
stall becomes the thing worth tracing. And if `spec_lint.py` ever produces
a real `ERROR` against this repo's own `docs/COURSE-SPEC.md` in CI, §3.3's
closing question gets its answer from this repo's own history instead of
staying open.

## 8. Sources

- `docs/CURRICULUM.md` § C4 - the pre-commit-hook framing and the
  trace-analysis-plus-ablation mandate this unit's two parts satisfy.
- `docs/COURSE-SPEC.md` SC-2, SC-4, SC-5 - the exact eval shapes this unit's
  `verify.sh` checks against, including SC-5's requirement that this run
  pass the generic validator directly.
- `units/b5-ship/README.md` § 6-7 - the original trace analysis and the
  specific next step ("moved to the end... or dropped") this unit's
  `assume-ready` arm carries out.
- `units/c3-enforcing-architecture/README.md` - the agent-directed
  remediation pattern `tools/pre-commit-spec-lint` reuses via
  `spec_lint.py`'s own `Fix:` blocks.
- `docs/SKILLS-MAP.md` § Gap analysis, item 4 (`measure-change`) - the
  plugin gap this unit's manual ablation process stands in for.
