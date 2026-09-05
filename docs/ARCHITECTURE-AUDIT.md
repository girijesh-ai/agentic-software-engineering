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
