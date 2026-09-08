# B2 · Spec → plan

**Prerequisites.** B1 (you can write a spec that survives `spec_lint`).
**Time.** ~2.5 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: plan-authoring, architecture-lens -->
**Serves.** SC-3.

---

## 1. The question

How does a plan step prove it did what the spec asked?

## 2. The failure

Hand an agent a spec and the phrase "implement this" and it will produce a plan-shaped
list of things to do — and every item on that list will look reasonable, because a
plan step that doesn't visibly trace to anything doesn't visibly fail to trace to
anything either. The gap only shows up later, when a reviewer (human or agent) tries
to check whether the implementation actually satisfies the spec and discovers there's
no map from "this code" back to "that requirement." At that point the only way to
check is to re-read the whole diff against the whole spec from scratch — exactly the
work a plan was supposed to save.

The concrete version, found while writing this unit's own plan
([`plan-team-sharing.md`](results/lab-materials/plan-team-sharing.md)): the first
draft of Step 6 (blocking removal of a team's last owner) had no natural home in the
spec's eight Success Criteria, because it resolves an *open question* the spec left
unresolved rather than satisfying a stated criterion. Writing "Serves: SC-4" on it
anyway — because every other step had a Serves line and leaving one blank looked like
an oversight — would have been a false trace: a reviewer checking SC-4 against Step 6
would find code that has nothing to do with SC-4's actual claim (owner full access),
sitting there under its number. The honest fix was a step that explicitly says
"Serves: none directly" and states why. A plan format that has no way to say "this
step is real but doesn't map to a criterion" quietly pressures you toward the false
trace instead.

## 3. The idea

### 3.1 A step with no verification is a step the agent grades itself on

If nothing checks whether "add the database migration" actually ran, the agent
decides for itself when that step is done — and it will decide generously, the same
way B1's thesis says an ungated spec criterion gets interpreted generously. Tracing
every step to a spec eval isn't paperwork; it's what makes "done" mean something
other than "the agent said so."

### 3.2 Architecture is a decision, not a byproduct

`docs/CURRICULUM.md` names this directly: module depth, interface width, and layer
boundaries get decided *before* code exists, or they get decided by accident once
4,000 lines already assume an answer. This unit's own plan makes exactly one such
decision up front — permission-checking moves from eight inline copies into one
`get_item_with_permission` dependency — and states it as Step 0, ahead of any
numbered, spec-traced step, because it's a decision about where the seams go, not a
requirement the spec asked for. Conflating the two (numbering it "Step 1" and forcing
a `Serves:` line onto it) would have been the same false-trace mistake as §2's Step 6,
in the other direction.

### 3.3 Two ways to plan, and knowing which one you're doing

`obra/superpowers` plans in *tasks*: 2–5 minute units with exact file paths and
verification steps. This spine plans in *criteria that steps trace back to*. A task
plan is easier to start writing. A criteria-traced plan is what makes an orphan-step
gate possible at all — you can mechanically ask "does every requirement have a step,
and does every step serve a requirement" only if steps carry that reference in the
first place. Neither is wrong; picking one without knowing you picked it is how a
team ends up unable to answer "did we build what we said we would."

## 4. The lab

**Step 1 — Write a real spec for the running thread (done for this unit).**
[`spec-team-sharing.md`](results/lab-materials/spec-team-sharing.md): team-based item
sharing with roles, the feature picked in B0. Three approaches considered, one chosen
and justified, eight Success Criteria, `spec_lint.py` clean.

**Step 2 — Plan it, tracing every step (done for this unit).**
[`plan-team-sharing.md`](results/lab-materials/plan-team-sharing.md): one architecture
decision made before any step, six steps, every step naming the SC(s) it serves or
explicitly stating it serves none. This is what B3 builds from.

**Step 3 — Write the gate that checks traceability mechanically.**
[`check_plan_traceability.py`](results/lab-materials/check_plan_traceability.py):
parses `**Step N — ...**` blocks, requires a `Serves:` line naming real `SC-n` IDs or
the literal phrase "none directly," and separately checks every SC in the spec has at
least one step. Confirmed it actually catches a real orphan step and a real uncovered
criterion before trusting it against the real plan (see the tool's own module
docstring for why "silence" isn't accepted as an exception).

**Step 4 — Ablate the *other* claim this unit makes: does traceability change
outcomes, not just auditability?** Held B1's five tasks and their final specs fixed
across both arms (only the plan varies), to isolate the one variable this unit is
actually about. Arm A gets a plan whose steps carry `Serves: SC-n`; Arm B gets the
identical steps with that line removed — same information about *what* to build,
differing only in whether the plan states *which requirement* each step is for.

## 5. The gate

```bash
./verify.sh
```

Passes when: `spec_lint.py` exits 0 on the spec; `check_plan_traceability.py` finds
zero orphan steps and zero uncovered criteria; and `results/authors-run.json`
validates (`tools/ablation.py validate`), not a dry run.

Traced to **SC-3** in [`docs/COURSE-SPEC.md`](../../docs/COURSE-SPEC.md).

## 6. Our numbers

Real run: `results/authors-run.json`, 30 invocations (2 arms × 5 tasks × 3 repeats),
`claude-haiku-4-5`, against the same `tiangolo/full-stack-fastapi-template` clone and
the same five verifier-first tasks B1 used — spec held constant, plan format is the
only variable. Verified 2026-09-08.

| Arm | Pass rate | Median agent wall (s) |
|---|---|---|
| Traced plan (`Serves: SC-n` on every step) | 80% (12/15) | 69.5 |
| Task-list plan (same steps, no SC references) | 100% (15/15) | 80.5 |

`task-list-plan` vs `traced-plan`: **+20.0pp** (95% CI +0.000 to +0.400 —
**inconclusive**, interval crosses zero). Numerically the untraced plan did *better*,
the opposite direction from this unit's own thesis. n=15 per arm is not enough to
call this real, and reading the two `traced-plan` failures directly says it isn't:

- `items-count`, one repeat: the agent stopped and asked a clarifying question about
  which of several implementation approaches to take instead of implementing
  anything. In a non-interactive `-p` invocation nobody answers, so the run ends with
  no code changes at all. Nothing in the traced plan asked for this; it reads as
  model-sampling variance in whether the agent treats "a spec exists" as license to
  re-litigate the approach.
- `items-search`, one repeat: the agent built a plausible client-side (frontend)
  search filter instead of the backend `?q=` parameter the plan specified. A
  different, reasonable-looking solution to an adjacent problem — this unit's own
  §2 thesis, borrowed from B1, happening to its own ablation.

Neither failure mentions or reacts to the presence or absence of a `Serves:` line.
**This is a null result on the pass-rate question, reported as one rather than
re-run until it looked better.** What the traced plan format buys, on this evidence,
is not measured here at all — it's the mechanical auditability
`check_plan_traceability.py` checks (§5), which a task-list plan doesn't offer
regardless of how often its code happens to pass tests.

## 7. What makes this obsolete

If a model reliably infers verification criteria from an untraced task list as
well as it does from an explicit `Serves:` line — which this session's own data does
not rule out — the traceability discipline stops buying anything a model doesn't
already do unprompted, and this unit's gate becomes a formatting preference. Watch
the ablation in §6 age; a larger, cleaner replication that still finds no pass-rate
effect would be the actual argument for retiring the SC-tracing requirement in favor
of the plain task-list format `obra/superpowers` already uses.

## 8. Sources

- `docs/CURRICULUM.md` § B2 — architecture-before-code, and the `obra/superpowers`
  comparison this unit's §3.3 is built on.
- `docs/COURSE-SPEC.md` SC-3, SC-5, SC-6 — the traceability, ablation-shape, and
  every-unit-survives-a-number criteria this unit's gate and lab satisfy.
- `units/b1-idea-to-spec/README.md` — the sensor-gap thesis this unit's §2 example
  borrows directly (a plausible-but-adjacent solution, this time inside the
  ablation itself).
- Direct exploration of `tiangolo/full-stack-fastapi-template` (via B0's map) for the
  architecture decision in `plan-team-sharing.md` § Architecture decision.
