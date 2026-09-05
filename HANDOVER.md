# HANDOVER

Read this once, at the start of the first Claude Code session on this repo. After that,
`AGENTS.md` is the standing brief and this file is history.

Written in the shape `handoff` produces: purpose, context, skills to invoke, artifacts,
first actions, done criteria.

---

## Purpose of the next session

Make the repo's own gates real, then produce the first honest number.

The repo currently asserts things about itself that nothing checks. `tools/audit.sh` is
referenced in six places and does not exist. Every *Our numbers* section in every unit is
a placeholder. Until both are fixed, this is a well-argued outline, not a course.

Do not write new units first. That instinct is wrong here and the reason is in
`docs/BUILD-ORDER.md`.

## Context you need

**What this is.** An open-source course on agentic software engineering: 22 units in four
tracks plus two annexes, built on
[`girijesh-ai/spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
(16 skills), which you install and then use to build the course itself.

**The thesis, in one paragraph.** Computational sensors (tests, linters, type checkers)
catch structural problems. Inferential sensors (AI review, LLM-as-judge) catch semantic
ones partially. Neither reliably catches well-formed code that solves the wrong problem.
The only instrument that catches that is a written statement of the right problem — so
the spec is part of the harness, it is load-bearing, and it is the one component nothing
checks. `tools/spec_lint.py` is what checking it looks like. Everything else follows.

**Three commitments that are not negotiable.** They are what the repo has instead of
authority, and an agent optimising for a green build will erode all three:

1. **Never invent a result.** `results/*.json` come from real `ablation.py` runs. A
   plausible hand-written table is the single worst thing that can happen to this repo.
   If numbers don't exist, the section stays marked as a placeholder.
2. **Null and negative results ship.** A unit whose harness did nothing is a finding.
   Never quietly re-run an experiment until it agrees with the prose.
3. **Every claim carries a source or a number.** "Best practice" is not a citation.

**Two rules that will otherwise cause rework.** Claude Code ships `/batch`, `/loop`,
`/review`, `/simplify`, `/debug` and Routines — don't teach what's in the box, teach the
built-in first and then where it stops. And don't rebuild what the ecosystem maintains:
ponytail owns over-engineering audits, Vercel maintains 157 frontend rules, Trail of Bits
ships the security scanner. `docs/ECOSYSTEM-MAP.md` §§ 2 and 7.

**The running thread.** Every lab runs against one real feature in one real repo, carried
from B0 through C6. This is why units get written in thread order rather than by
interest — C3's lab needs a real violation from B3, not an invented one.

## Skills to invoke

Install first; the course depends on it and it is B1's first lab step.

```bash
claude plugin marketplace add girijesh-ai/spec-driven-engineering
claude plugin install spec-driven-engineering@spec-driven-engineering-dev
```

Then use the spine on the course itself: `spec-from-idea` to decide what a unit must do,
`grill-me` to find the section you'd have skipped, `plan-from-spec` to sequence the
writing, `implement`, `review-code` (spec axis first), `finish-branch`. Use `handoff` at
around 60% context rather than 95% — quality degrades well before the window ends.

## Artifacts that already exist

Don't re-derive these. Read them.

| Question | File |
|---|---|
| What is this contractually required to do? | `docs/COURSE-SPEC.md` — 11 Success Criteria with evals |
| What units exist, in what order? | `docs/CURRICULUM.md` |
| What do I work on next? | `docs/BUILD-ORDER.md` |
| What does a finished unit look like? | `units/b1-idea-to-spec/README.md` — reference depth |
| Why this course and not the two that exist? | `docs/POSITIONING.md` |
| Do we cover Stanford CS146S? | `docs/CS146S-COVERAGE.md` + `cs146s.map.json` |
| What should we borrow from other repos? | `docs/ECOSYSTEM-MAP.md` |
| How do the 16 skills map to units? | `docs/SKILLS-MAP.md` + `skills.lock.json` |
| What happens when the plugin changes? | `docs/PLUGIN-CONTRACT.md` |
| What's wrong with the course? | `docs/ARCHITECTURE-AUDIT.md` — findings and their status |

Working tools, standard library only: `tools/spec_lint.py`, `tools/ablation.py`,
`tools/check_skills_map.py`, `tools/check_coverage.py`.

**Verify a complete checkout — 27 files.** If `tools/spec_lint.py`, `cs146s.map.json` or
`units/b1-idea-to-spec/README.md` are missing, stop and get them; `AGENTS.md` references
all three and nothing below will run.

## First actions, in order

**1. Write `tools/audit.sh`.** Everything else depends on it. It must check:

- `AGENTS.md` is ≤ 120 lines
- every `units/*/README.md` has all eight required sections (`docs/CURRICULUM.md`
  § Unit shape), including *What makes this obsolete*
- every unit declares `<!-- capabilities: … -->`
- internal markdown links resolve
- `docs/CS146S-COVERAGE.md` is under 12 months old
- every shipped unit has a non-dry-run `results/authors-run.json` whose id matches its
  directory

It will fail on first run. That is correct — it is measuring a half-built repo. Record
the failures in `AGENTS.md` § Known gaps rather than weakening the checks.

**2. Wire CI.** One workflow: `audit.sh`, `spec_lint.py docs/COURSE-SPEC.md`,
`check_skills_map.py --plugin-dir …`, `check_coverage.py --allow-planned`.

**3. Clear the W2 blocker.** `check_coverage.py` fails on CS146S Week 2 — our source
skipped it and a superset claim can't cover material nobody has read. Read the primary
syllabus, update `cs146s.map.json`. Cheapest task in the backlog; it's the only thing
between here and an unasterisked superset claim.

**4. Then, next session: `units/b1-idea-to-spec/verify.sh` and B1's real ablation.**
Four arms per that unit's § 6, against `tiangolo/full-stack-fastapi-template`, five tasks
× three repeats. Budget a few hours and a few dollars. If the spec turns out to make no
measurable difference, publish that. The repo promises it in three places and this is the
cheapest moment to find out whether we meant it.

## Done criteria for session one

- `tools/audit.sh` exists, runs, and every failure it reports is traceable to content
  that hasn't been written yet
- CI runs all four gates on push
- `check_coverage.py --allow-planned` exits 0, or the W2 entry honestly explains why not
- `AGENTS.md` § Known gaps reflects reality
- Everything committed; a note in the commit body saying what's still red and why

A session that ends red without updating Known gaps has lost information. That is worse
than ending early.

## What not to do

- Don't write new unit prose this session. `docs/BUILD-ORDER.md` § Order of value.
- Don't weaken a gate to make a build green. If a check is wrong, change it deliberately
  and say why in the commit.
- Don't add dependencies to `tools/`. Standard library only — a measurement tool that
  needs its own environment setup is a measurement tool nobody runs.
- Don't add skills to this repo. Workflow lives in the plugin; gaps get recorded in
  `skills.lock.json` § `expected_gaps`. `docs/PLUGIN-CONTRACT.md` § 5 is the boundary.
- Don't attempt two backlog items at once.
