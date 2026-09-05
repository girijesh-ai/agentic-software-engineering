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
