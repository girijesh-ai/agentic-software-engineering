# CLAUDE.md - everything about this repo, in one file
This file contains this repo's full documentation, concatenated for convenience so you never have to go looking for another file.


<!-- ===== BEGIN AGENTS.md ===== -->

# AGENTS.md

A **map, not a manual**. Stays under 120 lines. If you're writing a fifth paragraph
about something, it belongs in `docs/` and this file gets a pointer instead.

Enforced: `tools/audit.sh` fails the build if this file exceeds 120 lines.

## What this repo is

An open-source course on agentic software engineering. The product is documentation,
labs and measurement tooling — not an application.

It is also its own worked example. Learners are told to read our harness as a reference
implementation of what we're asking them to build. Sloppiness here is a content bug.

## Where the truth lives

| Question | Read |
|---|---|
| What is this course contractually required to do? | `docs/COURSE-SPEC.md` |
| What units exist, in what order? | `docs/CURRICULUM.md` |
| How do the 16 skills map to units? | `docs/SKILLS-MAP.md` |
| Why this course and not the two that exist? | `docs/POSITIONING.md` |
| Do we cover CS146S? | `docs/CS146S-COVERAGE.md` |
| What happens when the plugin changes? | `docs/PLUGIN-CONTRACT.md` |
| Is this actually a software engineering course? | `docs/ARCHITECTURE-AUDIT.md` |
| What should we borrow from other skills repos? | `docs/ECOSYSTEM-MAP.md` |
| What is the running thread? | `docs/CURRICULUM.md` § The running thread |
| What shape must a unit take? | `docs/CURRICULUM.md` § Unit shape |
| How is a claim measured? | `tools/ablation.py` |
| What checks a spec? | `tools/spec_lint.py` |

`docs/COURSE-SPEC.md` outranks everything. If a unit and the spec disagree, the spec is
right and the unit is a bug.

## Rules

**Every claim needs a source or a number.** A sentence asserting that some technique
works cites a primary source or points at a results file. "Best practice" is not a
citation. Unsupported, cut it.

**Never invent a result.** `results/*.json` come from `tools/ablation.py` against real
runs. A hand-written plausible table destroys the only thing this course has. If numbers
aren't available yet, mark the section a placeholder and say so.

**Null and negative results ship.** A unit whose harness did nothing is a finding.
Do not quietly retune an experiment until it agrees with the prose.

**Eight required sections per unit** — see `docs/CURRICULUM.md` § Unit shape —
including *What makes this obsolete*. `tools/audit.sh` checks.

**Skills belong to the plugin, not here.** Course content teaches; workflow lives in
`spec-driven-engineering`. If a unit needs a capability the plugin lacks, add it to
`expected_gaps` in `skills.lock.json` and to the gap analysis in `docs/SKILLS-MAP.md`
rather than shipping a shadow skill here. The boundary rule is
`docs/PLUGIN-CONTRACT.md` § 5.

**Reference capabilities, not skill names.** Every unit README carries
`<!-- capabilities: a, b, c -->`. Prose may name the current skill for readability, but
`skills.lock.json` is the contract and the only place a binding is decided.

**Prose style.** Short sentences. No em-dash asides. No "not X, but Y". No stock
openers. Write the way a senior engineer explains something to a peer at a whiteboard.
Cut adverbs.

**Don't teach what ships in the box, or rebuild what the ecosystem maintains.**
`/batch`, `/loop`, `/review`, `/simplify`, `/debug` and Routines are built in; ponytail,
Vercel and Trail of Bits maintain the rest. Teach the built-in first, show where it
stops, then teach past it. `docs/ECOSYSTEM-MAP.md` §§ 2 and 7.

**No dependencies in `tools/`.** Standard library only.

## Commands

```bash
tools/audit.sh                                            # all sensors; exits 0 on main
python3 tools/spec_lint.py docs/COURSE-SPEC.md            # the spec lints itself
python3 tools/ablation.py run cfg.json --dry-run -o /tmp/x.json
python3 tools/ablation.py validate units/b1-*/results/authors-run.json
python3 tools/check_skills_map.py --plugin-dir ../spec-driven-engineering
```

## Definition of done for a unit

1. README has all eight sections.
2. `verify.sh` exists, runs, and its gate traces to a named Success Criterion.
3. `results/authors-run.json` exists, validates, is not a dry run.
4. *Our numbers* reports what actually happened, nulls included.
5. `tools/audit.sh` exits 0.

Failing any of these means it doesn't merge, however good the prose is.

## Known gaps

Kept current so an agent doesn't rediscover them or paper over them:

- `tools/audit.sh` exits 0. B0-B5, C1, C3, C4 real results, every hypothesis
  inconclusive-to-opposite - read the §6s. C3: 28 failures, one cause. B4:
  spec-withheld matched spec-provided via sibling-code precedent. B5:
  structured handoff hurt completion (67% vs 100%, `init.sh` = Bash needing
  approval headless). C4 reran it on 5 fresh tasks: dead-even null (93/93),
  likely an interruption-narrative confound, not the wording.
- Wrong-problem grading ran (B1, 2 AI graders, 100% agreement, zero found) -
  disclosed substitute for human graders, not a closed gap; see B1's `grading/`.
- Running thread (B0-C4 done): `~/Documents/ai-swe-course-scratch/fsft`.
- Fall 2026 claim downgraded to `overlaps` (11 gaps, COV008); Fall 2025 holds
  unweakened, secondary evidence for 9/10 weeks (COV006).
- Architecture-audit findings F1-F6 are remediated (see that file's status table).
- `skills.lock.json` is pinned to plugin 1.0.1 and unverified against anything newer.
- `spec_lint.py` is heuristic and will false-positive; its job is to force the question.

Agent picking up work here: these, in this order, are the backlog. Pick exactly
one. Do not attempt two.

## What this repo is not

Not an agent framework. Not a beginner harness course — that's
`walkinglabs/learn-harness-engineering`, and we link rather than compete. Not
vendor-neutral theatre: labs name a specific CLI and stack with a documented porting
contract.

<!-- ===== END AGENTS.md ===== -->


<!-- ===== BEGIN docs/COURSE-SPEC.md ===== -->

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

<!-- ===== END docs/COURSE-SPEC.md ===== -->


<!-- ===== BEGIN docs/CURRICULUM.md ===== -->

# Curriculum

Twenty-two units in four tracks, a capstone, and two annexes.

**Two readers, matching the plugin's personas.** The 🔧 **developer** writing code today
enters at B3. The 🧭 **engineer** who owns a feature end to end enters at B0 and walks the
spine. Architecture is not a third track — it arrives inside the engineer's arc (B2, B4,
C1–C3), which is where it actually gets used. Leadership (D3–D4) and ML systems (Track E)
are annexes with their own front doors.

Each unit is **one question, one lab, one gate**. Tracks B and C are the course; A is
the prerequisite understanding, D is what happens after merge.

## The running thread

Every lab runs against **one real feature in one real repo**, picked at the start of
Track B and shipped across Tracks B and C. B0 onboards the agent to the repo. B1 specs
the feature. B2 plans it. B3 builds it. B4 reviews it. B5 lands it. C1 audits the harness
that just carried it. C2 fixes the docs it exposed as stale. C3 writes the linter for the
rule it violated. C4 measures whether any of that helped. C6 turns the repeated part into
a skill.

This is deliberate. The [architecture audit](ARCHITECTURE-AUDIT.md) found that twelve of
twenty-one units produced a document rather than software, which would let someone finish
most of the course without their product improving. Same units, same labs — but each
document is now an artifact of shipping something, and you finish holding working code
plus the harness that produced it.

If you have no candidate repo, use `tiangolo/full-stack-fastapi-template`. It has a
published external baseline (see [`ECOSYSTEM-MAP.md`](ECOSYSTEM-MAP.md) § 4) your numbers
can sit next to.

**Short on time?** The critical path is **A2, A3, B0, B1, B2, B4, C1, C2, C4**. That's the
spine plus the harness that holds it up, and it's the part that changes how you work
on Monday.

**Coverage against Stanford CS146S** is audited week by week in
[`CS146S-COVERAGE.md`](CS146S-COVERAGE.md), including what we deliberately skip and why.
Two units — A5 and C6 — exist because that audit found real gaps.

Legend: 🔧 uses a `spec-driven-engineering` skill · 🔬 lab with a pass/fail gate ·
📊 requires an ablation result · 🏛️ leadership track

---

## Track A — Foundations: how the machine actually fails

You cannot design a harness for a failure mode you don't understand. Five units, then
you never think about model internals again.

### A1 · What actually happens when you hit send

**Question.** Why does the same model solve an olympiad problem and then tell you 9.9
is less than 9.1?

Pre-training as lossy compression of the internet — the model learns what commonly
follows what, not what is true. Supervised fine-tuning as personality. RL as the thing
that teaches reasoning, and the practical consequence: **the model needs tokens to
think.** Asking for a complex answer in one shot without reasoning space is asking
someone to do calculus without scratch paper.

Then the Swiss cheese model of capability: unpredictable gaps, arbitrary shape. This
is the entire justification for the rest of the course. If capability were uniform you
would not need a harness; you would need a better prompt.

- **Lab.** Find three capability holes in your own domain. Document what triggered
  each. This becomes the seed of your team's guides.
- **Gate.** Three reproducible failures, each reproduced twice.

### A2 · Anatomy of an agent: model + harness 🔬

**Question.** Which of your problems are model problems and which are harness problems?

The equation the field converged on: **agent = model + harness**. Everything that
isn't weights — system prompt, tool definitions, context delivery, permissions,
sandbox, execution loop, memory, verification — is harness, and it is yours to
engineer.

Unroll the loop by hand: gather context → select tool → execute → observe → repeat →
terminate. Then locate every configuration point you actually control in your CLI of
choice. Most engineers discover they've been tuning the one knob (the prompt) with
twelve others untouched.

The evidence this matters: LangChain moved deepagents-cli from 52.8 to 66.5 on
Terminal-Bench 2.0 — rank 30 to top 5 — with the model held fixed at gpt-5.2-codex,
changing only the harness. Not a marginal effect.

**Then inventory what already ships.** Claude Code now includes `/batch` (5–30 parallel
subagents in isolated worktrees, one PR each), `/loop` (rerun a prompt on an interval),
`/review`, `/simplify`, `/debug`, and Routines (promote a workflow to run on a schedule,
via API, or on a GitHub event). Much of what people hand-build in 2026 is already in the
box, and the first harness question is always *what do I not have to build.*

- **Lab.** Map your agent's loop. For each stage, name what you can configure and what
  you can't. Run each built-in once against a real task. Classify last week's three worst
  failures as model or harness.
- **Gate.** Every stage annotated; three failures classified with a stated reason.

### A3 · Context is a budget, not a container 🔬📊

**Question.** You gave it more context and it got worse. Why?

Four named failure modes, and they behave differently so they need different fixes:

1. **Poisoning** — an early error enters the history, the agent fixates, never
   self-corrects.
2. **Distraction** — past roughly 100k tokens it stops reasoning fresh and starts
   repeating patterns from its own history.
3. **Confusion** — too many tools in the list degrades tool selection. Fewer, more
   expressive tools beat a long menu of narrow ones.
4. **Clash** — two contradictory facts in context, and accuracy falls off a cliff with
   no recovery.

Then the discipline: context as a working-memory budget. Compaction and what it loses.
Progressive disclosure — a small stable entry point that teaches the agent where to
look next, rather than an encyclopedia loaded up front.

**Two worked examples from the ecosystem.** `context-mode` (~16.3k stars) attacks
distraction by filtering verbose shell output before it reaches context and keeping a
session log that survives a reset — most of what an agent re-reads after thirty minutes
is `git status` and `npm test` noise, not project context. And a March 2026 result found
that constraining models to brief responses **improved accuracy by 26 points** on some
benchmarks: brevity is an accuracy intervention, not only a cost one.

- **Lab.** Reproduce all four failure modes deliberately. Then measure: same task, MCP
  server count halved.
- **Gate.** Four reproductions with transcripts. Ablation on tool-count reduction.
- **Obsolete when.** Larger effective context and better in-context retrieval will
  soften distraction. Clash and poisoning are structural and will not go away.

### A4 · Delegation economics

**Question.** Which tasks should you hand off, and which are a trap?

Sync agents respond in under a minute and keep you in flow. Async agents run 10
minutes to hours and let you multi-thread yourself. Between them is the **semi-async
dead zone**: 30 seconds to 5 minutes, too long to wait, too short to context-switch.
It destroys flow and buys nothing. The fix is to push the task out of the zone in
either direction — tighten the instructions until it's fast, or scope it up until it's
a real delegation.

Then defensive prompting: say *how*, not just *what*; anticipate non-obvious
dependencies up front; build explicit human checkpoints into multi-hour work; prefer
strongly typed languages because type errors are a free, high-quality feedback signal
for the agent.

- **Lab.** Time-classify twenty tasks from your backlog. Move every dead-zone task out
  of the zone and say which direction you moved it.

### A5 · Tools and MCP: designing the agent's hands 🔬📊

**Question.** You gave it the tool it asked for and it still called the wrong one.

Tool interfaces for agents have different constraints than interfaces for humans, and
the differences are counterintuitive:

- **Consolidate.** Fewer, more expressive tools beat a long menu of narrow ones. Every
  tool in the list costs context and degrades selection — this is context confusion from
  A3, arriving through a door you built yourself.
- **Make outputs semantically meaningful.** Return `user: Jane Doe`, not
  `user: A1B2C3D4`. An opaque identifier forces another round trip to become useful.
- **Allow verbosity control.** Let the agent manage its own context budget rather than
  deciding for it.
- **Mirror the team environment exactly.** Same language versions, same packages. A tool
  that works differently under the agent than under you produces failures you can't
  reproduce.

Then MCP, and the harder question of when *not* to reach for it. An MCP server is a
standing context cost paid on every turn whether the agent uses it or not. Sometimes the
better answer is code execution against a well-designed API — let the agent write and
run a script rather than adding twelve tools it might need. The trade-off is real in
both directions and this unit makes you measure it rather than pick a side.

- **Lab.** Take your worst-behaving tool. Rewrite its interface and its output format.
  Then ablate: same tasks, tool count halved.
- **Gate.** Measured difference in wrong-tool-selection rate.
- **Obsolete when.** Better tool-selection and retrieval over large tool sets will
  soften the consolidation pressure. Output legibility will not stop mattering.

---

## Track B — The Spine: spec-driven engineering

This is the course's backbone, and it maps one-to-one onto
[`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering).
You install the plugin in B1 and use it for the rest of the course. See
[`docs/SKILLS-MAP.md`](SKILLS-MAP.md).

```
spec-from-idea → plan-from-spec → implement → review-code → finish-branch
```

### B0 · Onboarding an agent to a codebase you didn't write 🔬📊

**Question.** The repo is 400k lines. The context window is not.

Every other unit assumes a repo you can shape. Most real work is the opposite: years of
unwritten conventions, a `README` that lies, and three people who know why the retry
logic is like that. The published harness literature is almost entirely greenfield, and
this is the gap the [architecture audit](ARCHITECTURE-AUDIT.md) called F3.

Covered: repo comprehension at a scale that doesn't fit in context — entry points,
call-graph sampling, and reading the git history as the only honest record of intent.
Building the **map before the harness**, because a coverage grid on a codebase you don't
understand measures the wrong thing. Separating conventions that are load-bearing from
conventions that are habit, which is the judgment `engineering-standards` can't make for
you. And the honest budget: on a legacy repo the backfill is steep, and pretending
otherwise is how harness projects get cancelled in week three.

This is also where you pick the repo and the feature that carry the running thread.

- **Lab.** Produce a repo map an agent can navigate, and a one-page "what's load-bearing
  here" note. Then ablate: same task, with and without the map.
- **Gate.** A fresh session, given only the map, correctly locates where a named
  behaviour is implemented in three out of four attempts.
- **Obsolete when.** Cheap effective context over a whole repo would retire the map.
  Watch this one — it may go before anything else in Track B.

### B1 · Idea → spec 🔧🔬📊

**Question.** Which agent failures can no sensor catch?

**Reference unit — written to full depth at [`units/b1-idea-to-spec/`](../units/b1-idea-to-spec/).**

The prompt is the new source code, and most teams throw it away. You craft a detailed
specification, generate code from it, commit the code, and discard the spec. That is
shredding the source and version-controlling the binary. The generated code is a lossy
projection of the intent; the nuance, the business logic and the reason live in the
spec and nowhere else.

Then the harder point. Computational sensors reliably catch structural problems.
Inferential sensors partially catch semantic ones. **Neither reliably catches
misdiagnosis, unnecessary features, or misunderstood instructions.** The failure that
burns teams is not malformed code — it's well-formed code solving the wrong problem,
and the only instrument that detects it is a written statement of the right problem.

Skills: `spec-from-idea`, `domain-modeling`, `grill-me`, `triage-issues`.

- **Lab.** Turn a real backlog item into a spec with measurable Success Criteria and
  Evals. Lint it. Pressure-test it. Measure whether it changed the outcome.
- **Gate.** `tools/spec_lint.py` exits 0. Ablation with and without the spec.

### B2 · Spec → plan 🔧🔬

**Question.** How does a plan step prove it did what the spec asked?

Every step in the plan carries a verification traced back to a specific eval in the
spec. A plan step with no traceable verification is a step nobody can check, which
means the agent will decide for itself when it's done — and it will decide generously.

This is also where architecture enters, before code exists: module depth, interface
width, layer boundaries. Deciding this after the agent has written 4,000 lines is
deciding it too late.

**Compare with `obra/superpowers`** (~40.9k stars), which occupies the same spine and
plans in *tasks* — 2–5 minute units with exact file paths and verification steps — where
this spine plans in *criteria that steps trace back to*. Both are defensible. The
traceable version is what makes B2's orphan-step gate and `spec_lint.py` possible at all;
the task version is easier to start. Know which you're choosing and why.

Skills: `plan-from-spec`, `codebase-architecture`.

- **Gate.** Every plan step traces to an eval ID. Orphan steps fail the lab.

### B3 · Plan → code 🔧🔬

**Question.** What does test-first mean when the agent writes both the test and the code?

Test-first at every seam, review before every commit. The uncomfortable question this
unit takes seriously: an AI-generated test suite that passes is weak evidence, because
the same misunderstanding that produced the code produced the test. Mutation testing
as the answer, plus approved-fixtures patterns where they fit.

Also `engineering-standards` as the thing code gets checked against, including its
YAGNI check — no unrequested abstractions, stdlib first, simplest correct solution —
applied at write time rather than left to review.

**The enforcement lesson.** `superpowers`' TDD skill *deletes code written before a
failing test exists*. Most TDD skills, including ours, ask nicely. That is the
guide/sensor distinction from C1 arriving early: a rule an agent can route around is a
guide, and a rule that deletes your work is a sensor. Ask of every standard you hold —
which one is this?

Also here: **debugging when the agent is confidently wrong**, which is the characteristic
failure of agentic debugging. The agent will produce a plausible root cause on demand and
you get no signal that it guessed. `/debug` and `debug-systematically` are the tools; the
discipline is refusing to accept a cause that hasn't been made to predict something.

Skills: `implement`, `test-driven-development`, `engineering-standards`,
`debug-systematically`.

- **Gate.** Mutation score on the agent-written suite above a stated bar.

### B4 · Code → review 🔧🔬📊

**Question.** What is code review actually for, now that finding bugs is automatable?

The hierarchy, and it's inverted from what most people assume. Bug-finding is near the
top of the pyramid, not the base. The base is **mental alignment** — keeping the team's
collective understanding of the system current. That is the part agents cannot do for
you, and the part that quietly rots when review becomes agent-to-agent.

The review quadrant: gold zone (AI owns it — simple bugs, performance, security, style
consistency), human-only zone (tribal knowledge, institutional memory, nuanced business
logic), and the annoyance zone (abstract best-practice noise that erodes trust and
should be suppressed).

Then two-axis review: does it satisfy the spec (primary), does it hold up against
standards and architecture (secondary). And the governance rule that matters — when no
spec exists, the reviewer says "spec axis skipped, no spec found" rather than silently
treating absence as satisfaction.

Skills: `review-code`, `engineering-standards`, `codebase-architecture`.

- **Gate.** Ablation: review with spec axis vs without, on the same set of PRs.

### B5 · Ship, and the session that outlives the context window 🔧🔬

**Question.** The context window ended mid-feature. Now what?

Every long task is a relay race where each runner arrives with amnesia. The published
answer: an **initializer** pass that sets up `init.sh`, a progress log and a
machine-readable feature list, then coding sessions that each pick exactly one feature,
verify end to end, and leave a clean state.

Two failure modes to design against, both well documented. The agent that tries to
one-shot the whole thing and dies mid-implementation with no notes. And the agent that
arrives later, sees that progress was made, and declares the job done.

Note the JSON detail — feature lists in JSON rather than Markdown, because models are
measurably less willing to quietly rewrite JSON. Small choice, large effect.

Skills: `finish-branch`, `handoff`, `resolve-merge-conflicts`, `dev-workflow`.

- **Gate.** Kill a session mid-feature. A fresh session resumes and finishes without
  human explanation.

### B6 · Generated interfaces and the validation problem 🔬📊

**Question.** The agent generated a working UI. How do you know it's right?

This unit exists because of a constraint, and the constraint improved it. It was
originally cut as a domain vertical; the superset requirement put it back, and on
second look it's the sharpest available test of the course's whole thesis — because
interfaces are where the sensors run out first.

Start with the historical frame: each generation of web architecture traded a
complexity tax for a capability, and agents change the arithmetic. Then the generation
pipeline as it actually works — intent understanding, context assembly, generation,
**automated validation**, and stream manipulation that corrects known bad patterns
mid-output. That fourth stage is the interesting one and the fifth is a guide in
disguise: intervening in the output stream is feedforward correction applied at
generation time rather than review time.

Then the hard part. `pytest` cannot tell you the button is in the wrong place, the
contrast fails, the focus order is nonsense, or the empty state is missing. Options,
in ascending cost: structural assertions (roles, labels, tab order), accessibility
audits as computational sensors, visual regression against approved snapshots, and
browser-driving so the agent can exercise its own output. Each catches a different
class and none catches all of them.

The honest conclusion is that this is the strongest case in the course for a
**human-in-the-loop sensor**, and C1's timing rule tells you where to put it: cheap
structural checks pre-commit, expensive human judgment post-integration, and never the
other way round.

- **Lab.** Have an agent generate one non-trivial interface. Build a three-tier
  validation ladder for it. Then seed three defects — one structural, one visual, one
  semantic — and measure which tier catches which.
- **Gate.** Structural tier under 10s; the semantic defect reaches a human rather than
  being silently passed.
- **Obsolete when.** Multimodal models that reliably evaluate their own rendered output
  collapse tiers two and three. This is the unit most likely to date fastest, and its
  presence is a bet that the validation problem outlives the generation problem.

---

## Track C — The Harness: making the spine hold

Track B gives you a workflow. Track C is why it survives contact with a real repo and
a real team. This is the "go beyond."

Six units. C1–C3 build the harness, C4 measures it, C5 scales it, C6 lets you extend
the tooling itself.

### C1 · Guides and sensors 🔬

**Question.** Are you steering the agent, or just grading it?

The vocabulary this course uses throughout, from Böckeler:

- **Guides** (feedforward) steer before the agent acts. **Sensors** (feedback) observe
  after so it can self-correct. Feedback-only gives you an agent that repeats mistakes.
  Feedforward-only gives you rules that never learn whether they worked.
- **Computational** controls are deterministic, milliseconds, reliable. **Inferential**
  controls are semantic, slow, expensive, non-deterministic.
- Three regulation categories: **maintainability** (easy, decades of tooling),
  **architecture fitness** (fitness functions), **behaviour** (the elephant — see B1).
- **Harnessability**: typed code affords a type checker, clean boundaries afford
  architecture rules, a 4,000-line god module affords nothing. The harness is most
  needed exactly where it's hardest to build.
- **Timing**: keep quality left. Fast cheap sensors before the commit, expensive ones
  post-integration, drift sensors running continuously outside the change lifecycle.

- **Lab.** Build the guides × sensors × {computational, inferential} coverage map for
  your repo, and defend your top three gaps.

### C2 · The repository is the only thing that exists 🔧🔬

**Question.** Why did your beautifully written 800-line `CLAUDE.md` make things worse?

Because a monolithic instruction file fails four ways: it crowds out the task, it makes
everything "important" so nothing is, it rots instantly, and it can't be mechanically
checked. The working pattern is `AGENTS.md` as a **table of contents** — roughly 100
lines — pointing into a structured `docs/` tree that is the system of record.

And the harder principle: **what the agent can't see doesn't exist.** The Slack thread
that aligned the team on an architectural pattern is invisible. So is the Google Doc,
and so is the thing in your staff engineer's head. Repository-local versioned artifacts
are all it has.

Then enforcement: linters and CI jobs that check the knowledge base is current,
cross-linked and structured, plus a recurring doc-gardening agent that finds stale docs
and opens fix-up PRs.

Skills: `writing-for-agents` (governs how your team authors all of this).

- **Gate.** Entry point under 120 lines; link checker green; gardener finds a real
  stale doc.

### C3 · Enforcing architecture and taste 🔬📊

**Question.** How do you make a rule that the agent can't route around?

Telling an agent "follow our coding standards" is probabilistic compliance. Wiring a
linter that blocks the PR is a deterministic constraint. Harness engineering is largely
the discipline of converting the first into the second.

**Enforce invariants, not implementations.** Require parsing at the boundary; don't
mandate the library. Fix the layer graph and the permitted dependency edges; leave the
code inside a layer free.

The highest-leverage trick in the whole course, and it costs about forty lines: **write
your custom lint error messages for the agent, not for you.** Inject remediation
instructions into the failure output — what's wrong, what not to touch, ranked likely
causes, the reproduce command. A sensor whose output is optimized for LLM consumption
is worth several sensors whose output is a verdict.

This is also the unit where rigid architecture stops being premature. Layered domains
with mechanically validated dependency directions is the kind of thing you'd normally
postpone until you have hundreds of engineers. With agents it's an early prerequisite,
because the constraint is what buys speed without decay.

**Order your rules by impact, not alphabetically.** Vercel's `react-best-practices`
ships 57 rules deliberately ordered — request waterfalls first, then bundle size, then
server performance, and `useMemo` far down. Most rule sets have no ordering, so an agent
optimises whatever it reads first. Their `web-design-guidelines` adds a second trick
worth stealing: it **fetches the current version of the guidelines before every run**, so
the rule set can't silently rot. That's a freshness sensor on a guide.

- **Lab.** Write one custom linter with a remediation-carrying message. Ablate against
  the same linter emitting a bare verdict.
- **Gate.** Measured difference in turns-to-fix between the two message styles.

### C4 · Making the spec computational 🔧🔬📊

**Question.** Your specs are the behaviour harness. What checks the specs?

This unit is the synthesis of Tracks B and C, and it's the part of this course that
doesn't exist elsewhere. If the spec is the only instrument that catches
wrong-problem failures (B1), then spec quality is a load-bearing property of your
system — and an unchecked load-bearing property is a bug waiting.

So: turn spec quality into a sensor. `tools/spec_lint.py` checks that every Success
Criterion is measurable, carries a named eval, and doesn't hide behind unfalsifiable
adjectives. It fails with agent-directed remediation, per C3. Wire it as a pre-commit
hook and the behaviour harness stops being a discipline you have to remember.

Then evals proper: what to measure when an agent has many trajectories to the same
outcome, trace analysis as the improvement loop, and ablation methodology —
`tools/ablation.py`, bootstrap intervals, and the discipline of publishing null results.

- **Gate.** `spec_lint` running in CI. One measured harness improvement driven by trace
  analysis rather than intuition.

### C5 · Loops, fleets, and the software factory 🔬📊

**Question.** `/batch` already runs thirty agents in worktrees. What's left to build?

Start with what ships: `/batch` decomposes the work, spawns one subagent per unit in an
isolated worktree, and opens a PR each. Fleet orchestration is no longer the hard part,
and a course that teaches you to hand-roll it in 2026 is teaching you to rebuild the box.

What `/batch` does not give you is the rest of this unit.

The loop family, from the minimal Ralph pattern (`while :; do cat PROMPT.md | agent;
done`) up through planner / generator / evaluator splits. Worktree isolation so
parallel agents don't collide. Loop detection — a per-file edit counter that nudges the
agent after N edits to the same file, which is explicitly a heuristic engineered around
a current model failure.

**Merge philosophy changes at throughput.** Minimal blocking gates, short-lived PRs,
flakes handled with a re-run rather than an indefinite block. When agent throughput far
exceeds human attention, corrections are cheap and waiting is expensive. This is
irresponsible at low throughput and correct at high. Know which one you are, and say
so explicitly rather than drifting.

Then **entropy and garbage collection**, the part everyone learns the hard way. Agents
replicate the patterns already in the repo, including the bad ones. One team spent
every Friday — 20% of the week — cleaning up slop before they encoded "golden
principles" and set recurring cleanup agents to scan for deviations and open small
auto-mergeable refactor PRs. Technical debt as a high-interest loan: pay it
continuously in small increments.

- **Lab.** Four agents, isolated worktrees, one backlog. Measure throughput, collision
  rate, and slop accumulation with and without a gardener.

> **A unit that was planned and cut.** The architecture audit recommended a C7 on
> large-scale change (migrations, sweeping refactors). Then `/batch` shipped, built
> explicitly for migrations and cross-file refactors, and the unit's content collapsed
> into "use `/batch`, then read the rest of C5." Cut rather than padded. Recorded here
> because a course that only ever grows is a course nobody finishes.

### C6 · Authoring skills that survive 🔧🔬📊

**Question.** You've been installing skills for five tracks. How do you write one?

A skill is a guide in the C1 sense — feedforward, inferential, loaded on demand. Which
means everything C1 says about guides applies: it can be wrong, it competes for context,
and without a sensor it never learns whether it worked.

**Two kinds of skill, and you should know which you're writing.** *Capability Uplift*
gives the agent an ability it lacks — PDF generation, browser testing, web scraping.
*Encoded Preference* encodes your way of doing something it can already do — review
checklists, house style, architectural conventions. The distinction has a sharp
consequence: **Capability Uplift skills die when the platform absorbs the capability**,
and several already have. Encoded Preference skills survive model improvement.
`spec-driven-engineering` is almost entirely Encoded Preference, which is why it's a
reasonable thing to build a course on.

**Five properties separate a working skill from a dead one**, and they're all cheap:
a description that reads like a routing rule rather than a topic label; deterministic
work done by bundled code rather than by asking the model to be careful; a lean
`SKILL.md` with detail in companion files that load on demand; one skill, one job; and
three worked examples in place of twenty bullet-pointed constraints. Start from
`skill-creator` rather than a blank file.

**Description design is the whole ballgame for triggering.** A skill that doesn't fire
is worth nothing regardless of how good its body is, and a skill that fires on
everything is worse than nothing because it burns context on every unrelated task.
Descriptions are written for the classifier, not the reader.

**Progressive disclosure inside the skill**, for the same reason `AGENTS.md` is a map
(C2). A skill body that dumps everything is a monolithic instruction file with a smaller
scope and identical failure modes.

**Skills need evals.** This is the part almost nobody does. Bounded tasks, deterministic
verifiers, and — critically — a **no-skill baseline**, because a skill that helps less
than nothing is indistinguishable from a skill that helps, if you never run the control.
This is `ablation.py` pointed at your own guides, and it's the same discipline the whole
course is built on.

**Then promotion and deprecation.** A skill isn't stable because you wrote it carefully;
it's stable because it was dry-run against a real task and survived. Renames keep the
old name working for a cycle as a pointer. Versioning matters more than it looks,
because your readers are slower than your CI.

There's a second reason this unit exists, stated plainly in
[`docs/PLUGIN-CONTRACT.md`](PLUGIN-CONTRACT.md) § 7: **you are the plugin's future
contributors.** The five capabilities in the gap analysis are unwritten because nobody
has written them, and after this unit you can.

- **Lab.** Write one skill for a workflow you repeat. Eval it against a no-skill
  baseline. Then optimise its description until it triggers reliably without
  over-triggering, and measure both.
- **Gate.** Positive delta against the no-skill baseline surviving a confidence
  interval, plus a trigger-precision number on a held-out prompt set. A skill that
  can't beat its own absence does not ship — that's the promotion rule.
- **Obsolete when.** Skill formats will churn; the eval discipline won't. When agents
  reliably author and self-evaluate their own skills, this becomes a review unit rather
  than an authoring one.

---

## Track D — Production, and the leadership annex

D1–D2 are part of the main arc: they're software engineering, just after merge. **D3–D4
are an annex** with a different reader — the person deciding whether a team adopts this.
They read standalone and are not prerequisites for the capstone.

### D1 · Security and safe autonomy 🔬

**Question.** What can an agent do to you that you haven't imagined yet?

Working attack classes, not theory: SSRF through a web-content tool reaching internal
network resources; credential exfiltration via encoding to bypass filters; and the YOLO
mode class where the agent modifies its own configuration to disable its safeguards.

Then the honest numbers on AI security scanning. Semgrep tested Claude Code and Codex
against 11 large Python web applications and measured **82–86% false positive rates**,
with identical scans returning 3, 6 and 11 findings on successive runs. A single AI
scan is a confident false sense of coverage. Use it as a sensor with known precision,
not as a gate.

Sandboxing, permission design, approval policies, secret handling — and the position
that a sandbox is a boundary, not a solution.

**Variant analysis**, from Trail of Bits' skills: you found one instance, now find its
siblings across the codebase. It's the cleanest generalisation of the harness idea —
Hashimoto's "never make that mistake again" applied to a *class* of defect rather than
one instance — and it's the pattern most teams skip after a security finding.

- **Lab.** Red-team your own harness. Plant an injection where your agent will read it.

### D2 · Agents after deployment 🔬

**Question.** What changes when the agent can see production?

SRE's conceptual inversion — treat operations as a software problem, hold the 50% toil
rule, spend the error budget deliberately. Then the distinction that matters:
**AI-assisted** means the engineer drives and the model helps write a log query faster.
**AI-native** means the engineer says "resolve this checkout failure" and specialist
agents run the investigation in parallel.

Making runtime legible to agents is the concrete work: an ephemeral observability stack
per worktree, logs and metrics queryable by the agent, the app bootable per worktree
and drivable through a browser protocol so the agent can reproduce a bug, record it,
fix it, and record the fix. Once that exists, prompts like "ensure service startup
completes under 800ms" become tractable rather than aspirational.

- **Lab.** Make one signal agent-legible. Then ask a question that was impossible before.

### D3 · Measuring the thing 🏛️📊

**Question.** How do you know any of this worked?

Baseline before you change anything, from systems you already have: cost per merged PR,
time-to-merge for agent-assisted work, **rework rate** (the honest one), review latency
relative to PR size, compute spend per engineer. Velocity metrics improve the moment
you adopt agents; rework tells you whether the improvement was real.

Then the measurement traps. Infrastructure noise alone can move agentic coding
benchmark scores by more than many leaderboard gaps, so an uncontrolled comparison is
worthless. If a sensor never fires, is that quality or inadequate detection? We have no
equivalent of code coverage for harness coverage yet, and pretending otherwise is how
teams end up confident and wrong.

### D4 · Rolling this out on a team 🏛️

**Question.** You're convinced. What do you tell twelve engineers on Monday?

**Harness templates.** Most organisations have three or four service topologies covering
80% of what they build. Those become bundles of guides and sensors. The argument is
Ashby's Law: a regulator needs at least as much variety as the system it governs and can
only regulate what it has a model of. An LLM can produce almost anything; committing to
a topology is a deliberate variety-reduction move that makes a comprehensive harness
achievable at all. Teams may start choosing stacks partly by which harnesses exist.

**What not to automate.** The harness externalises what an experienced engineer brings
implicitly — absorbed conventions, aesthetic disgust at a 300-line function, knowing
which convention is load-bearing and which is habit, memory of which debt is tolerated
for business reasons. It only goes so far. A good harness doesn't eliminate human
input; it directs it to where it matters most. Say where that is, out loud.

**The second codebase problem.** A harness is real, ongoing engineering work, and on a
legacy repo the backfill is steep. Budget it like infrastructure.

**The stop-loss.** State in advance what result would make you roll this back.

- **Lab.** Write the one-page plan against [`templates/rollout-plan.md`](../templates/rollout-plan.md).
- **Gate.** Peer review. No stated stop-loss is an automatic fail.

---

## Capstone

Ship a real change to a real open-source repository through the full spine, inside a
harness you built, with an ablation that shows what the harness was worth.

Deliverables: the merged (or at least opened) PR; the spec, plan and review artifacts;
the harness you added; `results/capstone.json`; and a short write-up including what
didn't work.

The bar is not "I built a lot of harness." It is "here is the measured difference,
including where there wasn't one."

---

## Track E — Specialization: ML systems

Optional, and only after Tracks A–C. Thirteen modules on what breaks when verification
is slow, expensive, statistical and only knowable in production.

Everything in Track C assumes tests are boolean, fast and deterministic. In ML systems
none of that holds, and the published literature says so explicitly — Anthropic names
generalisation beyond web development as future work. Track E is that generalisation.

See [`tracks/ml-systems/`](../tracks/ml-systems/), which has its own spec, curriculum
and reference module.

---

## Unit shape

Every unit README carries these sections, enforced by `tools/audit.sh`:

1. **The question** — one sentence.
2. **The failure** — a real, reproducible agent failure this unit addresses.
3. **The idea** — the concept, with primary sources.
4. **The lab** — runnable steps against a real repo.
5. **The gate** — `verify.sh`, pass/fail, traced to a Success Criterion.
6. **Our numbers** — the authors' ablation, including null and negative results.
7. **What makes this obsolete** — the model or tooling change that retires it.
8. **Sources** — primary only.

<!-- ===== END docs/CURRICULUM.md ===== -->


<!-- ===== BEGIN docs/SKILLS-MAP.md ===== -->

# Skills map

This course does not teach a workflow and then leave you to build it. The workflow is
an installable plugin — [`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering),
16 skills — and you install it in B1 and use it for everything after.

```bash
claude plugin marketplace add girijesh-ai/spec-driven-engineering
claude plugin install spec-driven-engineering@spec-driven-engineering-dev
```

That is the structural difference between this course and every other course in the
space. CS146S teaches you *about* agents. `learn-harness-engineering` teaches you to
build a harness from templates. Here, the curriculum and the tooling are the same
artifact, which means a unit that teaches something the plugin can't do is a bug in one
of them.

> **The plugin is at v1 and will grow.** This file is the human-readable view; the
> machine-readable binding lives in [`skills.lock.json`](../skills.lock.json), and
> [`tools/check_skills_map.py`](../tools/check_skills_map.py) keeps the two honest.
> Units declare capabilities rather than skill names, so a rename costs one edit here
> instead of twenty in prose. The rules are in
> [`PLUGIN-CONTRACT.md`](PLUGIN-CONTRACT.md).

---

## The spine, unit by unit

```
spec-from-idea → plan-from-spec → implement → review-code → finish-branch
       B1              B2            B3          B4             B5
```

| Unit | Primary skill | Supporting skills | What the unit teaches that the skill assumes |
|---|---|---|---|
| **B0** Brownfield onboarding | — *(gap: `repo-comprehension`)* | `codebase-architecture` | Building the map before the harness, on a repo that doesn't fit in context |
| **B1** Idea → spec | `spec-from-idea` | `domain-modeling`, `grill-me`, `triage-issues` | *Why* measurable Success Criteria are the only sensor for wrong-problem failures |
| **B2** Spec → plan | `plan-from-spec` | `codebase-architecture` | Why every step needs a verification traced to an eval, and what an orphan step costs |
| **B3** Plan → code | `implement` | `test-driven-development`, `engineering-standards`, `debug-systematically` | Why an agent-written passing test suite is weak evidence, and what to do about it |
| **B4** Code → review | `review-code` | `engineering-standards`, `codebase-architecture` | The review hierarchy — mental alignment sits below bug-finding, and agents can't do it |
| **B5** Ship & continuity | `finish-branch` | `handoff`, `resolve-merge-conflicts`, `dev-workflow` | The relay-race problem: every session arrives with amnesia |

## Supporting skills, and where they earn their place

| Skill | Introduced | Load-bearing in |
|---|---|---|
| `dev-workflow` | A2 | Every unit — it's the routing table when you don't know where you are |
| `engineering-standards` | B3 | B3, B4, C3 — the thing code is checked against, and the YAGNI backstop |
| `test-driven-development` | B3 | B3, and Track E's verification tiers |
| `domain-modeling` | B1 | B1 — the vocabulary specs get written in; ambiguity here poisons everything downstream |
| `codebase-architecture` | B2 | B2, B4, C3 — the same lens before code exists and after |
| `debug-systematically` | B3 | B3, D2 — and it's what stops the agent guess-and-check loop |
| `resolve-merge-conflicts` | B5 | B5, C5 — becomes critical the moment you run parallel worktrees |
| `triage-issues` | B1 | B1 — the intake valve; most bad specs start as unexamined tickets |
| `grill-me` | B1 | B1, D4 — pressure-testing a spec before committing, and a rollout plan before announcing |
| `handoff` | B5 | B5, C5 — the artifact that makes a session survivable by its successor |
| `writing-for-agents` | C2 | C2 — governs how your team authors skills, `AGENTS.md`, and the knowledge base |

## Where the course goes beyond the plugin

Tracks A, C and D cover ground the plugin doesn't, deliberately. The plugin is a
workflow; a harness is an environment.

| Course area | Plugin coverage | Why it's outside the plugin |
|---|---|---|
| Context failure modes (A3) | none | Diagnostic knowledge, not a workflow step |
| Guides & sensors vocabulary (C1) | implicit | The plugin *is* a set of guides; C1 teaches you to see that |
| Custom linters with agent-directed messages (C3) | none | Repo-specific; can't be shipped as a generic skill |
| Ablation methodology (C4) | none | Tooling — `tools/ablation.py` |
| Loops and fleets (C5) | none | Orchestration sits above the per-session workflow |
| Security and safe autonomy (D1) | none | Runtime and policy concern |
| Adoption and metrics (D3, D4) | none | Organisational, not technical |
| Tool and MCP design (A5) | none | Shapes the agent's hands, not its workflow |
| Skill authoring and evals (C6) | `writing-for-agents` covers style only | Teaching people to *write* skills is how the plugin grows |

---

## Gap analysis: what the course reveals the plugin is missing

Writing the curriculum surfaced five capabilities the units need and the plugin doesn't
have. This is the plugin's v2 roadmap, and it's a real benefit of building the course:
the course is an eval for the skill set.

Ordered by how often the curriculum reaches for something that isn't there.

**1. `audit-harness`** — produce the guides × sensors × {computational, inferential}
coverage map for a repo, flag the cells that are structurally impossible given the
codebase, and rank the gaps by cost to close. Needed by C1, and by Track E's M01.
Currently a manual exercise, which means most learners will do it badly or not at all.

**2. `write-sensor`** — author a custom check whose failure message carries remediation
into agent context: what's wrong, what must not be touched, ranked likely causes, the
reproduce command. This is the single highest-leverage technique in the course (C3) and
there's no skill for it. It pairs naturally with `engineering-standards`, which
currently states rules that nothing enforces.

**3. `lint-spec`** — wrap `tools/spec_lint.py` so `spec-from-idea` can check its own
output before handing off. Right now `spec-from-idea` produces Success Criteria and
nothing verifies they're measurable. That's a feedforward guide with no sensor, which
C1 identifies as exactly the failure pattern to avoid. The plugin should not be
committing it.

**4. `measure-change`** — run an ablation on a harness change and report whether the
effect survives a confidence interval. C4 depends on this. Making it a skill rather
than a CLI means the agent can propose a harness improvement *and* measure it, closing
the loop Hashimoto describes: agent makes a mistake → engineer the fix → verify the fix
actually removed the failure class.

**5. `garden-docs`** — scan the knowledge base for docs that no longer match code
behaviour and open targeted fix-up PRs. C2 teaches this as a recurring background task.
It's the entropy answer, and without it a `docs/`-as-system-of-record setup rots in
roughly a quarter.

Two of these — `lint-spec` and `write-sensor` — would close genuine holes in the
existing plugin regardless of whether the course ships. `lint-spec` in particular:
`review-code` already has a spec axis, but nothing checks that the spec it's reviewing
against was worth reviewing against.

All five are recorded in `skills.lock.json` under `expected_gaps`, which means they are
*declared* absences rather than silent ones. When one lands in the plugin,
`check_skills_map.py` reports it as info and the intake process in
[`PLUGIN-CONTRACT.md`](PLUGIN-CONTRACT.md) § 3 decides whether it's a lock-file edit, a
lab step, or a unit.

**This gap analysis is a claim with a shelf life.** C6 teaches readers to write skills
to the plugin's standard — description design, progressive disclosure, evals against a
no-skill baseline, promotion rules — precisely so this list gets shorter through
contribution rather than staying a wishlist. A course whose readers can close its own
gaps is a healthier arrangement than one that waits.

## A note on governance

The plugin's rule that `implement` and `review-code` say "no spec/plan found —
proceeding ad-hoc" and "spec axis skipped — no spec found" rather than silently
treating a missing spec as satisfied is worth teaching explicitly, in B4. It's a small
design decision and it's the difference between a harness that reports its own coverage
gaps and one that quietly claims coverage it doesn't have. C4's closing question —
if a sensor never fires, is that quality or inadequate detection? — is the general form
of the same idea.

<!-- ===== END docs/SKILLS-MAP.md ===== -->


<!-- ===== BEGIN docs/PLUGIN-CONTRACT.md ===== -->

# Plugin contract

The course depends on a plugin that is still moving.
[`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
is at v1 with 16 skills, all marked stable, and it will grow — the course's own
[gap analysis](SKILLS-MAP.md#gap-analysis) already names five capabilities it's
missing.

A course that hard-codes skill names into twenty unit READMEs rots on the first rename.
This file is how we avoid that, and the mechanism is the same one the course teaches:
don't rely on discipline where you can rely on a sensor.

---

## 1. Units reference capabilities, not skill names

A unit teaches a *capability* — "turn an idea into a spec with measurable success
criteria." Which skill provides that capability is a binding, and bindings change.

Every unit README carries a machine-readable declaration:

```html
<!-- capabilities: spec-authoring, domain-vocabulary, spec-pressure-test, issue-intake -->
```

Invisible when rendered, parseable by CI. Prose may name the current skill for
concreteness — `spec-from-idea` reads better than "the spec-authoring capability" — but
prose is not the contract. The comment is.

**The single binding site is [`skills.lock.json`](../skills.lock.json).** When the
plugin renames `spec-from-idea`, one line in one file changes and every unit stays
correct. When the plugin *splits* a skill in two, the capability may now map to two
skills, and only the lock file knows.

## 2. The lock file pins what we tested against

```json
{
  "plugin": "spec-driven-engineering",
  "tested_against": "1.0.1",
  "capabilities": {
    "spec-authoring": {"skills": ["spec-from-idea"], "units": ["b1"]}
  }
}
```

`tested_against` is a claim with a date behind it: the units were run against that
version. If a learner installs a newer plugin, the course still works — but we haven't
verified it, and the honest move is to say so rather than imply currency we don't have.

`tools/check_skills_map.py` compares the lock file against an actual plugin checkout and
reports four conditions, each with a different meaning:

| Condition | Severity | What it means |
|---|---|---|
| Capability declared in a unit, absent from the lock | error | Broken reference. The unit teaches something nothing provides. |
| Skill in the lock, absent from the plugin | error | Renamed, removed, or the pin is stale. Course is wrong. |
| Skill in the plugin, absent from the lock | **info** | The plugin grew. Intake needed — see §3. |
| `tested_against` differs from the plugin's version | warning | Re-verify, then bump the pin. |

The third row is the interesting one, and it's why the tool exists. A new skill is not
an error; it's a signal that the course has fallen behind its own tooling. Silence there
would be the failure mode C4 warns about — a sensor that never fires because it isn't
pointed at anything.

## 3. Intake: the plugin gains a skill

Run `check_skills_map.py`, see the unmapped skill, then answer three questions in a PR.

**1. Is this a new capability, or a better implementation of one we teach?**

A better implementation is a lock-file edit. Nothing else moves. If `spec-from-idea`
gains an interview mode, `spec-authoring` still points at it and B1's prose gets a
sentence.

A new capability needs a home, which is question 2.

**2. Does an existing unit gain a lab step, or does this need a unit?**

Default is a lab step. A new unit costs a reader thirty minutes and costs us the eight
required sections, a `verify.sh`, and an ablation. That price should be paid only when
the capability represents a distinct failure mode a reader wouldn't otherwise
understand.

Test: can you write *The failure* section — a real, reproducible agent failure this
capability addresses — without straining? If not, it's a lab step in an existing unit.

**3. Does it change what the course claims?**

Two of the five gap-list skills would. `lint-spec` moving into the plugin means C4 no
longer teaches building the sensor from scratch; it teaches wiring and calibrating one.
`write-sensor` moving in means C3's lab changes shape.

That's a feature, not churn. The course is an eval for the plugin: units are where you
find out that `engineering-standards` states rules nothing enforces, or that
`spec-from-idea` produces criteria nothing checks. When a unit's existence stops being
justified because the plugin absorbed the work, **delete the unit and say so in the
changelog**. A course that only grows is a course nobody finished.

## 4. Deprecation

The plugin's rule is that a renamed skill keeps its old name working for one release
cycle as a pointer. The course's rule is stricter, because our readers are slower than
our CI: **the lock file keeps the old binding for two cycles**, marked `deprecated`, and
`check_skills_map.py` warns on every one.

```json
"spec-authoring": {
  "skills": ["author-spec"],
  "deprecated_skills": ["spec-from-idea"],
  "deprecated_until": "2027-03-01",
  "units": ["b1"]
}
```

A learner three months behind should hit a warning, not a wall.

## 5. The boundary: what belongs in the plugin, what belongs here

This is the rule that stops the course from growing a shadow skill set, which is the
most likely way both artifacts get worse.

**Belongs in the plugin.** Anything an engineer invokes to do work. Repeatable,
portable across repos, useful without having read a word of the course.

**Belongs in the course.** Anything you need to *understand* rather than invoke:
diagnostic knowledge (the context failure modes), vocabulary (guides and sensors),
methodology (ablation design), judgment (which topology to harness first), and anything
irreducibly repo-specific — a custom linter for your layer graph can't be a generic
skill.

**Belongs in neither.** Tooling that is generic but not a workflow step: `spec_lint.py`
and `ablation.py` live in `tools/`. If `lint-spec` becomes a plugin skill, the tool
stays here and the skill wraps it — one implementation, two entry points.

When something is genuinely ambiguous, prefer the plugin. It has evals, promotion gates
and a version; the course has prose.

## 6. Growth scenarios, and what each costs

| The plugin... | Course cost | Who notices |
|---|---|---|
| adds a skill covering a taught capability | lock edit + a sentence | CI (info) |
| adds a skill covering a new capability | lock edit + lab step, or a new unit | CI (info) + a PR |
| renames a skill | lock edit, deprecation entry | CI (error until fixed) |
| splits a skill in two | lock edit, capability may fan out | CI (error) |
| removes a skill | capability needs a new provider or the unit changes | CI (error) |
| absorbs a course tool | unit rewrites from "build it" to "wire and calibrate it" | a human |
| ships a breaking version | re-run every unit's ablation, bump the pin | warning, then judgment |

The last row is the expensive one and it should be. A breaking plugin change invalidates
the numbers in every *Our numbers* section, and stale numbers are worse than no numbers
because they look like evidence.

## 7. Why C6 exists

The course teaches skill authoring (C6 · *Authoring skills that survive*) for a reason
that isn't obvious from the curriculum: **the readers are the plugin's future
contributors.**

A reader who finishes Track C and wants `write-sensor` should be able to build it to the
plugin's standard — the description that triggers reliably, the progressive-disclosure
body, the eval that proves it helps against a no-skill baseline, and the promotion rule
that says a skill isn't stable until it's been dry-run against a real task.

That closes a loop worth closing. The course is an eval for the plugin (§3), and C6
makes it a contribution funnel too. Both artifacts get better from the same readers.

## 8. Review cadence

- **Every plugin release:** run `check_skills_map.py`, triage anything it reports.
- **Every course release:** bump `tested_against` only after re-running the affected
  units, never as a courtesy.
- **Quarterly:** re-read §5. Boundary rules drift, and the symptom is a `tools/`
  directory quietly turning into a second skill set.

<!-- ===== END docs/PLUGIN-CONTRACT.md ===== -->


<!-- ===== BEGIN docs/POSITIONING.md ===== -->

# Positioning

Read this before writing a unit. It's the argument for the course's shape. If the
argument stops being true, the course changes.

The deep landscape research — every primary source, in detail — is in
[`tracks/ml-systems/docs/POSITIONING.md`](../tracks/ml-systems/docs/POSITIONING.md).
This file is the shorter argument for why *this* course, at this scope.

---

## 1. What the field settled on in 2026

Three phases, and the industry now names them:

| Phase | Question | Lever |
|---|---|---|
| Prompt engineering (2023–24) | How do I word this? | One call |
| Context engineering (2024–25) | What does the model see? | The window |
| **Harness engineering (2026)** | What system does the model operate inside? | The environment |

Mitchell Hashimoto put the term into circulation in February 2026 with a definition
small enough to hold in your head: when an agent makes a mistake, engineer a solution
so it never makes that mistake again. Six days later OpenAI published the field report
— roughly a million lines of code, ~1,500 merged PRs, five months, three engineers
growing to seven, **zero lines written by hand**. Humans steer, agents execute.

The evidence that this is a lever rather than a philosophy: LangChain moved
deepagents-cli from 52.8 to 66.5 on Terminal-Bench 2.0 — rank 30 to top 5 — by
changing only the harness, with the model held fixed at gpt-5.2-codex.

The vocabulary this course uses throughout comes from Böckeler at Thoughtworks:
**guides** (feedforward) and **sensors** (feedback), each either **computational**
(deterministic, fast, reliable) or **inferential** (semantic, slow, non-deterministic),
regulating three categories — maintainability, architecture fitness, and **behaviour**,
which she names as the open problem.

## 2. What already exists

**Stanford CS146S — *The Modern Software Developer*.** Ten weeks, Mihail Eric, public
materials and assignments, strong guest lineup. Fall 2026's syllabus (verified against
the live 10-week schedule, not just the site's overview) adds agent internals and
system-prompt design, RePPIT, agent skills and web skills, CLAUDE.md/AGENTS.md and
hooks, subagent patterns, agent-ready-repo scoring, background/cloud-delegated agents,
MCP portals and LLM gateways — a real expansion, not just MCP/skills/spec-driven/loop
engineering/software factory as the site's summary blurb implies. Excellent survey. It
is a survey: you finish it understanding the landscape and holding no workflow you can
run on Monday. Grading also shifted from Fall 2025's 80%-project weighting toward 50%
project + 30% open-source contributions — moving toward, not away from, the
ship-real-software emphasis this course already gates on (SC-11).

**walkinglabs/learn-harness-engineering.** ~9.6k stars, 1k forks, MIT, fifteen
languages, 12 lectures and 6 projects, a VitePress site, a `harness-creator` skill and
an audit tool. Genuinely good, and the five-subsystem model — instructions, state,
verification, scope, lifecycle — is the right decomposition. It is a beginner course
whose capstone is an Electron desktop app in TypeScript, and it teaches the environment
without teaching the workflow that runs inside it.

**`obra/superpowers`** (~40.9k stars) is the closest sibling and occupies the same
spine: brainstorm → plan → subagent execution → TDD → review. It is stronger on
enforcement (worktree isolation with a verified clean baseline; a TDD skill that deletes
code written before a failing test) and weaker on traceability (it plans in tasks, not in
criteria that steps trace back to). The course teaches the comparison in B2 and B3 rather
than pretending it doesn't exist. Full ecosystem survey in
[`ECOSYSTEM-MAP.md`](ECOSYSTEM-MAP.md).

**None of them teaches the join.** And the join is where the interesting failure is.

## 3. The hole

Böckeler's sharpest observation, and the thesis of this course:

> Computational sensors catch structural problems reliably. Inferential sensors catch
> semantic ones partially and expensively. **Neither reliably catches misdiagnosis,
> unnecessary features, or misunderstood instructions.** Correctness is outside every
> sensor's remit if the human didn't specify what they wanted.

So the spec is a load-bearing component of the harness — the *behaviour harness* — and
it is the only one nothing checks. CS146S teaches spec-driven development as a topic.
`learn-harness-engineering` treats the feature list as a scope primitive. Neither
closes the loop by making spec quality itself a sensor.

That's the hole, and it's a small enough hole to be a real wedge rather than a slogan.
`tools/spec_lint.py` in this repo is what closing it looks like: unfalsifiable
criteria, criteria with no named eval, and specs with no failure-path criterion all
fail the build, with remediation written for the agent that has to fix them.

Two supporting gaps:

**Nobody teaches the engineering manager.** CS146S teaches students,
`learn-harness-engineering` teaches an individual with one repo. Neither answers: which
of my twelve services first, what goes in a harness template, what do I report upward,
what's my stop-loss. Böckeler sketched harness templates per service topology and
justified them with Ashby's Law — a regulator needs at least as much variety as the
system it governs, so committing to a topology is a deliberate variety-reduction move.
Nobody turned that into a rollout playbook. Track D does.

**Nobody makes measurement the price of admission.** Both incumbents teach patterns and
then assert they work. This course requires an ablation per unit, publishes null and
negative results, and ships the tool.

## 4. The thesis

> **Agentic Software Engineering.** A course where the curriculum and the tooling are
> the same artifact: a working spine (idea → spec → plan → code → review → ship), the
> harness that makes the spine hold in a real repo, and a measurement discipline that
> tells you whether any of it worked.

Four commitments:

1. **The workflow is installable, not described.** `spec-driven-engineering` — 16
   skills — is installed in B1 and used for the rest of the course. This is
   structurally hard to copy: it requires having built and dogfooded a working skill
   set first.
2. **The spec is treated as the behaviour harness, and linted.** The join nobody else
   teaches, made computational.
3. **Nothing ships without an ablation.** Including null results. `tools/ablation.py`
   is the spine of the pedagogy, not an appendix.
4. **Obsolescence is stated per unit.** Half of any harness course is heuristics
   engineered around current model failures — LangChain says so about their own loop
   detection. Teach the diagnosis, not the patch.

## 5. Honest risks

- **The incumbent could add a spec track.** Mitigation: the plugin. A course can be
  copied; sixteen dogfooded, promotion-gated skills take a year of real use to build.
- **`spec_lint` is heuristic and will produce false positives.** Accepted, and stated in
  the tool's own docs. Its value is forcing the question, not being right every time.
  Track C teaches exactly this trade-off about inferential and heuristic sensors, so
  the tool being imperfect is on-message rather than embarrassing — provided we say so.
- **The tooling churns fast.** Mitigation: guides/sensors/computational/inferential is
  the invariant vocabulary. Tool specifics live in dated, clearly-marked appendices.
- **Author time.** Twenty-two units plus a thirteen-module track is a lot of nights.
  Mitigation: the critical path (A2, A3, B1, B2, B4, C1, C2, C4) ships first and is
  independently useful. Track E already has its spec and reference module.
- **Two audiences in one repo.** Track D's reader is not Track B's reader. Watch
  whether Track D wants its own home.

## 6. Relationship to `spec-driven-engineering`

The plugin is the tool. The course is why the tool is shaped that way.

They stay separate repos: the plugin should remain small enough to install and audit
without reading a curriculum, and the course needs to cover ground (context failure
modes, sensors, loops, security, adoption) that has no business inside a workflow
plugin.

The relationship runs both directions. The course is also an eval for the plugin —
writing the curriculum surfaced five capabilities the units reach for and the plugin
doesn't have, two of which close genuine holes regardless of whether the course ships.
See [`SKILLS-MAP.md`](SKILLS-MAP.md) § gap analysis.

<!-- ===== END docs/POSITIONING.md ===== -->


<!-- ===== BEGIN docs/ARCHITECTURE-AUDIT.md ===== -->

# Architecture audit

**Question put to the audit:** is this a *software engineering* course in the sense that
CS146S is one, or has it become something else wearing that name?

**Audited:** 2026-09-05, against the curriculum at 21 units.
**Method:** adversarial. The job was to find reasons the course fails its own name, not
to confirm that it passes. Findings are ordered by severity, not by comfort.

---

## Status as of 2026-09-05 (post-remediation)

| Finding | Status |
|---|---|
| F1 twelve of 21 units produce a document | **resolved** — running thread applied across B0–C6; SC-11 makes it contractual |
| F2 three audiences | **resolved** — Developer and Engineer are the course; leadership and ML are annexes |
| F3 greenfield bias | **partly resolved** — B0 (brownfield onboarding) added; the large-scale-change half was cut because `/batch` shipped |
| F4 the name oversells | **resolved by Path B** — the name is earned rather than changed |
| F5 debugging never taught | **resolved** — folded into B3 as a lab step, per the intake test |
| F6 capstone cliff | **resolved** — the running thread means software exists from B0 onward |
| F7 genre mismatch | informational, no action |

The recommendation below is Path B, and it was taken. This section is the record; the
original findings are kept intact underneath rather than edited away, because a
remediated audit that rewrites its own findings is not evidence of anything.

## Verdict (as written, pre-remediation)

**No. Not as it currently stands.**

This is an excellent course on *engineering the system that produces software*. It is
not yet a course on *engineering software*, and the difference is not semantic — it
shows up in what a graduate can do.

Three findings are severe enough to act on. One of them has a cheap structural fix that
resolves most of the problem without adding a single unit.

The good news: the gap is a *composition* problem, not a content problem. Almost nothing
here is wrong. The arrangement is.

---

## F1 — Twelve of twenty-one units produce a document, not software · SEVERE

This is the finding everything else follows from. Classifying every unit by what the
learner actually holds at the end:

| Deliverable | Units | Count |
|---|---|---|
| **Working product software** | B3, B5◐, C5◐, capstone | ~3 |
| **Tooling / harness** | A5, C2, C3, C6, D2 | 5 |
| **A document or analysis** | A1, A2, A3, A4, B1, B2, B4, C1, C4, D1, D3, D4 | 12 |

◐ = partial; the software is a by-product of demonstrating something else.

A learner can complete Tracks A, C and D — eleven units, most of the course's original
material — and never once ship a feature. They will hold a capability map, a coverage
grid, a linter, an ablation, a red-team report, a metrics baseline, and a rollout plan.
Every one of those is a real artifact. None of them is software.

**The counter-argument, stated fairly:** a spec is not "about" software any more than a
test is. It's a component. The course's own thesis (B1) is that the spec is a
load-bearing part of the system. Documents-as-deliverables is arguably the point.

**Why the counter-argument fails:** it proves specs belong in a software course, not
that a course consisting mostly of specs *is* one. The test is whether the learner's
product got better, and eleven units offer no evidence either way.

**Compare CS146S**, which weights its final project at 80% of the grade. That weighting
is the honest signal: CS146S is structurally a build course with lectures attached. Ours
is a study course with a build attached.

## F2 — Three audiences means it isn't one course · SEVERE

The README routes readers three ways: developer, architect, engineering leader. That was
presented as a feature. On audit it reads as a symptom.

A pure course has one reader and one arc. Ours has Track B for the engineer, Track C for
the architect, and D3–D4 for the manager — and D3–D4 aren't software engineering at all.
They're engineering management: baselining metrics, harness templates per topology,
stop-loss conditions, what to report upward.

That material is good and I'd keep it. It doesn't belong in the main arc.

**CS146S is purer here** and it costs them nothing, because they never claimed to serve
a manager.

## F3 — The course teaches greenfield habits for a brownfield world · SEVERE

Every lab assumes a repo you can shape. The hardest and most common agentic-coding
problem is the opposite: a large existing codebase with years of unwritten conventions,
where the agent's context is a rounding error against the repo size.

The course *acknowledges* this — "harnessability" in C1, the "second codebase problem"
in D4 — and then never gives it a lab. Acknowledging a hard problem in prose while
labbing only the easy version is exactly the failure B1 warns about: well-formed work
that solves the adjacent problem.

Related, and also missing: **large-scale change.** Migrations, framework upgrades,
sweeping refactors across hundreds of files — arguably the highest-ROI agentic use case
in industry today, and the one where the harness matters most because no human reviews
400 diffs carefully. It appears only as "entropy and garbage collection" inside C5.

## F4 — The name oversells · MODERATE

"Agentic Software Engineering" promises the full craft. What's delivered is workflow +
harness + measurement, with software engineering as the substrate rather than the
subject. A reader arriving from CS146S expecting the same genre will feel the swap
around Track C.

Two honest resolutions in §Recommendation. Renaming is the cheaper one; earning the name
is the better one.

## F5 — Debugging is mapped but never taught · MODERATE

`debug-systematically` is bound in the lock file to B3 and D2. No unit teaches the
diagnostic loop when the agent is *confidently wrong* — which is the characteristic
failure of agentic debugging and materially different from human debugging, because the
agent will produce a plausible root cause on demand and you have no signal that it
guessed.

This is a genuine software engineering skill, it's changed under agents, and we skip it.

## F6 — No unit produces a running system before the capstone · MODERATE

The capstone asks for a real change to a real open-source repo, gated on all ten Success
Criteria. Nothing before it has required the learner to hold a working system in their
hands. That's a large cliff, and it's the standard reason capstones don't get finished.

## F7 — Genre mismatch with CS146S is real but not a defect · INFORMATIONAL

CS146S is a **survey**: its unit of learning is a topic, its assessment is a project, its
reader is an enrolled student with deadlines. Ours is a **practicum**: unit of learning
is a lab, assessment is a gate, reader is a working engineer at night.

These are different genres and the comparison "is it as pure as CS146S" partly
mis-specifies. But F1–F3 stand independently of genre — a practicum that never has you
build anything is a badly designed practicum, not a different kind of good one.

---

## The graduate test

The sharpest way to see F1–F3. What can each course's graduate do on Monday?

| Capability | CS146S grad | Ours (current) | Ours (remediated) |
|---|---|---|---|
| Explain why the agent failed | partly | **yes** | yes |
| Run a repeatable idea→merge workflow | no | **yes** | yes |
| Build a sensor an agent can act on | no | **yes** | yes |
| Prove a harness change worked | no | **yes** | yes |
| Onboard an agent to a 1M-line legacy repo | no | **no** | yes |
| Run a 400-file migration safely | no | **no** | yes |
| Debug when the agent is confidently wrong | partly | **no** | yes |
| Ship a non-trivial feature end to end | **yes** | only at capstone | yes |
| Build a UI-heavy app with agents | **yes** | no (deliberate) | no (deliberate) |
| Decide adoption for a team | no | **yes** | yes (annex) |

Current column: we win five, lose three, tie two. The three losses are all F1–F3, and
they're the ones a hiring manager would test for.

---

## Recommendation

Two coherent paths. They are mutually exclusive; picking neither is how this stays
ambiguous.

### Path A — Rename and own it (cheap, honest, smaller)

Call it **"Harness and Spec Engineering for Coding Agents."** Stop competing with CS146S
on the software-engineering axis. Positioning gets sharper, F4 dissolves, F1 stops being
a defect because a harness course *should* mostly produce harnesses.

Cost: gives up the broader audience, and the capstone becomes odd.

### Path B — Earn the name (recommended)

Three changes, in order of leverage.

**B1. Introduce the running thread.** *This is the fix that matters and it costs no new
units.*

Right now each lab is a standalone exercise. Instead: the learner picks **one real
feature in one real repo at the start of Track B and ships it across Tracks B and C.**
B1 specs it. B2 plans it. B3 builds it. B4 reviews it. B5 lands it. C1 audits the harness
that just carried it. C2 fixes the docs it exposed as stale. C3 writes the linter for the
rule it violated. C4 measures whether any of that helped. C6 turns the repeated bit into
a skill.

Same twenty-one units. Same labs. But now twelve document-deliverables become *artifacts
of shipping something*, and the graduate holds working software plus the harness that
produced it. F1 and F6 both close.

This is also better pedagogy on the course's own terms: the harness stops being taught in
the abstract, which is precisely the mode C1 says doesn't work.

**B2. Add two units for the brownfield gap** (F3):

- **B0 · Onboarding an agent to a codebase you didn't write.** Repo comprehension at a
  scale that doesn't fit in context. Building the map before the harness. Which
  conventions are load-bearing versus habit. Deliberately placed *before* B1, because
  most readers' real work starts here and specs for legacy systems are a different craft.
- **C7 · Large-scale change.** Migrations and sweeping refactors. Verification when no
  human reviews 400 diffs. Batching, checkpointing, blast radius, rollback. The highest-
  ROI agentic use case in industry and currently a footnote in C5.

**B3. Move D3–D4 into a Leadership annex** (F2). Not deleted — relabelled and moved out
of the main arc, with its own front door. The main course then has one reader:
the engineer who ships. The annex has the manager. Track E already works this way, which
is evidence the pattern fits this repo.

**Optional, and I'd take it:** fold F5 into B3 as a third act — "debugging when the agent
is confidently wrong" — rather than a new unit. It's a lab step, not a unit, by the
intake test in `PLUGIN-CONTRACT.md` § 3.

Resulting shape: **23 units, one reader, one running thread, two annexes** (leadership,
ML). Track counts change; the wedge does not.

---

## What I'd leave alone

Findings should be balanced or they're just a complaint.

- **The thesis holds.** "The spec is the behaviour harness, and nothing checks it" is
  correct, well-sourced, and genuinely unoccupied. None of the above weakens it.
- **The measurement discipline is the best thing here.** Requiring an ablation per unit
  and publishing null results is a stronger commitment than either comparator makes, and
  it should survive any restructuring untouched.
- **The plugin contract is right.** Capability indirection, a version pin, and a drift
  sensor that reports plugin growth as *information* rather than failure — that's a
  well-designed dependency boundary and it needs no changes.
- **CS146S coverage is now honest.** Deliberate omissions are stated with reasons and an
  expiry date. That file should be the model for how every claim in the repo ages.
- **Track E stays as-is.** A specialization annex is the correct shape for it and it
  demonstrates that Path B's annex pattern works.

## The one-sentence version

The course currently teaches you to build an excellent factory and never asks you to
ship a product; the running thread fixes that without changing a single lab.

<!-- ===== END docs/ARCHITECTURE-AUDIT.md ===== -->


<!-- ===== BEGIN docs/ECOSYSTEM-MAP.md ===== -->

# Ecosystem map

The skills ecosystem is where the practice is actually being worked out, and it moves
faster than any course. This file is the survey: what exists, what's worth stealing,
what we must not duplicate, and — the uncomfortable part — what already-shipped tooling
makes some of our planned units unnecessary.

**Surveyed:** 2026-09-05. Star counts are as reported at that date and will be wrong
soon; they're here to indicate scale, not rank.

Base of the course remains
[`girijesh-ai/spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering).
Everything below is inspiration, contrast, or supplement to that spine.

---

## 1. The one conceptual frame worth adopting

Nate Herk's split, popularised through the Firecrawl roundup, is the most useful
taxonomy in the ecosystem and the course should teach it in C6:

- **Capability Uplift** — Claude *can't* do the task; the skill adds the ability.
  PDF generation, browser testing, web scraping, cross-agent delegation.
- **Encoded Preference** — Claude *can* do it; the skill encodes *your* way of doing it.
  Review checklists, house style, commit formats, architectural conventions.

Why it matters here: **`spec-driven-engineering` is almost entirely Encoded Preference,**
and that's a strategic fact, not a criticism. Encoded Preference skills are the ones that
survive model improvement — a Capability Uplift skill dies the moment the platform absorbs
the capability, which is exactly what happened to several skills below.

Paired with the five properties that separate a working skill from a dead one, all of
which belong in C6:

1. **The description reads like a routing rule.** "Helps with documents" doesn't
   activate. "Use when the user asks to extract form fields, fill, redact, or parse
   tables from a PDF" does.
2. **Code does the deterministic work.** Don't ask the model to sort, parse or validate
   carefully. Bundle a script — cheaper, repeatable, no hallucination surface.
3. **Lean SKILL.md, fat reference.** Core instructions fit on a phone screen; edge cases
   load on demand. This is progressive disclosure at skill scope, and it's the same
   argument C2 makes about `AGENTS.md`.
4. **One skill, one job.** Compound skills trigger at the wrong moment.
5. **Examples over rules.** Three worked examples beat twenty bullet-pointed
   constraints.

The failure signs are equally teachable: a 4,000-token SKILL.md that loads on every
adjacent task; vague triggers ("use for productivity tasks"); self-reported metadata
claiming capabilities the bundled code can't deliver; undocumented network calls in
bundled scripts.

Skills load at roughly 100 tokens each for name and description, with the body loading
only on match. That number is why "one skill, one job" is an economic argument rather
than an aesthetic one.

---

## 2. The finding that changes the curriculum

**Claude Code now ships built-ins that overlap several units we planned to teach from
scratch.**

| Built-in | What it does | What it hits |
|---|---|---|
| `/batch` | Orchestrates 5–30 parallel subagents in isolated git worktrees. Researches, decomposes, asks approval, one subagent per unit, each opens its own PR. Built for migrations, audits, cross-file refactors. | **C5 and the proposed C7 (large-scale change)** |
| `/loop` | Reruns a prompt on an interval or at the agent's own cadence. Loops expire after 7 days. | **C5's Ralph-loop material** |
| `/review` | Diff review for correctness plus cleanup. `--fix` applies, `--comment` posts to the PR, `ultra` escalates to a deep cloud review. | **B4** |
| `/simplify` | Cleanup-only pass over recently changed files. | **B3, and the ponytail comparison** |
| `/debug` | Session debug logging, read back to diagnose tool-call and config issues. | **F5 in the architecture audit** |
| **Routines** | Promote a skill workflow to run on a schedule, via API, or on a GitHub event. | **C5, D2** |

This is the course's own "what makes this obsolete" discipline firing in real time, and
it should be handled the way we tell learners to handle it: name it, don't hide it.

**The rule this implies, and it goes in `AGENTS.md`:** *don't teach what ships in the
box.* Every unit that touches an area with a built-in must (a) teach the built-in first,
(b) show where it stops, and (c) only then teach building past it. C5's lesson becomes
"`/batch` gives you fleet orchestration free — here's what it doesn't give you: merge
philosophy at throughput, slop accumulation, and the gardener." That's a better unit than
the one we had planned, and a shorter one.

---

## 3. The closest sibling, and the honest comparison

### obra/superpowers — ~40.9k stars, 3.1k forks

The one that matters most to read carefully, because it occupies **the same spine** as
`spec-driven-engineering`: brainstorm → design doc → plan → subagent-driven execution →
TDD → review before merge.

| | superpowers | spec-driven-engineering |
|---|---|---|
| Entry | `/brainstorm` — refine an idea through structured questions | `spec-from-idea` — idea → approaches → **measurable Success Criteria & Evals** |
| Planning | `/write-plan` — 2–5 minute tasks, exact file paths, verification steps | `plan-from-spec` — each step's verification **traced to a spec eval** |
| Execution | `/execute-plan` — fresh subagent per task, two-stage review | `implement` — test-first at every seam, review before each commit |
| Test discipline | `test-driven-development` — **deletes code written before a failing test** | `test-driven-development` — test-first, softer enforcement |
| Isolation | `using-git-worktrees` — verifies a clean baseline before any code | not covered |
| Missing spec | not addressed | **states "spec axis skipped — no spec found"** rather than assuming satisfaction |

**Where superpowers is stronger:** subagent orchestration, worktree isolation, and
enforcement teeth. Deleting code written before a failing test is a *computational*
guarantee where most TDD skills offer an *inferential* suggestion. That's a real design
lesson: it's a sensor, not a guide.

**Where the base repo is stronger:** the eval thread. superpowers plans in tasks;
`spec-driven-engineering` plans in criteria that plan steps trace back to and that
review checks against. That traceability is what makes `spec_lint.py` and B2's
orphan-step gate possible at all, and it's the course's whole thesis.

**What this means for the course.** Don't pretend superpowers doesn't exist — it's five
orders of magnitude more adopted. B2 and B3 should teach the comparison explicitly:
*here are two spines, here is what each enforces computationally versus inferentially,
here is why enforcement teeth matter more than workflow elegance.* That's a better unit
than one that only presents our own.

**What this means for the plugin.** Two borrowable ideas, both computational:
worktree-with-clean-baseline as a precondition, and delete-code-written-before-a-test as
enforcement. Both are cheap. Both fit `implement`.

---

## 4. The measurement exemplar

### DietrichGebert/ponytail — trending, Trendshift-listed, MIT

Forces the shortest solution that works: a ladder of seven questions, stopping at the
first rung that holds. Does this need to exist? Is it already in the repo? Does the
standard library do it? Does the platform do it? A date picker turns back into
`<input type="date">`.

**But the reason to study it isn't the skill. It's the benchmark.** Ponytail publishes
what this course has been demanding of itself and has not yet delivered:

- Headless Claude Code sessions editing a **real** open-source repo
  (`tiangolo/full-stack-fastapi-template`, FastAPI + React)
- **12 feature tickets**, scored on the git diff left behind
- **n=4**, one model held fixed (Haiku 4.5)
- **Three control arms**, not one: no-skill baseline, a terse-prose control ("caveman"),
  and a plain "YAGNI + one-liners" prompt
- A **separate adversarial safety tier**, scored independently
- Results reported as percent-of-baseline across LOC, tokens, cost and time, with
  per-task tables and a stated limitations section

Reported: −54% LOC (up to 94% where the agent over-builds, near zero where the code was
already minimal), −22% tokens, −20% cost, −27% time, 100% safe. The terse-prose control
*rose above baseline* on tokens, cost and time — which is the point of having controls.
The bare YAGNI prompt dropped a safety guard.

**This is the model for our `results/authors-run.json`.** Three specific things to copy:

1. **Control arms, not just on/off.** A prompt-only control tells you whether the skill
   is doing anything a sentence couldn't. Our `ablation.py` supports two arms; it should
   support three, and B1's four-arm table already anticipates this.
2. **A separate safety tier.** Effectiveness and safety are different questions and
   averaging them hides the case where the fast arm is the unsafe one.
3. **Reporting where the effect is near zero.** "Near zero where the code is already
   minimal" is the honest sentence that makes the 94% credible.

**It also answers `COURSE-SPEC.md` open question 2.** `tiangolo/full-stack-fastapi-template`
is a defensible shared lab repo: real, permissively licensed, Python-primary, small
enough to run cheaply, and now with a published baseline someone else produced — which
means a learner's numbers have something external to sit next to.

**Overlap check:** `engineering-standards` already carries a YAGNI check applied at
write time. Ponytail's `ponytail-review` and `ponytail-audit` do a deeper dedicated
over-engineering scan of a diff or whole repo. The base repo already credits this and
positions them as complementary, which is the right call — don't reimplement it.

---

## 5. What else is worth reading, and what to take

### forrestchang / multica-ai — Karpathy's guidelines · ~144k stars

One `CLAUDE.md`, four principles, zero dependencies, one of the fastest-growing AI
workflow repos ever. Think before coding (state assumptions; if multiple interpretations
exist, present them). Simplicity first. **Surgical changes** (touch only what you must;
if you notice unrelated dead code, mention it, don't delete it). Goal-driven execution
("add validation" becomes "write tests for invalid inputs, then make them pass").

**Take:** the *surgical changes* principle is the one the base repo doesn't state
explicitly, and orthogonal edits are a top-three complaint about agents. Also take the
lesson about form — 144k stars for a single file with no runtime is the strongest
possible evidence for "lean beats comprehensive." Cite it in C2 when arguing against the
800-line `CLAUDE.md`.

### mattpocock/skills · ~87.3k stars

Source of `handoff` and `grill-me`, both of which the base repo already carries and
credits, and whose bucket-plus-promotion-rule layout the base repo is structured after.
`grill-me` reports 156.2k installs. Its instruction is worth quoting in B1 as an example
of a description that is also the method: interview relentlessly, walk each branch of the
design tree, resolve dependencies one by one, and **provide a recommended answer for each
question** so the session moves rather than stalling.

**Take:** the recommended-answer rule. A pressure-test skill that only asks questions
blocks; one that proposes an answer per question converges. That's a design principle for
any elicitation skill.

### vercel-labs/agent-skills — fitness functions as skills

`web-design-guidelines` audits against 100+ accessibility and UX rules, always fetching
the current version of the guidelines before running. `react-best-practices` applies 57
performance rules **ordered by impact** — waterfalls first, bundle size, then server
performance, and only much later `useMemo`. `composition-patterns` replaces boolean prop
proliferation with compound components.

**Take, and it's the biggest one for Track C:** these are *architecture fitness functions
delivered as skills*, and the impact-ordering is the craft. Most rule sets are alphabetical
or arbitrary; ordering by impact is what stops an agent (or a junior) optimising the wrong
thing. C3 should teach impact-ordered rule sets as a design pattern, and the
always-fetch-latest trick as a freshness sensor.

### trailofbits/skills

CodeQL and Semgrep static analysis, **variant analysis** (find related instances of a
vulnerability across the codebase), and structured audit methodology from a firm that
does this professionally.

**Take:** variant analysis is a genuinely underused pattern and belongs in D1 next to the
Semgrep false-positive numbers. "You found one; now find its siblings" is a good
generalisation of the harness idea — Hashimoto's "never make that mistake again," applied
to a class rather than an instance.

### JuliusBrussee/caveman · ~68.1k stars

65% average output-token reduction (range 22–87%) by stripping narration while keeping
technical content byte-for-byte. Includes `/caveman-compress`, which rewrites your
`CLAUDE.md` and cuts ~46% of input tokens on every future session.

**Take:** a March 2026 result that constraining models to brief responses improved
accuracy by 26 points on some benchmarks. That's a strong, citable, counterintuitive
finding for A3's context-budget material — brevity as an accuracy intervention, not just
a cost one. Also worth noting as an experimental-design lesson: caveman is the control
arm in ponytail's benchmark, which is a nice example of one community skill serving as
another's control.

### mksglu/context-mode · ~16.3k stars

Filters verbose shell output before it reaches context, and keeps a running session log
so work resumes after a context reset. Sessions that died at 30 minutes run for hours.

**Take:** it names the real mechanism behind A3's distraction failure — after ~120k
tokens attention relationships strain and quality degrades, and most of what's being
re-read is `git status` and `npm test` junk rather than project context. Shell-output
filtering is a *guide* implemented as middleware, and it belongs in A3 as a worked
example.

### anthropics/skills

`frontend-design` (bans overused fonts, forces a committed aesthetic direction),
`webapp-testing` (Playwright against your local app), the document skills, `doc-coauthoring`,
and `skill-creator`.

**Take:** `frontend-design` and `webapp-testing` are the two that make the new B6 unit
possible — a guide for the generation and a sensor for the result. `skill-creator` is
what C6 should have learners use rather than hand-rolling.

### skills-directory/skill-codex

Delegates from Claude Code to Codex via `codex exec` with chosen model, reasoning effort
and sandbox mode. Plan in one agent, execute in another.

**Take:** cross-agent delegation is a real pattern now, and it resolves
`COURSE-SPEC.md` open question 1 differently than proposed. Rather than picking one
reference CLI and writing a porting contract, treat multi-agent as a first-class fact:
the Agent Skills spec is adopted across Claude Code, Codex CLI, Cursor, Gemini CLI and
Copilot, and a skill runs on all of them unmodified. Say that, then use one CLI for
concreteness without apologising.

### The trackers

`hesreallyhim/awesome-claude-code` (~53.5k), `travisvn/awesome-claude-skills` (~13k),
`VoltAgent/awesome-agent-skills`, `linny006/trending-claude-skills` (auto-refreshed),
`skills.sh` (Vercel's searchable directory with install counts), plus first-party
collections from `huggingface/skills` and `microsoft/skills`.

**Take:** install counts on skills.sh are the closest thing the ecosystem has to a
revealed-preference signal, and they're a better source than stars for deciding what to
teach. Also worth noting for the course's own maintenance: an auto-updating tracker is a
*sensor* on a landscape claim, which is exactly what `CS146S-COVERAGE.md` needs and
currently lacks.

---

## 6. What this changes

### In the course

1. **New rule: don't teach what ships in the box.** Every unit touching `/batch`,
   `/loop`, `/review`, `/simplify`, `/debug` or Routines teaches the built-in first, then
   where it stops. Goes in `AGENTS.md`.
2. **C5 shrinks and sharpens.** Fleet orchestration is free now. The unit becomes merge
   philosophy at throughput, slop accumulation, and the gardener — the parts `/batch`
   doesn't give you.
3. **C7 (large-scale change) may not need to exist.** `/batch` is explicitly built for
   migrations and cross-file refactors. Re-test the audit's F3 recommendation against
   this before writing the unit.
4. **B2/B3 gain an explicit superpowers comparison**, framed as computational versus
   inferential enforcement.
5. **C3 gains impact-ordered rule sets** and the always-fetch-latest freshness trick.
6. **C6 gains the Capability Uplift / Encoded Preference taxonomy** and the five
   properties, and points learners at `skill-creator` rather than a blank file.
7. **`ablation.py` gains a third arm** and a separate safety tier, following ponytail.
8. **The shared lab repo is decided:** `tiangolo/full-stack-fastapi-template`, with
   ponytail's published numbers as an external reference point.
9. **A3 gains two worked examples**: context-mode's shell-output filtering, and the
   brevity-improves-accuracy result.
10. **D1 gains variant analysis** from Trail of Bits.

### In the plugin

Three borrowable, all computational rather than inferential — which is the pattern worth
noticing:

- **Worktree with verified clean baseline** as a precondition to `implement` (superpowers).
- **Delete code written before a failing test** as enforcement in
  `test-driven-development` (superpowers). Currently a guide; should be a sensor.
- **A surgical-changes rule** in `engineering-standards` (Karpathy): touch only what you
  must, mention unrelated dead code rather than deleting it.

## 7. What we should not build

- **Another over-engineering auditor.** ponytail owns this, the base repo already credits
  it, and `engineering-standards` covers the write-time case.
- **Another handoff or grill-me.** Already in the base repo, already credited upstream.
- **A frontend rule set.** Vercel maintains 157 rules across three skills and keeps them
  current. B6 teaches *using* them as sensors, not replacing them.
- **A skill directory or awesome list.** Four exist, one auto-refreshes every 15 minutes.
- **A security scanner.** Trail of Bits ships the professional version.

The pattern: the ecosystem is strong on **Capability Uplift** and on **narrow Encoded
Preference** (one framework, one domain). It is thin on the *connective tissue* — how a
spec, a plan, a review and a harness compose into one system you can measure. That gap is
where the base repo sits, and it's the only thing this course should try to own.

<!-- ===== END docs/ECOSYSTEM-MAP.md ===== -->


<!-- ===== BEGIN docs/CS146S-COVERAGE.md ===== -->

# CS146S superset conformance

<!-- last-verified: 2026-09-08 -->

**The claim: this course is a superset of Stanford's CS146S Fall 2025** — the last
complete run — **and overlaps substantially with, but has 11 open gaps against,**
the announced Fall 2026 syllabus. Not "inspired by": every Fall 2025 topic maps to a
unit here, and many go further. Fall 2026 is weaker on purpose, stated as such rather
than quietly claimed: see § Fall 2026 for exactly which 11 topics and why.

That is a strong claim, so it is a **gate rather than a sentence**:

```bash
python3 tools/check_coverage.py --allow-planned
```

[`cs146s.map.json`](../cs146s.map.json) holds every topic and its mapping, split by a
`fall_2026_claim` field the gate reads separately from the main `claim`. The gate
fails on any topic marked `omitted` under a `superset` claim scope, or `unverified`
(you cannot claim coverage of material nobody has read) — full stop, no downgrade
available for either of those. An `omitted` topic under a scope already downgraded
from `superset` (Fall 2026, right now) is a disclosed gap (COV008, a warning), not a
silently passing error. It currently **holds**: Fall 2025 fully, Fall 2026 honestly
short by the 11 topics § Fall 2026 names.

This started as an audit that permitted deliberate omissions. The superset constraint
removed that permission, and two of the three skips became commitments. The constraint
made the course better — B6 in particular turned out to be the sharpest test of the
course's own thesis, which is not what I expected when I cut it.

**Audited against:** CS146S Fall 2025 public materials (the last complete run), plus
the live Fall 2026 syllabus — the actual 10-week schedule, not the earlier site
overview blurb (see § Fall 2026 for why that distinction turned out to matter).

**Current gate output:** 52 topics — 16 covered, 21 deeper, 4 planned, 11 omitted, 0
unverified. 0 errors; 16 warnings — the 11 Fall 2026 gaps (disclosed, COV008) plus
5 traceable to units not yet written or the map's secondary evidence base.

Verdicts: ✅ covered · ⬆️ covered and deepened · 🆕 gap found, unit added ·
📌 committed by the superset constraint (was a skip).

---

## Evidence base

The map is built from secondary sources throughout — a third-party course writeup
rather than the official syllabus — so every verdict below inherits that uncertainty.
`check_coverage.py` warns about this (COV006). Week 2 is the one exception: it was
unverified until this session, when it was checked directly against the live syllabus
at `themodernsoftware.dev/fall2025` rather than guessed from the W1→W3 progression.
Upgrading the remaining nine weeks to the same standard is the next highest-value hour
of work on this file; `check_coverage.py` will keep warning until it's done.

---

## Fall 2025, week by week

### W1 — Introduction to coding LLMs ✅

Pre-training as lossy compression, SFT as personality, RL as reasoning, the model needs
tokens to think, the Swiss cheese capability model, reliability strategies (few-shot,
chain-of-thought, self-consistency, RAG, reflection, role prompting).

**Us:** A1. Same ground, less depth on the training pipeline, more on turning the
capability holes into your team's guides. A student needs the mechanism; a working
engineer needs the diagnostic.

### W2 — The anatomy of coding agents ⬆️

Verified against the live syllabus, not guessed from neighboring weeks: agent
architecture and components, tool use and function calling, and MCP (Model Context
Protocol). Readings cover an MCP introduction, sample server implementations,
authorization, the SDK, and the registry. The paired assignment has students build a
coding agent from scratch, then a custom MCP server.

**Us:** A2 unrolls the agent loop stage by stage (gather context → select tool →
execute → observe → repeat → terminate), ties it to real Terminal-Bench evidence, and
inventories what Claude Code already ships built-in. A5 goes further on tools and MCP
specifically: interface design, when *not* to reach for an MCP server, code execution
as an alternative, and a measured tool-count ablation — deeper than an introduction and
a sample-server tour.

### W3 — The AI IDE: autonomous agents and a new developer role ⬆️

Sync vs async agents. The semi-async zone (avoid 30s–5min tasks — too long to wait, too
short to switch). The four context failure modes: poisoning, distraction, confusion,
clash. Defensive prompting. The prompt as the new source code, and generated code as a
lossy projection of the spec.

**Us:** A3 and A4 cover the failure modes and delegation economics. **B1 takes the
"prompt is the new source code" thesis further than CS146S does** — CS146S states it as
a principle; B1 makes it operational (specs are versioned, reviewed, diffed, and linted
in CI) and connects it to Böckeler's sensor gap, which is the load-bearing argument of
our whole course.

### W4 — Coding agent patterns: ergonomic tools and team knowledge 🆕

Designing tool interfaces for agent consumption: consolidate functions (fewer tools,
less context confusion), make outputs semantically meaningful (`user: Jane Doe`, not
`user: A1B2C3D4`), allow verbosity control so the agent manages its own context budget,
mirror the team environment exactly. Plus the `CLAUDE.md` pattern.

**Us, before this audit:** the `CLAUDE.md` half was C2. The **tool design half was
missing** — mentioned in A3 only as "fewer tools beat more tools," which is the
conclusion without the craft.

**Action taken: added A5 · Tools and MCP — designing the agent's hands.** Covers tool
interface design, MCP server design and when *not* to use one, code execution as an
alternative to tool proliferation, and measuring tool-count effects. This is also a
Fall 2026 headline topic, so the gap was doubly worth closing.

### W5 — The modern AI terminal: product principles and risk tolerance 📌

Market signals and valuations. Seven product principles across usability, control and
speed. The Strategic vs YOLO agent profile experiment — same prompt, two configurations,
and the YOLO agent won because it pivoted when data sources broke.

**Was skipped:** market signals, valuations, and product-design principles for building
a dev tool. Interesting, dated within a quarter, and our reader is building software
with agents rather than building an agent product.

**Now committed**, as `docs/appendix-landscape.md` — a dated, explicitly disposable
appendix rather than a unit. Superset by content, not by format. Putting a
quarterly-obsolescing market survey into the main arc would damage the course; leaving
it out entirely would break the claim. An appendix with a stated expiry is the honest
third option.

**Kept:** the Strategic vs YOLO finding, folded into A4 and D1. It's a genuinely
uncomfortable result — more guardrails lost to fewer guardrails on that task — and a
course that only argues for constraint should have to sit with it.

### W6 — AI testing and security ✅

Three working attack chains: SSRF via a web-content tool, credential theft via base64
encoding to bypass filters, and the YOLO-mode exploit where the agent modifies its own
config to disable safeguards. Plus Semgrep's numbers on AI security scanning: 82–86%
false positives across 11 large Python web apps, and identical scans returning 3, 6 and
11 findings on successive runs.

**Us:** D1, same material, plus prompt injection through data channels (Track E extends
this to datasets and model cards, which CS146S doesn't touch).

### W7 — Modern software support: AI-augmented code review ⬆️

The review hierarchy with mental alignment at the base, below bug-finding. The review
quadrant: gold zone, human-only zone, annoyance zone.

**Us:** B4, same framework, plus two-axis review against the spec and the governance
rule that a missing spec is reported as skipped rather than silently satisfied. That
rule is a small design decision with a large effect and it's original to
`spec-driven-engineering`.

### W8 — Automated UI and app building 📌

The historical complexity tax across web architecture generations. The v0-style
pipeline: intent understanding, context assembly, generation, automated validation,
stream manipulation to fix known bad patterns mid-output.

**Was skipped** as a domain vertical. **Now B6 · Generated interfaces and the
validation problem** — and cutting it was the wrong call independent of the superset
constraint.

Interfaces are where the sensors run out first. `pytest` cannot tell you the button is
in the wrong place, the contrast fails, the focus order is nonsense, or the empty state
is missing. That makes generated UI the sharpest available test of the course's thesis
rather than a vertical beside it, and it produces the clearest case in the whole
curriculum for a human-in-the-loop sensor placed where C1's timing rule says it belongs.

Stream manipulation also earns its keep: intervening in the output stream is feedforward
correction applied at generation time rather than review time, which is a guide in a
place most people don't think to put one.

B6 is also a **build** unit, which helps the deliverable-ratio problem in
`ARCHITECTURE-AUDIT.md` § F1.

### W9 — Agents post-deployment: from SRE to AI-native operations ✅

Traditional ops as trench warfare. SRE's inversion: operations as a software problem,
the 50% toil rule, the error budget. AI-assisted vs AI-native: the engineer driving
with help, versus the engineer saying "resolve this checkout failure" and specialist
agents investigating in parallel. Dynamic just-in-time runbooks over static ones.

**Us:** D2. Same, plus the concrete work of making runtime legible — an ephemeral
observability stack per worktree, logs and metrics the agent can query, the app bootable
and drivable per worktree.

### W10 — Final project ✅

**Us:** the capstone. CS146S weights it at 80% of the grade, which is the honest signal
that the project is the course. Ours is a real change to a real open-source repo, with
an ablation.

---

## Fall 2026, week by week

**This section was rebuilt from the live 10-week syllabus** (verified 2026-09-08),
replacing an earlier version built from the site's shallow overview blurb (5 flat
topics, no week structure — the same kind of secondary-source problem the original W2
blocker was). 11 of 30 Fall 2026 topics are genuinely uncovered, not guessed at, which
is why **the superset claim is deliberately downgraded for Fall 2026 specifically**
(`cs146s.map.json`'s `fall_2026_claim: "overlaps"`) rather than for the whole map.
Fall 2025 still holds as a full, unweakened superset — 0 errors, checked separately.
`check_coverage.py` reports the 11 Fall 2026 gaps as warnings (COV008, "disclosed
gap under a downgraded claim"), not the hard errors a superset topic marked `omitted`
would get; the distinction is the difference between an honest scope statement and a
silently broken promise.

| Week | Topic | Us |
|---|---|---|
| 1 | LLM + agent loop internals | ⬆️ A1, A2 |
| 1 | Core tool set and task flow | ✅ A2 |
| 1 | Production system-prompt / tool-definition design | ⚠️ **gap** |
| 2 | Advanced prompting | ✅ A1 |
| 2 | RePPIT + spec-driven development | 📌 planned — needs a named comparison in B2, the way B2 already compares itself to `obra/superpowers` |
| 2 | MCP fundamentals | ✅ A5 |
| 2 | Tool ergonomics | ⬆️ A5 |
| 3 | Skill authoring (SKILL.md) | ⬆️ C6 |
| 3 | Web skills | ⚠️ **gap** |
| 3 | CLI fluency | ⚠️ **gap** (implicit exposure via Claude Code throughout ≠ taught) |
| 4 | CLAUDE.md / AGENTS.md | ⬆️ C2 |
| 4 | Hooks as guardrails | ⚠️ **gap** |
| 4 | Subagent patterns (planner/implementer/reviewer) | ⚠️ **gap** |
| 5 | Agent-ready repo scoring/auditing | ⚠️ **gap** — distinct from B0 (B0 is an agent comprehending a repo; this is scoring the repo itself) |
| 5 | Common gaps blocking agents | ⬆️ B0 |
| 6 | AI review limits, architectures, workflow fit | ⬆️ B1, B4, C3 |
| 7 | SAST/SCA, prompt injection, triage | ⬆️ D1 |
| 8 | Local parallel fleets | ⬆️ C5 |
| 8 | Async cloud-delegated agents | ⚠️ **gap** |
| 8 | Issue-to-PR triggers (Slack/Linear/GitHub) | ⚠️ **gap** |
| 9 | Org adoption patterns | ⬆️ D4 |
| 9 | MCP portals | ⚠️ **gap** |
| 9 | LLM gateways / model routing | ⚠️ **gap** |
| 10 | Software factory, post-deployment ops | ✅ C5, ⬆️ D2 |
| 10 | "Where the field goes next" | ⚠️ **omitted by design** — a practicum gates labs, not speculation; the honest resolution is a dated appendix (the A6 precedent), not a claim of coverage |

Legend adds ⚠️ **gap** (genuinely uncovered, tracked in `AGENTS.md` § Known gaps) to
the existing ✅ ⬆️ 🆕 📌 set.

**Also new in Fall 2026, not a topic row:** grading shifts from 80/15/5
(project/assignments/participation) to **50/15/30/5**, adding a 30% "Open Source
Contributions" category. We already gate the capstone on a real merged/opened PR
(SC-11) — this is a place Fall 2026 moved toward our existing design, not away from it.

---

## The cost of the superset claim

Stated plainly so it can be revisited: two units exist because of a positioning promise
rather than because the thesis demanded them. A6 is partly a landscape unit and will date
faster than anything else here. B6 is a domain vertical.

Both are defensible — A6 became the built-ins unit the course needed anyway, and B6 is a
strong worked example — but if either starts feeling like ballast, the honest move is to
drop the superset claim rather than keep a weak unit alive to defend it.

## What CS146S has that we structurally can't

**Guest practitioners.** Their lineup includes the creator of Claude Code, Vercel's head
of AI research, Semgrep's CEO, an a16z GP. That is a genuine advantage of a Stanford
course and we should not pretend otherwise.

**Partial mitigation:** a `docs/field-notes/` section for short written interviews —
practitioners answering one question each about their own harness. Lower ceiling than a
lecture, but asynchronous, citable, and it ages better than a recording. Not v1.

**A cohort and deadlines.** The single biggest reason self-study stalls. Our substitute
is the gate: every unit has a `verify.sh` that passes or doesn't, which is a weaker
forcing function than a grade but stronger than a reading list.

## What we have that CS146S doesn't

- An installable workflow rather than a described one — sixteen skills, two commands.
- The spec treated as the behaviour harness, and linted (`tools/spec_lint.py`).
- Measurement as the price of admission: an ablation per unit, null results published.
- A leadership track — CS146S teaches students, not the person rolling this out.
- An ML specialization, where verification is slow, expensive and statistical.
- Obsolescence stated per unit.

## Where we go further

Nine of twenty-five topics are marked `deeper`, and the pattern is consistent: CS146S
states a principle, we make it operational and measurable.

| Topic | Them | Us |
|---|---|---|
| Prompt as source code | a principle | specs versioned, linted in CI, checked by `review-code` |
| Context failure modes | four named modes | reproduce all four, then ablate tool count |
| Review quadrant | a framework | two-axis review, plus the missing-spec governance rule |
| Agent skills | a platform capability | authoring, description design, evals vs a no-skill baseline |
| AI scanning limits | a cautionary statistic | the canonical example of an uncalibrated inferential sensor |
| Spec-driven development | one topic | five units and an installable 16-skill plugin |

## Maintenance

`check_coverage.py` warns when the map passes 12 months. Re-run when the Fall 2026
materials publish and annually after.

The failure mode is silent: their syllabus changes, ours doesn't, and this file keeps
claiming coverage we no longer have. A coverage claim with no expiry is the same mistake
as a sensor that never fires — which is the question C4 leaves you with, and it applies
to us as much as to anyone.

<!-- ===== END docs/CS146S-COVERAGE.md ===== -->
