# Curriculum

Thirteen modules in five parts. Every module is one question, one lab, one number.

**Short on time?** The core six are **M00, M01, M03, M04, M05, M11**. They stand
alone and cover the wedge. Ship those first.

Legend: 🔬 lab with a pass/fail gate · 📊 requires an ablation result · 🏛️ leadership track

---

## Part 0 — Measure first

### M00 · What is your harness actually worth? 🔬📊

**Question.** You believe your `CLAUDE.md` helps. By how much?

Before any theory, you instrument yourself. Pick five real tasks from your own ML
repo, write a verifier for each, and run them three times with your current harness
and three times with it stripped. Then look at the number.

Most people find one of three things, and all three are useful: the harness helps a
lot (now you can defend it), it helps a little (now you know where to invest), or it
does nothing measurable (now you've stopped paying a tax you thought was insurance).

You will also reproduce the two canonical long-running failures on purpose: the agent
that tries to one-shot the whole thing and dies mid-feature with no notes, and the
agent that looks at a half-built repo, sees progress, and declares the job done.

- **Lab.** Build `results/baseline.json` with `tools/ablation.py`.
- **Gate.** N≥5 tasks, K≥3 repeats, both arms, verifier recorded per task.
- **Serves.** SC-1.

---

## Part 1 — Harness fundamentals, on ML ground

### M01 · Agent = model + harness 🔬📊

**Question.** What are the parts, and which parts do you have?

Five subsystems: instructions, state, verification, scope, session lifecycle. Two
directions: **guides** steer before the agent acts, **sensors** observe after so it
can self-correct. Two execution types: **computational** (deterministic, milliseconds,
reliable) and **inferential** (semantic, slow, expensive, non-deterministic). Three
regulation categories: maintainability, architecture fitness, behaviour.

Then the uncomfortable part: **harnessability**. Typed code affords a type checker.
Clean module boundaries afford architecture rules. A 4,000-line `train.py` with global
state affords nothing. The harness is most needed exactly where it is hardest to build,
and ML repos are usually on the wrong side of that line.

- **Lab.** Produce a harness coverage map of your repo: every cell in the
  guides × sensors × {computational, inferential} grid, marked present, absent or
  impossible-here. Then justify why the three most expensive gaps are the right three
  to close first.
- **Gate.** Map is complete; each "impossible-here" cell names the structural property
  that would have to change.
- **Obsolete when.** The categories won't go obsolete. The specific gaps will.

### M02 · The repository is the only thing that exists 🔬

**Question.** Why did your beautifully written 800-line `CLAUDE.md` make things worse?

Because a giant instruction file crowds out the task, makes everything "important" so
nothing is, rots the moment it's written, and can't be mechanically checked. OpenAI's
answer: `AGENTS.md` is a table of contents, roughly 100 lines, pointing into a
structured `docs/` tree that is the system of record. Progressive disclosure — a
small stable entry point plus directions on where to look next.

The ML-specific version of this is worse than the general case. Model choices
justified in a Slack thread. A threshold set to 0.7 in a meeting eighteen months ago.
The reason you dropped that feature. A retraining cadence that lives in one person's
head. To the agent, none of it exists.

- **Lab.** Split a monolithic instruction file into map + knowledge base. Add a
  freshness linter and a doc-gardening task that opens fix-up PRs for docs that no
  longer match code behaviour.
- **Gate.** Entry point under 120 lines; link checker green; the gardener finds at
  least one genuinely stale doc.

### M03 · The spec is the behaviour harness 🔬📊

**Question.** Which agent failures can no sensor catch?

Böckeler's sharpest point: computational sensors reliably catch structural problems —
duplication, complexity, coverage, architectural drift, style. Inferential sensors
partially catch semantic ones — redundant tests, brute-force fixes, over-engineering —
expensively and probabilistically. **Neither reliably catches misdiagnosis,
unnecessary features, or misunderstood instructions.** Correctness is outside every
sensor's remit if you never said what you wanted.

The failure that actually burns teams is not malformed code. It is well-formed code
that solves the wrong problem, and the only instrument that detects it is a written
statement of the right problem.

This is where [`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
enters — not as an aside but as the behaviour harness. `spec-from-idea` produces
measurable Success Criteria; `plan-from-spec` makes each step carry a verification
traced back to one; `review-code` runs a spec axis before a standards axis.

- **Lab.** Take a real failure from your M00 baseline. Write the spec that would have
  caught it. Re-run that task with the spec as a guide and measure.
- **Gate.** Classification exercise, ≥4 of 5 (SC-5). Plus a measured re-run.
- **Obsolete when.** Never. As models improve, the spec becomes *more* of the
  bottleneck, not less.

---

## Part 2 — The ML wedge

This is the part nobody else has written.

### M04 · Verification when truth is statistical 🔬📊

**Question.** AUC moved from 0.834 to 0.831. Is that a regression?

The entire published harness literature assumes `pytest` returns green or red in
seconds. Your sensor returns a float, after four minutes, and it's different every
run. An agent cannot act on a float. It needs a boolean, and a wrong boolean is worse
than none — a too-tight threshold trains the agent to chase noise, a too-loose one
lets real damage through.

Covered: measuring your noise floor before choosing a threshold; seed pinning and
what stays non-deterministic anyway; tolerance bands vs. hard gates; the difference
between a metric regression and a contract violation; and writing failure messages
that carry remediation into agent context rather than just reporting a number. (That
last one is the highest-leverage trick in the course and costs almost nothing.)

- **Lab.** Build a calibrated verifier. See `modules/m04-verification-when-truth-is-statistical/`.
- **Gate.** Passes the true-pass, catches the true-regression, does *not* fire on the
  within-noise wobble (SC-3).
- **Obsolete when.** Models get good enough at statistical reasoning to interpret raw
  metric deltas in context. Watch this one; it may go first.

### M05 · When the sensor costs $40 and takes two hours 🔬📊

**Question.** How do you build a feedback loop you can't afford to run?

Computational sensors are supposed to be cheap enough to run on every change. A
training run is not. So you build a ladder:

- **Tier 1, micro-fixture, under 30 seconds.** Deliberately tiny data — the SandMLE
  insight, that constraining sandbox data to 50–200 samples cuts execution to under
  15 seconds and makes thousands of iterations feasible where a handful were before.
  Preserves the *structure* of the problem, not its scale. Catches shape errors,
  leakage, pipeline breakage, contract violations.
- **Tier 2, subset, under 10 minutes.** Catches most real regressions. Gates the PR.
- **Tier 3, full.** Nightly or on-demand. Gates the merge to main.

Plus: injecting time and cost budgets into agent context (LangChain's middleware
approach); hibernate-and-wake checkpointing so a six-hour step survives a context
boundary, as in Meta's Ranking Engineer Agent; and the honest accounting of when the
harness costs more than the mistakes it prevents.

- **Lab.** Build the three-tier ladder for one real pipeline; inject three defects and
  measure which tier catches each.
- **Gate.** Tier 1 under 30s wall time and catches ≥2 of 3 (SC-4).

### M06 · Data is part of the harness 🔬

**Question.** The agent wrote correct code against data it hallucinated the shape of.

Parse, don't validate — at the data boundary. Schema contracts the agent can read and
a linter can enforce. Fixture generation that preserves structure while shrinking
scale. Leakage detectors as a first-class sensor, because leakage is the ML
equivalent of a test that asserts `True == True` and agents produce it constantly.
PII guards as a hard boundary, not a guideline. And the "agent can't see the
warehouse" problem: what to materialise into the repo as a contract versus what to
expose through a tool.

- **Lab.** Write a schema contract and a leakage sensor; get an agent to violate both,
  then make the violations impossible.
- **Gate.** Both sensors fire on the seeded violations and stay silent on clean runs.

### M07 · The notebook problem 🔬

**Question.** How do you harness the least harnessable artifact in software?

Notebooks defeat almost every sensor: diffs are unreadable, execution order is
implicit, state is invisible, and they are where most ML work actually starts. This
module is about the exit ramp — not banning notebooks, but building the path from
exploration to a layered module with enforced dependency direction, and making
experiment history legible in the repo rather than trapped in a tracking UI.

Also: the layered-domain pattern from the OpenAI post, translated to ML. Types →
config → data access → features → training → serving, with dependency directions
enforced mechanically by a custom linter whose error messages tell the agent how to
fix the violation.

- **Lab.** Take one exploratory notebook to a linted module with a passing contract.
- **Gate.** Custom architecture linter rejects three seeded boundary violations.

### M08 · Sensors for ML systems in production 🔬📊

**Question.** What does a fitness function look like when the thing you're regulating
degrades on its own?

Architecture fitness harness, ML edition: latency and cost SLOs as guides plus tests
as sensors; drift detectors as continuous sensors outside the change lifecycle;
fairness constraints as enforceable gates; eval-suite regression as a CI gate.

Then the calibration problem for inferential sensors. LLM-as-judge is the most
seductive sensor in ML and the least trustworthy. The reference data point: Semgrep
tested Claude Code and Codex against 11 large Python web applications and measured
82–86% false positive rates, with identical scans returning 3, 6 and 11 findings on
successive runs. A single AI scan gives you a confident, false sense of coverage. So:
how to calibrate a judge, how to measure its agreement with humans, and when to fire it.

- **Lab.** Calibrate an LLM judge against a labelled set; report agreement and cost
  per correct catch versus a computational alternative.
- **Gate.** Reported precision/recall on a held-out set; a judge below the stated bar
  must be replaced or removed, not shipped with a caveat.

---

## Part 3 — Scale

### M09 · Loops and fleets 🔬📊

**Question.** One agent works. What breaks at ten?

The loop family, from Huntley's minimal Ralph pattern up through planner /
generator / evaluator splits. Worktree isolation so parallel agents don't collide.
Loop detection — LangChain's per-file edit counter that injects "consider
reconsidering your approach" after N edits to the same file, which is a heuristic
engineered around a current model failure and says so.

Merge philosophy at throughput: OpenAI runs minimal blocking gates, short-lived PRs,
and treats flakes with a re-run rather than an indefinite block, on the reasoning
that when agent throughput exceeds human attention, corrections are cheap and waiting
is expensive. This is irresponsible at low throughput and correct at high. Know which
one you are.

Then entropy. Agents replicate existing patterns including the bad ones. OpenAI's team
spent every Friday cleaning up slop until they encoded golden principles and ran
recurring cleanup agents that open small auto-mergeable refactor PRs. Technical debt
as a high-interest loan: pay it continuously, not in painful bursts.

- **Lab.** Run four agents in isolated worktrees against one backlog; measure
  throughput, collision rate and slop accumulation with and without a gardener.

### M10 · Safe autonomy in ML repos 🔬

**Question.** What can an agent do to you that a web app agent can't?

The general attack surface first: prompt injection, SSRF through web-fetching tools,
credential exfiltration via encoding, config-modification exploits where the agent
disables its own safeguards.

Then the ML-specific vectors that nobody covers: instructions embedded in a dataset
the agent will read; model cards and README files from public hubs; notebooks
downloaded from competitions; training data as an injection channel. An ML agent
ingests far more untrusted text than a web agent, and it ingests it as *data* while
the harness treats data as safe.

Sandboxing, permission design, secret handling, and the honest position that a
sandbox is a boundary, not a solution.

- **Lab.** Red-team your own harness: plant an injection in a dataset artifact and see
  whether your agent follows it. Then close the class of failure.

---

## Part 4 — The leadership layer 🏛️

### M11 · Rolling this out on a team 🏛️

**Question.** You're convinced. Now what do you tell twelve engineers on Monday?

**Harness templates.** Most organisations have three or four service topologies that
cover 80% of what they build. Böckeler's proposal is that these become bundles of
guides and sensors, and Ashby's Law is the argument: a regulator needs at least as
much variety as the system it governs and can only regulate what it has a model of.
An LLM can produce almost anything; committing to a topology is a deliberate
variety-reduction move that makes a comprehensive harness achievable at all. Teams may
start choosing stacks partly by which harnesses already exist.

**What to measure.** Cost per merged PR. Time-to-merge for agent-assisted work. Rework
rate — the honest one. Review latency relative to PR size. Compute spend per engineer.
Baseline these from systems you already have before you change anything, then use the
numbers to decide which harness layer to invest in next.

**What not to automate.** The harness is an attempt to externalise what an experienced
engineer brings implicitly — absorbed conventions, felt cognitive pain, social
accountability, organisational memory of which debt is tolerated for business reasons.
It only goes so far. A good harness doesn't try to eliminate human input; it directs
human input to where it matters most. Say out loud where that is on your team.

**The second codebase problem.** A harness is real, ongoing engineering work. On a
legacy repo with years of unwritten conventions, the backfill is steep. Budget for it
like infrastructure, because that is what it is.

**The stop-loss.** State in advance what result would make you roll this back. A plan
without one is an act of faith.

- **Lab.** Write the one-page rollout plan against `templates/rollout-plan.md`.
- **Gate.** Peer review; no stated stop-loss condition is an automatic fail (SC-6).

---

## Part 5 — Capstone

### M12 · Harness a real ML repo end to end 🔬📊

Take a real open-source Python ML repository. Build the full harness. Run the
ablation. Publish a HarnessCard — a structured report of what you built, what it cost,
what it caught, what it missed, and what would make it obsolete.

The deliverable is a PR to your own fork plus a results file. The bar is not "I built
a lot of harness." It is "here is the measured difference, including where there
wasn't one."

- **Gate.** All of SC-1 through SC-8 demonstrated on one repo.

---

## Module shape

Every module README has these sections, enforced by `tools/audit.sh`:

1. **The question** — one sentence.
2. **The failure** — a real, reproducible agent failure this module addresses.
3. **The idea** — the concept, with sources.
4. **The lab** — runnable steps against a real repo.
5. **The gate** — `verify.sh`, pass/fail, traced to a Success Criterion.
6. **Our numbers** — the authors' ablation result, including null and negative results.
7. **What makes this obsolete** — the model or tooling change that retires it.
8. **Sources** — primary only.
