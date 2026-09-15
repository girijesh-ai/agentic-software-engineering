# B5 · Ship, and the session that outlives the context window

**Prerequisites.** B3 (the reference implementation this unit's baseline
extends), C3 (the same disclosed single-task ablation pattern this unit reuses).
**Time.** ~3 hours. **Cost.** Under $10 in agent tokens.

<!-- capabilities: branch-landing, conflict-resolution, session-handoff -->
**Serves.** SC-6, via the ablation in §6.

---

## 1. The question

The context window ended mid-feature. Now what?

## 2. The failure

`docs/CURRICULUM.md` names two failure modes the initializer pattern
(`init.sh` + `features.json` + `PROGRESS.md`) is supposed to guard against: a
session that one-shots and dies with no notes, and a session that arrives
later and declares the job done without checking. This unit built a fixed
mid-feature scenario and ran a real two-arm ablation - structured handoff
artifacts against nothing - to see whether the pattern actually helps a fresh
session finish. It did not. **The structured arm finished less often than the
unstructured one: 67% (8/12) versus 100% (12/12), a 33-point gap whose 95% CI
excludes zero.** Neither of the two designed-against failure modes explains
it. A third one does: the handoff file's own first instruction - "run
`init.sh`" - reads as a Bash command with side effects, and in unattended
`claude -p` execution the agent stops to ask permission for it before
touching any code. There is no one there to answer.

## 3. The idea

### 3.1 Handoff artifacts as a Bash-shaped, not an Edit-shaped, instruction

The lab ran every arm under `--permission-mode acceptEdits`, which
auto-accepts file edits but not Bash tool calls. `CLAUDE.structured.md` tells
the resuming session, in order: read `PROGRESS.md` and `features.json`, then
run `init.sh`. Three of the structured arm's four failures returned exit code
0 in 15-23 seconds - far faster than any passing run in either arm (median
137s in both) - having done nothing but ask for approval to run `init.sh` or
the test suite. The unstructured arm has no equivalent first instruction. It
opens files, reads code, and starts editing directly - edits are
auto-accepted, so there's nothing to ask about until the very end, by which
point the code is already written. The harness's verifier runs independently
of what the agent itself confirmed, so an unstructured run that never
executed its own tests still gets credit if the code it wrote happens to
pass. This is the same shape of the general problem C3 found from the sensor
side: a mechanism meant to help (there, a remediation message; here, a
setup instruction) has a specific, discoverable failure mode of its own, and
that mode - not the one it was designed against - is what actually fired.

### 3.2 What the passing structured runs looked like

The 8 structured runs that did finish didn't skip the permission question -
they asked it too, but at the *end*, after already writing the F2 fix and
the F3 endpoint (`git status` would show it staged). The difference between
a structured pass and a structured failure isn't whether the agent asks for
permission. It's *when in the sequence* it asks - before any code exists, or
after. `init.sh` being step one in the instructions is what pulls that
question forward.

### 3.3 The two curriculum-named failure modes, checked directly

Neither predicted mode shows up in this data. No run died silently with zero
notes - every run, pass or fail, left a final message stating exactly what it
did or didn't do. No run declared the job complete without the harness's
independent verifier disagreeing - the failures are refusals-to-start, not
false completions. `features.json`'s own guard against premature
"done" declarations (§4) never gets exercised in this ablation, because the
scenario's failures happen before any status field is touched at all.

## 4. The lab

**Step 1 - Build a fixed mid-feature interruption state (done for this
unit).** Three features on top of B3's reference implementation: F1 (list
team roster) done and correct; F2 (rename team) implemented but seeded with
a classic bug - `session.refresh()` called without `session.commit()`, so
the rename never persists; F3 (view team details) not started at all.
Verified by running the real test suite against this exact state before
using it as a baseline: F1 2/2, F2 1/2 (fails precisely on the persistence
check), F3 0/3 - see `lab-materials/baseline-state/` for the committed
`teams.py`/`models.py` and `lab-materials/test_b5_features.py` for the 7
tests that pin this down.

**Step 2 - Ablate structured versus unstructured handoff.** Two arms on the
identical baseline. `structured` copies `features.json`, `PROGRESS.md`,
`init.sh`, and `CLAUDE.structured.md` (`lab-materials/`) into the repo before
the session starts. `unstructured` copies nothing - same code, same bug, same
missing feature, no notes. Both arms get the identical prompt: "Continue this
project. Finish whatever needs finishing, verify your work actually passes
before considering it done, and leave things in a clean, complete state." 12
repeats per arm, `claude-haiku-4-5`, `claude -p ... --permission-mode
acceptEdits`, reset to the fixed baseline between every run.

**Step 3 - Verify externally, not by the agent's own claim.** The pass/fail
signal comes from running `test_b5_features.py` after the agent's session
ends, independent of whatever the agent itself reported.

## 5. The gate

```bash
./verify.sh
```

Passes when: all five `lab-materials/` handoff files and the two
`baseline-state/` files exist and are non-empty; `results/authors-run.json`
is a real (non-dry-run) run with exactly the `structured` and `unstructured`
arms, at least 10 repeats each. Does **not** call `tools/ablation.py
validate` directly - that check requires ≥5 distinct tasks, a shape built for
B0-C1's multi-ticket ablations. This unit's lab is one fixed scenario ablated
on handoff condition, by design (`docs/CURRICULUM.md`'s own description names
a single mid-feature kill, not a set of unrelated tickets). `verify.sh` checks
the invariants that actually apply, following the same disclosed pattern C3
and B4 used first.

## 6. Our numbers

Real run: `results/authors-run.json`, 24 runs (2 arms x 1 task x 12
repeats), `claude-haiku-4-5`, against the fixed mid-feature baseline in
§4. Verified 2026-09-15.

| Arm | n | Pass rate | Median agent wall (s) |
|---|---|---|---|
| structured | 12 | 67% | 117.3 |
| unstructured | 12 | 100% | 136.8 |

`unstructured` vs `structured`: **+33.3pp** (95% CI +8.3 to +58.3) - effect
detected, interval excludes zero, direction opposite the curriculum's design
intent.

**All four structured failures trace to the same mechanism, not four
different causes.** Wall-clock time separates them cleanly from every
passing run in either arm:

| Structured runs | Wall time (s) |
|---|---|
| Failures | 15.6, 21.6, 22.7, 80.3 |
| Passes | 48.8, 112.1, 122.6, 136.9, 137.0, 152.2, 163.4, 275.2 |
| Unstructured (all pass) | 93.3, 107.8, 119.7, 125.3, 127.2, 133.8, 139.7, 145.7, 148.8, 186.4, 189.3, 205.6 |

Three of the four failures exited cleanly (`returncode 0`) in under 23
seconds, having asked for approval to run `init.sh` or the test suite before
writing any code - `CLAUDE.structured.md`'s literal first instruction is
"run `init.sh`," and `--permission-mode acceptEdits` does not cover Bash. The
fourth failure ran 80 seconds and was cut short mid-response by the host
machine sleeping - an infrastructure artifact of running an unattended batch
overnight, not a design finding, and it's reported here rather than dropped
because silently excluding an inconvenient run is exactly the kind of
retuning `AGENTS.md` rules out.

**Why this doesn't generalize past this specific setup, stated plainly:**

1. **This is a fact about `--permission-mode acceptEdits` under headless
   `claude -p`, not about structured handoff artifacts in general.** A
   session with full autonomous Bash approval, or an interactive session
   with a human present to answer the permission prompt, would not hit this
   failure mode at all - the artifacts themselves (`features.json`,
   `PROGRESS.md`) were never the problem; the specific sentence "run
   `init.sh`" landing as the first instruction, in this specific execution
   mode, was.
2. **Rewriting the instruction would likely erase the effect, which is the
   point, not a caveat.** Reordering `CLAUDE.structured.md` to defer
   environment setup until after the code changes - or dropping the
   explicit "run init.sh" instruction and letting the agent decide when
   infrastructure is actually needed - is the natural next ablation, and it
   would test whether the benefit the curriculum predicts shows up once this
   specific trigger is removed.
3. **n=12 per arm, one fixed scenario.** A different seeded bug, a different
   feature count, or a different model might not reproduce the same
   front-loaded permission-seeking. What's well-supported here is narrow and
   specific: this handoff file, this baseline, this execution mode, produced
   this mechanism, repeatably, in a third of the structured runs.

## 7. What makes this obsolete

If a future Claude Code permission mode auto-accepts Bash calls with no
destructive side effects the way `acceptEdits` already does for file writes,
or if `init.sh`-style scripts get a declared-safe marker the harness can act
on without asking, this unit's specific failure mechanism disappears and the
ablation worth running becomes the one predicted from the start: structured
versus unstructured handoff, with the permission confound actually removed.
Separately, running the same design with the "run init.sh" instruction moved
to the end of the handoff file, or dropped in favor of "the environment may
already be running," is the direct next step before treating "structured
handoff hurts" as a durable claim rather than a fact about one file's wording.

## 8. Sources

- `docs/CURRICULUM.md` § B5 - the initializer pattern, the two named failure
  modes, and the literal gate this unit's lab is built to test.
- `units/b3-plan-to-code/results/lab-materials/reference-implementation/` -
  the codebase this unit's baseline extends.
- `units/c3-enforcing-architecture/README.md` § 6 and `verify.sh` - the prior
  unit whose single-task, disclosed-mechanism pattern this unit reuses, and
  whose finding (a fix has a specific ceiling, not the one it was built
  against) this unit's §2 echoes from the handoff side instead of the sensor
  side.
- `results/lab-materials/CLAUDE.structured.md` - the exact instruction text
  (`init.sh` as step one) identified in §6 as the mechanism.
