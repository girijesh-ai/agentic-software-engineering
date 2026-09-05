# Positioning: why this course, and why it isn't the one that already exists

Read this before writing a single module. It is the argument for the course's shape.
If the argument stops being true, the course should change.

---

## 1. What the field settled on in 2026

The vocabulary moved in three phases:

| Phase | Question it answered | Lever |
|---|---|---|
| Prompt engineering (2023–24) | How do I word this? | One call |
| Context engineering (2024–25) | What does the model see? | The window |
| **Harness engineering (2026)** | What system does the model operate inside? | The environment |

Mitchell Hashimoto put the term into circulation on 5 Feb 2026 in *My AI Adoption
Journey*, with a definition small enough to hold in your head: any time an agent
makes a mistake, engineer a solution so it never makes that mistake again. Six days
later OpenAI's Ryan Lopopolo published *Harness engineering: leveraging Codex in an
agent-first world*, which gave the discipline its field report: ~1M lines of code,
~1,500 merged PRs, 5 months, 3 engineers growing to 7, and **zero lines of
human-written code**. Their framing — humans steer, agents execute — is the
canonical citation.

The load-bearing claims from that post, all of which this course teaches:

- **Give the agent a map, not a manual.** A monolithic `AGENTS.md` fails four ways:
  it crowds out the task, it makes everything "important" so nothing is, it rots
  instantly, and it can't be mechanically checked. Theirs is ~100 lines and points
  into a structured `docs/` tree that is the system of record.
- **What the agent can't see doesn't exist.** Slack threads, Google Docs and
  tacit knowledge are illegible. Repository-local versioned artifacts are all it has.
- **Enforce invariants, not implementations.** Layered domains, validated dependency
  directions, custom linters whose *error messages carry remediation instructions*
  into agent context.
- **Throughput changes the merge philosophy.** Minimal blocking gates, short-lived
  PRs, corrections are cheap and waiting is expensive.
- **Entropy needs garbage collection.** Agents replicate existing patterns including
  the bad ones. Their team burned 20% of every week on manual slop cleanup until they
  encoded "golden principles" and ran recurring cleanup agents instead.

Anthropic's *Effective harnesses for long-running agents* (Nov 2025) supplies the
session-lifecycle half: an **initializer agent** that writes `init.sh`, a progress
log and a JSON feature list, then **coding agents** that each pick one feature, verify
it end-to-end, and leave a clean state. Their two named failure modes — the agent
one-shotting the app until it runs out of context mid-feature, and a later agent
looking around, seeing progress, and declaring the job done — are the two failures
every learner will reproduce in Module 00.

Böckeler's *Harness engineering for coding agent users* (Thoughtworks, Apr 2026)
supplies the cleanest mental model, and this course adopts its vocabulary wholesale:

- **Guides** (feedforward) steer before the agent acts. **Sensors** (feedback)
  observe after and let it self-correct. Feedback-only means an agent that repeats
  mistakes; feedforward-only means one that never learns whether its rules worked.
- **Computational** controls are deterministic, milliseconds, reliable.
  **Inferential** controls are semantic, slow, expensive, non-deterministic.
- Three regulation categories: **maintainability**, **architecture fitness**,
  **behaviour**. The first is easy — we have decades of tooling. The last is the
  elephant in the room.
- **Harnessability / ambient affordances**: not every codebase can be harnessed
  equally. The harness is most needed exactly where it is hardest to build.

LangChain's *Improving Deep Agents with harness engineering* supplies the proof that
this is a lever and not a vibe: **harness-only changes, model held fixed at
gpt-5.2-codex, moved deepagents-cli from 52.8 to 66.5 on Terminal-Bench 2.0** — top
30 to top 5. No model swap. The winning changes were build-verify loops, middleware
that injects directory maps and time-budget warnings, and loop-detection that nudges
an agent out of doom loops after N edits to the same file.

That is the state of the art. It is well documented and freely available.

---

## 2. The two things this course is measured against

### Stanford CS146S — *The Modern Software Developer*

Mihail Eric, Fall 2025, ten weeks, publicly available materials and assignments.
The Fall 2026 edition advertises MCP, agent skills, spec-driven development, loop
engineering and the software factory. Fall 2025's spine ran: coding-LLM internals →
the AI IDE and sync/async agents → coding-agent patterns and `CLAUDE.md` → the modern
terminal → testing and security → AI-augmented code review → automated UI building →
post-deployment and AI-native operations.

**What it does that we should keep.** Guest practitioners. The four context-window
failure modes (poisoning, distraction, confusion, clash). The semi-async zone —
avoid delegating tasks that take 30 seconds to 5 minutes, because that duration
shatters flow without buying parallelism. The Semgrep numbers on AI security
scanning: 82–86% false positives, and identical scans returning 3, 6 and 11 bugs on
successive runs. The code-review hierarchy that puts *mental alignment* at the base
of the pyramid, below bug-finding.

**What it does that we should not copy.** It is a survey. It is graded on a final
project weighted at 80%, which is where the actual learning lives, and the lecture
sequence is optimised for enrolled undergraduates with deadlines, not for a working
engineer studying at night. Its centre of gravity is web/UI. It has essentially
nothing on ML systems, and nothing at all for the person who has to roll this out
across a team.

### walkinglabs/learn-harness-engineering — ~9.6k stars, ~1k forks, 15 languages

**This is the finding that should change your plan.** An open-source, project-based,
12-lecture / 6-project harness engineering course already exists, is MIT licensed, is
translated into fifteen languages, has a VitePress site, a PDF build pipeline, a
`harness-creator` skill and an `audit-harness.sh` tool. It cites exactly the sources
above. Its five-subsystem model — instructions, state, verification, scope, session
lifecycle — is good. Its lecture titles are good. Its capstone is an Electron
personal-knowledge-base desktop app in TypeScript.

Shipping "CS146S plus harness engineering" as a general course means shipping the
second-best version of a repo with a 9.6k-star head start, a translation programme,
and the awesome-list that feeds it. Don't.

---

## 3. Where the hole actually is

Three gaps, and they are the same shape as one specific author's job.

### Gap A — the ML wedge (the main one)

Every published harness — OpenAI's, Anthropic's, LangChain's, walkinglabs' — assumes
**software engineering verification**: a test suite that is boolean, deterministic,
and returns in seconds. Anthropic's own post says so explicitly, calling the demo
"optimized for full-stack web app development" and naming generalisation to other
fields as future work.

ML breaks all three assumptions:

| Assumption | Holds in SWE | In ML systems |
|---|---|---|
| Verification is boolean | `pytest` is green or red | AUC 0.834 vs 0.831 — is that a pass? |
| Verification is fast | milliseconds to seconds | minutes to hours, sometimes days |
| Verification is cheap | free | GPU-hours, per-run dollars |
| Verification is deterministic | mostly | seeds, non-determinism, data drift |
| The artifact is legible | source files | notebooks, weights, datasets, experiment logs |
| "Correct" is knowable now | tests encode it | only visible in production, weeks later |

The research community has already noticed. Meta's Ranking Engineer Agent runs
multi-day ML pipeline automation with hibernate-and-wake checkpointing so 6-hour
tasks survive interruption. MLE-Dojo builds a gym over 200+ Kaggle challenges for
iterative MLE workflows. SandMLE attacks the cost problem head-on by generating
synthetic micro-scale sandboxes (50–200 samples) that cut verification to under 15
seconds so on-policy rollouts become feasible at all. There is active academic work
on whether MLE agents can even hold fairness constraints.

There is a body of research. **There is no practitioner curriculum.** Nobody has
written down how a working ML team builds guides and sensors when the sensor costs
$40 and takes two hours and returns a float.

### Gap B — the leadership layer

CS146S teaches students. learn-harness-engineering teaches an individual developer
with one repo. Neither teaches the person who has to answer: which of my twelve
services gets a harness first, what do I put in a harness template, what do I tell my
staff engineer who thinks this is ceremony, what do I report upward, and what do I
measure so I know it worked.

Böckeler already sketched the artifact — **harness templates** per service topology,
justified by Ashby's Law of Requisite Variety: a regulator needs at least as much
variety as the system it governs and can only regulate what it has a model of, so
committing to a topology is a deliberate variety-reduction move that makes a
comprehensive harness achievable. Nobody has turned that into a rollout playbook.

### Gap C — measurement as pedagogy

Both incumbents teach harness patterns and then assert they work. LangChain proved
the lever exists with an ablation. Anthropic quantified how much infrastructure noise
alone moves agentic coding benchmarks. But no course makes the learner *run the
ablation themselves* as the price of admission to the next module.

That inversion is cheap to implement and very hard to copy, because it forces every
module to survive contact with a number.

---

## 4. The thesis

> **Harness Engineering for ML Systems.** A Python-native, measurement-first course
> for engineers and engineering leaders who have to make coding agents reliable in
> codebases where verification is slow, expensive, statistical, and sometimes only
> knowable in production.

Three commitments that follow from it:

1. **Python and ML repos throughout.** Not Electron. Not a TypeScript CRUD app.
   Training pipelines, feature stores, inference services, eval suites.
2. **No claim ships without an ablation.** Every module has a with-harness /
   without-harness comparison and a committed results file. Authors run it before
   publishing; learners run it before advancing. `tools/ablation.py` is the spine.
3. **The spec is the behaviour harness.** Böckeler's sharpest observation is that no
   sensor — computational or inferential — reliably catches well-formed code that
   solves the wrong problem. The only instrument that catches it is a written
   statement of what the right problem was. That is what
   [`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
   already is, and it becomes this course's behaviour harness rather than a
   dependency to be explained.

---

## 5. Honest risks

- **The incumbent may extend downward into ML.** Mitigation: depth. A translated
  beginner course is unlikely to build the tiered-verification and cost-budget
  material, because that requires having actually run ML pipelines under an agent.
- **The ML wedge shrinks the audience.** Accepted deliberately. A course that is the
  only one for 5% of engineers beats a course that is the fourth-best for all of them.
- **The tooling churns fast.** Mitigation: teach *guides / sensors / computational /
  inferential* as the invariant vocabulary, and confine tool specifics to clearly
  marked, dated appendices.
- **Half the harness may be obsolete in eighteen months.** LangChain says this out
  loud about their own loop-detection middleware: these are heuristics engineered
  around today's model failures and will become unnecessary as models improve. Teach
  the diagnosis, not the patch. Every module ends with "what makes this obsolete."
- **Author time.** Thirteen modules is a lot. Mitigation: the core six ship first
  (M00, M01, M03, M04, M05, M11) and are independently useful.

## Source map

Primary, in rough order of usefulness to an author:

- OpenAI — *Harness engineering: leveraging Codex in an agent-first world* (Feb 2026)
- Anthropic — *Effective harnesses for long-running agents* (Nov 2025)
- Anthropic — *Harness design for long-running application development*
- Böckeler / Thoughtworks — *Harness engineering for coding agent users* (Apr 2026)
- LangChain — *Improving Deep Agents with harness engineering*; *The Anatomy of an Agent Harness*
- HumanLayer — *Skill Issue: Harness Engineering for Coding Agents*; *12-Factor Agents*
- Anthropic — *Demystifying evals for AI agents*; *Writing effective tools for agents*
- Hashimoto — *My AI Adoption Journey* (Feb 2026), plus the Ghostty `AGENTS.md`
- Huntley — *Ralph Wiggum as a Software Engineer* (the minimal loop)
- Stanford CS146S materials and assignment repo
- `walkinglabs/awesome-harness-engineering` — the standing landscape map
- MLE-Dojo, SandMLE, Meta REA — the ML-agent research frontier
