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
