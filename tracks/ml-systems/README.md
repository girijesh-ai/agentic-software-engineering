# Harness Engineering for ML Systems

**Every published harness assumes your tests are boolean, fast and deterministic.
Yours return a float, in four minutes, and it's different every run.**

This is a Python-native, measurement-first course on making coding agents reliable in
codebases where verification is slow, expensive, statistical, and sometimes only
knowable in production. Thirteen modules, every one gated on a lab, every one backed
by an ablation with a confidence interval.

> **Status: v0, spec complete, content in progress.** The curriculum, the course spec
> and the measurement tooling are done and usable. One reference module (M04) is
> written to the target depth. The rest is the build.
> Start at [`docs/COURSE-SPEC.md`](docs/COURSE-SPEC.md).

---

## Is this the right course for you?

**Probably not, if you're new to coding agents.** Start with
[walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering)
— it's excellent, it's free, and it covers the fundamentals better than a second
introduction would. Come back when you've got a harness working on a normal codebase
and you're hitting the wall on your ML repos.

**Probably not, if you want tool tips.** There are no prompt tricks here. The subject
is the system around the model.

**Yes, if you run agents daily on Python ML code** and you're tired of the agent that
declares a training script working because it exited 0, tunes a threshold until the
number moves, or burns two GPU-hours discovering the fixture had leakage.

**Yes, if you own a team** doing AI/ML delivery and need an adoption decision you can
defend with numbers rather than enthusiasm. Module 11 is written for you specifically,
and it's the one part of this you can read standalone.

## Pick your entry point

### 🔬 You want your agents to stop lying to you

Start at **[M00 — What is your harness actually worth?](docs/CURRICULUM.md#m00--what-is-your-harness-actually-worth-)**

Not a lecture. You instrument yourself first: five real tasks from your own repo,
three repeats each, with and without your current harness. Most people are surprised
by the number in one direction or the other, and either surprise is worth having
before you read another word of theory.

Then **[M04](modules/m04-verification-when-truth-is-statistical/)** and
**[M05](docs/CURRICULUM.md#m05--when-the-sensor-costs-40-and-takes-two-hours-)** — the
two modules that don't exist anywhere else.

### 🏛️ You have to decide whether your team does this

Read **[`docs/POSITIONING.md`](docs/POSITIONING.md)** for the evidence base — including
the one experiment that shows harness changes alone, model held fixed, moving a coding
agent from rank 30 to top 5 on Terminal-Bench 2.0.

Then **[M11 — Rolling this out on a team](docs/CURRICULUM.md#m11--rolling-this-out-on-a-team-️)**:
harness templates per service topology, the four metrics worth reporting, what you
should explicitly not automate, and why a rollout plan without a stop-loss condition
is an act of faith.

### 🧭 You're evaluating whether the course is any good

Read [M04](modules/m04-verification-when-truth-is-statistical/) end to end. It's the
reference module and every other module has to hit its depth. If it doesn't teach you
something you didn't know, the rest won't either.

---

## What's different about it

**Python and ML repos, throughout.** Training pipelines, feature stores, inference
services, eval suites. Not an Electron app.

**Nothing ships without an ablation.** [`tools/ablation.py`](tools/ablation.py) is the
spine of the course, not an appendix. Authors run it before publishing a module;
learners run it before advancing. It reports a bootstrap confidence interval and will
happily tell you your harness did nothing — which is the point. Null and negative
results are published.

**The spec is treated as the behaviour harness.** No sensor, computational or
inferential, reliably catches well-formed code that solves the wrong problem. The only
instrument that catches it is a written statement of what the right problem was. The
16 skills in
[`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
are that instrument, and M03 wires them in as the behaviour harness rather than
teaching them as a separate topic.

**Obsolescence is stated, not hidden.** Half of what any harness course teaches today
is a heuristic engineered around a current model failure. LangChain says so about
their own loop-detection middleware. Every module here ends with *what makes this
obsolete* — so you learn the diagnosis rather than memorising the patch.

**The repo is its own worked example.** [`AGENTS.md`](AGENTS.md) is under 120 lines and
acts as a map. `tools/audit.sh` enforces module shape, link integrity and staleness in
CI. If we can't harness a documentation repo, you shouldn't take our advice on
harnessing a training pipeline.

## Layout

```
harness-engineering-for-ml/
├── AGENTS.md                  # this repo's own harness: a map, not a manual
├── docs/
│   ├── COURSE-SPEC.md         # Success Criteria & Evals — the contract
│   ├── CURRICULUM.md          # 13 modules
│   └── POSITIONING.md         # research synthesis + why this isn't the incumbent
├── modules/
│   └── m04-.../               # reference module, sets the depth bar
├── templates/                 # rollout plan, harness spec, ablation report
└── tools/
    └── ablation.py            # the measurement spine (stdlib only)
```

## Prerequisites

A coding agent CLI you can point at a real repo with file-edit and command-execution
permissions. Python 3.11+. An ML codebase of your own — the labs are far more useful
against your code than against a toy. Comfort with pytest, git, and reading a stack
trace. No GPU required; the micro-fixture approach in M05 is designed around not
having one.

## Contributing

The most valuable contribution is **a results file that contradicts us**. If you run a
module's ablation and the harness does nothing, open a PR with the JSON. That is not
an embarrassment to the course, it is the course working.

Second most valuable: a lab that fails on a stack we didn't test. Third: a module
written to M04's depth, with real numbers.

Please don't send: additional links without a lab attached, or "we should also
cover X" without the ablation that shows X matters.

## Prior art, credited properly

This course stands on published work and cites it inline rather than reheating it:

- **OpenAI** — *Harness engineering: leveraging Codex in an agent-first world*, the
  field report that named the discipline.
- **Anthropic** — *Effective harnesses for long-running agents*, the session-lifecycle
  half, which explicitly names generalisation beyond web development as future work.
  This course is one attempt at that generalisation.
- **Birgitta Böckeler / Thoughtworks** — *Harness engineering for coding agent users*.
  The guides/sensors and computational/inferential vocabulary used throughout is hers.
- **LangChain** — *Improving Deep Agents with harness engineering*, the evidence that
  the harness is the lever.
- **Mitchell Hashimoto** — the original framing: when an agent makes a mistake,
  engineer it so it can't make that mistake again.
- **Stanford CS146S**, *The Modern Software Developer* (Mihail Eric) — the survey this
  course assumes you've read.
- **walkinglabs/learn-harness-engineering** — the general-purpose course this one
  deliberately does not duplicate. Read it first.

Full source map in [`docs/POSITIONING.md`](docs/POSITIONING.md).

## License

MIT for code. CC BY 4.0 for course content.
