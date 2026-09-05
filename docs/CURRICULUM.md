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
