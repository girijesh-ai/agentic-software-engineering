# Course spec: Harness Engineering for ML Systems

Written with `spec-from-idea`. This file is the thing every other artifact in the
repo is checked against. If a module can't trace to a Success Criterion here, it
doesn't ship.

---

## Problem

An engineer running coding agents on an ML codebase hits failures that no published
harness guidance addresses. The agent declares a training script "working" because it
exits 0. It tunes a threshold until a metric moves and calls that a fix. It edits a
notebook into a state nobody can review. It burns two GPU-hours discovering that the
fixture had leakage. It cannot tell a real 0.3-point regression from seed noise, so
it either chases ghosts or ignores real damage.

The existing literature assumes tests are boolean, fast, cheap and deterministic.
In ML systems none of those hold. Engineers are left to improvise the most important
part of the harness — the sensor — with no guidance at all.

Meanwhile the person who owns the team has a second, unaddressed problem: which repo
to harness first, what to standardise, what to measure, and how to know whether any
of it worked.

## Who this is for

**Primary.** ML engineers and senior/staff engineers who already use Claude Code,
Codex or similar daily on Python ML codebases and are dissatisfied with the
reliability. They can read a stack trace, run a training job, and let an agent edit
files and execute commands in a real repo.

**Secondary.** Engineering managers and tech leads responsible for AI/ML delivery who
need to make an adoption decision they can defend with numbers.

**Explicitly not for.** People new to coding agents (send them to
`walkinglabs/learn-harness-engineering` first — this course assumes its content).
People who want prompt tips. People who won't run the labs.

## Non-goals

- Teaching Python, ML fundamentals, or how to use a specific agent CLI.
- Being a general agentic-coding course. That space is well served.
- Vendor neutrality theatre. Labs are written against a named agent CLI and a named
  stack, with a documented porting contract; the concepts are portable, the commands
  aren't pretending to be.
- Building an agent framework. We build harnesses *around* existing agents.

## Approaches considered

**A. Fork the existing course and add ML modules.** Fastest. Rejected: inherits an
Electron/TypeScript capstone and a beginner arc that our audience should skip, and
positions us as a derivative.

**B. General "CS146S + harness engineering" course.** Broadest audience. Rejected:
head-on collision with a 9.6k-star incumbent that is already translated into fifteen
languages. See `POSITIONING.md` §2.

**C. ML-native, measurement-first, with a leadership track.** Chosen. Narrower
audience, defensible wedge, and the labs can only be written by someone who has
actually run ML pipelines under an agent — which is the moat.

---

## Success Criteria & Evals

Each criterion is measurable and has a named eval. `SC-*` are the contract; anything
not listed here is out of scope for v1.

### SC-1 — A learner can quantify their own harness

**Criterion.** After M00, a learner has a committed `results/baseline.json` for their
own repo: N≥5 tasks × K≥3 repeats, run with and without their current harness,
reporting pass rate, wall time, turns, and cost per task with a bootstrap confidence
interval.

**Eval.** `python tools/ablation.py validate results/baseline.json` exits 0. Requires
both arms present, K≥3, and a `verifier` command recorded per task.

### SC-2 — Every module survives contact with a number

**Criterion.** Each shipped module directory contains `results/authors-run.json`
produced by `tools/ablation.py`, and its README states the observed delta including
cases where the delta was null or negative.

**Eval.** CI job `module-results` fails the build if any `modules/m*/` lacks a
non-empty `results/authors-run.json` whose `module_id` matches its directory.

### SC-3 — A learner can build a sensor for a statistical target

**Criterion.** After M04, a learner has a verifier for an ML task that (a) returns a
boolean an agent can act on, (b) derives its threshold from a measured noise floor
rather than a guessed constant, (c) pins seeds and records them, and (d) emits a
failure message containing remediation instructions.

**Eval.** `modules/m04-*/verify.sh` runs the learner's verifier against three seeded
fixtures — a true pass, a true regression, and a within-noise wobble — and asserts
pass / fail / pass respectively. A verifier that fails the wobble case is
mis-calibrated and the lab does not pass.

### SC-4 — A learner can make expensive verification affordable

**Criterion.** After M05, a learner has a three-tier verification ladder for one real
pipeline: a micro-fixture tier under 30 seconds, a subset tier under 10 minutes, and
a full tier, with a documented rule for which tier gates which event.

**Eval.** `verify.sh` times tier 1 and fails if it exceeds 30s wall time; asserts the
tier-1 fixture catches at least 2 of 3 seeded defects injected by the lab.

### SC-5 — A learner can distinguish a spec failure from a harness failure

**Criterion.** After M03, given five recorded agent failures, a learner correctly
classifies each as missing guide / missing sensor / missing spec, and for the
spec-class failures demonstrates that no computational or inferential sensor would
have caught it.

**Eval.** Scored classification exercise with a published answer key and stated
rationale; ≥4 of 5 to pass. The answer key is itself an artifact under review.

### SC-6 — An engineering leader leaves with a defensible rollout

**Criterion.** After M11, a leader has a one-page rollout plan naming: the first
topology to harness and why, the four metrics they will report, the human-judgment
work they are explicitly *not* automating, and their stop-loss condition.

**Eval.** Peer review against `templates/rollout-plan.md`'s checklist in a public
discussion thread; a plan with no stated stop-loss condition does not pass.

### SC-7 — The repo is its own worked example

**Criterion.** This repository is harnessed to its own standard: an `AGENTS.md` under
120 lines acting as a map, a linted `docs/` knowledge base, and CI sensors enforcing
link integrity, module-shape conformance, and staleness.

**Eval.** `tools/audit.sh` exits 0 on `main`. Any module README missing a required
section fails the build. A learner can read our harness as the reference
implementation of what we're asking them to build.

### SC-8 — Obsolescence is stated, not hidden

**Criterion.** Every module ends with a "What makes this obsolete" section naming the
model capability or tooling change that would retire the technique.

**Eval.** `tools/audit.sh` greps for the required heading in every module README.

---

## Out of scope for v1

Multi-agent orchestration frameworks. RL environment design for training MLE agents.
Non-Python stacks. A hosted docs site (Markdown on GitHub first; VitePress only once
content quality is proven). Translations (the incumbent's fifteen-language spread is
not a fight worth picking early).

## Open questions

1. **Which agent CLI is the reference?** Labs need one to be concrete. Proposal:
   Claude Code as reference, with a `docs/porting.md` contract for Codex and others.
   Decide before M01 ships.
2. **What is the shared capstone repo?** Needs to be real, Python, ML, permissively
   licensed, and small enough to run cheaply. Candidates to evaluate: a scikit-learn
   pipeline template, a small HF fine-tune, or a purpose-built repo with seeded
   defects. Purpose-built gives control over the defect set (which SC-4's eval needs)
   at the cost of realism.
3. **How do learners with no GPU do M05?** Micro-fixtures are the answer, but the
   full tier needs *something*. Options: CPU-only tier-3, a recorded trace to replay,
   or a small hosted budget.
4. **Does the leadership track belong in this repo or its own?** M11 has a different
   audience and a different shape. Keep it here for v1; split if it grows past one
   module.

## Traceability

| Module | Serves |
|---|---|
| M00 Baseline | SC-1 |
| M01 Anatomy | SC-1, SC-7 |
| M02 Repo as record | SC-7 |
| M03 Spec as behaviour harness | SC-5 |
| M04 Statistical verification | SC-3 |
| M05 Expensive verification | SC-4 |
| M06 Data harness | SC-3, SC-4 |
| M07 Notebook path | SC-7 |
| M08 ML sensors | SC-3 |
| M09 Loops and fleets | SC-2 |
| M10 Safe autonomy | SC-2 |
| M11 Leadership | SC-6 |
| M12 Capstone | all |
| Every module | SC-2, SC-8 |
