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
