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
materials and assignments, strong guest lineup. The Fall 2026 edition advertises MCP,
agent skills, spec-driven development, loop engineering and the software factory.
Excellent survey. It is a survey: you finish it understanding the landscape and holding
no workflow you can run on Monday, and the real learning is concentrated in a final
project weighted at 80%.

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
