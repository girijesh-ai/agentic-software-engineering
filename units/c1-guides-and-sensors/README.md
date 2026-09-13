# C1 · Guides and sensors

**Prerequisites.** B0-B3 (this unit audits the harness they just carried a real
feature through).
**Time.** ~2 hours. **Cost.** $0 — no new agent invocations; see §4.

<!-- capabilities: harness-audit, minimality-guide -->
**Serves.** SC-6 (via a meta-analysis of B1-B3's own already-collected data, not a
fresh ablation — see §4 for why that's the honest way to satisfy it here).

---

## 1. The question

Are you steering the agent, or just grading it?

## 2. The failure

Four units in (B0-B3), this course had produced four real ablations and never once
asked whether they had anything in common. Each README's §6 reported its own effect
in isolation: B0's map helped speed, not correctness; B1's spec helped correctness a
lot; B2's plan-traceability format didn't move anything; B3's live test beat
self-testing by the largest margin in the course. Read separately, that's four
unrelated results. Read through Böckeler's guide/sensor vocabulary, it's one pattern
with an exception worth taking seriously — see §6.

The sharper, more uncomfortable failure showed up while building the coverage map
itself (§3, `coverage-map.md`): this course's own harness has an inferential-sensor
row with exactly one entry, and that entry has never run. B1 flagged "wrong-problem
failures needs a human grader" in its very first real ablation. Three units later,
it's still flagged, not fixed. Naming a gap once is diagnosis. Naming it three times
without acting on it is the failure this unit exists to stop being polite about.

## 3. The idea

### 3.1 The vocabulary, applied rather than defined

Guides steer before the agent acts; sensors observe after so it can self-correct.
Computational controls are deterministic and cheap; inferential ones are semantic,
slow, and model-judged. [`coverage-map.md`](results/lab-materials/coverage-map.md)
classifies every real mechanism in this repo against both axes — not a hypothetical
audit, the actual `tools/`, CI, skills, and per-unit gates that exist today.

### 3.2 What the map shows before the numbers do

Every mechanism this course has actually built is computational except three
plugin skills (`spec-from-idea`, `plan-from-spec`, `grill-me`), and all three of
those were used by the author preparing a static artifact, never by an agent being
measured. This asymmetry is visible in the map alone, before running a single
comparison — which is the point of building the map before reaching for a number
(the same order B0 argues for repo comprehension).

### 3.3 Harnessability cuts both ways

A 4,000-line god module affords no harness; clean boundaries afford a real one. The
inverse is also true of this course's own harness: the reason B1-B3's verifiers are
trustworthy is that each is a small, focused pytest file checking one behavior. The
reason `spec_lint.py` stays computational instead of becoming an LLM-judge call is
that its checks (a named eval, a failure-behavior criterion, an unfalsifiable
adjective) are exactly the kind of thing regex can catch reliably. Cheap sensors stay
cheap by being scoped to what determinism can actually verify — reaching for
inference where a regex would do is the harnessability lesson in reverse.

### 3.4 Timing, and where this course's own harness violates its own principle

"Keep quality left" means fast, cheap sensors before the commit; expensive ones
after; drift sensors running continuously. Every sensor this course has built fires
once, at the end of an agent's turn. `top-three-gaps.md` § Gap 3 takes this
seriously rather than filing it as a footnote: it's the most likely reason B3's
test-first arm reached 93%, not 100%, despite having the strongest single
intervention this course has measured.

## 4. The lab

**Step 1 — Build the coverage map (done for this unit).**
[`coverage-map.md`](results/lab-materials/coverage-map.md): every mechanism in
`tools/`, CI, the plugin, and each unit's own gate, classified guide/sensor x
computational/inferential.

**Step 2 — Defend the top three gaps (done for this unit).**
[`top-three-gaps.md`](results/lab-materials/top-three-gaps.md), each argued from
the map and from B0-B3's actual data, not asserted.

**Step 3 — Re-read B0-B3's data through the guide/sensor axis instead of running a
fifth ablation.** This unit's "number" comes from regrouping 105 already-real,
already-validated runs from B1, B2, and B3 (same five tasks, same repo, same model,
same verifiers throughout) by whether the intervention was a live, checkable sensor
or a static guide, rather than by their original arm labels. No new agent
invocations were made — see `results/authors-run.json`'s `config.agent_command`
field, which documents this explicitly rather than pretending a fresh run happened.
This is the deliberate exception to "always run `ablation.py` fresh": the data
already exists, is real, and re-asking the same five tasks a fifth time would cost
real money to re-confirm something already measured three times over.

## 5. The gate

```bash
./verify.sh
```

Passes when: `coverage-map.md` and `top-three-gaps.md` exist and are non-empty;
`results/authors-run.json` validates (`tools/ablation.py validate`), is not a dry
run, and every run's `original_unit` field traces to a `results/authors-run.json`
that itself validates in `units/b1-idea-to-spec`, `units/b2-spec-to-plan`, or
`units/b3-plan-to-code`.

## 6. Our numbers

Meta-analysis of 105 real runs from
[`b1`](../b1-idea-to-spec/results/authors-run.json),
[`b2`](../b2-spec-to-plan/results/authors-run.json), and
[`b3`](../b3-plan-to-code/results/authors-run.json) (same five tasks, same
`tiangolo/full-stack-fastapi-template` clone, same `claude-haiku-4-5`, same
verifiers throughout), regrouped by guide/sensor category rather than original arm.
Full record in `results/authors-run.json`. Verified 2026-09-13.

| Group | Pass rate | n |
|---|---|---|
| Nothing (B1 no-harness) | 73% | 15 |
| Guide-only (6 arms pooled: B1 prompt-only/spec-unlinted/spec-linted-grilled, B2 both arms, B3 self-tested) | 81% | 90 |
| Guide+sensor (B3 test-first) | 93% | 15 |

Pooled comparisons: `guide-only` vs `nothing` +7.8pp (95% CI -14.4 to +33.3,
inconclusive), `guide+sensor` vs `guide-only` +12.2pp (95% CI -4.4 to +24.4,
inconclusive), `guide+sensor` vs `nothing` +20.0pp (95% CI -6.7 to +46.7,
inconclusive). **None of the three pooled comparisons are statistically real at
this n.**

**That null result is itself the finding, and it's a warning about this unit's own
method.** Two of the six arms folded into "guide-only" showed real, CI-excludes-zero
effects in their *original*, properly controlled comparisons: B1's spec vs no-harness
(+26.7pp, real) and B3's own test-first vs self-tested (-40.0pp, real, reported in
B3 §6). Pooling six guide conditions of wildly different quality — a generic
CLAUDE.md paragraph that scored *worse* than nothing, next to a pressure-tested spec
that scored 100% — erases both real effects into a single inconclusive bucket. The
guide/sensor axis is a real, useful vocabulary (§3), but this unit's own attempt to
test it by crude pooling demonstrates that the axis alone, without controlling for
how specific and falsifiable a guide is, is not a strong enough predictor to recover
signal that a properly matched pairwise comparison already found. Report this as a
method lesson, not a reason to distrust B1's or B3's original numbers — those still
hold, individually, exactly as published.

## 7. What makes this obsolete

The vocabulary (guide/sensor, computational/inferential) is a lens, not a
technology — it doesn't date the way a specific tool does. What could obsolete this
unit's *lab* specifically: a plugin skill that builds the coverage map
automatically from a repo's own CI config and skill bindings, which would turn
Step 1 into a report to read rather than an exercise to do by hand
(`skills.lock.json`'s `harness-audit` expected-gap entry already names this exact
replacement).

## 8. Sources

- `docs/CURRICULUM.md` § C1 — the guide/sensor/computational/inferential vocabulary,
  from Böckeler, this unit's lab and gap analysis are built on directly.
- `units/b0-onboarding-a-codebase/README.md`, `units/b1-idea-to-spec/README.md`,
  `units/b2-spec-to-plan/README.md`, `units/b3-plan-to-code/README.md` § 6 —
  the four original, properly controlled ablations this unit's own meta-analysis
  regroups and, in §6, shows the limits of regrouping.
- `AGENTS.md` § Known gaps — the "wrong-problem failures ungraded" line, carried
  since B1, the evidence behind Gap 1.
