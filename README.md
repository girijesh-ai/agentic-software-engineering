# Agentic Software Engineering

**Give your agent a workflow to run, a harness to run it inside, and a number that
tells you whether either one is worth anything.**

Most material in this space teaches one of those three. This course is the join. Four
tracks, twenty-two units, one capstone, and two annexes — built on
[`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering),
which you install in the second unit and use for everything after.

> **Status: v0.** Spec, curriculum, skills map and tooling are done and usable. Two
> reference units are written to full depth: [`B1 · Idea → spec`](units/b1-idea-to-spec/)
> and, in the ML track, [`M04 · Verification when truth is statistical`](tracks/ml-systems/modules/m04-verification-when-truth-is-statistical/).
> The rest is the build. Start at [`docs/COURSE-SPEC.md`](docs/COURSE-SPEC.md).

---

## The argument

Böckeler's observation, which this whole course hangs on:

> Computational sensors — tests, linters, type checkers — catch structural problems
> reliably. Inferential sensors — AI review, LLM-as-judge — catch semantic ones
> partially and expensively. **Neither reliably catches misdiagnosis, unnecessary
> features, or misunderstood instructions.**

The failure that actually burns teams isn't malformed code. It's well-formed,
well-tested code that solves the wrong problem — and the only instrument that catches
it is a written statement of what the right problem was.

So the spec is part of the harness. It's the *behaviour harness*, it's load-bearing,
and it's the one component nothing checks. [`tools/spec_lint.py`](tools/spec_lint.py)
is what checking it looks like.

## Is this the right course for you?

**Not if you've never used a coding agent.** Start with
[walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering)
— it's free, excellent, and covers the fundamentals better than a second introduction
would. Come back when you have a harness working and you're hitting the wall on
workflow.

**Not if you want prompt tips.** The subject is the system around the model.

**Yes if you run agents daily** and you're tired of confident PRs that pass every check
and solve a problem you didn't have.

**Yes if you own a team** and need an adoption decision you can defend with numbers.
Track D is written for you and reads standalone.

## Pick your entry point

### 🔧 Developer — writing code today

You have a plan or a well-understood fix and you're about to write code.

Start at **[B3 · Plan → code](docs/CURRICULUM.md#b3--plan--code-)**, then
**[B4 · Code → review](docs/CURRICULUM.md#b4--code--review-)**. Back up to
**[A3](docs/CURRICULUM.md#a3--context-is-a-budget-not-a-container-)** when sessions start
degrading, and **[C3](docs/CURRICULUM.md#c3--enforcing-architecture-and-taste-)** when you
are tired of repeating the same review comment.

Mirrors the `implement` / `test-driven-development` / `review-code` /
`debug-systematically` / `engineering-standards` entry point in the plugin.

### 🧭 Engineer — owns a feature end to end

You own the work from "someone described an idea" to "it shipped."

Start at **[B1 · Idea → spec](units/b1-idea-to-spec/)** — the reference unit, written to
full depth — and follow the spine through B5. Then Track C, which is what makes the spine
survive a real repo.

Mirrors the `spec-from-idea` / `plan-from-spec` / `domain-modeling` / `grill-me` /
`finish-branch` / `handoff` entry point in the plugin.

**These two are the course.** Architecture is not a third track: it arrives inside the
engineer's arc, where it belongs — `codebase-architecture` in B2 before code exists and
in B4 after, then C1–C3 where "follow our standards" becomes a check that blocks a PR.

### 🏛️ Leading a team (annex)

Different reader, different shape, so it sits outside the main arc:
**[Track D3–D4](docs/CURRICULUM.md#track-d--production-and-the-organisation)** — harness
templates per topology, the metrics worth reporting, what not to automate, and why a
rollout plan with no stop-loss is an act of faith.

### 🔬 Research and ML systems (annex)

**[Track E](tracks/ml-systems/)** — what breaks when verification is slow, expensive,
statistical, and only knowable in production.

### 🧐 You don't believe any of it

Start at **[C4 · Making the spec computational](docs/CURRICULUM.md#c4--making-the-spec-computational-)**
and run [`tools/ablation.py`](tools/ablation.py) against your own repo. It will happily
tell you your harness does nothing. That result is publishable here.

---

## What's different about it

**The workflow is installable, not described.** Sixteen skills, two commands, and
you're running the spine. See [`docs/SKILLS-MAP.md`](docs/SKILLS-MAP.md) for how every
skill maps to a unit — and for the five capabilities the curriculum revealed the plugin
is missing.

```bash
claude plugin marketplace add girijesh-ai/spec-driven-engineering
claude plugin install spec-driven-engineering@spec-driven-engineering-dev
```

**One real feature runs through the whole thing.** You pick a repo and a feature at the
start of Track B and ship it across Tracks B and C — B0 onboards the agent to the repo,
B1 specs it, B3 builds it, B5 lands it, C1 audits the harness that carried it. You finish
holding working code plus the harness that produced it, not a folder of analysis.

**It is a superset of Stanford CS146S Fall 2025, and that's a gate rather than a
claim.** [`cs146s.map.json`](cs146s.map.json) maps all 22 of their topics;
[`tools/check_coverage.py`](tools/check_coverage.py) fails the build on any Fall 2025
topic marked omitted or unverified. It holds. Fall 2026's announced 10-week syllabus
is a separate, deliberately weaker claim — overlaps substantially, 11 of 30 topics
genuinely open — stated as a downgrade rather than rounded up to superset. See
[`docs/CS146S-COVERAGE.md`](docs/CS146S-COVERAGE.md) for both, and exactly which 11.

**Nothing ships without an ablation.** Authors run one before publishing a unit;
learners run one before advancing. Bootstrap confidence intervals, and null results get
published. A unit whose harness did nothing is a finding — publishing it is why anyone
should believe the units where the harness did something.

**Obsolescence is stated per unit.** Half of what any harness course teaches is a
heuristic engineered around a current model failure. Every unit ends with *what makes
this obsolete*, so you learn the diagnosis rather than memorising the patch. B1's answer
is unusual: nothing does, and the spec gets *more* load-bearing as models improve.

**It's built to outlive its own dependencies.** The plugin is at v1 and will grow. Units
declare *capabilities*, not skill names; [`skills.lock.json`](skills.lock.json) is the
single place a capability binds to a skill; and
[`tools/check_skills_map.py`](tools/check_skills_map.py) fails loudly on a rename and
reports — as information, not failure — every plugin skill the course hasn't caught up
with yet. See [`docs/PLUGIN-CONTRACT.md`](docs/PLUGIN-CONTRACT.md).

**We audit our CS146S coverage rather than asserting it.**
[`docs/CS146S-COVERAGE.md`](docs/CS146S-COVERAGE.md) goes week by week and marks each
one covered, deepened, or deliberately skipped with a reason. Two units exist because
that audit found real gaps.

**The repo is its own worked example.** [`AGENTS.md`](AGENTS.md) is a map under 120
lines, `docs/` is the system of record, and CI enforces unit shape and link integrity.
If we can't harness a documentation repo, don't take our advice on harnessing yours.

## Layout

```
agentic-software-engineering/
├── AGENTS.md                 # this repo's own harness: a map, not a manual
├── docs/
│   ├── COURSE-SPEC.md        # Success Criteria & Evals — the contract
│   ├── CURRICULUM.md         # 4 tracks, 19 units, capstone
│   ├── SKILLS-MAP.md         # the 16 skills → units, plus the plugin's gap analysis
│   ├── PLUGIN-CONTRACT.md    # how the course survives the plugin evolving
│   ├── CS146S-COVERAGE.md    # superset conformance, gated by tools/check_coverage.py
│   ├── ECOSYSTEM-MAP.md      # what to learn and borrow from the trending skills repos
│   ├── ARCHITECTURE-AUDIT.md # the adversarial audit, findings still open
│   └── POSITIONING.md        # why this course and not the two that exist
├── units/
│   └── b1-idea-to-spec/      # reference unit, sets the depth bar
├── skills.lock.json          # capability → skill bindings, with a version pin
├── tools/
│   ├── spec_lint.py          # the behaviour harness, made computational
│   ├── check_skills_map.py   # drift sensor for the course/plugin boundary
│   └── ablation.py           # the measurement spine
├── templates/                # rollout plan, spec, ablation report
└── tracks/
    └── ml-systems/           # Track E — 13 modules, own spec and reference module
```

## Track E — ML systems

Everything in Track C assumes tests are boolean, fast and deterministic. In ML systems
none of that holds, and the published literature says so — Anthropic explicitly names
generalisation beyond web development as future work.

[`tracks/ml-systems/`](tracks/ml-systems/) is that generalisation: thirteen modules on
building sensors when the sensor returns a float, after four minutes, differently every
run. Optional, and only after Tracks A–C.

## Prerequisites

A coding agent CLI you can point at a real repo with file-edit and command-execution
permissions. Python 3.11+ for the tooling (standard library only — a measurement tool
that needs its own environment setup is a measurement tool nobody runs). Git. A
codebase of your own; the labs are far more useful against your code than a toy.

## Contributing

Most valuable contribution: **a results file that contradicts us.** Run a unit's
ablation, find the harness did nothing, open a PR with the JSON. That is the course
working, not the course failing.

Then: a lab that breaks on a stack we didn't test. Then: a unit written to B1's depth,
with real numbers.

Please don't send links without a lab attached, or "we should also cover X" without the
measurement showing X matters.

## Prior art, credited properly

- **Stanford CS146S**, *The Modern Software Developer* (Mihail Eric) — the survey this
  course assumes and then goes past.
- **walkinglabs/learn-harness-engineering** — the general harness course we deliberately
  don't duplicate. Read it first if you're new.
- **OpenAI** — *Harness engineering: leveraging Codex in an agent-first world*.
- **Anthropic** — *Effective harnesses for long-running agents*; *Building effective
  agents*; *Demystifying evals for AI agents*.
- **Birgitta Böckeler / Thoughtworks** — *Harness engineering for coding agent users*.
  The guides/sensors vocabulary used throughout is hers, as is the observation the
  course is built on.
- **LangChain** — *Improving Deep Agents with harness engineering*; *The Anatomy of an
  Agent Harness*.
- **Mitchell Hashimoto** — the original framing, and the Ghostty `AGENTS.md` where every
  line traces to a specific agent mistake.
- **HumanLayer** — *12-Factor Agents*; *Skill Issue*.
- **Geoffrey Huntley** — the Ralph loop.

Full source map in [`docs/POSITIONING.md`](docs/POSITIONING.md) and
[`tracks/ml-systems/docs/POSITIONING.md`](tracks/ml-systems/docs/POSITIONING.md).

## License

MIT for code. CC BY 4.0 for course content.
