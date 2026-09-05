# Course spec: Agentic Software Engineering

Written with `spec-from-idea`, linted with `tools/spec_lint.py`. This file is what
every other artifact in the repo is checked against. A unit that can't trace to a
Success Criterion here doesn't ship.

---

## Problem

An engineer who uses coding agents daily has three separate things they don't have,
and the available material gives them at most one each.

They don't have a **workflow** — a repeatable path from an idea someone described in a
meeting to a merged change, where each stage checks its work against the stage before
it. They have a chat window and habits.

They don't have a **harness** — the guides, sensors and constraints that make that
workflow survive a real repo, a real team, and an agent that will happily route around
any rule not backed by a check.

And they don't have a **measurement** — any way to know whether the `CLAUDE.md` they
spent a weekend on is worth anything.

The material that exists is split along exactly these lines. University courses survey
the landscape without leaving you a working workflow. The harness courses teach the
environment but assume you already know what you're building. Nobody teaches the join,
and the join is where the interesting failure lives: the spec is the behaviour harness,
and nothing checks the spec.

## Who this is for

**Primary.** Engineers and senior/staff engineers who already run coding agents on
real codebases most days and are dissatisfied with the reliability. They can let an
agent edit files and run commands, read a stack trace, and are willing to run labs
against their own repo rather than a toy.

**Secondary.** Tech leads and engineering managers who have to make and defend an
adoption decision. Track D is written for them and reads standalone.

**Explicitly not for.** People who have never used a coding agent — the pacing will
lose you. People who want prompt tips. People who won't run the labs, because the labs
are the course and the prose is the connective tissue.

## Non-goals

- Teaching programming, git, or a specific agent CLI's flags.
- Building an agent framework. We harness existing agents.
- Vendor-neutrality theatre. Labs name a reference CLI and stack, with a documented
  porting contract. The concepts are portable; the commands aren't pretending to be.
- Competing with `walkinglabs/learn-harness-engineering` on beginner harness
  fundamentals. We link to it and assume it.
- Translations, a hosted docs site, or video, before the content is proven.

## Approaches considered

**A. Extend `spec-driven-engineering` with a `docs/course/` directory.** Cheapest, and
keeps workflow and teaching in one place. Rejected: the plugin should stay a tight,
installable tool. A course inside it makes the repo about learning rather than about
working, and it can't carry Tracks A, C and D without bloating.

**B. A general agentic-coding course.** Broadest audience. Rejected on its own terms —
CS146S covers the survey, `learn-harness-engineering` covers the harness, and a third
general course with neither an installable workflow nor original measurement has no
reason to exist.

**C. Spine-first course with the plugin as its tooling, harness engineering as the
"go beyond", and measurement as the pedagogy.** Chosen. The curriculum and the tooling
are the same artifact, which is structurally hard for anyone else to copy — it requires
having built and dogfooded a 16-skill workflow first.

---

## Success Criteria & Evals

`SC-*` are the contract. Anything not listed is out of scope for v1.

### SC-1 — A learner can tell a model problem from a harness problem

**Criterion.** After A2, given five of their own recorded agent failures, a learner
classifies each as model-limited or harness-fixable, and for the harness-fixable ones
names the specific configuration point that would address it.

**Eval.** `units/a2-*/verify.sh` scores a written classification against a rubric;
≥4 of 5 with a stated reason passes. A classification with no named configuration
point does not count as correct.

### SC-2 — A learner can write a spec that survives a lint

**Criterion.** After B1, a learner has a spec in their own repo where every Success
Criterion is falsifiable, names an eval, and at least one criterion describes
behaviour on failure.

**Eval.** `python3 tools/spec_lint.py <spec>` exits 0. Not `--strict`; warnings are
allowed at this stage.

### SC-3 — A learner can trace a plan to its spec

**Criterion.** After B2, every step in a learner's implementation plan names the
Success Criterion ID it serves and the verification that proves it.

**Eval.** `units/b2-*/verify.sh` parses the plan and fails on any orphan step — a step
with no `SC-n` reference — and on any referenced ID absent from the spec.

### SC-4 — A learner can build a sensor an agent can act on

**Criterion.** After C3, a learner has one custom check in their repo whose failure
output carries remediation into agent context: what's wrong, what must not be touched,
ranked likely causes, and a reproduce command.

**Eval.** `units/c3-*/verify.sh` asserts the check fires on a seeded violation and that
its output contains all four elements. Plus an ablation (SC-5) comparing turns-to-fix
against the same check emitting a bare verdict.

### SC-5 — A learner can measure a harness change

**Criterion.** After C4, a learner has a committed results file for a harness change on
their own repo: N≥5 tasks × K≥3 repeats, two arms, with a bootstrap confidence
interval — and they can say whether the effect survived it.

**Eval.** `python3 tools/ablation.py validate <results>` exits 0. A result whose
interval crosses zero still passes the eval; reporting it honestly is the point.

### SC-6 — Every unit survives contact with a number

**Criterion.** Each shipped unit contains `results/authors-run.json` produced by
`tools/ablation.py`, and its *Our numbers* section reports what happened including null
and negative results.

**Eval.** CI job `unit-results` fails the build if any `units/*/` lacks a non-empty,
non-dry-run `results/authors-run.json` whose module id matches the directory.

### SC-7 — The repo is its own worked example

**Criterion.** `AGENTS.md` is under 120 lines and acts as a map; `docs/` is the system
of record; CI enforces unit shape, link integrity and staleness.

**Eval.** `tools/audit.sh` exits 0 on `main`. Any unit README missing a required
section fails the build.

### SC-8 — Obsolescence is stated, not hidden

**Criterion.** Every unit ends with *What makes this obsolete*, naming the model
capability or tooling change that retires the technique.

**Eval.** `tools/audit.sh` greps for the required heading in every unit README.

### SC-11 — A learner ships working software, not just documents

**Criterion.** By the end of Track C a learner has landed one real change in one real
repository, carried through B0→C6 as the running thread, with the spec, plan, review and
harness artifacts that produced it.

**Eval.** The capstone gate additionally requires a merged or opened PR whose diff is
traceable to a Success Criterion in the learner's own spec. A learner holding only
analysis artifacts has not passed, regardless of their quality.

**Why this exists.** The architecture audit found twelve of twenty-one units produced a
document rather than software. This criterion is the contract that stops that recurring.

### SC-9 — The course survives the plugin evolving

**Criterion.** The plugin is at v1 and will grow. No unit hard-codes a skill name as its
only reference; every unit declares the capabilities it teaches, and one file binds
capability to skill. When the plugin renames, splits or adds a skill, the course either
still works or fails loudly — never silently teaches a name nobody has.

**Eval.** `python3 tools/check_skills_map.py --plugin-dir <checkout>` exits 0. It errors
on a capability no unit binds and on a binding the plugin no longer provides, warns on a
stale version pin, and reports — as info, not failure — every plugin skill the course
does not yet know about. See [`PLUGIN-CONTRACT.md`](PLUGIN-CONTRACT.md).

### SC-10 — Coverage claims have an expiry

**Criterion.** The claim that this course covers CS146S is auditable week by week, dated,
and states its deliberate omissions rather than implying completeness.

**Eval.** [`CS146S-COVERAGE.md`](CS146S-COVERAGE.md) exists, carries a date, names every
week with a verdict, and `tools/audit.sh` warns when it is over 12 months old.

---

## Out of scope for v1

Multi-agent framework design. Non-reference agent CLIs beyond the porting contract.
Translations. A hosted site. Video. Certification.

## Open questions

1. ~~**Reference agent CLI.**~~ **Resolved.** The Agent Skills spec is adopted by Claude
   Code, Codex CLI, Cursor, Gemini CLI and Copilot, and a skill runs on all of them
   unmodified. So: multi-agent is a stated fact rather than a porting apology, labs use
   Claude Code for concreteness, and cross-agent delegation (`skill-codex`) is taught in
   A5 as a real pattern rather than a compatibility footnote.
2. ~~**Shared lab repo.**~~ **Resolved:** `tiangolo/full-stack-fastapi-template`. Real,
   permissively licensed, Python-primary, cheap to run — and it already carries a
   published external ablation baseline from ponytail's benchmark (12 feature tickets,
   n=4, three control arms), which means a learner's numbers have something independent
   to sit beside. Labs stay dual-track: your repo for value, this one for the gate.
3. **Does the plugin absorb the five proposed skills, or does the course ship its own?**
   See `docs/SKILLS-MAP.md` § gap analysis and `skills.lock.json` § `expected_gaps`.
   Leaning toward the plugin absorbing `lint-spec` and `write-sensor` since they close
   existing holes regardless. Note that C6 now teaches readers to write them, so this
   may resolve itself through contribution rather than decision.
4. **Does Track D justify its own repo?** Different audience, different shape. Keep it
   here for v1; split if it outgrows four units.

## Traceability

| Track | Units | Serves |
|---|---|---|
| A Foundations | A1–A5 | SC-1 |
| B Spine | **B0** brownfield onboarding | SC-11 |
| B Spine | B1–B5 | SC-2, SC-3 |
| C Harness | C1–C6 | SC-4, SC-5 |
| D Production & org | D1–D4 | SC-5 |
| E ML specialization | `tracks/ml-systems/` | its own spec |
| The running thread | B0–C6 | SC-11 |
| Every unit | — | SC-6, SC-8, SC-9 |
| Repo itself | — | SC-7, SC-10 |
